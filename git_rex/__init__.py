import os
import sys
from logging import getLogger
from optparse import OptionParser, Values
from subprocess import DEVNULL, call
from typing import Optional

from . import git
from .editor import EditorError, EditorUnset, spawn_editor
from .log_config import configure_logging
from .messages import (
    NoCodeFound,
    UnexpectedCodeBlock,
    UnsupportedCodeSyntax,
    UnterminatedCodeBlock,
    cleanup_message,
    extract_scripts,
)

TEMP_REX_SCRIPT = ".git/REX_SCRIPT"
log = getLogger(__name__)

DEFAULT_COMMIT_TEMPLATE = """Automated commit created with git-rex

The following commands were executed:

# Enter your script here. It will be executed, and all files created
# or changed committed to your repository.
```bash

```

# Please enter the commit message for your changes. Lines starting
# with '#', except those in script sections, will be ignored, and an
# empty commit message, or one with no script commands to execute,
# aborts the commit.
"""


class UnstagedChanges(Exception):
    pass


class UserCodeError(Exception):
    def __init__(self, resultcode: int):
        self.resultcode = resultcode


def run_scripts(commit_message: str) -> None:
    scripts = extract_scripts(commit_message)
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


def reexecute_commit(commit: git.Commit, *, no_commit: bool) -> None:
    """git rex commit"""
    run_scripts(commit.message)
    git.add_all()
    if no_commit:
        git.store_commit_message(commit.message)
    else:
        git.commit_with_meta_from(commit)


def edit_commit(commit: Optional[git.Commit], *, no_commit: bool) -> None:
    """git rex --edit [commit]"""
    original_message = commit.message if commit else DEFAULT_COMMIT_TEMPLATE
    raw_edited_message = spawn_editor(original_message, filename=".git/COMMIT_EDITMSG")
    commit_message = cleanup_message(raw_edited_message)
    run_scripts(commit_message)
    git.add_all()
    if no_commit:
        git.store_commit_message(commit_message)
    else:
        git.commit(commit_message)


def parser() -> OptionParser:
    usage = "Usage: %prog [options] [commit]"
    description = "Reapplies a commit by running commands from the commit message"

    parser = OptionParser(usage=usage, description=description)
    parser.add_option(
        "-e", "--edit", action="store_true", help="Edit commit message before executing"
    )
    parser.add_option(
        "-n",
        "--no-commit",
        action="store_true",
        help="Execute commands and stage changes, but do not commit them",
    )
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
    try:
        os.chdir(git.top_level())

        is_clean = (
            git.no_unstaged_changes() if options.no_commit else git.is_clean_repo()
        )
        if not is_clean:
            raise UnstagedChanges()

        if options.edit:
            edit_commit(options.commit, no_commit=options.no_commit)
        else:
            if not options.commit:
                parser().print_help()
                sys.exit(64)
            reexecute_commit(options.commit, no_commit=options.no_commit)
    except UnstagedChanges:
        log.error("cannot reexecute: You have unstaged changes.")
        log.error("Please commit or stash them.")
        sys.exit(64)
    except NoCodeFound:
        if options.edit:
            log.fatal("Aborting commit as no code found to execute")
        else:
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
    except EditorUnset:
        log.error("Terminal is dumb, but EDITOR unset")
        sys.exit(64)
    except EditorError as e:
        log.error("There was a problem with the editor %s", e.editor_command)
        sys.exit(64)
    except git.GitFailure as e:
        log.fatal("%s", e.message)
        sys.exit(64)
    except UserCodeError as e:
        sys.exit(e.resultcode)
