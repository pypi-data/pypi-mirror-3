# Namespace Trie
# Copyright (C) 2012  Paul Horn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'knutwalker@gmail.com (Paul Horn)'


import copy

try:
    # Python 2.7 and 3.1
    from weakref import WeakSet
except ImportError:
    from weakrefset import WeakSet

try:
    # Python 2.7 and 3.1
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from collections import deque



class String(object):
    """ A weakref-able Proxy class for strings"""
    def __init__(self, s):
        self.__value = s

    #noinspection PyUnusedLocal
    def __call__(self, *args, **kwargs):
        return self.__value

    def __getattr__(self, item):
        return getattr(self.__value, item)

    def __getitem__(self, item):
        return self.__value[item]

    def __str__(self):
        return self.__value

    def __unicode__(self):
        return unicode(self.__value)

    def __repr__(self):
        return "String({0:>s})".format(repr(self.__value))

    def __hash__(self):
        return hash(self.__value)

    def __len__(self):
        return len(self.__value)

    def __cmp__(self, other):
        return cmp(self.__value, other)


class NsNode(OrderedDict):
    pass



class NsTrie(object):
    def __init__(self, trie=None, separator='.'):

        self.__sep = separator
        self.__child_nodes = WeakSet()
        self.__struct = NsNode()

        if trie:
            for val in trie:
                self.add(val)

    def __iter__(self):
        def to_l(node):
            if isinstance(node, NsNode):
                return [(k, to_l(v)) for k,v in node.iteritems()]
            return str(node)
        return iter(to_l(self.__struct))

    def iterdepth(self):
        def it(trie, prepend=''):
            for path, subtrie in trie.iteritems():
                p = self.__sep.join((prepend, path)).lstrip(self.__sep)
                yield p
                if hasattr(subtrie, 'iteritems'):
                    for i in it(subtrie, p):
                        yield i

        return it(self.__struct)

    def iterbreadth(self):
        queue = deque(self.__struct.iteritems())

        while queue:
            prepend, trie = queue.popleft()
            yield prepend
            if hasattr(trie, 'iteritems'):
                for path, subtrie in trie.iteritems():
                    p = self.__sep.join((prepend, path)).lstrip(self.__sep)
                    queue.append((p, subtrie))

    @property
    def child_nodes(self):
        return set(str(s) for s in self.__child_nodes)

    def __repr__(self):
        return "NsTrie({0!r})".format(list(self.child_nodes))

    def __str__(self):
        return repr(self)

    def __unicode__(self):
        return unicode(repr(self))

    def to_dict(self):
        def to_d(d):
            ret = {}
            for k, v in d:
                if isinstance(v, list):
                    v = to_d(v)
                ret[k] = v
            return ret
        return to_d(self)

    def __len__(self):
        return len(self.__child_nodes)

    def __contains__(self, item):
        return String(item) in self.__child_nodes or item in self.iterdepth()

    def has(self, item, child_only=True):
        if child_only:
            return String(item) in self.__child_nodes
        return item in self.iterdepth()

    def __getitem__(self, value):

        path = value.split(self.__sep)
        trie = self.__struct

        for ns in path:
            trie = trie[ns]

        return copy.deepcopy(trie)

    def get(self, value):
        return self[value]

    def __setitem__(self, value, _):

        value = String(value)
        if value in self.__child_nodes:
            return
        self.__child_nodes.add(value)

        trie = self.__struct

        path = value.split(self.__sep)
        node = path.pop()

        for ns in path:
            if ns not in trie or isinstance(trie[ns], String):
                trie[ns] = NsNode()
            trie = trie[ns]

        trie[node] = value

    def add(self, value):
        self[value] = True

    def __delitem__(self, value):

        path = value.split(self.__sep)
        trie = parent = self.__struct

        node = None
        new_path = []

        for ns in path:
            node = ns
            parent = trie
            trie = parent[node]
            new_path.append(node)

        del parent[node]

        new_path.pop()
        if new_path:
            self.add(self.__sep.join(new_path))


    def remove(self, value):
        del self[value]
