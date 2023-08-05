# -*- coding: utf-8 -*-
'''Goto - urllib object wrapper'''

__version__ = '0.1.1'


import sys
import types

from . import goto
from . import utils


class CallableModule(types.ModuleType):
    def __init__(self):
        g = globals()
        for name in ['__version__', '__file__', '__package__',
                    '__name__', '__doc__']:
            setattr(self, name, g.get(name))

    __call__ = staticmethod(goto.goto)
    decode_qs = staticmethod(utils.decode_qs)  
    url_fix = staticmethod(goto.url_fix)


sys.modules[__name__] = CallableModule()
