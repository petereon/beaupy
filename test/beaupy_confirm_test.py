from unittest import mock

import click
from ward import raises, test

from beaupy._beaupy import Config, Live, confirm, warnings
import beaupy


@test("`confirm` with `Try test` as a question and defaults otherwise", tags=["v1", "confirm"])
def _():
    click.getchar = lambda: beaupy.key.ENTER
    Live.update = mock.MagicMock()
    res = confirm(question="Try test")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n  Yes\n[pink1]>[/pink1] No\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == False


@test("`confirm` with `Try test` as a question, `No` as a yes_text, `Yes` as a no_text and defaults otherwise", tags=["v1", "confirm"])
def _():
    click.getchar = lambda: beaupy.key.ENTER
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (N/Y) \n  No\n[pink1]>[/pink1] Yes\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == False


@test(
    "`confirm` with `Try test` as a question, `No` as a yes_text, `Yes` as a no_text and defaults otherwise, doing a step up to switch to yes",
    tags=["v1", "confirm"],
)
def _():
    steps = iter([beaupy.key.UP, beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (N/Y) \n  No\n[pink1]>[/pink1] Yes\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (N/Y) No\n[pink1]>[/pink1] No\n  Yes\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == True


@test("`confirm` with `Try test` as a question and yes as a default", tags=["v1", "confirm"])
def _():
    steps = iter([beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == True


@test("`confirm` with `Try test` as a question and yes as a default, going down to select no", tags=["v1", "confirm"])
def _():
    steps = iter([beaupy.key.DOWN, beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[pink1]>[/pink1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test("`confirm` with `Try test` as a question and yes as a default going up to select no", tags=["v1", "confirm"])
def _():
    steps = iter([beaupy.key.UP, beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[pink1]>[/pink1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `some long text ` as a cursor",
    tags=["v1", "confirm"],
)
def _():
    steps = iter([beaupy.key.UP, beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor="some long text")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]some long text[/pink1] Yes\n               No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(
            renderable="Try test (Y/N) No\n               Yes\n[pink1]some long text[/pink1] No\n\n(Confirm with [bold]enter[/bold])"
        ),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color",
    tags=["v1", "confirm"],
)
def _():
    steps = iter([beaupy.key.UP, beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color",
    tags=["v1", "confirm"],
)
def _():
    steps = iter([beaupy.key.UP, beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color, typing the `no` answer",
    tags=["v1", "confirm"],
)
def _():
    steps = iter(["n", "o", beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 3
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color, case sensitive typing the `no` answer",
    tags=["v1", "confirm"],
)
def _():
    steps = iter(
        [
            "n",
            "o",
            beaupy.key.ENTER,
            beaupy.key.BACKSPACE,
            beaupy.key.BACKSPACE,
            "N",
            "o",
            beaupy.key.ENTER,
        ]
    )

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(
        question="Try test",
        default_is_yes=True,
        cursor_style="bold orange1",
        has_to_match_case=True,
    )
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) \n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) N\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 8
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color and no char prompt",
    tags=["v1", "confirm"],
)
def _():
    steps = iter([beaupy.key.UP, beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", char_prompt=False, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test: \n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test: Yes\n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == True


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color and enter empty confirms",
    tags=["v1", "confirm"],
)
def _():
    steps = iter([beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", cursor_style="bold orange1", default_is_yes=True, enter_empty_confirms=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == True


@test("`confirm` with `Test` as a question and empty cursor style", tags=["v1", "confirm"])
def _():
    steps = iter([beaupy.key.ENTER])

    click.getchar = lambda: next(steps)
    warnings.warn = mock.MagicMock()
    confirm(question="Test", cursor_style="")

    warnings.warn.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")


@test("`confirm` with `Test` as a question with KeyboardInterrupt and raise_on_interrupt as False", tags=["v1", "confirm"])
def _():
    steps = iter([beaupy.key.CTRL_C])
    Config.raise_on_interrupt = False
    click.getchar = lambda: next(steps)
    res = confirm(question="Test", cursor_style="red")

    assert res == None


@test("`confirm` with `Test` as a question with KeyboardInterrupt and raise_on_interrupt as True", tags=["v1", "confirm"])
def _():
    steps = iter([beaupy.key.CTRL_C])
    Config.raise_on_interrupt = True
    click.getchar = lambda: next(steps)

    with raises(KeyboardInterrupt) as ex:
        confirm(question="Test", cursor_style="red")
    assert ex.raised.args[0] == beaupy.key.CTRL_C


@test("`confirm` with `Test` as a question, typing `N` and pressing `\\t`", tags=["v1", "confirm"])
def _():
    steps = iter(["N", "\t", beaupy.key.ENTER])
    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) N\n  Yes\n[red]>[/red] No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) No\n  Yes\n[red]>[/red] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert ret is False


@test("`confirm` with `Test` as a question, typing `Y`", tags=["v1", "confirm"])
def _():
    steps = iter(["Y", beaupy.key.ENTER])
    click.getchar = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) Y\n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert ret is True
