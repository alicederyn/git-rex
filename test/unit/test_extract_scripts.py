import pytest

from git_rex.messages import (
    NoCodeFound,
    UnexpectedCodeBlock,
    UnsupportedCodeSyntax,
    UnterminatedCodeBlock,
    extract_scripts,
)


def test_no_code_block():
    with pytest.raises(NoCodeFound):
        extract_scripts("Some commit\n\nNo code")


def test_unterminated_code_block():
    with pytest.raises(UnterminatedCodeBlock):
        extract_scripts("Some commit\n\n```bash\ndo a thing")


def test_no_bash_label():
    with pytest.raises(UnsupportedCodeSyntax) as ex:
        extract_scripts("Some commit\n\n```\ndo a thing\n```")

    assert ex.value.lineno == 3


def test_label_on_closing_ticks():
    with pytest.raises(UnexpectedCodeBlock) as ex:
        extract_scripts("Some commit\n\n```bash\ndo a thing\n```bash")

    assert ex.value.lineno == 5
