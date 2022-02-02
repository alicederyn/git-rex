import os
import sys
from logging import getLogger
from optparse import OptionParser, Values
from subprocess import DEVNULL, call

from . import git
from .log_config import configure_logging
from .messages import (
    NoCodeFound,
    UnexpectedCodeBlock,
    UnsupportedCodeSyntax,
    UnterminatedCodeBlock,
    extract_scripts,
)

TEMP_REX_SCRIPT = ".git/REX_SCRIPT"
log = getLogger(__name__)


class UnstagedChanges(Exception):
    pass


class UserCodeError(Exception):
    def __init__(self, resultcode: int):
        self.resultcode = resultcode


def reexecute(commit: git.Commit) -> None:
    if not git.is_clean_repo():
        raise UnstagedChanges()
    scripts = extract_scripts(commit.message)
    try:
        for script in scripts:
            with open(TEMP_REX_SCRIPT, "w") as f:
                print("set -eo pipefail", file=f)
                print("\n".join(script), file=f)
            resultcode = call(["bash", TEMP_REX_SCRIPT], stdin=DEVNULL)
            if resultcode != 0:
                raise UserCodeError(resultcode)
    finally:
        os.remove(TEMP_REX_SCRIPT)
    git.add_all()
    git.commit_with_meta_from(commit)


def parser() -> OptionParser:
    usage = "Usage: %prog commit"
    description = "Reapplies a commit by running commands from the commit message"

    parser = OptionParser(usage=usage, description=description)
    return parser


def parse_options() -> Values:
    (options, args) = parser().parse_args()
    if len(args) > 1:
        log.fatal(
            "Too many commits specified: %s", " ".join(f"'{arg}'" for arg in args)
        )
        sys.exit(64)
    options.commit = git.Commit(args[0]) if args else None
    return options


def main() -> None:
    configure_logging()
    options = parse_options()
    if not options.commit:
        parser().print_help()
        sys.exit(64)
    try:
        os.chdir(git.top_level())
        reexecute(commit=options.commit)
    except UnstagedChanges:
        log.error("cannot reexecute: You have unstaged changes.")
        log.error("Please commit or stash them.")
        sys.exit(64)
    except NoCodeFound:
        log.fatal("No code section found in commit")
        sys.exit(64)
    except UnsupportedCodeSyntax as e:
        log.fatal("%d: Code sections must specify bash syntax", e.lineno)
        sys.exit(64)
    except UnexpectedCodeBlock as e:
        log.fatal("%d: Unexpected start of new code section", e.lineno)
        sys.exit(64)
    except UnterminatedCodeBlock:
        log.fatal("Code block not terminated in commit message")
        sys.exit(64)
    except git.GitFailure as e:
        log.fatal("%s", e.message)
        sys.exit(64)
    except UserCodeError as e:
        sys.exit(e.resultcode)
