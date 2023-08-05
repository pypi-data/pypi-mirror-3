# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Infrastructure for running."""

from __future__ import absolute_import
import logging
import os
import time
import signal

import ZODB.POSException
import transaction
import zope.app.appsetup.product
import zope.app.security.interfaces
import zope.app.component.hooks
import zope.app.server.main
import zope.app.wsgi
import zope.security.management
import zope.security.testing
import zope.publisher.base


log = logging.getLogger(__name__)


Exit = object()


class RunnerRequest(zope.publisher.base.BaseRequest):
    """A custom publisher request for the runner."""

    def __init__(self, *args):
        super(RunnerRequest, self).__init__(None, {}, positional=args)


class MainLoop(object):

    def __init__(self, app, ticks, worker, principal=None, once=False):
        self._is_running = False
        self.app = app
        self.ticks = ticks
        self.worker = worker
        self.once = once
        if principal is None:
            self.interaction = False
        else:
            self.interaction = True
            self.principal_id = principal

    def stopMainLoop(self, signum, frame):
        log.info("Received signal %s, terminating." % signum)
        self._is_running = False

    def __call__(self):
        old_site = zope.app.component.hooks.getSite()
        zope.app.component.hooks.setSite(self.app)

        self._is_running = True

        while self._is_running:
            ticks = None
            self.begin()
            try:
                ticks = self.worker()
            except (KeyboardInterrupt, SystemExit):
                self.abort()
                break
            except Exception, e:
                log.error("Error in worker: %s", e, exc_info=True)
                self.abort()
            else:
                try:
                    self.commit()
                except ZODB.POSException.ConflictError, e:
                    # Ignore silently, the next run will be a retry anyway.
                    log.warning("Conflict error", exc_info=True)
                    self.abort()

            if self.once or ticks is Exit:
                self._is_running = False
            else:
                if ticks is None:
                    ticks = self.ticks
                log.debug("Sleeping %s seconds" % ticks)
                time.sleep(ticks)

        zope.app.component.hooks.setSite(old_site)

    def begin(self):
        transaction.begin()
        if self.interaction:
            request = RunnerRequest()
            request.setPrincipal(self.principal)
            zope.security.management.newInteraction(request)

    def abort(self):
        transaction.abort()
        if self.interaction:
            zope.security.management.endInteraction()

    def commit(self):
        transaction.commit()
        if self.interaction:
            zope.security.management.endInteraction()

    @property
    def principal(self):
        auth = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication)
        return auth.getPrincipal(self.principal_id)


class appmain(object):
    """Decorator to simplify the actual entry point functions for main loops.
    """

    def __init__(self, ticks=1, principal=None):
        self.ticks = ticks
        self.principal = principal
        self.once = False

    def get_principal(self):
        if callable(self.principal):
            return self.principal()
        # BBB: depcreated:
        return self.principal

    def __call__(self, worker_method):
        def configure(appname, configfile):
            db, app = init(appname, configfile)
            mloop = MainLoop(app, self.ticks, worker_method,
                             principal=self.get_principal(),
                             once=self.once)
            # XXX do we want more signal handlers?
            signal.signal(signal.SIGHUP, mloop.stopMainLoop)
            signal.signal(signal.SIGTERM, mloop.stopMainLoop)
            mloop()
            db.close()
        # Just to make doctests look nice.
        configure.__name__ = worker_method.__name__
        return configure


class once(appmain):

    def __init__(self, principal=None):
        super(once, self).__init__(principal=principal)
        self.once = True


def init(appname, configfile):
    """Initialise the Zope environment (without network servers) and return a
    specific root-level object.
    """
    options = zope.app.server.main.load_options(['-C', configfile])
    zope.app.appsetup.product.setProductConfigurations(options.product_config)

    db = zope.app.wsgi.config(
        configfile,
        schemafile=os.path.join(
            os.path.dirname(zope.app.server.main.__file__), 'schema.xml'))

    root = db.open().root()
    app = root['Application']
    if appname is not None:
        app = app[appname]
    return db, app


def from_config(section, variable):
    """Return a callable that returns a value from product config."""
    def get_config():
        config = zope.app.appsetup.product.getProductConfiguration(section)
        if config is None:
            raise KeyError('No such section %s' % section)
        return config[variable]
    return get_config
