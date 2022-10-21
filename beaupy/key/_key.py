from sys import platform

# Taken and adapted from https://github.com/magmax/python-readchar

LF = '\n'
CR = '\r'

SPACE = ' '
ESC = '\x1b'
TAB = '\t'

# CTRL
CTRL_A = '\x01'
CTRL_B = '\x02'

CTRL_E = '\x05'
CTRL_F = '\x06'
CTRL_G = '\x07'
CTRL_H = '\x08'
CTRL_I = TAB
CTRL_J = LF
CTRL_K = '\x0b'
CTRL_L = '\x0c'
CTRL_M = CR
CTRL_N = '\x0e'
CTRL_O = '\x0f'
CTRL_P = '\x10'
CTRL_Q = '\x11'
CTRL_R = '\x12'
CTRL_S = '\x13'
CTRL_T = '\x14'
CTRL_U = '\x15'
CTRL_V = '\x16'
CTRL_W = '\x17'
CTRL_Y = '\x19'

# ALT
ALT_ENTER = '\x1b\r'

if platform.startswith(('linux', 'darwin')):  # pragma: no cover
    # common
    BACKSPACE = '\x7f'

    # cursors
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    LEFT = '\x1b[D'
    RIGHT = '\x1b[C'

    # navigation keys
    INSERT = '\x1b[2~'
    HOME = '\x1b[H'
    END = '\x1b[F'
    PAGE_UP = '\x1b[5~'
    PAGE_DOWN = '\x1b[6~'

    ENTER = '\r'
    DELETE = '\x1b[3~'

elif platform in ('win32', 'cygwin'):  # pragma: no cover
    # common
    BACKSPACE = '\x08'

    # cursors
    UP = 'àH'
    DOWN = 'àP'
    LEFT = 'àK'
    RIGHT = 'àM'

    # navigation keys
    INSERT = 'àR'
    HOME = 'àG'
    END = 'àO'
    PAGE_UP = 'àI'
    PAGE_DOWN = 'àQ'

    ENTER = '\r'
    DELETE = 'àS'

else:  # pragma: no cover
    raise NotImplementedError('This OS is not supported')
