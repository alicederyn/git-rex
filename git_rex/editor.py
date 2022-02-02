import os
from shlex import quote
from subprocess import call

from .git import core_editor


class EditorUnset(Exception):
    pass


class EditorError(Exception):
    def __init__(self, editor_command, returncode):
        self.editor_command = editor_command
        self.returncode = returncode


def is_terminal_dumb() -> bool:
    # Copied from editor.c in git
    term = os.getenv("TERM")
    return not term or term == "dumb"


def editor_command() -> str:
    # Copied from editor.c in git
    editor = os.getenv("GIT_EDITOR")
    if not editor:
        editor = core_editor()
    if not editor and not is_terminal_dumb():
        editor = os.getenv("VISUAL")
    if not editor:
        editor = os.getenv("EDITOR")
    if not editor and is_terminal_dumb():
        raise EditorUnset()
    if not editor:
        editor = "vi"
    return editor


def spawn_editor(initial_text: str, *, filename: str) -> str:
    with open(filename, "w") as f:
        f.write(initial_text)
    edit_cmd = editor_command()
    returncode = call(f"{edit_cmd} {quote(filename)}", shell=True)
    if returncode != 0:
        raise EditorError(edit_cmd, returncode)
    with open(filename) as f:
        return f.read()
