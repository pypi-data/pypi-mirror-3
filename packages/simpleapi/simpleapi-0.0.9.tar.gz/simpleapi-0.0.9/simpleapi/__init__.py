# -*- coding: utf-8 -*-

from client import *
from server import *
from message import *

__author__ = 'Florian Schlachter'

VERSION = (0, 0, 9)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    return version

__version__ = get_version()