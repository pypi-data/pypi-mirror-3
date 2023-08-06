##############################################################################
#
# Copyright (c) 2004-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import doctest
import sys
import unittest

def test_suite():
    suite = unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE,
            ),
        ])
    if not sys.platform.lower().startswith('win'):
        suite.addTest(doctest.DocFileSuite('unix-sockets.txt'))
    return suite
