import pytest
from yakh.key import Keys

from beaupy import __main__ as cli
from beaupy import _beaupy as b


def feed(*keys):
    steps = iter(keys)
    b.get_key = lambda: next(steps)


def test_select_prints_choice(capsys):
    feed(Keys.DOWN_ARROW, Keys.ENTER)
    assert cli.main(['select', 'a', 'b', 'c']) == 0
    assert capsys.readouterr().out == 'b\n'


def test_select_multiple_prints_one_per_line(capsys):
    feed(' ', Keys.DOWN_ARROW, Keys.DOWN_ARROW, ' ', Keys.ENTER)
    assert cli.main(['select-multiple', 'a', 'b', 'c']) == 0
    assert capsys.readouterr().out == 'a\nc\n'


def test_confirm_exit_code():
    feed(Keys.UP_ARROW, Keys.ENTER)
    assert cli.main(['confirm', 'ok?']) == 0
    feed(Keys.ENTER)  # default is No
    assert cli.main(['confirm', 'ok?']) == 1


def test_interrupt_exits_130(capsys):
    def interrupt():
        raise KeyboardInterrupt

    b.get_key = interrupt
    assert cli.main(['select', 'a', 'b']) == cli.CANCELLED
    assert capsys.readouterr().out == ''


def test_requires_command():
    with pytest.raises(SystemExit):
        cli.main([])
