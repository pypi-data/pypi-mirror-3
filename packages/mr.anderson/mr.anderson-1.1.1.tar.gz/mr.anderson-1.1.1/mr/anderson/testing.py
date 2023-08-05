# -*- coding: utf-8 -*-
import sys
try:
    import unittest2 as unittest
except ImportError:
    if sys.version_info <= (2, 6):
        raise RuntimeError("These tests require unittest2")
    else:
        # Python 2.7 unittest == unittest2
        import unittest
