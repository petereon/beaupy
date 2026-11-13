import os
import select
import sys
import time

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


def test_prompt_prints_typed_text(capsys):
    feed('h', 'i', Keys.ENTER)
    assert cli.main(['prompt', 'name?']) == 0
    assert capsys.readouterr().out == 'hi\n'


def test_escape_exits_130(capsys):
    feed(Keys.ESC)
    assert cli.main(['select', 'a', 'b']) == cli.CANCELLED
    assert capsys.readouterr().out == ''


@pytest.mark.skipif(sys.platform == 'win32', reason='needs a pty')
def test_real_terminal_end_to_end():
    """Runs `python -m beaupy` in a pty: UI goes to the terminal (stderr), only the answer to stdout."""
    import pty

    out_r, out_w = os.pipe()
    pid, fd = pty.fork()
    if pid == 0:  # pragma: no cover - child process
        os.dup2(out_w, 1)
        os.execv(sys.executable, [sys.executable, '-m', 'beaupy', 'select', 'a', 'b', 'c'])
    os.close(out_w)

    def drain(seconds: float, until: bytes = b'') -> bytes:
        # the pty buffer is small: an undrained master blocks the app's redraw writes
        seen, deadline = b'', time.time() + seconds
        while (not until or until not in seen) and time.time() < deadline:
            if select.select([fd], [], [], 0.1)[0]:
                seen += os.read(fd, 4096)
        return seen

    try:
        assert b'confirm' in drain(10, until=b'confirm')  # footer drawn => raw mode imminent; yakh drops keys typed before it
        drain(0.3)
        os.write(fd, b'\x1b[B')
        drain(0.3)
        os.write(fd, b'\r')
        for _ in range(100):
            done, status = os.waitpid(pid, os.WNOHANG)
            if done:
                break
            drain(0.1)
        else:
            os.kill(pid, 9)
            os.waitpid(pid, 0)
            pytest.fail('CLI did not exit')
        assert os.waitstatus_to_exitcode(status) == 0
        assert os.read(out_r, 100) == b'b\n'
    finally:
        os.close(out_r)
        os.close(fd)
