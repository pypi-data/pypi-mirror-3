from __future__ import absolute_import

import os

from tdm_loader.tdm_loader import *

try:
    with open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'rb') as fobj:
        __version__ = fobj.read().strip()
except IOError:
    __version__ = 'unknown'


