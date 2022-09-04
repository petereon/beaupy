from ward import test

from beaupy._internals import _render_prompt


@test("Test that prompt is rendered properly")
def _():
    result = _render_prompt(False, ["a", "b"], "Test prompt", 1, None)
    assert result == "Test prompt\n> a[black on white]b[/black on white] "


@test("Test that prompt is rendered with error")
def _():
    result = _render_prompt(False, ["a", "b"], "Test prompt", 1, "Test Error")
    assert result == "Test prompt\n> a[black on white]b[/black on white] \n[red]Error:[/red] Test Error"
