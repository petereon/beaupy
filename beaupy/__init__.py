import sys

import beaupy.spinners as spinners  # noqa
from beaupy._beaupy import (  # noqa
    Config,
    KeyBindings,
    confirm,
    prompt,
    select,
    select_multiple,
)
from beaupy._internals import (  # noqa
    Abort,
    ConversionError,
    RemovedInV4Error,
    ValidationError,
    _RemovedGlobalsModule,
)

sys.modules[__name__].__class__ = _RemovedGlobalsModule
