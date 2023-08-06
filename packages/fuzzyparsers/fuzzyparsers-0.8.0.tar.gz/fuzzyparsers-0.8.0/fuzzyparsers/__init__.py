# -*- coding: utf-8 -*-
##############################################################################
#  Copyright (C) 2010-12, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the MIT license
##############################################################################
"""
fuzzyparsers library initialization
"""

from strings import default_match, fuzzy_match
from dates import *

# backwards compatibility function
sanitized_date = parse_date

__version_info__ = ['0', '8', '0']
__version__ = '.'.join(__version_info__)
