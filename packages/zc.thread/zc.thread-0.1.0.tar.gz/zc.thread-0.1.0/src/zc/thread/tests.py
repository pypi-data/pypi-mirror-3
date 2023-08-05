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
import doctest
import mock
import os
import unittest
import zc.thread

class TestThread(unittest.TestCase):

    def test_default(self):
        with mock.patch('threading.Thread') as Thread:
            @zc.thread.Thread
            def foo():
                return 42

            Thread.call_args[1].pop('target')()
            self.assert_(foo.value == 42 and foo.exception is None)
            Thread.assert_called_with(name='foo', args=(), kwargs={})
            foo.setDaemon.assert_called_with(True)
            foo.start.assert_called_with()

    def test_undecorated_and_exception_return(self):
        with mock.patch('threading.Thread') as Thread:
            def foo2():
                raise ValueError(42)

            t = zc.thread.Thread(foo2)
            Thread.call_args[1].pop('target')()
            Thread.assert_called_with(name='foo2', args=(), kwargs=dict())
            t.setDaemon.assert_called_with(True)
            t.start.assert_called_with()
            self.assert_(t.value is None)
            self.assert_(isinstance(t.exception, ValueError))
            self.assert_(t.exception.args == (42,))

            t = zc.thread.Thread(foo2, args=(1, 2))
            Thread.call_args[1].pop('target')(1, 2)
            Thread.assert_called_with(name='foo2', args=(1, 2), kwargs=dict())
            t.setDaemon.assert_called_with(True)
            t.start.assert_called_with()
            self.assert_(t.value is None)
            self.assert_(isinstance(t.exception, TypeError))

    def test_passing_arguments(self):
        with mock.patch('threading.Thread') as Thread:
            @zc.thread.Thread(args=(1, 2), kwargs=dict(a=1), daemon=False,
                              start=False)
            def foo(*a, **k):
                return a, k

            Thread.call_args[1].pop('target')(1, 2, **dict(a=1))
            self.assert_(foo.value == ((1, 2), dict(a=1)))
            Thread.assert_called_with(name='foo', args=(1, 2), kwargs=dict(a=1))
            foo.setDaemon.assert_called_with(False)
            self.assert_(not foo.start.called)

    def test_Thread_wo_mock(self):
        @zc.thread.Thread
        def foo():
            return 42

        foo.join()
        self.assert_(foo.value == 42)

    def test_Process_w_mock(self):
        with mock.patch('multiprocessing.Process') as Process:
            @zc.thread.Process
            def foo():
                print 'foo called'
            Process.call_args[1].pop('target')()
            Process.assert_called_with(name='foo', args=(), kwargs={})
            self.assert_(foo.daamon)
            foo.start.assert_called_with()
            Process.reset_mock()

            def foo2():
                pass
            t = zc.thread.Process(foo2)
            Process.assert_called_with(
                target=foo2, name='foo2', args=(), kwargs={})
            self.assert_(t.daamon)
            t.start.assert_called_with()
            Process.reset_mock()

            @zc.thread.Process(daemon=False, start=False, args=(42,),
                               kwargs=dict(a=1))
            def foo3():
                print 'foo3 called'
            Process.call_args[1].pop('target')()
            Process.assert_called_with(name='foo3', args=(42,), kwargs=dict(a=1))
            self.assert_(not foo3.daemon)
            self.assert_(not foo3.start.called)

    def test_Process_wo_mock(self):
        import multiprocessing
        queue = multiprocessing.Queue()
        zc.thread.Process(run_process, args=(queue,)).join(11)
        self.assert_(queue.get() != os.getpid())

def run_process(queue):
    queue.put(os.getpid())

def test_suite():
    return unittest.makeSuite(TestThread)
