##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

def _options(daemon=True, start=True, args=(), kwargs=None):
    return daemon, start, args, kwargs or {}


def Thread(func=None, **options):
    """Create and (typically) start a thread

    If no function is passed, then a decorator function is
    returned. Typical usage is::

       @zc.thread.Thread
       def mythreadfunc():
           ...

       ...

       mythread.join()

    Options:

        deamon=True
           Thread daemon flag. Set to false to cause process exit to
           block until the thread has exited.

        start=True
           True to automatically start the thread.

        args=()
           Positional arguments to pass to the thread function.

        kwargs={}
           keyword arguments to pass to the thread function.

    """
    if func is None:
        return lambda f: Thread(f, **options)
    daemon, start, args, kwargs = _options(**options)
    import threading

    def run(*args, **kw):
        try:
            v = func(*args, **kw)
            thread.value = v
        except Exception, v:
            thread.exception = v

    thread = threading.Thread(
        target=run, name=getattr(func, '__name__', None),
        args=args, kwargs=kwargs)
    thread.setDaemon(daemon)
    thread.value = thread.exception = None
    if start:
        thread.start()
    return thread

def Process(func=None, **options):
    """Create and (typically) start a multiprocessing process

    If no function is passed, then a decorator function is
    returned. Typical usage is::

       @zc.thread.Process
       def mythreadfunc():
           ...

       ...

       mythread.join()

    Options:

        deamon=True
           Process daemon flag. Set to false to cause process exit to
           block until the process has exited.

        start=True
           True to automatically start the process.

        args=()
           Positional arguments to pass to the process function.

        kwargs={}
           keyword arguments to pass to the process function.

    """
    if func is None:
        return lambda f: Process(f, **options)
    daemon, start, args, kwargs = _options(**options)
    import multiprocessing
    process = multiprocessing.Process(
        target=func, name=getattr(func, '__name__', None),
        args=args, kwargs=kwargs)
    process.daemon = daemon
    if start:
        process.start()
    return process
