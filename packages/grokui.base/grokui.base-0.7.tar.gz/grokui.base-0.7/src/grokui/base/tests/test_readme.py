# -*- coding: utf-8 -*-

import unittest, doctest
import grokui.base
from zope.fanstatic.testing import ZopeFanstaticBrowserLayer

def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        '../README.txt',
        optionflags=(doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE|
                     doctest.REPORT_NDIFF))
    readme.layer = ZopeFanstaticBrowserLayer(grokui.base)
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
