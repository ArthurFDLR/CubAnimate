#==============================================================================
#   Copyright 2014 AlphaOmega Technology
#
#   Licensed under the AlphaOmega Technology Open License Version 1.0
#   You may not use this file except in compliance with this License.
#   You may obtain a copy of the License at
#
#       http://www.alphaomega-technology.com.au/license/AOT-OL/1.0
#==============================================================================
"""
Equation Module
===============

This is the only module you should need to import

It maps the Expression Class from `Equation.core.Expression`

Its recomended you use the code::

    from Equation import Expression
    ...

to import the Expression Class, as this is the only Class/Function you
should use.

.. moduleauthor:: Glen Fletcher <glen.fletcher@alphaomega-technology.com.au>
"""


all = ['util']

from .core import Expression, recalculateFMatch
from .equation_base import equation_extend

def load():
    import os
    import os.path
    import sys
    import traceback
    import importlib
    
    if not hasattr(load, "loaded"):
        load.loaded = False
    if not load.loaded:
        load.loaded = True
        equation_extend()
        recalculateFMatch()
load()

del load