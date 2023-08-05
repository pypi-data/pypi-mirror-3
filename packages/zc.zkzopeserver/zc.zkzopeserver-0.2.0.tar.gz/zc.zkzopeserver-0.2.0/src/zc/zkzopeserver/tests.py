##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import asyncore
import doctest
import manuel.capture
import manuel.doctest
import manuel.testing
import re
import time
import unittest
import urllib
#import zc.ngi.async
import zc.thread
import zc.zk.testing
import zope.testing.renormalizing

maxactive = active = 0
def reset():
    global active, maxactive
    r = maxactive
    maxactive = active = 0
    return r

def slow_app(environ, start_response):
    global active, maxactive
    active += 1
    maxactive = max(maxactive, active)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    time.sleep(.1)
    start_response(status, response_headers)
    active -= 1
    return ['Hello world!\n']

def test_options():
    """
    Make sure various advertized options work:

    >>> @zc.thread.Thread
    ... def server():
    ...     zc.zkzopeserver.run(
    ...         slow_app, {},
    ...         zookeeper='zookeeper.example.com:2181',
    ...         path='/fooservice/providers',
    ...         session_timeout='4242',
    ...         host='127.0.0.1',
    ...         port='3042',
    ...         threads='3',
    ...         )

    >>> import zc.zkzopeserver
    >>> zc.zkzopeserver.event_for_testing.wait(1)
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')

    Did it get registered with the given host and port?

    >>> zk.print_tree('/fooservice/providers')
    /providers
      /127.0.0.1:3042
        pid = 3699

    How many can we do at once? Should be 3

    >>> [url] = [('http://%s/' % addr)
    ...          for addr in zk.get_children('/fooservice/providers')]

    >>> def get():
    ...     f = urllib.urlopen(url)
    ...     if not f.read().startwith('Hello world!'):
    ...         print '?'
    ...     f.close()

    >>> _ = reset()
    >>> threads = [zc.thread.Thread(get) for i in range(6)]
    >>> _ = [t.join() for t in threads]

    >>> reset()
    3

    Did session_timeout get passed? If we're using the mock ZooKeeper,
    we camn tell:

    >>> if ZooKeeper is not None:
    ...    ZooKeeper.recv_timeout(0)
    4242

    When the server stops, it's unregistered:

    >>> zc.zkzopeserver.stop_for_testing(server)
    >>> zk.print_tree('/fooservice/providers')
    /providers

    >>> zk.close()
    """


def test_suite():
    checker = zope.testing.renormalizing.RENormalizing([
        (re.compile('pid = \d+'), 'pid = 9999'),
        (re.compile(r' \d+ \d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d+'),
         ' IIIII DDDD-MM-DD HH:MM:SS.SS'),
        ])
    suite = unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel(checker=checker) + manuel.capture.Manuel(),
            'README.txt',
            setUp=zc.zk.testing.setUp, tearDown=zc.zk.testing.tearDown,
            ),
        doctest.DocTestSuite(
            setUp=zc.zk.testing.setUp, tearDown=zc.zk.testing.tearDown,
            checker=checker,
            ),
        ))
    return suite
