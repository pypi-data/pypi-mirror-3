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
"""Testing support

This module provides a mock of zookeeper needed to test use of zc.zk.
It's especially useful for testing packages that build on zc.zk.

It provides setUp and tearDown functions that can be used with
doctests or with regular ```unittest`` tests.
"""
import json
import mock
import os
import random
import re
import sys
import threading
import time
import traceback
import zc.zk
import zc.thread
import zookeeper

__all__ = ['assert_', 'setUp', 'tearDown', 'testing_with_real_zookeeper']

def assert_(cond, mess='', error=True):
    """A simple assertion function.

    If ``error``, raise an AssertionError if the assertion fails,
    otherwise, print a message.
    """
    if not cond:
        if error:
            raise AssertionError(mess)
        else:
            print 'assertion failed: ', mess

def wait_until(func=None, timeout=9):
    """Wait until a function returns true.

    Raise an AssertionError on timeout.
    """
    if func():
        return
    deadline = time.time()+timeout
    while not func():
        time.sleep(.01)
        if time.time() > deadline:
            raise AssertionError('timeout')

def setup_tree(tree, connection_string, root='/test-root'):
    zk = zc.zk.ZooKeeper(connection_string)
    if zk.exists(root):
        zk.delete_recursive(root)
    zk.create(root, '', zc.zk.OPEN_ACL_UNSAFE)
    zk.import_tree(tree or """
    /fooservice
      /providers
      database = '/databases/foomain'
      threads = 1
      favorite_color = 'red'
    """, root)
    zk.close()

def testing_with_real_zookeeper():
    """Test whether we're testing with a real ZooKeeper server.

    The real connection string is returned.
    """
    return os.environ.get('TEST_ZOOKEEPER_CONNECTION')

def setUp(test, tree=None, connection_string='zookeeper.example.com:2181'):
    """Set up zookeeper emulation.

    Standard (mock) testing
    -----------------------

    The first argument is a test case object (either doctest or unittest).

    You can optionally pass:

    tree
       An initial ZooKeeper tree expressed as an import string.
       If not passed, an initial tree will be created with examples
       used in the zc.zk doctests.

    connection_string
       The connection string to use for the emulation server. This
       defaults to 'zookeeper.example.com:2181'.

    Testing with a real ZooKeeper Server
    ------------------------------------

    You can test against a real ZooKeeper server, instead of a mock by
    setting the environment variable TEST_ZOOKEEPER_CONNECTION to the
    connection string of a test server.

    The tests will create a top-level node with a random name that
    starts with 'zc.zk.testing.test-roo', and use that as the virtual
    root for your tests.  Although this is the virtual root, of the
    zookeeper tree in your tests, the presense of the node may be
    shown in your tests. In particularm ``zookeeper.create`` returns
    the path created and the string returned is real, not virtual.
    This node is cleaned up by the ``tearDown``.

    A doctest can determine if it's running with a stub ZooKeeper by
    checking whether the value of the ZooKeeper gloval variable is None.
    A regular unit test can check the ZooKeeper test attribute.
    """

    globs = getattr(test, 'globs', test.__dict__)
    teardowns = []
    faux_zookeeper = None
    real_zk = testing_with_real_zookeeper()
    if real_zk:
        test_root = '/zc.zk.testing.test-root%s' % random.randint(0, sys.maxint)
        globs['/zc.zk.testing.test-root'] = test_root
        setup_tree(tree, real_zk, test_root)

        orig_init = zookeeper.init
        cm = mock.patch('zookeeper.init')
        m = cm.__enter__()
        def init(addr, watch=None, session_timeout=1000):
            if addr != connection_string:
                return orig_init(addr, watch, session_timeout)
            else:
                return orig_init(real_zk+test_root, watch, session_timeout)
        m.side_effect = init
        teardowns.append(cm.__exit__)

        teardowns.append(lambda : setattr(zc.zk.ZooKeeper, 'test_sleep', 0))
        zc.zk.ZooKeeper.test_sleep = .01
        time.sleep(float(os.environ.get('TEST_ZOOKEEPER_SLEEP', 0)))

    else:
        if tree:
            faux_zookeeper = ZooKeeper(connection_string, Node())
        else:
            faux_zookeeper = ZooKeeper(
                connection_string,
                Node(
                    fooservice = Node(
                        json.dumps(dict(
                            database = "/databases/foomain",
                            threads = 1,
                            favorite_color= "red",
                            )),
                        providers = Node()
                        ),
                    zookeeper = Node('', quota=Node()),
                    ),
                )
        for name in ZooKeeper.__dict__:
            if name[0] == '_':
                continue
            cm = mock.patch('zookeeper.'+name)
            m = cm.__enter__()
            m.side_effect = getattr(faux_zookeeper, name)
            teardowns.append(cm.__exit__)

        if tree:
            zk = zc.zk.ZooKeeper(connection_string)
            zk.import_tree(tree)
            zk.close()

    globs['wait_until'] = wait_until
    globs['zc.zk.testing'] = teardowns
    globs['ZooKeeper'] = faux_zookeeper
    globs.setdefault('assert_', assert_)

def tearDown(test):
    """The matching tearDown for setUp.

    The single argument is the test case passed to setUp.
    """
    globs = getattr(test, 'globs', test.__dict__)
    for cm in globs['zc.zk.testing']:
        cm()
    real_zk = testing_with_real_zookeeper()
    if real_zk:
        zk = zc.zk.ZooKeeper(real_zk)
        root = globs['/zc.zk.testing.test-root']
        if zk.exists(root):
            zk.delete_recursive(root)
        zk.close()


class Session:

    def __init__(self, zk, handle, watch=None, session_timeout=None):
        self.zk = zk
        self.handle = handle
        self.nodes = set() # ephemeral nodes
        self.add = self.nodes.add
        self.remove = self.nodes.remove
        self.watch = watch
        self.state = zookeeper.CONNECTING_STATE
        self.session_timeout = session_timeout

    def connect(self):
        self.newstate(zookeeper.CONNECTED_STATE)

    def disconnect(self):
        self.newstate(zookeeper.CONNECTING_STATE)

    def expire(self):
        self.zk._clear_session(
            self, zookeeper.SESSION_EVENT, zookeeper.EXPIRED_SESSION_STATE)
        self.newstate(zookeeper.EXPIRED_SESSION_STATE)

    def newstate(self, state):
        self.state = state
        if self.watch is not None:
            self.watch(self.handle, zookeeper.SESSION_EVENT, state, '')

    def check(self):
        if self.state == zookeeper.CONNECTING_STATE:
            raise zookeeper.ConnectionLossException()
        elif self.state == zookeeper.EXPIRED_SESSION_STATE:
            raise zookeeper.SessionExpiredException()
        elif self.state != zookeeper.CONNECTED_STATE:
            raise AssertionError('Invalid state')

exception_codes = {
    zookeeper.ApiErrorException: zookeeper.APIERROR,
    zookeeper.AuthFailedException: zookeeper.AUTHFAILED,
    zookeeper.BadArgumentsException: zookeeper.BADARGUMENTS,
    zookeeper.BadVersionException: zookeeper.BADVERSION,
    zookeeper.ClosingException: zookeeper.CLOSING,
    zookeeper.ConnectionLossException: zookeeper.CONNECTIONLOSS,
    zookeeper.DataInconsistencyException: zookeeper.DATAINCONSISTENCY,
    zookeeper.InvalidACLException: zookeeper.INVALIDACL,
    zookeeper.InvalidCallbackException: zookeeper.INVALIDCALLBACK,
    zookeeper.InvalidStateException: zookeeper.INVALIDSTATE,
    zookeeper.MarshallingErrorException: zookeeper.MARSHALLINGERROR,
    zookeeper.NoAuthException: zookeeper.NOAUTH,
    zookeeper.NoChildrenForEphemeralsException:
    zookeeper.NOCHILDRENFOREPHEMERALS,
    zookeeper.NoNodeException: zookeeper.NONODE,
    zookeeper.NodeExistsException: zookeeper.NODEEXISTS,
    zookeeper.NotEmptyException: zookeeper.NOTEMPTY,
    zookeeper.NothingException: zookeeper.NOTHING,
    zookeeper.OperationTimeoutException: zookeeper.OPERATIONTIMEOUT,
    zookeeper.RuntimeInconsistencyException: zookeeper.RUNTIMEINCONSISTENCY,
    zookeeper.SessionExpiredException: zookeeper.SESSIONEXPIRED,
    zookeeper.SessionMovedException: zookeeper.SESSIONMOVED,
    zookeeper.SystemErrorException: zookeeper.SYSTEMERROR,
    zookeeper.UnimplementedException: zookeeper.UNIMPLEMENTED,
}

badpath = re.compile(r'(^([^/]|$))|(/\.\.?(/|$))|(./$)').search

class ZooKeeper:

    def __init__(self, connection_string, tree):
        self.connection_strings = set([connection_string])
        self.root = tree
        self.sessions = {}
        self.lock = threading.RLock()
        self.failed = {}

    def init(self, addr, watch=None, session_timeout=4000):
        with self.lock:
            handle = 0
            while handle in self.sessions:
                handle += 1
            self.sessions[handle] = Session(
                self, handle, watch, session_timeout)
            if addr in self.connection_strings:
                self.sessions[handle].connect()
            else:
                self.failed.setdefault(addr, set()).add(handle)
            return handle

    def _allow_connection(self, connection_string):
        self.connection_strings.add(connection_string)
        for handle in self.failed.pop(connection_string, ()):
            if handle in self.sessions:
                self.sessions[handle].connect()

    def _check_handle(self, handle, checkstate=True):
        try:
            session = self.sessions[handle]
        except KeyError:
            raise zookeeper.ZooKeeperException('handle out of range')
        if checkstate:
            session.check()
        return session

    def _traverse(self, path):
        node = self.root
        for name in path.split('/')[1:]:
            if not name:
                continue
            try:
                node = node.children[name]
            except KeyError:
                raise zookeeper.NoNodeException('no node')

        return node

    def _clear_session(self, session, event=None, state=None):
        with self.lock:
            self.root.clear_watchers(session.handle, event, state)
            for path in list(session.nodes):
                self._delete(session.handle, path)

    def _doasync(self, completion, handle, nreturn, func, *args):
        if completion is None:
            return func(*args)

        if isinstance(nreturn, int):
            nerror = nreturn
        else:
            nreturn, nerror = nreturn

        @zc.thread.Thread
        def doasync():
            try:
                # print 'doasync', func, args
                with self.lock:
                    status = 0
                    try:
                        r = func(*args)
                    except Exception, v:
                        status = exception_codes.get(v.__class__, -1)
                        r = (None, ) * nerror
                    if not isinstance(r, tuple):
                        if nreturn == 1:
                            r = (r, )
                        else:
                            r = ()
                    completion(*((handle, status) + r))
            except:
                traceback.print_exc(file=sys.stdout)

        return 0

    def close(self, handle):
        with self.lock:
            self._clear_session(self._check_handle(handle, False))
            del self.sessions[handle]

    def state(self, handle):
        with self.lock:
            return self._check_handle(handle, False).state

    def create(self, handle, path, data, acl, flags=0):
        with self.lock:
            self._check_handle(handle)
            base, name = path.rsplit('/', 1)
            if base.endswith('/'):
                raise zookeeper.BadArgumentsException('bad arguments')
            node = self._traverse(base)
            if name in node.children:
                raise zookeeper.NodeExistsException()
            node.children[name] = newnode = Node(data)
            newnode.acl = acl
            newnode.flags = flags
            node.children_changed(handle, zookeeper.CONNECTED_STATE, base)
            if flags & zookeeper.EPHEMERAL:
                self.sessions[handle].add(path)
            return path

    def acreate(self, handle, path, data, acl, flags=0, completion=None):
        return self._doasync(completion, handle, 1,
                            self.create, handle, path, data, acl, flags)

    def _delete(self, handle, path, version=-1):
        node = self._traverse(path)
        if version != -1 and node.version != version:
            raise zookeeper.BadVersionException('bad version')
        if node.children:
            raise zookeeper.NotEmptyException('not empty')
        base, name = path.rsplit('/', 1)
        bnode = self._traverse(base)
        del bnode.children[name]
        node.deleted(handle, zookeeper.CONNECTED_STATE, path)
        bnode.children_changed(handle, zookeeper.CONNECTED_STATE, base)
        if path in self.sessions[handle].nodes:
            self.sessions[handle].remove(path)

    def delete(self, handle, path, version=-1):
        with self.lock:
            self._check_handle(handle)
            self._delete(handle, path, version)
        return 0

    def adelete(self, handle, path, version=-1, completion=None):
        return self._doasync(completion, handle, 0,
                             self.delete, handle, path, version)

    def exists(self, handle, path, watch=None):
        if watch is not None:
            raise TypeError('exists watch not supported')
        if badpath(path):
            raise zookeeper.BadArgumentsException('bad argument')
        with self.lock:
            self._check_handle(handle)
            try:
                self._traverse(path)
                return True
            except zookeeper.NoNodeException:
                return False

    def aexists(self, handle, path, watch=None, completion=None):
        return self._doasync(completion, handle, 1,
                             self.exists, handle, path, watch)

    def get_children(self, handle, path, watch=None):
        with self.lock:
            self._check_handle(handle)
            node = self._traverse(path)
            if watch:
                node.child_watchers += ((handle, watch), )
            return list(node.children)

    def aget_children(self, handle, path, watch=None, completion=None):
        return self._doasync(completion, handle, 1,
                             self.get_children, handle, path, watch)

    def get(self, handle, path, watch=None):
        with self.lock:
            self._check_handle(handle)
            node = self._traverse(path)
            if watch:
                node.watchers += ((handle, watch), )
            return node.data, node.meta()

    def aget(self, handle, path, watch=None, completion=None):
        return self._doasync(completion, handle, 2,
                             self.get, handle, path, watch)

    def recv_timeout(self, handle):
        with self.lock:
            return self._check_handle(handle, False).session_timeout

    def set(self, handle, path, data, version=-1, async=False):
        with self.lock:
            self._check_handle(handle)
            node = self._traverse(path)
            if version != -1 and node.version != version:
                raise zookeeper.BadVersionException('bad version')
            node.data = data
            node.changed(handle, zookeeper.CONNECTED_STATE, path)
            if async:
                return node.meta()
            else:
                return 0

    def aset(self, handle, path, data, version=-1, completion=None):
        return self._doasync(completion, handle, 1,
                             self.set, handle, path, data, version, True)

    def get_acl(self, handle, path):
        with self.lock:
            self._check_handle(handle)
            node = self._traverse(path)
            return node.meta(), node.acl

    def aget_acl(self, handle, path, completion=None):
        return self._doasync(completion, handle,
                             self.get_acl, handle, path)

    def set_acl(self, handle, path, aversion, acl):
        with self.lock:
            self._check_handle(handle)
            node = self._traverse(path)
            if aversion != node.aversion:
                raise zookeeper.BadVersionException("bad version")
            node.aversion += 1
            node.acl = acl

            return 0

    def aset_acl(self, handle, path, aversion, acl, completion=None):
        return self._doasync(completion, handle, 0,
                             self.set_acl, handle, path, aversion, acl)

class Node:
    watchers = child_watchers = ()
    flags = 0
    version = aversion = cversion = 0
    acl = zc.zk.OPEN_ACL_UNSAFE

    def meta(self):
        return dict(
            version = self.version,
            aversion = self.aversion,
            cversion = self.cversion,
            ctime = self.ctime,
            mtime = self.mtime,
            numChildren = len(self.children),
            dataLength = len(self.data),
            ephemeralOwner=(1 if self.flags & zookeeper.EPHEMERAL else 0),
            )

    def __init__(self, data='', **children):
        self.data = data
        self.children = children
        self.ctime = self.mtime = time.time()

    def children_changed(self, handle, state, path):
        watchers = self.child_watchers
        self.child_watchers = ()
        for h, w in watchers:
            w(h, zookeeper.CHILD_EVENT, state, path)
        self.cversion += 1

    def changed(self, handle, state, path):
        watchers = self.watchers
        self.watchers = ()
        for h, w in watchers:
            w(h, zookeeper.CHANGED_EVENT, state, path)
        self.version += 1
        self.mtime = time.time()

    def deleted(self, handle, state, path):
        watchers = self.watchers
        self.watchers = ()
        for h, w in watchers:
            w(h, zookeeper.DELETED_EVENT, state, path)
        watchers = self.child_watchers
        self.watchers = ()
        for h, w in watchers:
            w(h, zookeeper.DELETED_EVENT, state, path)

    def clear_watchers(self, handle, event, state, path='/'):
        if state is not None:
            for (h, w) in self.watchers:
                if h == handle:
                    w(h, event, state, path)
            for (h, w) in self.child_watchers:
                if h == handle:
                    w(h, event, state, path)

        self.watchers = tuple(
            (h, w) for (h, w) in self.watchers
            if h != handle
            )
        self.child_watchers = tuple(
            (h, w) for (h, w) in self.child_watchers
            if h != handle
            )
        for name, child in self.children.items():
            child.clear_watchers(handle, event, state, path + '/' + name)
