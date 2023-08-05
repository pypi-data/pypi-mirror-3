# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.runner
import unittest
import zope.app.appsetup.product


class TestFromConfig(unittest.TestCase):

    def setUp(self):
        self.old_config = zope.app.appsetup.product.saveConfiguration()
        zope.app.appsetup.product.setProductConfiguration('test', dict(
            foo='bar'))

    def tearDown(self):
        zope.app.appsetup.product.restoreConfiguration(self.old_config)

    def test_invalid_section(self):
        self.assertRaises(KeyError,
                          gocept.runner.from_config('invalid', 'foo'))

    def test_invalid_value(self):
        self.assertRaises(KeyError,
                          gocept.runner.from_config('test', 'invalid'))

    def test_valid(self):
        self.assertEqual('bar',
                         gocept.runner.from_config('test', 'foo')())

    def test_returns_callable(self):
        self.assertTrue(callable(gocept.runner.from_config('baz', 'boink')))
