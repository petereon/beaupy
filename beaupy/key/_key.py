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
CTRL_X = '\x18'
CTRL_Y = '\x19'
CTRL_Z = '\x1a'

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

    # funcion keys
    F1 = '\x1bOP'
    F2 = '\x1bOQ'
    F3 = '\x1bOR'
    F4 = '\x1bOS'
    F5 = '\x1b[15~'
    F6 = '\x1b[17~'
    F7 = '\x1b[18~'
    F8 = '\x1b[19~'
    F9 = '\x1b[20~'
    F10 = '\x1b[21~'
    F11 = '\x1b[23~'
    F12 = '\x1b[24~'

    # SHIFT+_
    SHIFT_TAB = '\x1b[Z'

    # aliases
    ENTER = '\r'
    DELETE = '\x1b[3~'

elif platform in ('win32', 'cygwin'):  # pragma: no cover
    # common
    BACKSPACE = '\x08'

    # cursors
    UP = '\x00\x48'
    DOWN = '\x00\x50'
    LEFT = '\x00\x4b'
    RIGHT = '\x00\x4d'

    # navigation keys
    INSERT = '\x00\x52'
    SUPR = '\x00\x53'
    HOME = '\x00\x47'
    END = '\x00\x4f'
    PAGE_UP = '\x00\x49'
    PAGE_DOWN = '\x00\x51'

    # funcion keys
    F1 = '\x00\x3b'
    F2 = '\x00\x3c'
    F3 = '\x00\x3d'
    F4 = '\x00\x3e'
    F5 = '\x00\x3f'
    F6 = '\x00\x40'
    F7 = '\x00\x41'
    F8 = '\x00\x42'
    F9 = '\x00\x43'
    F10 = '\x00\x44'
    F11 = '\x00\x85'  # only in second source
    F12 = '\x00\x86'  # only in second source

    # other
    ESC_2 = '\x00\x01'
    ENTER_2 = '\x00\x1c'

    # aliases
    ENTER = '\r'
    DELETE = SUPR

else:  # pragma: no cover
    raise NotImplementedError('This OS is not supported')
