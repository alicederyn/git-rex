import pytest

from git_rex.messages import (
    NoCodeFound,
    UnexpectedCodeBlock,
    UnsupportedCodeSyntax,
    UnterminatedCodeBlock,
    cleanup_message,
)


def test_removes_comments_only_outside_of_code_blocks():
    message = "My commit\n\n# A comment\n```bash\n# do a thing\ndo_thing\n```\n"
    cleaned_message = cleanup_message(message)
    assert cleaned_message == "My commit\n\n```bash\n# do a thing\ndo_thing\n```\n"


def test_no_code_block():
    with pytest.raises(NoCodeFound):
        cleanup_message("Some commit\n\nNo code")


def test_unterminated_code_block():
    with pytest.raises(UnterminatedCodeBlock):
        cleanup_message("Some commit\n\n```bash\ndo a thing")


def test_no_bash_label():
    with pytest.raises(UnsupportedCodeSyntax) as ex:
        cleanup_message("Some commit\n\n```\ndo a thing\n```")

    assert ex.value.lineno == 3


def test_label_on_closing_ticks():
    with pytest.raises(UnexpectedCodeBlock) as ex:
        cleanup_message("Some commit\n\n```bash\ndo a thing\n```bash")

    assert ex.value.lineno == 5


def test_only_blank_lines_and_comments_in_code():
    with pytest.raises(NoCodeFound):
        cleanup_message("Some commit\n\n```bash\n\n# a comment\n\n```")
