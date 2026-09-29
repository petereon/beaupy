import sys

import beaupy.spinners as spinners  # noqa: F401
from beaupy._beaupy import Config as Config
from beaupy._beaupy import KeyBindings as KeyBindings
from beaupy._beaupy import confirm as confirm
from beaupy._beaupy import prompt as prompt
from beaupy._beaupy import select as select
from beaupy._beaupy import select_multiple as select_multiple
from beaupy._internals import Abort as Abort
from beaupy._internals import ConversionError as ConversionError
from beaupy._internals import RemovedInV4Error as RemovedInV4Error
from beaupy._internals import ValidationError as ValidationError
from beaupy._internals import _RemovedGlobalsModule

sys.modules[__name__].__class__ = _RemovedGlobalsModule
