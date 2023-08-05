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
import re
import threading
import zc.zk
import zope.server.dualmodechannel
import zope.server.taskthreads

event_for_testing = threading.Event()
server_for_testing = None

# Note to the reader and tester
# -----------------------------
# zope.server and zc.monitor were, for better or worser, designed to
# be used as or in main programs. They expect to be instantiated
# exactly once and to be used through the end of the program.  Neither
# provide a clean shutdown mechanism.  In normal usage, this probably
# isn't a problem, but it's awkward for testing.
#
# We've worked around this by providing here a way to shutdown a
# running server, assuming there is only one at a time. :/  See the 3
# "_for_testing" variables.  We've leveraged a similar mechanism in
# zc.monitor. See the use of last_listener below.

def stop_for_testing(thread=None):
    zope.server.dualmodechannel.the_trigger.pull_trigger(
        server_for_testing.close)
    event_for_testing.clear()
    if thread is not None:
        thread.join(1)

def run(wsgi_app, global_conf,
        zookeeper, path, session_timeout=None,
        name=__name__, host='', port=0, threads=1, monitor_server=None,
        zservertracelog=None,
        ):
    port = int(port)
    threads = int(threads)

    task_dispatcher = zope.server.taskthreads.ThreadedTaskDispatcher()
    task_dispatcher.setThreadCount(threads)
    if zservertracelog == 'true':
        from zc.zservertracelog.tracelog import Server
    else:
        from zope.server.http.wsgihttpserver import WSGIHTTPServer as Server

    server = Server(wsgi_app, name, host, port, task_dispatcher=task_dispatcher)

    props = {}
    if monitor_server:
        host, port = monitor_server.rsplit(':', 1)
        global zc
        import zc.monitor
        props['monitor'] = "%s:%s" % zc.monitor.start((host, int(port)))

    server.ZooKeeper = zc.zk.ZooKeeper(
        zookeeper, session_timeout and int(session_timeout))
    server.ZooKeeper.register_server(
        path, "%s:%s" % server.socket.getsockname(), **props)

    map = asyncore.socket_map
    poll_fun = asyncore.poll

    global server_for_testing
    server_for_testing = server
    event_for_testing.set()

    try:
        while server.accepting:
            poll_fun(30.0, map)
    finally:
        server.ZooKeeper.close()
        if monitor_server:
            zc.monitor.last_listener.close()
