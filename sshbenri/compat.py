# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import sys


py3k = sys.version_info >= (3, 0)
py2k = sys.version_info < (3, 0)


if py3k:
    string_types = str
    input_func = input
else:
    string_types = basestring
    input_func = raw_input
