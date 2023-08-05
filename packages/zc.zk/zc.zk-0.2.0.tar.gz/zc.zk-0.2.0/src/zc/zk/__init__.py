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
import collections
import json
import logging
import os
import re
import sys
import threading
import weakref
import zc.thread
import zookeeper

logger = logging.getLogger(__name__)

@zc.thread.Thread
def loggingthread():
    r, w = os.pipe()
    zookeeper.set_log_stream(os.fdopen(w, 'w'))
    log = logging.getLogger('ZooKeeper').log
    f = os.fdopen(r)
    levels = dict(ZOO_INFO = logging.INFO,
                  ZOO_WARN = logging.WARNING,
                  ZOO_ERROR = logging.ERROR,
                  ZOO_DEBUG = logging.DEBUG,
                  )
    while 1:
        line = f.readline().strip()
        try:
            if '@' in line:
                level, message = line.split('@', 1)
                level = levels.get(level.split(':')[-1])
            else:
                level = None

            if level is None:
                log(logging.INFO, line)
            else:
                log(level, message)
        except Exception, v:
            logging.getLogger('ZooKeeper').exception("Logging error: %s", v)


def parse_addr(addr):
    host, port = addr.split(':')
    return host, int(port)

def encode(props):
    if len(props) == 1 and 'string_value' in props:
        return props['string_value']

    if props:
        return json.dumps(props, separators=(',',':'))
    else:
        return ''

def decode(sdata, path='?'):
    s = sdata.strip()
    if not s:
        data = {}
    elif s.startswith('{') and s.endswith('}'):
        try:
            data = json.loads(s)
        except:
            logger.exception('bad json data in node at %r', path)
            data = dict(string_value = sdata)
    else:
        data = dict(string_value = sdata)
    return data

def join(*args):
    return '/'.join(args)

def world_permission(perms=zookeeper.PERM_READ):
    return dict(perms=perms, scheme='world', id='anyone')

OPEN_ACL_UNSAFE = [world_permission(zookeeper.PERM_ALL)]
READ_ACL_UNSAFE = [world_permission()]


_text_is_node = re.compile(
    r'/(?P<name>\S+)'
    '(\s*:\s*(?P<type>\S.*))?'
    '$').match
_text_is_property = re.compile(
    r'(?P<name>\S+)'
    '\s*=\s*'
    '(?P<expr>\S.*)'
    '$'
    ).match
_text_is_link = re.compile(
    r'(?P<name>\S+)'
    '\s*->\s*'
    '(?P<target>/\S+)'
    '$'
    ).match

class CancelWatch(Exception):
    pass

class LinkLoop(Exception):
    pass

class FailedConnect(Exception):
    pass

class ZooKeeper:

    def __init__(self, zkaddr=2181, timeout=1):
        if isinstance(zkaddr, int):
            zkaddr = "127.0.0.1:%s" % zkaddr
        self.timeout = timeout
        self.zkaddr = zkaddr
        self.watches = WatchManager()
        self.connected = threading.Event()
        handle = zookeeper.init(zkaddr, self._watch_session)
        self.connected.wait(timeout)
        if not self.connected.is_set():
            zookeeper.close(handle)
            raise FailedConnect(zkaddr)

    handle = None
    def _watch_session(self, handle, event_type, state, path):
        assert event_type == zookeeper.SESSION_EVENT
        assert not path
        if state == zookeeper.CONNECTED_STATE:
            if self.handle is None:
                self.handle = handle
                for watch in self.watches.clear():
                    self._watch(watch, False)
            else:
                assert handle == self.handle
            self.connected.set()
            logger.info('connected %s', handle)
        elif state == zookeeper.CONNECTING_STATE:
            self.connected.clear()
        elif state == zookeeper.EXPIRED_SESSION_STATE:
            self.connected.clear()
            zookeeper.close(self.handle)
            self.handle = None
            zookeeper.init(self.zkaddr, self._watch_session)
        else:
            logger.critical('unexpected session event %s %s', handle, state)

    def register_server(self, path, addr, **kw):
        kw['pid'] = os.getpid()
        if not isinstance(addr, str):
            addr = '%s:%s' % addr
        self.connected.wait(self.timeout)
        path = self.resolve(path)
        zookeeper.create(self.handle, path + '/' + addr, encode(kw),
                         [world_permission()], zookeeper.EPHEMERAL)

    def _watch(self, watch, wait=True):
        event_type = watch.event_type
        if wait:
            self.connected.wait(self.timeout)
        watch.real_path = real_path = self.resolve(watch.path)
        key = event_type, real_path
        if self.watches.add(key, watch):
            try:
                self._watchkey(key)
            except zookeeper.ConnectionLossException:
                # We lost a race here. We got disconnected between
                # when we resolved the watch path and the time we set
                # the watch. This is very unlikely.
                watches = set(self.watches.pop(key))
                for w in watches:
                    w._deleted()
                if watch in watches:
                    watches.remove(watch)
                if watches:
                    # OMG, how unlucky can we be?
                    # someone added a watch between the time we added
                    # the key and failed to add the watch in zookeeper.
                    logger.critical('lost watches %r', watches)
                raise
        else:
            # We already had a watch for the key.  We need to pass this one
            # it's data.
            zkfunc = getattr(zookeeper, self.__zkfuncs[event_type])
            watch._notify(zkfunc(self.handle, real_path))

    __zkfuncs = {
        zookeeper.CHANGED_EVENT: 'get',
        zookeeper.CHILD_EVENT: 'get_children',
        }
    def _watchkey(self, key):
        event_type, real_path = key
        zkfunc = getattr(zookeeper, self.__zkfuncs[event_type])

        def handler(h, t, state, p, reraise=False):
            try:
                assert h == self.handle
                assert state == zookeeper.CONNECTED_STATE
                assert p == real_path
                if key not in self.watches:
                    return

                if t == zookeeper.DELETED_EVENT:
                    self._rewatch(key)
                else:
                    assert t == event_type
                    try:
                        v = zkfunc(self.handle, real_path, handler)
                    except zookeeper.NoNodeException:
                        self._rewatch(key)
                    else:
                        for watch in self.watches.watches(key):
                            watch._notify(v)
            except:
                logger.exception("%s(%s) handler failed",
                                 self.__zkfuncs[event_type], real_path)
                if reraise:
                    raise

        handler(self.handle, event_type, self.state, real_path, True)

    def _rewatch(self, key):
        event_type = key[0]
        for watch in self.watches.pop(key):
            try:
                real_path = self.resolve(watch.path)
            except (zookeeper.NoNodeException, LinkLoop):
                logger.exception("%s path went away", watch)
                watch._deleted()
            else:
                self._watch(watch, False)

    def children(self, path):
        return Children(self, path)

    def get_properties(self, path):
        return decode(self.get(path)[0])

    def properties(self, path):
        return Properties(self, path)

    def import_tree(self, text, path='/', trim=False, acl=OPEN_ACL_UNSAFE,
                    dry_run=False):
        # Step 1, build up internal tree repesentation:
        root = _Tree()
        indents = [(-1, root)] # sorted [(indent, node)]
        lineno = 0
        for line in text.split('\n'):
            lineno += 1
            line = line.rstrip()
            if not line:
                continue
            data = line.strip()
            if data[0] == '#':
                continue
            indent = len(line) - len(data)

            m = _text_is_property(data)
            if m:
                expr = m.group('expr')
                try:
                    data = eval(expr, {})
                except Exception, v:
                    raise ValueError("Error %s in expression: %r" % (v, expr))
                data = m.group('name'), data
            else:
                m = _text_is_link(data)
                if m:
                    data = (m.group('name') + ' ->'), m.group('target')
                else:
                    m = _text_is_node(data)
                    if m:
                        data = _Tree(m.group('name'))
                        if m.group('type'):
                            data.properties['type'] = m.group('type')
                    else:
                        if '->' in data:
                            raise ValueError(lineno, data, "Bad link format")
                        else:
                            raise ValueError(lineno, data, "Unrecognized data")

            if indent > indents[-1][0]:
                if not isinstance(indents[-1][1], _Tree):
                    raise ValueError(
                        lineno, line,
                        "Can't indent under properties")
                indents.append((indent, data))
            else:
                while indent < indents[-1][0]:
                    indents.pop()

                if indent > indents[-1][0]:
                    raise ValueError(lineno, data, "Invalid indentation")

            if isinstance(data, _Tree):
                children = indents[-2][1].children
                if data.name in children:
                    raise ValueError(lineno, data, 'duplicate node')
                children[data.name] = data
                indents[-1] = indent, data
            else:
                if indents[-2][1] is root:
                    raise ValueError("Can't above imported nodes.")
                properties = indents[-2][1].properties
                name, value = data
                if name in properties:
                    raise ValueError(lineno, data, 'duplicate property')
                properties[name] = value

        # Step 2 Create The nodes
        while path.endswith('/'):
            path = path[:-1] # Mainly to deal w root: /
        self._import_tree(path, root, acl, trim, dry_run, True)

    def _import_tree(self, path, node, acl, trim, dry_run, top=False):
        self.connected.wait(self.timeout)
        if not top:
            new_children = set(node.children)
            for name in self.get_children(path):
                if name in new_children:
                    continue
                cpath = join(path, name)
                if trim:
                    self.delete_recursive(cpath, dry_run)
                else:
                    print 'extra path not trimmed:', cpath

        for name, child in node.children.iteritems():
            cpath = path + '/' + name
            data = encode(child.properties)
            if self.exists(cpath):
                if dry_run:
                    new = child.properties
                    old = self.get_properties(cpath)
                    old = decode(self.get(cpath)[0])
                    for n, v in sorted(old.items()):
                        if n not in new:
                            if n.endswith(' ->'):
                                print '%s remove link %s %s' % (cpath, n, v)
                            else:
                                print '%s remove property %s = %s' % (
                                    cpath, n, v)
                        elif new[n] != v:
                            if n.endswith(' ->'):
                                print '%s %s link change from %s to %s' % (
                                    cpath, n[:-3], v, new[n])
                            else:
                                print '%s %s change from %s to %s' % (
                                    cpath, n, v, new[n])
                    for n, v in sorted(new.items()):
                        if n not in old:
                            if n.endswith(' ->'):
                                print '%s add link %s %s' % (cpath, n, v)
                            else:
                                print '%s add property %s = %s' % (
                                    cpath, n, v)
                else:
                    self.set(cpath, data)
                    meta, oldacl = self.get_acl(cpath)
                    if acl != oldacl:
                        self.set_acl(cpath, meta['aversion'], acl)
            else:
                if dry_run:
                    print 'add', cpath
                    continue
                else:
                    self.create(cpath, data, acl)
            self._import_tree(cpath, child, acl, trim, dry_run)

    def delete_recursive(self, path, dry_run=False):
        for name in self.get_children(path):
            self.delete_recursive(join(path, name))

        if self.get_children(path):
            print "%s not deleted due to ephemeral descendent." % path
            return

        ephemeral = self.get(path)[1]['ephemeralOwner']
        if dry_run:
            if ephemeral:
                print "wouldn't delete %s because it's ephemeral." % path
            else:
                print "would delete %s." % path
        else:
            if ephemeral:
                print "Not deleting %s because it's ephemeral." % path
            else:
                logger.info('deleting %s', path)
                self.delete(path)

    def export_tree(self, path='/', ephemeral=False, name=None):
        output = []
        out = output.append
        self.connected.wait(self.timeout)

        def export_tree(path, indent, name=None):
            children = self.get_children(path)
            if path == '/':
                path = ''
                if 'zookeeper' in children:
                    children.remove('zookeeper')
                if name is not None:
                    out(indent + '/' + name)
                    indent += '  '
            else:
                data, meta = self.get(path)
                if meta['ephemeralOwner'] and not ephemeral:
                    return
                if name is None:
                    name = path.rsplit('/', 1)[1]
                properties = decode(data)
                type_ = properties.pop('type', None)
                if type_:
                    name += ' : '+type_
                out(indent + '/' + name)
                indent += '  '
                links = []
                for i in sorted(properties.iteritems()):
                    if i[0].endswith(' ->'):
                        links.append(i)
                    else:
                        out(indent+"%s = %r" % i)
                for i in links:
                    out(indent+"%s %s" % i)

            for name in children:
                export_tree(path+'/'+name, indent)

        export_tree(path, '', name)
        return '\n'.join(output)+'\n'

    def resolve(self, path, seen=()):
        if self.exists(path):
            return path
        if path in seen:
            seen += (path,)
            raise LinkLoop(seen)

        try:
            base, name = path.rsplit('/', 1)
            base = self.resolve(base, seen)
            newpath = base + '/' + name
            if self.exists(newpath):
                return newpath
            props = self.get_properties(base)
            newpath = props.get(name+' ->')
            if not newpath:
                raise zookeeper.NoNodeException()

            seen += (path,)
            return self.resolve(newpath, seen)
        except zookeeper.NoNodeException:
            raise zookeeper.NoNodeException(path)

    def _set(self, path, data):
        self.connected.wait(self.timeout)
        return zookeeper.set(self.handle, path, data)


    def ln(self, target, source):
        base, name = source.rsplit('/', 1)
        if target[-1] == '/':
            target += name
        properties = self.get_properties(base)
        properties[name+' ->'] = target
        self._set(base, encode(properties))

    def close(self):
        zookeeper.close(self.handle)
        del self.handle

    @property
    def state(self):
        if self.handle is None:
            return zookeeper.CONNECTING_STATE
        return zookeeper.state(self.handle)


def _make_method(name):
    return (lambda self, *a, **kw:
            getattr(zookeeper, name)(self.handle, *a, **kw))

for name in (
    'acreate', 'add_auth', 'adelete', 'aexists', 'aget', 'aget_acl',
    'aget_children', 'aset', 'aset_acl', 'async', 'client_id',
    'create', 'delete', 'exists', 'get', 'get_acl',
    'get_children', 'is_unrecoverable', 'recv_timeout', 'set',
    'set2', 'set_acl', 'set_debug_level', 'set_log_stream',
    'set_watcher', 'zerror',
    ):
    setattr(ZooKeeper, name, _make_method(name))

del _make_method

class WatchManager:
    # Manage {key -> w{watches}} in a thread-safe manner.
    # (And also provide a hard set to allow nodeinfos w callbacks
    #  to keep themselves around.)

    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

        def _remove(ref, selfref=weakref.ref(self)):
            self = selfref()
            if self is None:
                return
            key = ref.key
            with self.lock:
                refs = self.data.get(key, ())
                if ref in refs:
                    refs.remove(ref)
                    if not refs:
                        del self.data[key]

        self._remove = _remove

    def __len__(self):
        with self.lock:
            return sum(
                len([r for r in refs if r() is not None])
                for refs in self.data.itervalues()
                )

    def __contains__(self, key):
        with self.lock:
            return key in self.data

    def add(self, key, value):
        ref = weakref.KeyedRef(value, self._remove, key)
        newkey = False
        with self.lock:
            try:
                refs = self.data[key]
            except KeyError:
                self.data[key] = refs = set()
                newkey = True
            refs.add(ref)
        return newkey

    def pop(self, key):
        with self.lock:
            watches = [ref() for ref in self.data.pop(key, ())]

        for watch in watches:
            if watch is not None:
                yield watch

    def watches(self, key):
        with self.lock:
            watches = [ref() for ref in self.data.get(key, ())]

        for watch in watches:
            if watch is not None:
                yield watch

    def clear(self):
        # Clear data and return an iterator on the old values
        with self.lock:
            old = self.data
            self.data = {}

        for refs in old.itervalues():
            for ref in refs:
                v = ref()
                if v is not None:
                    yield v


class NodeInfo:

    def __init__(self, session, path):
        self.session = session
        self.path = path
        self.callbacks = []
        session._watch(self)

    def setData(self, data):
        self.data = data

    deleted = False
    def _deleted(self):
        self.deleted = True
        self.data = {}
        for callback in self.callbacks:
            try:
                callback()
            except TypeError:
                pass
            except:
                logger.exception('Error %r calling %r', self, callback)

    def __repr__(self):
        return "%s%s.%s(%s, %s)" % (
            self.deleted and 'DELETED: ' or '',
            self.__class__.__module__, self.__class__.__name__,
            self.session.handle, self.path)

    def _notify(self, data):
        self.setData(data)
        for callback in list(self.callbacks):
            try:
                callback(self)
            except Exception, v:
                self.callbacks.remove(callback)
                if isinstance(v, CancelWatch):
                    logger.debug("cancelled watch(%r, %r)", self, callback)
                else:
                    logger.exception("watch(%r, %r)", self, callback)

    def __call__(self, func):
        func(self)
        self.callbacks.append(func)
        return self

    def __iter__(self):
        return iter(self.data)

class Children(NodeInfo):

    event_type = zookeeper.CHILD_EVENT

class Properties(NodeInfo, collections.Mapping):

    event_type = zookeeper.CHANGED_EVENT

    def setData(self, data):
        sdata, self.meta_data = data
        self.data = decode(sdata, self.path)

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def copy(self):
        return self.data.copy()

    def _set(self, data):
        self.data = data
        zookeeper.set(self.session.handle, self.path, encode(data))

    def set(self, data=None, **properties):
        data = data and dict(data) or {}
        data.update(properties)
        self._set(data)

    def update(self, data=None, **properties):
        d = self.data.copy()
        if data:
            d.update(data)
        d.update(properties)
        self._set(d)

    def __hash__(self):
        # Gaaaa, collections.Mapping
        return hash(id(self))

class _Tree:
    # Internal tree rep for import/export

    def __init__(self, name='', properties=None, **children):
        self.name = name
        self.properties = properties or {}
        self.children = children
        for name, child in children.iteritems():
            child.name = name
