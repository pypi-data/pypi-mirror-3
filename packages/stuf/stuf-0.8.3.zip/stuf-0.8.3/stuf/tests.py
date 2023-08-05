# -*- coding: utf-8 -*-
# pylint: disable-msg=w0108
'''test stuf'''

from __future__ import absolute_import
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestStuf(unittest.TestCase):

    @property
    def _makeone(self):
        from stuf import stuf
        return stuf

    @property
    def _maketwo(self):
        from stuf import istuf
        return istuf

    def setUp(self):
        self.stuf = self._makeone(
            test1='test1', test2='test2', test3=dict(e=1)
        )

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test3.e, 1)

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test3']['e'], 1)

    def test__setattr__(self):
        self.stuf.max = 3
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3.e = 5
        self.assertEqual(self.stuf.max, 3)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3.e, 5)

    def test__setitem__(self):
        self.stuf['max'] = 3
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3']['e'] = 5
        self.assertEqual(self.stuf['max'], 3)
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3']['e'], 5)

    def test__delattr__(self):
        del self.stuf.test1
        del self.stuf.test2
        del self.stuf.test3.e
        self.assertTrue(len(self.stuf.test3) == 0)
        del self.stuf.test3
        self.assertTrue(len(self.stuf) == 0)
        self.assertRaises(AttributeError, lambda: self.stuf.test1)
        self.assertRaises(AttributeError, lambda: self.stuf.test2)
        self.assertRaises(AttributeError, lambda: self.stuf.test3)
        self.assertRaises(AttributeError, lambda: self.stuf.test3.e)

    def test__delitem__(self):
        del self.stuf['test1']
        del self.stuf['test2']
        del self.stuf['test3']['e']
        self.assertFalse('e' in self.stuf['test3'])
        self.assertTrue(len(self.stuf['test3']) == 0)
        del self.stuf['test3']
        self.assertTrue(len(self.stuf) == 0)
        self.assertFalse('test1' in self.stuf)
        self.assertFalse('test2' in self.stuf)
        self.assertFalse('test3' in self.stuf)

    def test_get(self):
        self.assertEqual(self.stuf.get('test1'), 'test1')
        self.assertEqual(self.stuf.get('test2'), 'test2')
        self.assertIsNone(self.stuf.get('test4'), 'test4')
        self.assertEqual(self.stuf.get('test3').get('e'), 1)
        self.assertIsNone(self.stuf.get('test3').get('r'))

    def test__cmp__(self):
        tstuff = self._maketwo(
            (('test1', 'test1'), ('test2', 'test2'), ('test3', dict(e=1)))
        )
        self.assertEqual(self.stuf, tstuff)

    def test__len__(self):
        self.assertEqual(len(self.stuf), 3)
        self.assertEqual(len(self.stuf.test3), 1)

    def test_clear(self):
        self.stuf.test3.clear()
        self.assertEqual(len(self.stuf.test3), 0)
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 0)

    def test_items(self):
        slist = list(self.stuf.items())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', {'e': 1}) in slist)

    def test_iteritems(self):
        slist = list(self.stuf.iteritems())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', {'e': 1}) in slist)

    def test_iterkeys(self):
        slist = list(self.stuf.iterkeys())
        slist2 = list(self.stuf.test3.iterkeys())
        self.assertTrue('test1' in slist)
        self.assertTrue('test2' in slist)
        self.assertTrue('test3' in slist)
        self.assertTrue('e' in slist2)

    def test_itervalues(self):
        slist = list(self.stuf.itervalues())
        slist2 = list(self.stuf.test3.itervalues())
        self.assertTrue('test1' in slist)
        self.assertTrue('test2' in slist)
        self.assertTrue({'e': 1} in slist)
        self.assertTrue(1 in slist2)

    def test_pop(self):
        self.assertEqual(self.stuf.test3.pop('e'), 1)
        self.assertEqual(self.stuf.pop('test1'), 'test1')
        self.assertEqual(self.stuf.pop('test2'), 'test2')
        self.assertEqual(self.stuf.pop('test3'), {})

    def test_popitem(self):
        item = self.stuf.popitem()
        self.assertEqual(len(item) + len(self.stuf), 4, item)

    def test_setdefault(self):
        self.assertEqual(self.stuf.test3.setdefault('e', 8), 1)
        self.assertEqual(self.stuf.test3.setdefault('r', 8), 8)
        self.assertEqual(self.stuf.setdefault('test1', 8), 'test1')
        self.assertEqual(self.stuf.setdefault('pow', 8), 8)

    def test_update(self):
        tstuff = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        tstuff['test1'] = 3
        tstuff['test2'] = 6
        tstuff['test3'] = dict(f=2)
        self.stuf.update(tstuff)
        self.assertEqual(self.stuf['test1'], 3, self.stuf.items())
        self.assertEqual(self.stuf['test2'], 6)
        self.assertEqual(self.stuf['test3'], dict(f=2), self.stuf)

    def test_values(self):
        slist1 = self.stuf.test3.values()
        slist2 = self.stuf.values()
        self.assertTrue(1 in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue({'e': 1} in slist2)

    def test_keys(self):
        slist1 = self.stuf.test3.keys()
        slist2 = self.stuf.keys()
        self.assertTrue('e' in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue('test3' in slist2)

    def test_pickle(self):
        import pickle
        tstuf = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        pkle = pickle.dumps(tstuf)
        nstuf = pickle.loads(pkle)
        self.assertEquals(tstuf, nstuf)

    def test_copy(self):
        tstuf = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        nstuf = tstuf.copy()
        self.assertEquals(tstuf, nstuf)


class TestDefaultStuf(unittest.TestCase):

    @property
    def _makeone(self):
        from stuf import defaultstuf
        return defaultstuf

    @property
    def _maketwo(self):
        from stuf import idefaultstuf
        return idefaultstuf

    def setUp(self):
        self.stuf = self._makeone(
            list, test1='test1', test2='test2', test3=dict(e=1)
        )

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test4, [])
        self.assertEqual(self.stuf.test3.e, 1)
        self.assertEqual(self.stuf.test3.f, [])

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test4'], [])
        self.assertEqual(self.stuf['test3']['e'], 1)
        self.assertEqual(self.stuf['test3']['f'], [])

    def test__setattr__(self):
        self.stuf.max = 3
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3.e = 5
        self.assertEqual(self.stuf.max, 3)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3.e, 5)

    def test__setitem__(self):
        self.stuf['max'] = 3
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3']['e'] = 5
        self.assertEqual(self.stuf['max'], 3)
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3']['e'], 5)

    def test__delattr__(self):
        del self.stuf.test1
        del self.stuf.test2
        del self.stuf.test3.e
        self.assertTrue(len(self.stuf.test3) == 0)
        del self.stuf.test3
        self.assertTrue(len(self.stuf) == 0)
        self.assertEqual(self.stuf.test1, [])
        self.assertEqual(self.stuf.test2, [])
        self.assertEqual(self.stuf.test3, [])
        self.assertRaises(AttributeError, lambda: self.stuf.test3.e)

    def test__delitem__(self):
        del self.stuf['test1']
        del self.stuf['test2']
        del self.stuf['test3']['e']
        self.assertFalse('e' in self.stuf['test3'])
        self.assertTrue(len(self.stuf['test3']) == 0)
        self.assertEqual(self.stuf['test3']['e'], [])
        del self.stuf['test3']
        self.assertTrue(len(self.stuf) == 0)
        self.assertFalse('test1' in self.stuf)
        self.assertFalse('test2' in self.stuf)
        self.assertFalse('test3' in self.stuf)
        self.assertEqual(self.stuf['test1'], [])
        self.assertEqual(self.stuf['test2'], [])
        self.assertEqual(self.stuf['test3'], [])
        self.assertRaises(TypeError, lambda: self.stuf['test3']['e'])

    def test_get(self):
        self.assertEqual(self.stuf.get('test1'), 'test1')
        self.assertEqual(self.stuf.get('test2'), 'test2')
        self.assertIsNone(self.stuf.get('test4'), 'test4')
        self.assertEqual(self.stuf.get('test3').get('e'), 1)
        self.assertIsNone(self.stuf.get('test3').get('r'))

    def test__cmp__(self):
        tstuff = self._maketwo(
            list,
            (1, 2),
            {},
            (('test1', 'test1'), ('test2', 'test2'), ('test3', dict(e=1))),
        )
        self.assertEqual(self.stuf, tstuff)

    def test__len__(self):
        self.assertEqual(len(self.stuf), 3)
        self.assertEqual(len(self.stuf.test3), 1)

    def test_clear(self):
        self.stuf.test3.clear()
        self.assertEqual(len(self.stuf.test3), 0)
        self.assertEqual(self.stuf['test3']['e'], [])
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 0)
        self.assertEqual(self.stuf['test1'], [])
        self.assertEqual(self.stuf['test2'], [])
        self.assertEqual(self.stuf['test3'], [])

    def test_items(self):
        self.assertEqual(self.stuf['test4'], [])
        slist = list(self.stuf.items())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', {'e': 1}) in slist)
        self.assertTrue(('test4', []) in slist)

    def test_iteritems(self):
        slist = list(self.stuf.iteritems())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', {'e': 1}) in slist)

    def test_iterkeys(self):
        slist = list(self.stuf.iterkeys())
        slist2 = list(self.stuf.test3.iterkeys())
        self.assertTrue('test1' in slist)
        self.assertTrue('test2' in slist)
        self.assertTrue('test3' in slist)
        self.assertTrue('e' in slist2)

    def test_itervalues(self):
        slist = list(self.stuf.itervalues())
        slist2 = list(self.stuf.test3.itervalues())
        self.assertTrue('test1' in slist)
        self.assertTrue('test2' in slist)
        self.assertTrue({'e': 1} in slist)
        self.assertTrue(1 in slist2)

    def test_pop(self):
        self.assertEqual(self.stuf.test3.pop('e'), 1)
        self.assertEqual(self.stuf.pop('test1'), 'test1')
        self.assertEqual(self.stuf.pop('test2'), 'test2')
        self.assertEqual(self.stuf.pop('test3'), {})

    def test_popitem(self):
        item = self.stuf.popitem()
        self.assertEqual(len(item) + len(self.stuf), 4, item)

    def test_setdefault(self):
        self.assertEqual(self.stuf.test3.setdefault('e', 8), 1)
        self.assertEqual(self.stuf.test3.setdefault('r', 8), 8)
        self.assertEqual(self.stuf.setdefault('test1', 8), 'test1')
        self.assertEqual(self.stuf.setdefault('pow', 8), 8)

    def test_update(self):
        tstuff = self._makeone(
            list, (1, 2), test1='test1', test2='test2', test3=dict(e=1)
        )
        tstuff['test1'] = 3
        tstuff['test2'] = 6
        tstuff['test3'] = dict(f=2)
        self.stuf.update(tstuff)
        self.assertEqual(self.stuf['test1'], 3)
        self.assertEqual(self.stuf['test2'], 6)
        self.assertEqual(self.stuf['test3'], dict(f=2), self.stuf)

    def test_values(self):
        slist1 = self.stuf.test3.values()
        slist2 = self.stuf.values()
        self.assertTrue(1 in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue({'e': 1} in slist2)

    def test_keys(self):
        slist1 = self.stuf.test3.keys()
        slist2 = self.stuf.keys()
        self.assertTrue('e' in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue('test3' in slist2)

    def test_pickle(self):
        import pickle
        tstuf = self._makeone(
            list, ([],), test1='test1', test2='test2', test3=dict(e=1)
        )
        pkle = pickle.dumps(tstuf)
        nstuf = pickle.loads(pkle)
        self.assertEquals(tstuf, nstuf)

    def test_copy(self):
        tstuf = self._makeone(
            list, ([],), test1='test1', test2='test2', test3=dict(e=1)
        )
        nstuf = tstuf.copy()
        self.assertEquals(tstuf, nstuf)


class TestFixedStuf(unittest.TestCase):

    @property
    def _makeone(self):
        from stuf import fixedstuf
        return fixedstuf

    @property
    def _maketwo(self):
        from stuf import ifixedstuf
        return ifixedstuf

    def setUp(self):
        self.stuf = self._makeone(
            test1='test1', test2='test2', test3=dict(e=1)
        )

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test3.e, 1)

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test3']['e'], 1)

    def test__setattr__(self):
        self.assertRaises(AttributeError, lambda: setattr(self.stuf, 'max', 3))
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3.e = 5
        self.assertRaises(AttributeError, lambda: self.stuf.max)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3.e, 5)

    def test__setitem__(self):
        self.assertRaises(KeyError, lambda: self.stuf.__setitem__('max', 3))
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3']['e'] = 5
        self.assertRaises(KeyError, lambda: self.stuf.__getitem__('max'))
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3']['e'], 5)

    def test__delattr__(self):
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test1))
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test3.e))

    def test__delitem__(self):
        del self.stuf.test3['e']
        self.assertRaises(KeyError, lambda: self.stuf.test3['e'])
        del self.stuf['test1']
        self.assertRaises(KeyError, lambda: self.stuf['test1'])

    def test_get(self):
        self.assertEqual(self.stuf.get('test1'), 'test1')
        self.assertEqual(self.stuf.get('test2'), 'test2')
        self.assertIsNone(self.stuf.get('test4'), 'test4')
        self.assertEqual(self.stuf.get('test3').get('e'), 1)
        self.assertIsNone(self.stuf.get('test3').get('r'))

    def test__cmp__(self):
        tstuff = self._maketwo(
            (('test1', 'test1'), ('test2', 'test2'), ('test3', dict(e=1)))
        )
        self.assertEqual(self.stuf, tstuff)

    def test__len__(self):
        self.assertEqual(len(self.stuf), 3)
        self.assertEqual(len(self.stuf.test3), 1)

    def test_clear(self):
        self.assertRaises(KeyError, lambda: self.stuf.__setitem__('max', 3))
        self.stuf.clear()
        self.stuf['test1'] = 'test1again'
        self.stuf['test3'] = 5

    def test_items(self):
        slist = list(self.stuf.items())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        dummy = self._maketwo({'e': 1})
        self.assertTrue(('test3', dummy) in slist, slist)

    def test_iteritems(self):
        slist = list(self.stuf.iteritems())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', self._maketwo({'e': 1})) in slist, slist)

    def test_iterkeys(self):
        slist = list(self.stuf.iterkeys())
        slist2 = list(self.stuf.test3.iterkeys())
        self.assertTrue('test1' in slist)
        self.assertTrue('test2' in slist)
        self.assertTrue('test3' in slist)
        self.assertTrue('e' in slist2)

    def test_itervalues(self):
        slist1 = list(i for i in self.stuf.itervalues())
        slist2 = list(i for i in self.stuf.test3.itervalues())
        self.assertTrue(1 in slist2)
        self.assertTrue('test1' in slist1)
        self.assertTrue(self._maketwo({'e': 1}) in slist1)
        self.assertTrue('test2' in slist1)

    def test_pop(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.pop('e'))
        self.assertRaises(AttributeError, lambda: self.stuf.pop('test1'))

    def test_popitem(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.popitem())
        self.assertRaises(AttributeError, lambda: self.stuf.popitem())

    def test_setdefault(self):
        self.assertEqual(self.stuf.test3.setdefault('e', 8), 1)
        self.assertRaises(KeyError, lambda: self.stuf.test3.setdefault('r', 8))
        self.assertEqual(self.stuf.setdefault('test1', 8), 'test1')
        self.assertRaises(KeyError, lambda: self.stuf.setdefault('pow', 8))

    def test_update(self):
        tstuff = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        tstuff['test1'] = 3
        tstuff['test2'] = 6
        tstuff['test3'] = dict(f=2)
        self.stuf.update(tstuff)
        self.assertEqual(self.stuf['test1'], 3)
        self.assertEqual(self.stuf['test2'], 6)
        self.assertEqual(
            self.stuf['test3'], self._maketwo(dict(f=2)), self.stuf['test3']
        )

    def test_values(self):
        slist1 = self.stuf.test3.values()
        slist2 = self.stuf.values()
        self.assertTrue(1 in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue(self._maketwo({'e': 1}) in slist2)

    def test_keys(self):
        slist1 = self.stuf.test3.keys()
        slist2 = self.stuf.keys()
        self.assertTrue('e' in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue('test3' in slist2)

    def test_copy(self):
        tstuf = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        nstuf = tstuf.copy()
        self.assertEquals(tstuf, nstuf)

    def test_pickle(self):
        import pickle
        tstuf = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        pkle = pickle.dumps(tstuf)
        nstuf = pickle.loads(pkle)
        self.assertEquals(tstuf, nstuf)


class TestFrozenStuf(unittest.TestCase):

    @property
    def _makeone(self):
        from stuf import frozenstuf
        return frozenstuf

    @property
    def _maketwo(self):
        from stuf import ifrozenstuf
        return ifrozenstuf

    def setUp(self):
        self.stuf = self._makeone(
            test1='test1', test2='test2', test3=dict(e=1)
        )

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test3.e, 1)

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test3']['e'], 1)

    def test__setattr__(self):
        self.assertRaises(AttributeError, setattr(self.stuf, 'max', 3))
        self.assertRaises(
            AttributeError, setattr(self.stuf, 'test1', 'test1again')
        )
        self.assertRaises(
            AttributeError, setattr(self.stuf.test3, 'e', 5)
        )

    def test__setitem__(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.__setitem__('max', 3)
        )
        self.assertRaises(
            AttributeError,
            lambda: self.stuf.__setitem__('test2', 'test2again'),
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.__setitem__('e', 5)
        )

    def test__delattr__(self):
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test1))
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test3.e))

    def test__delitem__(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.__delitem__('test1'),
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.__delitem__('test1'),
        )

    def test_get(self):
        self.assertEqual(self.stuf.get('test1'), 'test1')
        self.assertEqual(self.stuf.get('test2'), 'test2')
        self.assertIsNone(self.stuf.get('test4'), 'test4')
        self.assertEqual(self.stuf.get('test3').get('e'), 1)
        self.assertIsNone(self.stuf.get('test3').get('r'))

    def test__cmp__(self):
        tstuff = self._maketwo(
            (('test1', 'test1'), ('test2', 'test2'), ('test3', dict(e=1)))
        )
        self.assertEqual(self.stuf, tstuff)

    def test__len__(self):
        self.assertEqual(len(self.stuf), 3)
        self.assertEqual(len(self.stuf.test3), 1)

    def test_clear(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.clear())
        self.assertRaises(AttributeError, lambda: self.stuf.clear())

    def test_items(self):
        slist = list(self.stuf.items())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', self._maketwo({'e': 1})) in slist, slist)

    def test_iteritems(self):
        slist = list(self.stuf.iteritems())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', self._maketwo({'e': 1})) in slist, slist)

    def test_iterkeys(self):
        slist = list(self.stuf.iterkeys())
        slist2 = list(self.stuf.test3.iterkeys())
        self.assertTrue('test1' in slist)
        self.assertTrue('test2' in slist)
        self.assertTrue('test3' in slist)
        self.assertTrue('e' in slist2)

    def test_itervalues(self):
        slist1 = list(self.stuf.itervalues())
        slist2 = list(self.stuf.test3.itervalues())
        self.assertTrue('test2' in slist1)
        self.assertTrue(self._maketwo({'e': 1}) in slist1)
        self.assertTrue(1 in slist2)
        self.assertTrue('test1' in slist1)

    def test_pop(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.pop('e'))
        self.assertRaises(AttributeError, lambda: self.stuf.pop('test1'))

    def test_popitem(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.popitem())
        self.assertRaises(AttributeError, lambda: self.stuf.popitem())

    def test_setdefault(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.setdefault('e', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.setdefault('r', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.setdefault('test1', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.setdefault('pow', 8)
        )

    def test_update(self):
        tstuff = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.update(tstuff),
        )
        self.assertRaises(AttributeError, lambda: self.stuf.update(tstuff))

    def test_values(self):
        slist1 = self.stuf.test3.values()
        slist2 = self.stuf.values()
        self.assertTrue(1 in slist1)
        self.assertTrue(self._maketwo({'e': 1}) in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue('test1' in slist2)

    def test_keys(self):
        slist1 = self.stuf.test3.keys()
        slist2 = self.stuf.keys()
        self.assertTrue('e' in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue('test3' in slist2)

    def test_copy(self):
        tstuf = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        nstuf = tstuf.copy()
        self.assertEquals(tstuf, nstuf)

    def test_pickle(self):
        import pickle
        tstuf = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        pkle = pickle.dumps(tstuf)
        nstuf = pickle.loads(pkle)
        self.assertEquals(tstuf, nstuf)


class TestOrderedStuf(unittest.TestCase):

    @property
    def _makeone(self):
        from stuf import orderedstuf
        return orderedstuf

    @property
    def _maketwo(self):
        from stuf import iorderedstuf
        return iorderedstuf

    def setUp(self):
        self.stuf = self._makeone(
            test1='test1', test2='test2', test3=dict(e=1)
        )

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test3.e, 1)

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test3']['e'], 1)

    def test__setattr__(self):
        self.stuf.max = 3
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3.e = 5
        self.assertEqual(self.stuf.max, 3)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3.e, 5)

    def test__setitem__(self):
        self.stuf['max'] = 3
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3']['e'] = 5
        self.assertEqual(self.stuf['max'], 3)
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3']['e'], 5)

    def test__delattr__(self):
        del self.stuf.test1
        del self.stuf.test2
        del self.stuf.test3.e
        self.assertTrue(len(self.stuf.test3) == 0)
        del self.stuf.test3
        self.assertTrue(len(self.stuf) == 0)
        self.assertRaises(AttributeError, lambda: self.stuf.test1)
        self.assertRaises(AttributeError, lambda: self.stuf.test2)
        self.assertRaises(AttributeError, lambda: self.stuf.test3)
        self.assertRaises(AttributeError, lambda: self.stuf.test3.e)

    def test__delitem__(self):
        del self.stuf['test1']
        del self.stuf['test2']
        del self.stuf['test3']['e']
        self.assertFalse('e' in self.stuf['test3'])
        self.assertTrue(len(self.stuf['test3']) == 0)
        del self.stuf['test3']
        self.assertTrue(len(self.stuf) == 0)
        self.assertFalse('test1' in self.stuf)
        self.assertFalse('test2' in self.stuf)
        self.assertFalse('test3' in self.stuf)

    def test_get(self):
        self.assertEqual(self.stuf.get('test1'), 'test1')
        self.assertEqual(self.stuf.get('test2'), 'test2')
        self.assertIsNone(self.stuf.get('test4'), 'test4')
        self.assertEqual(self.stuf.get('test3').get('e'), 1)
        self.assertIsNone(self.stuf.get('test3').get('r'))

    def test__cmp__(self):
        tstuff = self._maketwo(
            (('test1', 'test1'), ('test2', 'test2'), ('test3', dict(e=1)))
        )
        self.assertEqual(self.stuf, tstuff)

    def test__len__(self):
        self.assertEqual(len(self.stuf), 3)
        self.assertEqual(len(self.stuf.test3), 1)

    def test_clear(self):
        self.stuf.test3.clear()
        self.assertEqual(len(self.stuf.test3), 0)
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 0)

    def test_items(self):
        slist = list(self.stuf.items())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', {'e': 1}) in slist)

    def test_iteritems(self):
        slist = list(self.stuf.iteritems())
        self.assertTrue(('test1', 'test1') in slist)
        self.assertTrue(('test2', 'test2') in slist)
        self.assertTrue(('test3', self._maketwo({'e': 1})) in slist)

    def test_iterkeys(self):
        slist = list(self.stuf.iterkeys())
        slist2 = list(self.stuf.test3.iterkeys())
        self.assertTrue('test1' in slist)
        self.assertTrue('test2' in slist)
        self.assertTrue('test3' in slist)
        self.assertTrue('e' in slist2)

    def test_itervalues(self):
        slist = list(self.stuf.itervalues())
        slist2 = list(self.stuf.test3.itervalues())
        self.assertTrue('test1' in slist)
        self.assertTrue('test2' in slist)
        self.assertTrue(self._maketwo({'e': 1}) in slist)
        self.assertTrue(1 in slist2)

    def test_pop(self):
        self.assertEqual(self.stuf.test3.pop('e'), 1)
        self.assertEqual(self.stuf.pop('test1'), 'test1')
        self.assertEqual(self.stuf.pop('test2'), 'test2')
        self.assertEqual(self.stuf.pop('test3'), {})

    def test_popitem(self):
        item = self.stuf.popitem()
        self.assertEqual(len(item) + len(self.stuf), 4, item)

    def test_setdefault(self):
        self.assertEqual(self.stuf.test3.setdefault('e', 8), 1)
        self.assertEqual(self.stuf.test3.setdefault('r', 8), 8)
        self.assertEqual(self.stuf.setdefault('test1', 8), 'test1')
        self.assertEqual(self.stuf.setdefault('pow', 8), 8)

    def test_update(self):
        tstuff = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        tstuff['test1'] = 3
        tstuff['test2'] = 6
        tstuff['test3'] = dict(f=2)
        self.stuf.update(tstuff)
        self.assertEqual(self.stuf['test1'], 3)
        self.assertEqual(self.stuf['test2'], 6)
        self.assertEqual(self.stuf['test3'], dict(f=2), self.stuf)

    def test_values(self):
        slist1 = self.stuf.test3.values()
        slist2 = self.stuf.values()
        self.assertTrue(1 in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue(self._maketwo({'e': 1}) in slist2)

    def test_keys(self):
        slist1 = self.stuf.test3.keys()
        slist2 = self.stuf.keys()
        self.assertTrue('e' in slist1)
        self.assertTrue('test1' in slist2)
        self.assertTrue('test2' in slist2)
        self.assertTrue('test3' in slist2)

    def test_copy(self):
        tstuf = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        nstuf = tstuf.copy()
        self.assertEquals(tstuf, nstuf)

    def test_pickle(self):
        import pickle
        tstuf = self._makeone(test1='test1', test2='test2', test3=dict(e=1))
        pkle = pickle.dumps(tstuf)
        nstuf = pickle.loads(pkle)
        self.assertEquals(tstuf, nstuf)


if __name__ == '__main__':
    unittest.main()
