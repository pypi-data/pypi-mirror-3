import unittest

from zope.component import queryMultiAdapter
from zope.publisher.browser import TestRequest

from zope.fanstatic.testing import ZopeFanstaticBrowserLayer

import horae.app.tests
from horae.app.app import Horae

# In this file we create a unittest, a functional unittest.

browser_layer = ZopeFanstaticBrowserLayer(horae.app.tests)


class MyFunctionalTestCase(unittest.TestCase):

    layer = browser_layer

    def test_foo(self):
        index = queryMultiAdapter((Horae(), TestRequest()), name='index')
        self.assertNotEqual(index, None)

        # There is no view called 'index2'
        index2 = queryMultiAdapter((Horae(), TestRequest()), name='index2')
        self.assertEqual(index2, None)
