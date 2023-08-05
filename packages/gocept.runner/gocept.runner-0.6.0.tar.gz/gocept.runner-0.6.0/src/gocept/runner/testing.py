# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import zope.app.testing.functional


layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'Layer', allow_teardown=True)
