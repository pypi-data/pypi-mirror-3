=================================================
zope.server wrapper that registers with ZooKeeper
=================================================

``zc.zkzopeserver`` provides a wrapper for the zope.server WSGI runner
that registers with ZooKeeper.  By registering with ZooKeeper, you can
let the operating system assign ports and have clients find your
server by looking in ZooKeeper.

Basic Usage
===========

The wrapper is used in a past-deploy configuration file::

   [server:main]
   use = egg:zc.zkzopeserver
   zookeeper = zookeeper.example.com:2181
   path = /fooservice/providers

.. -> server_config

The wrapper supports the following options:

zookeeper
   required ZooKeeper connection string

path
   required path at which to register your server

   Your server is registered by adding a ZooKeeper ephemeral node as a
   child of the path with the server address as the name.

host
   host name or ip to listen on, defaultiong to ''

port
   The port to listen on, defaulting to 0

session_timeout
   A ZooKeeper session timeout in milliseconds

threads
   The size of the thread pool, defaulting to 1

monitor_server
   A ``zc.monitor`` server address.

   The value is an address of the form HOST:PORT.  See `Monitor
   server`_ below. (Host can be empty to listen on all interfaces.)

.. test

    >>> import ConfigParser, StringIO
    >>> parser = ConfigParser.RawConfigParser()
    >>> parser.readfp(StringIO.StringIO(server_config))
    >>> kw = dict(parser.items('server:main'))

    >>> import pkg_resources
    >>> dist = kw.pop('use').split(':')[1]
    >>> [run] = [v.load()
    ...          for v in pkg_resources.get_entry_map(
    ...                 'zc.zkzopeserver', 'paste.server_runner'
    ...                  ).values()]

    >>> import wsgiref.simple_server, zc.thread
    >>> @zc.thread.Thread
    ... def server():
    ...     run(wsgiref.simple_server.demo_app, {}, **kw)

    >>> import zc.zkzopeserver
    >>> zc.zkzopeserver.event_for_testing.wait(1)

    >>> import urllib, zc.zk
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')

    >>> [port] = [int(c.split(':')[1])
    ...           for c in zk.get_children('/fooservice/providers')]
    >>> print urllib.urlopen('http://127.0.0.1:%s/' % port).read()
    ... # doctest: +ELLIPSIS
    Hello world!
    ...

    >>> zc.zkzopeserver.stop_for_testing(server)
    >>> zk.get_children('/fooservice/providers')
    []

Monitor server
==============

The `zc.monitor <http://pypi.python.org/pypi/zc.monitor>`_ package
provides a simple extensible command server for gathering monitoring
data or providing run-time control of servers.  If ``zc.monitor`` is
in the Python path, ``zc.zkzopeserver`` can start a monitor server
and make it's address available as the ``monitor`` property of a
server's ephemeral port.  To see how this works, let's update the
earler example::

   [server:main]
   use = egg:zc.zkzopeserver
   zookeeper = zookeeper.example.com:2181
   path = /fooservice/providers
   monitor_server = 127.0.0.1:0

.. -> server_config

When our web server is running, the ``/fooservice/providers`` node
would look something like::

    /providers
      /0.0.0.0:61181
        monitor = u'127.0.0.1:61182'
        pid = 4525

.. -> expected_tree

    >>> parser = ConfigParser.RawConfigParser()
    >>> parser.readfp(StringIO.StringIO(server_config))
    >>> kw = dict(parser.items('server:main'))
    >>> del kw['use']

    >>> @zc.thread.Thread
    ... def server():
    ...     run(wsgiref.simple_server.demo_app, {}, **kw)

    >>> zc.zkzopeserver.event_for_testing.wait(1)

    >>> [port] = [int(c.split(':')[1])
    ...           for c in zk.get_children('/fooservice/providers')]
    >>> print urllib.urlopen('http://127.0.0.1:%s/' % port).read()
    ... # doctest: +ELLIPSIS
    Hello world!
    ...

    >>> import re, zope.testing.renormalizing
    >>> checker = zope.testing.renormalizing.RENormalizing([
    ...     (re.compile('pid = \d+'), 'pid = 999'),
    ...     (re.compile('(0\.0\.[01]):\d+'), '\1:99999'),
    ...     ])
    >>> actual_tree = zk.export_tree('/fooservice/providers', True)
    >>> checker.check_output(expected_tree.strip(), actual_tree.strip(), 0)
    True

    >>> zc.zkzopeserver.stop_for_testing(server)
    >>> zk.get_children('/fooservice/providers')
    []

Some notes on the monitor server:

- A monitor server won't be useful unless you've registered some
  command plugins.

- ``zc.monitor`` isn't a dependency of ``zc.zkzopeserver`` and won't
  be in the Python path unless you install it.


Change History
==============

0.1.0 (2011-12-11)
------------------

Initial release


.. test cleanup

    >>> zk.close()
