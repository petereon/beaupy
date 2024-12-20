import pytest
from beaupy._internals import _render_prompt, Abort
from yakh.key import Key
from questo import prompt as qprompt


def test_prompt_is_rendered_properly():
    result = _render_prompt(False, qprompt.PromptState(value='ab', title='Test prompt', cursor_position=1))
    assert result == "Test prompt\n> a[black on white]b[/black on white] \n\n([bold]enter[/bold] to confirm)"


def test_prompt_is_rendered_with_error():
    result = _render_prompt(False, qprompt.PromptState(value='ab', title='Test prompt', error='Test Error', cursor_position=1))
    assert result == "Test prompt\n> a[black on white]b[/black on white] \n\n([bold]enter[/bold] to confirm)\n[red]Error:[/red] Test Error"


def test_abort_prints_printable_key_correctly():
    key = Key("test", (1, 2, 3), is_printable=True)
    with pytest.raises(Abort) as excinfo:
        raise Abort(key)
    assert str(excinfo.value) == "Aborted by user with key test"


def test_abort_prints_non_printable_key_correctly():
    key = Key("test", (1, 2, 3), is_printable=False)
    with pytest.raises(Abort) as excinfo:
        raise Abort(key)
    assert str(excinfo.value) == "Aborted by user with key (1, 2, 3)"
