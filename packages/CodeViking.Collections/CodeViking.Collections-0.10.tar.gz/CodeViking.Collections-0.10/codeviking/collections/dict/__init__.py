__import__('pkg_resources').declare_namespace(__name__)

import _dictchain, _FrozenDict, _dirdict, _filedict, _multidict
from _dictchain import *
from _FrozenDict import *
from _filedict import *
from _dirdict import *
from _multidict import *

__all__ = (_dictchain.__all__ + _FrozenDict.__all__ +
           _dirdict.__all__ + _filedict.__all__ + _multidict.__all__)
