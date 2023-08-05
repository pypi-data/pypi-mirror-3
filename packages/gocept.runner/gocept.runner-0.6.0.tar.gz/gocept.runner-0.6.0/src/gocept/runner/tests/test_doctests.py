# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import doctest
import gocept.runner.testing
import unittest
import zope.app.testing.functional


flags = doctest.ELLIPSIS


def test_suite():
    suite = unittest.TestSuite()
    test = zope.app.testing.functional.FunctionalDocFileSuite(
        'README.txt',
        package='gocept.runner',
        optionflags=flags)
    test.layer = gocept.runner.testing.layer
    suite.addTest(test)

    suite.addTest(doctest.DocFileSuite(
        'appmain.txt',
        'once.txt',
        package='gocept.runner',
        optionflags=flags))

    return suite
