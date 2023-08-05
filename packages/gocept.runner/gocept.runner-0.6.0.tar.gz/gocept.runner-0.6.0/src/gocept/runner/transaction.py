# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import absolute_import
import ZODB.POSException
import decorator
import logging
import transaction


log = logging.getLogger(__name__)


@decorator.decorator
def transaction_per_item(func):
    for action in func():
        try:
            action()
        except Exception, e:
            log.error("Error in item %s: %s", action, e, exc_info=True)
            transaction.abort()
        else:
            try:
                transaction.commit()
            except ZODB.POSException.ConflictError:
                log.warning("Conflict error", exc_info=True)
                transaction.abort()
