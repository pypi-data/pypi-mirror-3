Runner details
==============

Main loop
+++++++++

The main loop loops until it encounters a KeyboardInterrupt or a SystemExit
exception and calls the worker once a second.

Define a worker function which exits when it is called the 3rd time:

>>> work_count = 0
>>> def worker():
...     print "Working"
...     global work_count
...     work_count += 1
...     if work_count >= 3:
...         raise SystemExit(1)


Call the main loop:

>>> import gocept.runner.runner
>>> gocept.runner.runner.MainLoop(getRootFolder(), 0.1, worker)()
Working
Working
Working
>>> work_count
3


During the loop the site is set:

>>> import zope.app.component.hooks
>>> zope.app.component.hooks.getSite() is None
True
>>> def worker():
...     print zope.app.component.hooks.getSite()
...     raise SystemExit(1)
>>> gocept.runner.runner.MainLoop(getRootFolder(), 0.1, worker)()
<zope.site.folder.Folder object at 0x...>



After the loop, no site is set again:

>>> zope.app.component.hooks.getSite() is None
True


When the worker passes without error a transaction is commited:

>>> work_count = 0
>>> def worker():
...     print "Working"
...     global work_count
...     work_count += 1
...     if work_count >= 2:
...         raise SystemExit(1)
...     site = zope.app.component.hooks.getSite()
...     site.worker_done = 1
>>> gocept.runner.runner.MainLoop(getRootFolder(), 0.1, worker)()
Working
Working

We have set the attribute ``worker_done`` now:

>>> getRootFolder().worker_done
1


When the worker produces an error, the transaction is aborted:

>>> work_count = 0
>>> def worker():
...     global work_count
...     work_count += 1
...     print "Working"
...     site = zope.app.component.hooks.getSite()
...     site.worker_done += 1
...     if work_count < 3:
...         raise ValueError('hurz')
...     raise SystemExit(1)
>>> gocept.runner.runner.MainLoop(getRootFolder(), 0.1, worker)()
Working
Working
Working


We still have the attribute ``worker_done`` set to 1:b

>>> getRootFolder().worker_done
1


Controlling sleep time
++++++++++++++++++++++

The worker function can control the sleep time.

Register a log handler so we can observe this:

>>> import logging
>>> import StringIO
>>> log = StringIO.StringIO()
>>> log_handler = logging.StreamHandler(log)
>>> logging.root.addHandler(log_handler)
>>> old_log_level = logging.root.level
>>> logging.root.setLevel(logging.DEBUG)


>>> work_count = 0
>>> def worker():
...     global work_count
...     work_count += 1
...     new_sleep = work_count * 0.1
...     if work_count == 3:
...         print "Will sleep default"
...         return None
...     if work_count > 3:
...         raise SystemExit(1)
...     print "Will sleep", new_sleep
...     return new_sleep
>>> gocept.runner.runner.MainLoop(getRootFolder(), 0.15, worker)()
Will sleep 0.1
Will sleep 0.2
Will sleep default

The real sleep values are in the log:

>>> print log.getvalue(),
new transaction
commit
Sleeping 0.1 seconds
new transaction
commit
Sleeping 0.2 seconds
new transaction
commit
Sleeping 0.15 seconds
new transaction
abort

When an error occours within the worker, the default sleep time will be used:

>>> log.seek(0)
>>> log.truncate()
>>> work_count = 0
>>> def worker():
...     global work_count
...     work_count += 1
...     if work_count == 1:
...         new_sleep = 0.1
...     elif work_count == 2:
...         print "Failing"
...         raise Exception("Fail!")
...     elif work_count == 3:
...         print "Will sleep default"
...         return None
...     elif work_count > 3:
...         return gocept.runner.Exit
...     print "Will sleep", new_sleep
...     return new_sleep
>>> gocept.runner.runner.MainLoop(getRootFolder(), 0.15, worker)()
Will sleep 0.1
Failing
Will sleep default

The real sleep values are in the log:

>>> print log.getvalue(),
new transaction
commit
Sleeping 0.1 seconds
new transaction
Error in worker: Fail!
Traceback (most recent call last):
  ...
Exception: Fail!
abort
Sleeping 0.15 seconds
new transaction
commit
Sleeping 0.15 seconds
new transaction
commit

Restore old log handler:

>>> logging.root.removeHandler(log_handler)
>>> logging.root.setLevel(old_log_level)
