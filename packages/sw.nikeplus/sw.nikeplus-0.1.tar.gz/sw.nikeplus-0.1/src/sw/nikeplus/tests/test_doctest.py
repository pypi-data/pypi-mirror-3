# -*- coding: utf-8 -*-
# Copyright (c) 2012 Sebastian Wehrmann
# See also LICENSE.txt

import doctest
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocFileSuite(
            "../nikeplus.txt",
            optionflags=doctest.ELLIPSIS))
    return suite
