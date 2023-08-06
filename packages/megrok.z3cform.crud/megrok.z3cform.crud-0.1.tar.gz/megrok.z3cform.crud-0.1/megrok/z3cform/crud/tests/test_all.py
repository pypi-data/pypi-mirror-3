import unittest
import doctest

from zope.app.wsgi.testlayer import BrowserLayer

import megrok.z3cform.crud.tests

browser_layer = BrowserLayer(megrok.z3cform.crud.tests)

def test_suite():
    readme = doctest.DocFileSuite(
        '../README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )
    readme.layer = browser_layer
    
    batch = doctest.DocFileSuite(
       '../batch.txt',
       optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
       ),

    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite