# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Example to demonstrate how to create a "run" script."""

import gocept.runner


@gocept.runner.appmain(ticks=1)
def example():
    """Example function. This is called every ticks secons."""
    print "Calculating..."
