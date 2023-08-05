#!/usr/bin/env python
# -*- coding: utf-8 -*-
from common import *

if MAJOR_VERSION < 3:
    from api3 import *
else:
    from api4 import *


__version__ = '0.0.2'
__date__ = '2011-10-04'
__author__ = "Marc 'BlackJack' Rintsch"
__contact__ = 'marc@rintsch.de'
# 
# Due to lm-sensors 2.x using this license.
# 
__license__ = 'GPL v2'
