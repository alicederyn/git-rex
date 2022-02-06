import os
import sys
from argparse import ArgumentParser
from logging import getLogger

from . import git
from .bash import UserCodeError
from .editor import EditorError, EditorUnset, spawn_editor
from .log_config import configure_logging
from .messages import (
    NoExecutableCodeFound,
    NoScriptBlockFound,
    UnexpectedCodeBlock,
    UnsupportedCodeSyntax,
    UnterminatedCodeBlock,
    cleanup_message,
    extract_scripts,
)

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


class InvocationError(Exception):
    pass


class UnstagedChanges(Exception):
    pass


def run_scripts(commit_message: str) -> None:
    for script in extract_scripts(commit_message):
        script.execute()


def parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Reapplies a commit by running commands from the commit message",
        allow_abbrev=False,
    )
    parser.add_argument(
        "commit", nargs="?", type=git.Commit, help="commit to reexecute"
    )
    parser.add_argument(
        "-e", "--edit", action="store_true", help="Edit commit message before executing"
    )
    parser.add_argument(
        "-n",
        "--no-commit",
        action="store_true",
        help="Execute commands and stage changes, but do not commit them",
    )
    return parser


def rex() -> None:
    args = parser().parse_args()
    os.chdir(git.top_level())

    is_clean = git.no_unstaged_changes() if args.no_commit else git.is_clean_repo()
    if not is_clean:
        raise UnstagedChanges()

    if args.edit:
        """git rex --edit [commit]"""
        original_message = (
            args.commit.message if args.commit else DEFAULT_COMMIT_TEMPLATE
        )
        raw_edited_message = spawn_editor(
            original_message, filename=".git/COMMIT_EDITMSG"
        )
        commit_message = cleanup_message(raw_edited_message)
        run_scripts(commit_message)
        git.add_all()
        if args.no_commit:
            git.store_commit_message(commit_message)
        elif args.commit and args.commit.message == commit_message:
            git.commit_with_meta_from(args.commit)
        else:
            git.commit(commit_message)
    else:
        """git rex commit"""
        if not args.commit:
            raise InvocationError()
        run_scripts(args.commit.message)
        git.add_all()
        if args.no_commit:
            git.store_commit_message(args.commit.message)
        else:
            git.commit_with_meta_from(args.commit)


def main() -> None:
    configure_logging()
    try:
        rex()
    except InvocationError:
        parser().print_help()
        sys.exit(64)
    except UnstagedChanges:
        log.error("cannot reexecute: You have unstaged changes.")
        log.error("Please commit or stash them.")
        sys.exit(64)
    except NoScriptBlockFound:
        log.fatal("No code section found in commit")
        sys.exit(64)
    except NoExecutableCodeFound:
        log.fatal("Aborting commit as no code found to execute")
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
