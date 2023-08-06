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
import bobo
import doctest
import gevent
import gevent.socket
import hashlib
import manuel.capture
import manuel.doctest
import manuel.testing
import marshal
import mock
import os
import pprint
import re
import time
import traceback
import unittest
import webob
import zc.resumelb.util
import zc.resumelb.worker
import zc.zk.testing
import zope.testing.loggingsupport
import zope.testing.setupstack
import zope.testing.wait
import zope.testing.renormalizing

pid = os.getpid()

###############################################################################
# Bobo test app:

@bobo.resource
def hi(request):
    body = request.environ['wsgi.input'].read()
    return "\n\n%s -> %s %s %s\n\n" % (
        request.url, pid, len(body), hashlib.sha1(body).hexdigest())

@bobo.query('/gen.html')
def gen(size=0):
    size = int(size)
    return webob.Response(
        app_iter=['hello world\n'*1000]*size,
        content_length=12000*size)

@bobo.query('/sneaky.html')
def sneaky():
    # The app_iter has empty strings!
    return webob.Response(
        app_iter=['', 'hello world\n'],
        content_length=12)

@bobo.query('/sleep.html')
def sleep(bobo_request, dur=0, size=1):
    time.sleep(float(dur))
    if 'tracelog' in bobo_request.environ:
        bobo_request.environ['tracelog'].log('test', 'T')
        bobo_request.environ['tracelog'].log('test2')

    size = int(size)
    if size > 1:
        r = webob.Response()
        r.app_iter = ('hello world\n' for i in range(size))
        r.content_length = 12*size
        r.content_type = 'text/html'
        return r
    else:
        return 'hello world\n'

@bobo.query('/gsleep.html')
def gsleep(dur=0):
    gevent.sleep(float(dur))
    return 'hello world\n'

def app():
    return bobo.Application(bobo_resources=__name__)

#
###############################################################################

def newenv(rclass, *a, **kw):
    r = webob.Request.blank(*a, **kw)
    env = r.environ.copy()
    inp = env.pop('wsgi.input')
    del env['wsgi.errors']
    env['zc.resumelb.request_class'] = rclass
    return env

def print_response(worker_socket, rno, size_only=False):
    d = zc.resumelb.util.read_message(worker_socket)
    try: rn, (status, headers) = d
    except:
      print 'wtf', `d`
      return
    #rn, (status, headers) = read_message(worker_socket)
    if rn != rno:
       raise AssertionError("Bad request numbers", rno, rn)
    print rno, status
    for h in sorted(headers):
        print "%s: %s" % h
    print
    size = 0
    while 1:
        rn, data = zc.resumelb.util.read_message(worker_socket)
        if rn != rno:
           raise AssertionError("Bad request numbers", rno, rn)
        if data:
            if size_only:
                size += len(data)
            else:
                print data,
        else:
            break
    if size_only:
       print size

def test_loading_recipes_with_no_history_argument():
    """A bug as introduced that caused resumes to be loaded
    incorrectly when no history was given to the constructor.  It
    cause invalif perf_data to be initialized.

    >>> with open('resume.mar', 'w') as f:
    ...     marshal.dump(dict(a=1.0, b=2.0), f)

    >>> worker = zc.resumelb.worker.Worker(
    ...   zc.resumelb.tests.app(), ('127.0.0.1', 0),
    ...   resume_file='resume.mar')

    >>> pprint.pprint(worker.perf_data)
    {'a': (0, 1.0, 9999), 'b': (0, 0.5, 9999)}

    >>> worker.stop()
    """

def workers_generate_500s_for_bad_apps():
    """If an app is poorly behaved and raises exceptions, a worker
    will generate a 500.

    >>> def baddapp(*args):
    ...     raise Exception("I'm a bad-app")

    >>> worker = zc.resumelb.worker.Worker(baddapp, ('127.0.0.1', 0))
    >>> worker_socket = gevent.socket.create_connection(worker.addr)
    >>> zc.resumelb.util.read_message(worker_socket)
    (0, {})

    >>> env = newenv('', '/hi.html')
    >>> handler = zope.testing.loggingsupport.InstalledHandler(
    ...     'zc.resumelb.worker')
    >>> zc.resumelb.util.write_message(worker_socket, 1, env, '')
    >>> print_response(worker_socket, 1)
    1 500 Internal Server Error
    Content-Length: 23
    Content-Type: text/html; charset=UTF-8
    <BLANKLINE>
    A system error occurred

    >>> for record in handler.records:
    ...     print record.name, record.levelname
    ...     print record.getMessage()
    ...     if record.exc_info:
    ...         traceback.print_exception(*record.exc_info)
    ... # doctest: +ELLIPSIS
    zc.resumelb.worker ERROR
    Uncaught application exception for 1
    Traceback (most recent call last):
    ...
    Exception: I'm a bad-app

    >>> handler.uninstall()
    >>> worker.stop()
    """


def test_classifier(env):
    return "yup, it's a test"

def setUp(test):
    zope.testing.setupstack.setUpDirectory(test)
    zope.testing.setupstack.context_manager(test, mock.patch('gevent.signal'))
    global pid
    pid = 6115
    test.globs['wait'] = zope.testing.wait.Wait(getsleep=lambda : gevent.sleep)
    old = zc.resumelb.worker.STRING_BUFFER_SIZE
    zope.testing.setupstack.register(
        test, setattr, zc.resumelb.worker, 'STRING_BUFFER_SIZE', old)
    zc.resumelb.worker.STRING_BUFFER_SIZE = 9999

    old = zc.resumelb.util.queue_size_bytes
    zope.testing.setupstack.register(
        test, setattr, zc.resumelb.util, 'queue_size_bytes', old)
    zc.resumelb.util.queue_size_bytes = 999
    test.globs['newenv'] = newenv
    test.globs['print_response'] = print_response

def zkSetUp(test):
    setUp(test)
    zc.zk.testing.setUp(test)
    os.environ['COLUMNS'] = '70'

def zkTearDown(test):
    zc.zk.testing.tearDown(test)
    zope.testing.setupstack.tearDown(test)

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel(
                checker = zope.testing.renormalizing.OutputChecker([
                    (re.compile(r'127.0.0.1:\d+'), '127.0.0.1:P'),
                    (re.compile(r"'127.0.0.1', \d+"), "'127.0.0.1', P'"),
                    (re.compile(r"<socket fileno=\d+"), "<socket fileno=F"),
                    ])
                ) + manuel.capture.Manuel(),
            'lb.test', 'pool.test', 'worker.test', 'bytesizedqueue.test',
            'bufferedqueue.test',
            setUp=setUp, tearDown=zope.testing.setupstack.tearDown),
        manuel.testing.TestSuite(
            manuel.doctest.Manuel(
                checker = zope.testing.renormalizing.OutputChecker([
                    (re.compile(
                        r'\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\] "(.+) \d+\.\d+'
                        ),
                     'ACCESS'),
                    (re.compile(r"u'pid': \d+"), "u'pid': PID"),
                    ])
                ) + manuel.capture.Manuel(),
            'zk.test',
            setUp=zkSetUp, tearDown=zkTearDown),
        doctest.DocTestSuite(
            setUp=setUp, tearDown=zope.testing.setupstack.tearDown),
        ))

