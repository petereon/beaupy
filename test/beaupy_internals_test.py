from ward import test

from beaupy._internals import _render_prompt, Abort
from yakh.key import Key


@test("Test that prompt is rendered properly")
def _():
    result = _render_prompt(False, ["a", "b"], "Test prompt", 1, None)
    assert result == "Test prompt\n> a[black on white]b[/black on white] \n\n(Confirm with [bold]enter[/bold])"


@test("Test that prompt is rendered with error")
def _():
    result = _render_prompt(False, ["a", "b"], "Test prompt", 1, "Test Error")
    assert (
        result == "Test prompt\n> a[black on white]b[/black on white] \n\n(Confirm with [bold]enter[/bold])\n[red]Error:[/red] Test Error"
    )

@test("Test that abort prints printable key correctly")
def _():
    key = Key("test", (1,2,3), is_printable=True)
    try:
        raise Abort(key)
    except Abort as e:
        assert str(e) == "Aborted by user with key test"

@test("Test that abort prints non-printable key correctly")
def _():
    key = Key("test", (1,2,3), is_printable=False)
    try:
        raise Abort(key)
    except Abort as e:
        assert str(e) == "Aborted by user with key (1, 2, 3)"