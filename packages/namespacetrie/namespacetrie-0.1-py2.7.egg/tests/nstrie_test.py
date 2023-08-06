#!/usr/bin/env python
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


import weakref
from namespacetrie.nstrie import NsTrie, String, NsNode

import unittest


class StringTestCase(unittest.TestCase):

    def setUp(self):
        self.s = 'foo'
        self.S = String(self.s)

    def test_init(self):
        S = String('bar')

        self.assertIs('bar', S._String__value)
        self.assertFalse(self.s is self.S)

    def test_call(self):
        self.assertIs(self.s, self.S())

    def test_getattr(self):
        for attr in dir(self.s):
            if not attr.startswith('_') and not attr.endswith('_'):
                self.assertEqual(getattr(self.s, attr), getattr(self.S, attr))

    def test_getitem(self):
        for i in xrange(len(self.s)):
            self.assertIs(self.s[i], self.S[i])

    def test_str(self):
        self.assertIs(self.s, str(self.S))

    def test_unicode(self):
        self.assertEqual(unicode(self.s), unicode(self.S))

    def test_repr(self):
        expected = 'String(' + repr(self.s) + ')'
        self.assertEqual(expected, repr(self.S))

    def test_hash(self):
        self.assertEqual(hash(self.s), hash(self.S))

    def test_len(self):
        self.assertIs(len(self.s), len(self.S))

    def test_cmp(self):
        self.assertEqual(0, cmp(self.S, self.s))
        self.assertFalse(self.S < self.s)
        self.assertFalse(self.S > self.s)
        self.assertTrue(self.S == self.s)

    def test_weakrefable(self):
        s = String('bar')
        try:
            r = weakref.ref(s)
        except TypeError:
            self.fail("Creating a weak reference of String should not throw "
                      "a TypeError")

        self.assertEqual(s, r())
        del s
        self.assertIs(r(), None)



class NsTrieTestCase(unittest.TestCase):

    def to_py(self, node):
        if isinstance(node, NsNode):
            return dict((k,self.to_py(v)) for k,v in node.iteritems())
        if isinstance(node, (list, tuple, set)):
            t = type(node)
            o = t.__new__(t)
            o.__init__(self.to_py(i) for i in node)
            return o
        return str(node)

    #noinspection PyUnresolvedReferences
    def test_init(self):
        trie = NsTrie()

        self.assertEqual(trie._NsTrie__child_nodes, weakref.WeakSet())
        self.assertEqual(trie._NsTrie__struct, NsNode())

    #noinspection PyUnresolvedReferences
    def test_add(self):
        trie1 = NsTrie()
        trie1.add('com.example.foo')

        trie2 = NsTrie()
        trie2['com.example.foo'] = True

        expected = {
            'com': {
                'example': {
                    'foo': 'com.example.foo'
                }
            }
        }

        self.assertDictEqual(expected, self.to_py(trie1._NsTrie__struct))
        self.assertDictEqual(expected, self.to_py(trie2._NsTrie__struct))

        expected = set(('com.example.foo',))

        self.assertSetEqual(expected, set(self.to_py(s) for s in trie1._NsTrie__child_nodes))
        self.assertSetEqual(expected, set(self.to_py(s) for s in trie2._NsTrie__child_nodes))


    def test_iter(self):

        modules = [
            'com.example.foo.Foo',
            'com.example.foo.Bar',
            'com.example.Baz',
            'com.example.baz.Boo',
            'org.example.foo'
        ]

        trie = NsTrie(modules)

        expected = [
            ('com', [
                ('example', [
                    ('foo', [
                        ('Foo', 'com.example.foo.Foo'),
                        ('Bar', 'com.example.foo.Bar'),
                    ]),
                    ('Baz', 'com.example.Baz'),
                    ('baz', [
                        ('Boo', 'com.example.baz.Boo'),
                    ]),
                ]),
            ]),
            ('org', [
                ('example', [
                    ('foo', 'org.example.foo'),
                ]),
            ]),
        ]

        actual = list(iter(trie))

        self.assertListEqual(actual, expected,
                         msg="iteration should be in insertion order and "
                             "depth first")

    def test_iterdepth(self):

        modules = [
            'com.example.foo.Foo',
            'com.example.foo.Bar',
            'com.example.Baz',
            'com.example.baz.Boo',
            'org.example.foo'
        ]

        trie = NsTrie(modules)

        expected = [
            'com',
            'com.example',
            'com.example.foo',
            'com.example.foo.Foo',
            'com.example.foo.Bar',
            'com.example.Baz',
            'com.example.baz',
            'com.example.baz.Boo',
            'org',
            'org.example',
            'org.example.foo',
        ]

        actual = list(trie.iterdepth())

        self.assertListEqual(actual, expected,
                         msg="iterdepth should behave exactly the same as "
                             "default iteration")

    def test_iterbreadth(self):

        modules = [
            'com.example.foo.Foo',
            'com.example.foo.Bar',
            'com.example.Baz',
            'com.example.baz.Boo',
            'org.example.foo'
        ]

        trie = NsTrie(modules)

        expected = [
            'com',
            'org',
            'com.example',
            'org.example',
            'com.example.foo',
            'com.example.Baz',
            'com.example.baz',
            'org.example.foo',
            'com.example.foo.Foo',
            'com.example.foo.Bar',
            'com.example.baz.Boo',
        ]

        actual = list(trie.iterbreadth())

        self.assertListEqual(actual, expected,
                         msg="breadth first iteration should be level-wise "
                             "and respect insertion order")

    def test_child_nodes(self):

        expected = set(('com.example.foo',))
        trie = NsTrie(expected)
        self.assertSetEqual(expected, trie.child_nodes)

        trie.child_nodes.discard('com.example.foo')

        self.assertSetEqual(expected, trie.child_nodes,
                            msg="Manipulating the returnvalue of child_nodes must "
                                "not alter the underlying object from NsTrie")

    def test_repr(self):

        trie = NsTrie(('com.example.foo', 'com.example.bar'))
        expected = "NsTrie(['com.example.bar', 'com.example.foo'])"

        self.assertEqual(expected, repr(trie))
        self.assertEqual(expected, str(trie))
        self.assertEqual(unicode(expected), unicode(trie))

    def test_to_dict(self):
        trie = NsTrie((
            'com.example.foo',
            'org.example.foo',
            'org.example.bar',
            'com.foo.Baz',
        ))

        expected = {
            'com': {
                'example': {
                    'foo': 'com.example.foo',
                },
                'foo': {
                    'Baz': 'com.foo.Baz',
                },
            },
            'org': {
                'example': {
                    'foo': 'org.example.foo',
                    'bar': 'org.example.bar',
                },
            },
        }

        self.assertDictEqual(expected, trie.to_dict())

    def test_len(self):
        trie = NsTrie(('com.example.foo', 'com.example.bar'))
        self.assertEqual(2, len(trie))

    def test_contains(self):
        trie = NsTrie(('com.example.foo', 'com.example.bar'))

        self.assertTrue('com' in trie)
        self.assertTrue('com.example' in trie)
        self.assertTrue('com.example.foo' in trie)
        self.assertTrue('com.example.bar' in trie)
        self.assertFalse('example' in trie)
        self.assertFalse('example.bar' in trie)
        self.assertFalse('bar' in trie)
        self.assertFalse('foo' in trie)

    def test_has(self):
        trie = NsTrie(('com.example.foo', 'com.example.bar'))

        self.assertFalse(trie.has('com'))
        self.assertFalse(trie.has('com.example'))
        self.assertTrue(trie.has('com.example.foo'))
        self.assertTrue(trie.has('com.example.bar'))

        self.assertTrue(trie.has('com', False))
        self.assertTrue(trie.has('com.example', False))
        self.assertTrue(trie.has('com.example.foo', False))
        self.assertTrue(trie.has('com.example.bar', False))

    def test_get(self):
        trie = NsTrie(('com.example.foo', 'com.example.bar'))

        expected = NsNode([
            ('foo', String('com.example.foo')),
            ('bar', String('com.example.bar'))
        ])

        self.assertEqual(expected, trie.get('com.example'))
        self.assertEqual(expected, trie['com.example'])

        with self.assertRaises(KeyError):
            trie.get('org.example.foo')


    #noinspection PyUnresolvedReferences
    def test_remove(self):
        trie = NsTrie((
            'com.example.foo',
            'com.example.bar'
        ))

        trie.remove('com.example')

        self.assertDictEqual({'com': 'com'}, trie.to_dict())
        self.assertSetEqual(set(('com',)), trie.child_nodes)
        self.assertEqual(1, len(trie))

        with self.assertRaises(KeyError):
            trie.remove('org.example.foo')

    def test_sorted(self):
        modules = [
            'com.example.foo.Foo',
            'com.example.foo.Bar',
            'com.example.Baz',
            'com.example.baz.Boo',
            'org.example.foo'
        ]

        trie = NsTrie(modules)

        expected = [
            'com',
            'org',
            'com.example',
            'org.example',
            'com.example.foo',
            'com.example.Baz',
            'com.example.baz',
            'org.example.foo',
            'com.example.foo.Foo',
            'com.example.foo.Bar',
            'com.example.baz.Boo',
        ]

        sorted_by_depth_with_depth = sorted(trie.iterdepth(),
                                            key=lambda s: s.count('.'))
        sorted_by_depth_with_breadth = sorted(trie.iterbreadth(),
                                              key=lambda s: s.count('.'))

        self.assertEqual(expected, sorted_by_depth_with_depth)
        self.assertListEqual(sorted_by_depth_with_depth,
                             sorted_by_depth_with_breadth)

        expected = [
            'com',
            'com.example',
            'com.example.Baz',
            'com.example.baz',
            'com.example.baz.Boo',
            'com.example.foo',
            'com.example.foo.Bar',
            'com.example.foo.Foo',
            'org',
            'org.example',
            'org.example.foo',
        ]

        self.assertListEqual(expected, sorted(trie.iterdepth()))

        expected = [
            ('com', [
                ('example', [
                    ('foo', [
                        ('Foo', 'com.example.foo.Foo'),
                        ('Bar', 'com.example.foo.Bar'),
                    ]),
                    ('Baz', 'com.example.Baz'),
                    ('baz', [
                        ('Boo', 'com.example.baz.Boo'),
                    ]),
                ]),
            ]),
            ('org', [
                ('example', [
                    ('foo', 'org.example.foo'),
                ]),
            ]),
        ]

        self.assertListEqual(sorted(trie), expected)

        expected = [expected[1], expected[0]]

        self.assertListEqual(sorted(trie, reverse=True), expected)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
