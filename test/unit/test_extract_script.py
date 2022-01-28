import pytest

from git_rex import NoCodeFound, ScriptError, UnterminatedCodeBlock, extract_script


def test_no_code_block():
    with pytest.raises(NoCodeFound):
        extract_script("Some commit\n\nNo code")


def test_unterminated_code_block():
    with pytest.raises(UnterminatedCodeBlock):
        extract_script("Some commit\n\n```bash\ndo a thing")


def test_no_bash_label():
    with pytest.raises(ScriptError) as ex:
        extract_script("Some commit\n\n```\ndo a thing\n```")

    assert ex.value.lineno == 3
    assert ex.value.message == "Code sections must specify bash syntax"


def test_label_on_closing_ticks():
    with pytest.raises(ScriptError) as ex:
        extract_script("Some commit\n\n```bash\ndo a thing\n```bash")

    assert ex.value.lineno == 5
    assert ex.value.message == "Unexpected start of new code section"
