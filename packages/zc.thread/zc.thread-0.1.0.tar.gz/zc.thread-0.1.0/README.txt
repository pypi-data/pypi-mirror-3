Thread-creation helper
**********************

The thread-creation API provided by the Python ``threading`` module is
annoying. :)

This package provides a very simple thread-creation API that:

- Makes threads daemonic and allows daemonicity to be passed to the
  constructor.  For example::

    zc.thread.Thread(mythreadfunc)

  Starts a daemonic thread named ``'mythreadfunc'`` running
  ``mythreadfunc``.

- Allows threads to be defined via decorators, as in::

    import zc.thread

    @zc.thread.Thread
    def mythread():
        ...

  In the example above, a daemonic thread named ``mythread`` is
  created and started.  The thread is also assigned to the variable
  ``mythread``.

  You can control whether threads are daemonic and wether they are
  started by default::

    import zc.thread

    @zc.thread.Thread(daemon=False, start=False)
    def mythread():
        ...

- After a thread finished, you can get the return value of the
  target function from the thread's ``value`` attribute, or, if the
  function raises an exception, you can get the exception object from
  the thread's ``exception`` attribute. (This feature was inspired by
  the same feature in gevent greenlets.)

There's also a Process constructor/decorator that works like Thread,
but with multi-processing processes.

Changes
*******

0.1.0 (2011-11-27)
==================

Initial release
