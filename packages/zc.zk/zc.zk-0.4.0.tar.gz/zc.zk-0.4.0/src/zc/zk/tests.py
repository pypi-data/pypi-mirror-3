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
import json
import logging
import manuel.capture
import manuel.doctest
import manuel.testing
import mock
import os
import pprint
import re
import StringIO
import sys
import threading
import time
import zc.zk
import zc.zk.testing
import zc.thread
import zookeeper
import zope.testing.loggingsupport
import zope.testing.renormalizing
import unittest

class LoggingTests(unittest.TestCase):

    def test_logging(self):
        logger = logging.getLogger('ZooKeeper')
        f = StringIO.StringIO()
        h = logging.StreamHandler(f)
        logger.addHandler(h)
        logger.setLevel(logging.DEBUG)
        try:
            handle = zookeeper.init('zookeeper.example.com:2181')
            zookeeper.close(handle)
        except:
            pass
        zc.zk.testing.wait_until(lambda : 'environment' in f.getvalue())
        logger.setLevel(logging.NOTSET)
        logger.removeHandler(h)

def side_effect(mock):
    return lambda func: setattr(mock, 'side_effect', func)

class zklogger(object):

    def __init__(self):
        logger = logging.getLogger('zc.zk')
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        logger.addHandler(h)
        self.h = h
        logger.setLevel(logging.DEBUG)

    def uninstall(self):
        logger = logging.getLogger('zc.zk')
        logger.removeHandler(self.h)
        logger.setLevel(logging.NOTSET)

class Tests(unittest.TestCase):

    @mock.patch('zookeeper.init')
    def setUp(self, init):
        @zc.thread.Thread
        def getzk():
            zk = zc.zk.ZooKeeper()
            return zk

        zc.zk.testing.wait_until(lambda : init.call_args)
        (zkaddr, self.__session_watcher), kw = init.call_args
        self.assertEqual((zkaddr, kw), ('127.0.0.1:2181', {}))
        self.__session_watcher(
            0, zookeeper.SESSION_EVENT, zookeeper.CONNECTED_STATE, '')
        getzk.join(1)
        self.__zk = getzk.value
        self.assertEqual(self.__zk.handle, 0)

        self.__teardowns = []
        cm = mock.patch('zookeeper.exists')
        @side_effect(cm.__enter__())
        def exists(handle, path):
            return True

    def tearDown(self):
        while self.__teardowns:
            self.__teardowns.pop()()

    def state_side_effect(self, handle):
        self.assertEqual(handle, self.__zk.handle)
        return zookeeper.CONNECTED_STATE

    @mock.patch('zookeeper.close')
    def test_close(self, close):
        self.__zk.close()
        close.assert_called_with(0)
        self.assertEqual(self.__zk.handle, None)

    @mock.patch('zookeeper.create')
    def test_register_server(self, create):
        @side_effect(create)
        def _(handle, path_, data, acl, flags):
            self.assertEqual((handle, path_), (0, '/foo/127.0.0.1:8080'))
            self.assertEqual(json.loads(data), dict(pid=os.getpid(), a=1))
            self.assertEqual(acl, [zc.zk.world_permission()])
            self.assertEqual(flags, zookeeper.EPHEMERAL)

        self.__zk.register_server('/foo', ('127.0.0.1', 8080), a=1)

    @mock.patch('zookeeper.close')
    @mock.patch('zookeeper.init')
    @mock.patch('zookeeper.state')
    @mock.patch('zookeeper.get_children')
    def test_children(self, get_children, state, init, close):
        state.side_effect = self.state_side_effect

        path = '/test'
        @side_effect(get_children)
        def _(handle, path_, handler=None):
            if handler is not None:
                self.__handler = handler
            self.assertEqual((handle, path_), (0, path))
            return data

        # Get the data the first time
        data = []
        children = self.__zk.children(path)
        self.assertEqual(list(children), data)

        # When tree updates, children are updated
        data = ['a']
        self.__handler(0, zookeeper.CHILD_EVENT, zookeeper.CONNECTED_STATE,
                       path)
        self.assertEqual(list(children), data)

        # callbacks are called too:
        cb = mock.Mock(); children(cb)
        cb.assert_called_with(children)
        cb.reset_mock()
        self.assertEqual(len(children.callbacks), 1)
        data = ['a', 'b']
        self.__handler(0, zookeeper.CHILD_EVENT, zookeeper.CONNECTED_STATE,
                       path)
        self.assertEqual(list(children), data)
        cb.assert_called_with(children)

        # if a callback raises an exception, the exception is logged
        # and callback is discarded
        h = zope.testing.loggingsupport.Handler('zc.zk', level=logging.DEBUG)
        h.install()
        cb.side_effect = ValueError
        data = ['a']
        self.__handler(0, zookeeper.CHILD_EVENT, zookeeper.CONNECTED_STATE,
                       path)
        self.assertEqual(list(children), data)
        self.assertEqual(len(children.callbacks), 0)
        self.assertEqual(h.records[0].name, 'zc.zk')
        self.assertEqual(h.records[0].levelno, logging.ERROR)
        h.clear()

        # if a callback raises zc.zk.CancelWatch, the cancel is logged
        # and callback is discarded
        cb = mock.Mock(); children(cb)
        self.assertEqual(len(children.callbacks), 1)
        cb.side_effect = zc.zk.CancelWatch
        data = []
        self.__handler(0, zookeeper.CHILD_EVENT, zookeeper.CONNECTED_STATE,
                       path)
        self.assertEqual(list(children), data)
        self.assertEqual(len(children.callbacks), 0)
        self.assertEqual(h.records[0].name, 'zc.zk')
        self.assertEqual(h.records[0].levelno, logging.DEBUG)
        h.clear()

        h.uninstall()

        # If a session expires, it will be reestablished with watches intact.
        cb = mock.Mock(); children(cb)
        self.__session_watcher(
            0, zookeeper.SESSION_EVENT, zookeeper.EXPIRED_SESSION_STATE, "")
        close.assert_called_with(0)
        self.assertEqual(self.__zk.handle, None)
        data = ['test']
        self.__session_watcher(
            0, zookeeper.SESSION_EVENT, zookeeper.CONNECTED_STATE, "")
        self.assertEqual(list(children), data)
        cb.assert_called_with(children)


    @mock.patch('zookeeper.close')
    @mock.patch('zookeeper.init')
    @mock.patch('zookeeper.state')
    @mock.patch('zookeeper.get')
    def test_get_properties(self, get, state, init, close):
        state.side_effect = self.state_side_effect

        path = '/test'
        @side_effect(get)
        def _(handle, path_, handler=None):
            if handler is not None:
                self.__handler = handler
            self.assertEqual((handle, path_), (0, path))
            return json.dumps(data), {}

        # Get the data the first time
        data = {}
        properties = self.__zk.properties(path)
        self.assertEqual(dict(properties), data)

        # When node updates, properties are updated
        data = dict(a=1)
        self.__handler(0, zookeeper.CHANGED_EVENT, zookeeper.CONNECTED_STATE,
                     path)
        self.assertEqual(dict(properties), data)

        # callbacks are called too:
        cb = mock.Mock(); properties(cb)
        cb.assert_called_with(properties)
        cb.reset_mock()
        self.assertEqual(len(properties.callbacks), 1)
        self.__handler(0, zookeeper.CHANGED_EVENT, zookeeper.CONNECTED_STATE,
                     path)
        self.assertEqual(dict(properties), data)
        cb.assert_called_with(properties)

        # if a callback raises an exception, the exception is logged
        # and callback is discarded
        h = zope.testing.loggingsupport.Handler('zc.zk', level=logging.DEBUG)
        h.install()
        cb.side_effect = ValueError
        data = dict(a=1)
        self.__handler(0, zookeeper.CHANGED_EVENT, zookeeper.CONNECTED_STATE,
                     path)
        self.assertEqual(dict(properties), data)
        self.assertEqual(len(properties.callbacks), 0)
        self.assertEqual(h.records[0].name, 'zc.zk')
        self.assertEqual(h.records[0].levelno, logging.ERROR)
        h.clear()

        # if a callback raises zc.zk.CancelWatch, the cancel is logged
        # and callback is discarded
        cb = mock.Mock(); properties(cb)
        self.assertEqual(len(properties.callbacks), 1)
        cb.side_effect = zc.zk.CancelWatch
        data = {}
        self.__handler(0, zookeeper.CHANGED_EVENT, zookeeper.CONNECTED_STATE,
                     path)
        self.assertEqual(dict(properties), data)
        self.assertEqual(len(properties.callbacks), 0)
        self.assertEqual(h.records[0].name, 'zc.zk')
        self.assertEqual(h.records[0].levelno, logging.DEBUG)
        h.clear()

        h.uninstall()

        # If a session expires, it will be reestablished with watches intact.
        cb = mock.Mock(); properties(cb)
        self.__session_watcher(
            0, zookeeper.SESSION_EVENT, zookeeper.EXPIRED_SESSION_STATE, "")
        close.assert_called_with(0)
        self.assertEqual(self.__zk.handle, None)
        data = dict(test=1)
        self.__session_watcher(
            0, zookeeper.SESSION_EVENT, zookeeper.CONNECTED_STATE, "")
        self.assertEqual(dict(properties), data)
        cb.assert_called_with(properties)

    @mock.patch('zookeeper.state')
    @mock.patch('zookeeper.get')
    @mock.patch('zookeeper.set')
    def test_set_properties(self, set, get, state):
        state.side_effect = self.state_side_effect

        path = '/test'
        @side_effect(get)
        def _(handle, path_, handler=None):
            if handler is not None:
                self.__handler = handler
            self.assertEqual((handle, path_), (0, path))
            return json.dumps(data), {}

        data = dict(a=1)
        properties = self.__zk.properties(path)
        self.assertEqual(dict(properties), data)

        @side_effect(set)
        def _(handle, path_, data, version=-1):
            self.__set_data = json.loads(data)
            self.assertEqual((handle, path_), (0, path))

        properties.update(b=2)
        self.assertEqual(self.__set_data, dict(a=1, b=2))
        self.assertEqual(dict(properties), self.__set_data)

        properties.set(c=3)
        self.assertEqual(self.__set_data, dict(c=3))
        self.assertEqual(dict(properties), self.__set_data)

    @mock.patch('zookeeper.state')
    @mock.patch('zookeeper.get')
    @mock.patch('zookeeper.set')
    def test_special_values(self, set, get, state):
        state.side_effect = self.state_side_effect

        path = '/test'
        @side_effect(get)
        def _(handle, path_, handler=None):
            if handler is not None:
                self.__handler = handler
            self.assertEqual((handle, path_), (0, path))
            return data, {}

        data = ''
        properties = self.__zk.properties(path)
        self.assertEqual(dict(properties), {})

        data = 'xxx'
        properties = self.__zk.properties(path)
        self.assertEqual(dict(properties), dict(string_value='xxx'))

        data = '{xxx}'
        properties = self.__zk.properties(path)
        self.assertEqual(dict(properties), dict(string_value='{xxx}'))

        data = '\n{xxx}\n'
        properties = self.__zk.properties(path)
        self.assertEqual(dict(properties), dict(string_value='\n{xxx}\n'))

        @side_effect(set)
        def _(handle, path_, data, version=-1):
            self.__set_data = data
            self.assertEqual((handle, path_), (0, path))

        properties.set(b=2)
        self.assertEqual(self.__set_data, '{"b":2}')
        properties.set()
        self.assertEqual(self.__set_data, '')
        properties.set(string_value='xxx')
        self.assertEqual(self.__set_data, 'xxx')

def test_children():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> _ = zk.create('/test', '', zc.zk.OPEN_ACL_UNSAFE)
    >>> children = zk.children('/test')
    >>> sorted(children)
    []

    >>> len(children)
    0
    >>> bool(children)
    False

    >>> def create(path):
    ...     zk.create(path, '', zc.zk.OPEN_ACL_UNSAFE)
    >>> create('/test/a')
    >>> sorted(children)
    ['a']

    >>> len(children)
    1
    >>> bool(children)
    True

We can register callbacks:

    >>> @children
    ... def cb(c):
    ...     print 'good', sorted(c)
    good ['a']

When we register a callback, it gets called immediately with a children object.

    >>> create('/test/b')
    good ['a', 'b']
    >>> sorted(children)
    ['a', 'b']

If a callback raises an error immediately, it isn't saved:

    >>> @children
    ... def bad(c):
    ...     raise ValueError
    Traceback (most recent call last):
    ...
    ValueError

    >>> create('/test/c')
    good ['a', 'b', 'c']

    >>> len(children)
    3
    >>> bool(children)
    True

If a callback raises an error later, it is logged and the callback is
cancelled:

    >>> logger = zklogger()

    >>> badnow = False
    >>> @children
    ... def bad(c):
    ...     assert c is children
    ...     print 'bad later', sorted(c)
    ...     if badnow:
    ...         raise ValueError
    bad later ['a', 'b', 'c']

    >>> _ = zk.delete('/test/c')
    good ['a', 'b']
    bad later ['a', 'b']

    >>> badnow = True
    >>> _ = zk.delete('/test/b') # doctest: +ELLIPSIS
    good ['a']
    bad later ['a']
    ERROR watch(zc.zk.Children(0, /test), <function bad at ...>)
    Traceback (most recent call last):
    ...
    ValueError

    >>> _ = zk.delete('/test/a')
    good []

A callback can also cancel itself by raising CancelWatch:

    >>> cancelnow = False
    >>> @children
    ... def cancel(c):
    ...     assert c is children
    ...     print 'cancel later', sorted(c)
    ...     if cancelnow:
    ...         raise zc.zk.CancelWatch
    cancel later []

    >>> create('/test/a')
    good ['a']
    cancel later ['a']

    >>> cancelnow = True
    >>> create('/test/b') # doctest: +ELLIPSIS
    good ['a', 'b']
    cancel later ['a', 'b']
    DEBUG cancelled watch(zc.zk.Children(0, /test), <function cancel at ...>)

    >>> logger.uninstall()

    >>> zk.close()

    """

def test_handler_cleanup():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> _ = zk.create('/test', '', zc.zk.OPEN_ACL_UNSAFE)

Children:

    >>> children = zk.children('/test')
    >>> len(zk.watches)
    1
    >>> del children
    >>> len(zk.watches)
    0

    >>> children = zk.children('/test')
    >>> @children
    ... def kids(c):
    ...     print c
    zc.zk.Children(0, /test)
    >>> len(zk.watches)
    1
    >>> del children
    >>> len(zk.watches)
    1
    >>> del kids
    >>> len(zk.watches)
    0

    >>> @zk.children('/test')
    ... def kids(c):
    ...     print c
    zc.zk.Children(0, /test)

    >>> len(zk.watches)
    1
    >>> del kids
    >>> len(zk.watches)
    0

Properties:

    >>> properties = zk.properties('/test')
    >>> len(zk.watches)
    1
    >>> del properties
    >>> len(zk.watches)
    0

    >>> properties = zk.properties('/test')
    >>> @properties
    ... def props(c):
    ...     print c
    zc.zk.Properties(0, /test)
    >>> len(zk.watches)
    1
    >>> del properties
    >>> len(zk.watches)
    1
    >>> del props
    >>> len(zk.watches)
    0

    >>> @zk.properties('/test')
    ... def props(c):
    ...     print c
    zc.zk.Properties(0, /test)

    >>> len(zk.watches)
    1
    >>> del props
    >>> len(zk.watches)
    0

    >>> zk.close()

    """

def test_deleted_node_with_watchers():
    """

Set up some handlers.

    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> _ = zk.create('/test', '{"a": 1}', zc.zk.OPEN_ACL_UNSAFE)

    >>> children = zk.children('/test')
    >>> @children
    ... def _(arg):
    ...     print 1, list(arg)
    1 []

    >>> @children
    ... def _(arg=None):
    ...     print 2, arg
    2 zc.zk.Children(0, /test)

    >>> _ = zk.create('/test/a', '', zc.zk.OPEN_ACL_UNSAFE)
    1 ['a']
    2 zc.zk.Children(0, /test)

    >>> _ = zk.delete('/test/a')
    1 []
    2 zc.zk.Children(0, /test)

    >>> properties = zk.properties('/test')
    >>> @properties
    ... def _(arg):
    ...     print 3, dict(arg)
    3 {u'a': 1}

    >>> @properties
    ... def _(arg=None):
    ...     print 4, arg
    4 zc.zk.Properties(0, /test)

    >>> zk.set('/test', '{"b": 2}')
    3 {u'b': 2}
    4 zc.zk.Properties(0, /test)
    0

Hack data into the child watcher to verify it's cleared:

    >>> children.data = 'data'

Now delete the node.  The handlers that accept no arguments will be called:

    >>> _ = zk.delete('/test')
    4 None
    2 None

Note that the handlers that accept 0 arguments were called.

And the data are cleared:

    >>> list(children), list(properties)
    ([], [])

    >>> zk.close()
    """


def resilient_import():
    """
We can use vatious spacing in properties and links:

    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> zk.import_tree('''
    ... /test
    ...   a=1
    ...   b      =1
    ...   c=      1
    ...   ad->/x
    ...   af          ->/x
    ...   ae->         /x
    ... ''')

    >>> print zk.export_tree('/test'),
    /test
      a = 1
      b = 1
      c = 1
      ad -> /x
      ae -> /x
      af -> /x

When an expression is messed up, we get sane errors:

    >>> zk.import_tree('''
    ... /test
    ...   a= 1+
    ... ''') # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: Error unexpected EOF while parsing (<string>, line 1)
    in expression: '1+'

    >>> zk.import_tree('''
    ... /test
    ...   a ->
    ... ''') # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: (3, 'a ->', 'Bad link format')

    >>> zk.import_tree('''
    ... /test
    ...   a -> 1
    ... ''') # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ValueError: (3, 'a -> 1', 'Bad link format')

    >>> zk.close()
    """

def import_dry_run():
    """

    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> zk.import_tree('''
    ... /test
    ...   a=1
    ...   b = 2
    ...   /c1
    ...     /c12
    ...   /c2
    ...   ae->         /x
    ...   ad->         /y
    ... ''')

    >>> zk.import_tree('''
    ... /test
    ...   a=2
    ...   /c1
    ...     /c12
    ...       a = 1
    ...       b -> /b
    ...       /c123
    ...   ae->         /z
    ... ''', dry_run=True)
    /test a change from 1 to 2
    /test remove link ad -> /y
    /test ae link change from /x to /z
    /test remove property b = 2
    extra path not trimmed: /test/c2
    /test/c1/c12 add property a = 1
    /test/c1/c12 add link b -> /b
    add /test/c1/c12/c123

    >>> print zk.export_tree('/test'),
    /test
      a = 1
      b = 2
      ad -> /y
      ae -> /x
      /c1
        /c12
      /c2

    >>> zk.close()
    """

def property_set_and_update_variations():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> data = zk.properties('/fooservice')
    >>> @data
    ... def _(data):
    ...     pprint.pprint(dict(data), width=70)
    {u'database': u'/databases/foomain',
     u'favorite_color': u'red',
     u'threads': 1}

    >>> data.set(dict(x=1))
    {u'x': 1}
    >>> data.set(dict(x=1), x=2, y=3)
    {u'x': 2, u'y': 3}
    >>> data.set(z=1)
    {u'z': 1}
    >>> data.update(a=1)
    {u'a': 1, u'z': 1}
    >>> data.update(dict(b=1), a=2)
    {u'a': 2, u'b': 1, u'z': 1}
    >>> data.update(dict(c=1))
    {u'a': 2, u'b': 1, u'c': 1, u'z': 1}
    >>> data.update(dict(d=1), d=2)
    {u'a': 2, u'b': 1, u'c': 1, u'd': 2, u'z': 1}

    >>> zk.close()
    """

def test_resolve():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> zk.import_tree('''
    ... /top
    ...  /a
    ...    top -> /top
    ...    loop -> /top/a/b/loop
    ...    /b
    ...      top -> /top
    ...      loop -> /top/a/loop
    ...      /c
    ...        top -> /top
    ...        /d
    ...          name = 'd'
    ...          /e
    ...          top -> /top
    ...          loop -> /top/a/b/c/d/loop
    ...
    ... ''')


    >>> zk.resolve('/top/a/b/c/d')
    '/top/a/b/c/d'

    >>> zk.resolve('/top/a/top/a/b/top/a/b/c/top/a/b/c/d')
    u'/top/a/b/c/d'

    >>> sorted(zk.properties('/top/a/top/a/b/top/a/b/c/top/a/b/c/d').items())
    [(u'loop ->', u'/top/a/b/c/d/loop'), (u'name', u'd'), (u'top ->', u'/top')]

    >>> zk.register_server('/top/a/top/a/b/top/a/b/c/top/a/b/c/d', 'addr')
    >>> sorted(map(str, zk.children('/top/a/top/a/b/top/a/b/c/top/a/b/c/d')))
    ['addr', 'e']

    >>> zk.resolve('/top/a/top/a/b/top/x')
    Traceback (most recent call last):
    ...
    NoNodeException: /top/a/top/a/b/top/x

    >>> zk.resolve('/top/a/b/c/d/loop')
    Traceback (most recent call last):
    ...
    LinkLoop: ('/top/a/b/c/d/loop', u'/top/a/b/c/d/loop')

    >>> zk.resolve('/top/a/loop/b/c/d')
    Traceback (most recent call last):
    ...
    LinkLoop: ('/top/a/loop', u'/top/a/b/loop', u'/top/a/loop')

    >>> zk.close()
    """

def test_ln_target_w_trailing_slash():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> zk.ln('/databases/main', '/fooservice/')
    >>> pprint.pprint(zk.get_properties('/fooservice'))
    {u' ->': u'/databases/main',
     u'database': u'/databases/foomain',
     u'favorite_color': u'red',
     u'threads': 1}

    >>> zk.close()
    """

def test_export_top_w_name():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> print zk.export_tree('/', name='top'),
    /top
      /fooservice
        database = u'/databases/foomain'
        favorite_color = u'red'
        threads = 1
        /providers

    >>> zk.close()
    """

def test_set():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> zk.get('/')[0]
    ''
    >>> zk.set('/', 'a'); zk.get('/')[0]
    0
    'a'

    >>> zk.set('/', 'b', 0)
    Traceback (most recent call last):
    ...
    BadVersionException: bad version

    >>> zk.set('/', 'b'); zk.get('/')[0]
    0
    'b'

    >>> r = zk.aset('/', 'c', -1, check_async()); event.wait(1)
    ... # doctest: +ELLIPSIS
    async callback got (...
    >>> r
    0

    >>> zk.get('/')[0]
    'c'

    >>> r = zk.aset('/', 'd', 0,
    ...             check_async(expected_status=zookeeper.BADVERSION)
    ...             ); event.wait(1)
    async callback got (None,)

    >>> r
    0

    >>> r = zk.aset('/', 'd', 3, check_async()); event.wait(1)
    ... # doctest: +ELLIPSIS
    async callback got (...
    >>> r
    0

>>> time.sleep(1)

    >>> zk.get('/')[0]
    'd'

    >>> zk.close()
    """

def test_delete():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> _ = zk.create('/test', '', zc.zk.OPEN_ACL_UNSAFE)

Synchronous variations:

    >>> _ = zk.create('/test/a', '', zc.zk.OPEN_ACL_UNSAFE)
    >>> _ = zk.set('/test/a', '1')
    >>> _ = zk.set('/test/a', '2')
    >>> zk.delete('/test/a', 0)
    Traceback (most recent call last):
    ...
    BadVersionException: bad version

    >>> zk.get_children('/test')
    ['a']
    >>> _ = zk.delete('/test/a', 2)
    >>> zk.get_children('/test')
    []

    >>> _ = zk.create('/test/a', '', zc.zk.OPEN_ACL_UNSAFE)
    >>> _ = zk.set('/test/a', '1')
    >>> _ = zk.set('/test/a', '2')
    >>> _ = zk.delete('/test/a', -1)
    >>> zk.get_children('/test')
    []

    >>> _ = zk.create('/test/a', '', zc.zk.OPEN_ACL_UNSAFE)
    >>> _ = zk.set('/test/a', '1')
    >>> _ = zk.set('/test/a', '2')
    >>> _ = zk.delete('/test/a')
    >>> zk.get_children('/test')
    []


Asynchronous variations:

    >>> _ = zk.create('/test/a', '', zc.zk.OPEN_ACL_UNSAFE)
    >>> _ = zk.set('/test/a', '1')
    >>> _ = zk.set('/test/a', '2')
    >>> r = zk.adelete('/test/a', 0,
    ...             check_async(expected_status=zookeeper.BADVERSION)
    ...             ); event.wait(1)
    async callback got ()
    >>> r
    0

    >>> zk.get_children('/test')
    ['a']
    >>> r = zk.adelete('/test/a', 2, check_async()); event.wait(1)
    async callback got ()
    >>> r, zk.get_children('/test')
    (0, [])

    >>> _ = zk.create('/test/a', '', zc.zk.OPEN_ACL_UNSAFE)
    >>> _ = zk.set('/test/a', '1')
    >>> _ = zk.set('/test/a', '2')
    >>> r = zk.adelete('/test/a', -1, check_async()); event.wait(1)
    async callback got ()
    >>> r, zk.get_children('/test')
    (0, [])

    >>> _ = zk.create('/test/a', '', zc.zk.OPEN_ACL_UNSAFE)
    >>> _ = zk.set('/test/a', '1')
    >>> _ = zk.set('/test/a', '2')
    >>> r = zk.adelete('/test/a', completion=check_async()); event.wait(1)
    async callback got ()
    >>> r, zk.get_children('/test')
    (0, [])

    >>> zk.close()
    """

def test_set_acl():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> _ = zk.create('/test', '', zc.zk.OPEN_ACL_UNSAFE)
    >>> zk.get_acl('/test')[1] == zc.zk.OPEN_ACL_UNSAFE
    True
    >>> zk.set_acl('/test', 0, [zc.zk.world_permission(17)])
    0
    >>> zk.get_acl('/test')[1] == [zc.zk.world_permission(17)]
    True

    >>> zk.set_acl('/test', 0, [zc.zk.world_permission(17)])
    Traceback (most recent call last):
    ...
    BadVersionException: bad version

    >>> zk.set_acl('/test', 1, [zc.zk.world_permission(18)])
    0
    >>> zk.get_acl('/test')[1] == [zc.zk.world_permission(18)]
    True

    >>> r = zk.aset_acl('/test', 0, [zc.zk.world_permission(19)],
    ...                 check_async(expected_status=zookeeper.BADVERSION)
    ...                 ); event.wait(1)
    async callback got ()
    >>> r
    0

    >>> r = zk.aset_acl('/test', 2, [zc.zk.world_permission(19)],
    ...                 check_async()); event.wait(1)
    async callback got ()
    >>> r
    0
    >>> zk.get_acl('/test')[1] == [zc.zk.world_permission(19)]
    True

    >>> zk.close()
    """

def test_server_registeration_event():
    """
    >>> import sys, zc.zk.event, zope.event
    >>> zc.zk.event.notify is zope.event.notify
    True
    >>> sys.modules['zope.event'] = None
    >>> _ = reload(zc.zk.event)
    >>> zc.zk.event.notify is zope.event.notify
    False
    >>> zc.zk.event.notify is zc.zk.event._noop
    True
    >>> def notify(e):
    ...     print e
    ...     e.properties['test'] = 1
    >>> zc.zk.event.notify = notify

    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> zk.register_server('/fooservice/providers', '1.2.3.4:5678')
    RegisteringServer('1.2.3.4:5678', '/fooservice/providers', {'pid': 1793})

    >>> zk.print_tree('/fooservice/providers')
    /providers
      /1.2.3.4:5678
        pid = 1793
        test = 1

    >>> zk.close()

    >>> sys.modules['zope.event'] = zope.event
    >>> _ = reload(zc.zk.event)
    >>> zc.zk.event.notify is zope.event.notify
    True
    """

def connection_edge_cases():
    """
We can pass a session timeout, and it will be passed to ZooKeeper:

    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181', 4242)
    >>> zk.recv_timeout()
    4242
    >>> zk.close()

Connecting to an invalid address caused a FailedConnect to be raised:

    >>> zc.zk.ZooKeeper('192.0.2.42:2181')
    Traceback (most recent call last):
    ...
    FailedConnect: 192.0.2.42:2181

    """

def register_server_at_root():
    """
    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> zk.register_server('/', 'a:b')
    >>> zk.print_tree() # doctest: +ELLIPSIS
    /a:b
      pid = 2318
    /fooservice
    ...
    >>> zk.close()
    """

event = threading.Event()
def check_async(show=True, expected_status=0):
    event.clear()
    def check(handle, status, *args):
        if show:
            print 'async callback got', args
        event.set()
        zc.zk.testing.assert_(
            status==expected_status,
            "Bad cb status %s" % status,
            error=False)
    return check

def setUpEphemeral_node_recovery_on_session_reestablishment(test):
    zc.zk.testing.setUp(test)
    test.globs['check_async'] = check_async
    test.globs['event'] = event

def setUpREADME(test):
    zc.zk.testing.setUp(test)
    cm = mock.patch('socket.getfqdn')
    m = cm.__enter__()
    m.side_effect = lambda : 'server.example.com'
    test.globs['zc.zk.testing'].append(cm.__exit__)

checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('pid = \d+'), 'pid = 9999'),
    (re.compile("{'pid': \d+}"), 'pid = 9999'),
    (re.compile('/zc\.zk\.testing\.test-root\d+'), ''),
    (re.compile(r'2 None\n4 None'), '4 None\n2 None'),
    ])

def test_suite():
    suite = unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel(
                checker=checker, optionflags=doctest.NORMALIZE_WHITESPACE) +
            manuel.capture.Manuel(),
            'README.txt',
            setUp=setUpREADME, tearDown=zc.zk.testing.tearDown,
            ),
        doctest.DocTestSuite(
            setUp=zc.zk.testing.setUp, tearDown=zc.zk.testing.tearDown,
            checker=checker,
            ),
        ))
    if not zc.zk.testing.testing_with_real_zookeeper():
        suite.addTest(unittest.makeSuite(Tests))
        suite.addTest(unittest.makeSuite(LoggingTests))
        suite.addTest(doctest.DocFileSuite(
            'ephemeral_node_recovery_on_session_reestablishment.test',
            'wait_for_zookeeper.test',
            setUp=setUpEphemeral_node_recovery_on_session_reestablishment,
            tearDown=zc.zk.testing.tearDown,
            checker=checker,
            ))
    return suite
