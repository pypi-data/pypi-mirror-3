# -*- coding: utf-8 -*-
'''stuf has attributes'''

from __future__ import absolute_import

from .core import defaultstuf, fixedstuf, frozenstuf, orderedstuf, stuf

idefaultstuf = defaultstuf
ifixedstuf = fixedstuf
ifrozenstuf = frozenstuf
iorderedstuf = orderedstuf
istuf = stuf

__all__ = ['defaultstuf', 'fixedstuf', 'frozenstuf', 'orderedstuf', 'stuf']
