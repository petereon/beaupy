from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _version
from sys import modules as _modules

import beaupy.spinners as spinners
from beaupy._beaupy import Config, KeyBindings, confirm, prompt, select, select_multiple
from beaupy._internals import Abort, ConversionError, RemovedInV4Error, ValidationError, _RemovedGlobalsModule

try:
    __version__ = _version('beaupy')
except _PackageNotFoundError:  # running from a source tree that isn't installed
    __version__ = '0+unknown'

__all__ = [
    'Abort',
    'Config',
    'ConversionError',
    'KeyBindings',
    'RemovedInV4Error',
    'ValidationError',
    '__version__',
    'confirm',
    'prompt',
    'select',
    'select_multiple',
    'spinners',
]

_modules[__name__].__class__ = _RemovedGlobalsModule
