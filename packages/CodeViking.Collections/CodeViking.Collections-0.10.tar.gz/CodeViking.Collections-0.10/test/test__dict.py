'''
Created on Apr 8, 2012

@author: dan
'''
import abc, json, os, pickle, random, shutil, tempfile, unittest
from codeviking.collections.dict import (JsonMapper, PickleMapper, DirDict,
    DirDictReader, FileDict, FileDictReader, FrozenDict, JsonDictReader,
    PickleDictReader, JsonDict, PickleDict, MultiDict, FrozenMultiDict)

pool = [c for c in 'abcdefghijklmnopqrstuvwxyz']

def rand_name(len=10):
    return ''.join(random.sample(pool, len))

def rand_id(max_depth=1):
    d = random.randint(1, max_depth)
    return '/'.join([rand_name() for i in range(d)])

def rand_dict(value_func, size=10, id_depth=4):
    result = {}
    for i in range(size):
        k = rand_id(id_depth)
        v = value_func()
        result[k] = v
    return result

def dir_to_dict(path):
    result = dict()
    for c in os.listdir(path):
        p = os.path.join(path, c)
        if c.endswith('.json') and os.path.isfile(p):
            f = open(p, 'r')
            k = c[:-5]
            result[k] = json.load(f)
        elif os.path.isdir(p):
            child = dir_to_dict(p)
            result.update({c + '/' + k: v for k, v in child.items()})
    return result


class FrozenDictTestBase(unittest.TestCase):
    __test__ = False
    Dclass = dict
    def setUp(self):
        self.d0_items = (('a', 1), ('b', 2), ('c', 3), ('d', 4))
        self.d0 = {k:v for k, v in self.d0_items}
        self.v_default = 'default'
        self.k_nonex = 'nonexistantkey'

    def d_from(self, other):
        return self.Dclass(other)

    def test_get(self):
        d = self.d_from(self.d0)
        for k, v in self.d0_items:
            self.assertEqual(v, d[k])
            self.assertEqual(v, d.get(k))

    def test_get_default(self):
        d = self.d_from(self.d0)
        for k, v in self.d0_items:
            self.assertEqual(v, d.get(k, self.v_default))
        self.assertEqual(self.v_default, d.get(self.k_nonex, self.v_default))

    def test_iter(self):
        d = self.d_from(self.d0)
        for k in d:
            self.assertIn(k, self.d0)

    def test_get_keyerror(self):
        d = self.d_from(self.d0)
        def f():
            return d[self.k_nonex]
        self.assertRaises(KeyError, f)

    def test_items(self):
        d = self.d_from(self.d0)
        self.assertItemsEqual(self.d0_items, d.items())

    def test_keys(self):
        d = self.d_from(self.d0)
        self.assertItemsEqual([k for k, _ in self.d0_items], d.keys())

    def test_values(self):
        d = self.d_from(self.d0)
        self.assertItemsEqual([v for _, v in self.d0_items], d.values())

    def test_in(self):
        d = self.d_from(self.d0)
        for k, _ in self.d0_items:
            self.assertTrue(k in d)
        self.assertFalse(self.k_nonex in d)

    def test_equal(self):
        d = self.d_from(self.d0)
        self.assertEqual(d, self.d0)
        k = self.d0_items[0][0]
        del self.d0[k]
        self.assertNotEqual(d, self.d0)

    def test_len(self):
        d = self.d_from(self.d0)
        self.assertEqual(len(d), len(self.d0))


class DictTestBase(FrozenDictTestBase):

    def setUp(self):
        super(DictTestBase, self).setUp()
        self.v_new = 'a_new_value'
        self.k_new = 'new'
        self.v_overwrite = 'overwrite'
        self.d_update = {'quick': 'monkey', 'a': 'frisbee'}

    def test_del(self):
        d = self.d_from(self.d0)
        n = len(d)
        for k in self.d0.keys():
            del d[k]
            n -= 1
            self.assertEqual(n, len(d))

    def test_del_keyerror(self):
        d = self.d_from(self.d0)

        def f():
            del d[self.k_nonex]
        self.assertRaises(KeyError, f)

    def test_put(self):
        d = self.d_from(self.d0)
        d[self.k_new ] = self.v_new
        self.assertEqual(len(d), len(self.d0) + 1)
        self.assertEqual(d[self.k_new ], self.v_new)
        self.assertTrue(self.k_new  in d)
        self.assertTrue(self.k_new  in d.keys())
        self.assertTrue(self.v_new  in d.values())

    def test_put_overwrite(self):
        d = self.d_from(self.d0)
        k, _ = self.d0_items[0]
        d[k] = self.v_overwrite
        self.assertEqual(len(d), len(self.d0))
        self.assertEqual(d[k], self.v_overwrite)
        self.assertTrue(k in d)
        self.assertTrue(k in d.keys())
        self.assertTrue(self.v_overwrite in d.values())

    def test_update(self):
        d = self.d_from(self.d0)
        n = len(d)
        k0 = self.d_update.keys()[0]
        k1 = self.d_update.keys()[1]
        d.update(self.d_update)
        self.assertEqual(n + 1, len(d))
        self.assertEqual(self.d_update[k0], d[k0])
        self.assertEqual(self.d_update[k1], d[k1])

class DictTest(DictTestBase):
    __test__ = True
    Dclass = dict


class FrozenDictTest(FrozenDictTestBase):
    __test__ = True
    Dclass = FrozenDict

    def test_hash(self):
        d1 = self.d_from(self.d0)
        d2 = self.d_from(self.d0)
        d = dict()
        d[d1] = 1
        d[d2] = 2
        self.assertEqual(hash(d1), hash(d2))
#        TODO: fix this when FrozenDict hashes properly.
#        self.assertEqual(1, len(d))
#        self.assertEqual(2, d[d1])
#        self.assertEqual(2, d[d2])


class TestDirDictReaderJson(FrozenDictTestBase):
    __test__ = True
    Dclass = DirDictReader
    Mclass = JsonMapper

    def d_from(self, other):
        t = self.temp_dir()
        mapper = self.Mclass()
        for k, v in other.items():
            p = os.path.join(t, mapper.key_to_rpath(k))
            d = os.path.dirname(p)
            if not os.path.exists(d):
                os.makedirs(d)
            mapper.save_value(v, p)
        return self.Dclass(root_path=t, mapper=self.Mclass())

    def random_dict(self, n):
        return rand_dict(lambda: rand_dict(rand_id, size=n, id_depth=1))

#    def test_d_to_f(self):
#        self.maxDiff = None
#        d = self.random_dict(1)
#        r = DictReader(d)
#        w = JsonWriter(self.t1)
#        for (k, v) in r.items():
#            w.put(k, v)
#        i = dict()
#        i.update(w)
#        self.assertDictEqual(d, i)

    def temp_dir(self):
        d = tempfile.mkdtemp(prefix='test__dict.')
        self._temp_dirs.append(d)
        return d

    def setUp(self):
        self._temp_dirs = []
        super(TestDirDictReaderJson, self).setUp()

    def tearDown(self):
        for d in self._temp_dirs:
            try:
                shutil.rmtree(d)
            except:
                pass
        self._temp_dirs = []


    def testName(self):
        pass

class TestDirDictJson(TestDirDictReaderJson, DictTestBase):
    Dclass = DirDict


class TestDirDictReaderPickle(TestDirDictReaderJson):
    __test__ = True
    Dclass = DirDictReader
    Mclass = PickleMapper

class TestDirDictPickle(TestDirDictJson):
    __test__ = True
    Dclass = DirDict
    Mclass = PickleMapper


class TestFileDictReaderBase(unittest.TestCase):
    @abc.abstractmethod
    def dumps(self, other):
        raise NotImplementedError

    def d_from(self, other):
        fd, path = tempfile.mkstemp('.json', 'test__dict')
        self._temp_files.append(path)
        os.write(fd, self.dumps(other))
        os.close(fd)
        return self.Dclass(path)

    def setUp(self):
        self._temp_files = []
        super(TestFileDictReaderBase, self).setUp()

    def tearDown(self):
        for f in self._temp_files:
            try:
                os.remove(f)
            except:
                pass
        self._temp_files = []


class TestJsonDictReader(TestFileDictReaderBase, FrozenDictTestBase):
    __test__ = True
    Dclass = JsonDictReader

    def dumps(self, other):
        return json.dumps(other)


class TestPickleDictReader(TestFileDictReaderBase, FrozenDictTestBase):
    __test__ = True
    Dclass = PickleDictReader

    def dumps(self, other):
        return pickle.dumps(other)



class TestFileDictBase(TestFileDictReaderBase, DictTestBase):

    def from_file(self, d):
        raise NotImplementedError

    def test_del_f(self):
        d = self.d_from(self.d0)
        n = len(d)
        for k in self.d0.keys():
            del d[k]
            n -= 1
            self.assertEqual(n, len(self.from_file(d)))


    def test_put_f(self):
        d = self.d_from(self.d0)
        d['new'] = 'new_value'
        self.assertEqual(len(self.from_file(d)), len(self.d0) + 1)
        self.assertEqual(self.from_file(d)['new'], 'new_value')
        self.assertTrue('new' in self.from_file(d))
        self.assertTrue('new' in self.from_file(d).keys())
        self.assertTrue('new_value' in self.from_file(d).values())

    def test_put_overwrite_f(self):
        d = self.d_from(self.d0)
        k, _ = self.d0_items[0]
        d[k] = 'overwrite'
        self.assertEqual(len(self.from_file(d)), len(self.d0))
        self.assertEqual(self.from_file(d)[k], 'overwrite')
        self.assertTrue(k in self.from_file(d))
        self.assertTrue(k in self.from_file(d).keys())
        self.assertTrue('overwrite' in self.from_file(d).values())

    def test_update_f(self):
        d = self.d_from(self.d0)
        n = len(d)
        d.update({'quick': 'monkey', 'a': 'frisbee'})
        self.assertEqual(n + 1, len(self.from_file(d)))
        self.assertEqual('monkey', self.from_file(d)['quick'])
        self.assertEqual('frisbee', self.from_file(d)['a'])

    @abc.abstractmethod
    def loads(self, path):
        raise NotImplementedError


class TestJsonDict(TestFileDictBase):
    __test__ = True
    Dclass = JsonDict

    def from_file(self, d):
        d.flush()
        return json.load(open(d.path, 'r'))

    def dumps(self, other):
        return json.dumps(other)


class TestPickleDict(TestFileDictBase):
    __test__ = True
    Dclass = PickleDict

    def from_file(self, d):
        d.flush()
        return pickle.load(open(d.path, 'r'))

    def dumps(self, other):
        return pickle.dumps(other)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


class TestFrozenMultiDict(FrozenDictTestBase):
    __test__ = True
    Dclass = FrozenMultiDict

    def setUp(self):
        self.d0_items = (('a', (1, 2, 3)),
                         ('b', (8, 10, 3)),
                         ('c', (221, 87, 9)),
                         ('d', (18, 34, 5)))
        self.d0 = {k:v for k, v in self.d0_items}
        self.v_default = ('default0', 'default1', 'default2')
        self.k_nonex = 'nonexistantkey'

    def d_from(self, d):
        m0, m1, m2 = dict(), dict(), dict()
        for k, v in d.items():
            m0[k], m1[k], m2[k] = v
        return self.Dclass([('one', m0), ('two', m1), ('three', m2)])


class TestMultiDict(TestFrozenMultiDict, DictTest):
    __test__ = True
    Dclass = MultiDict

    def setUp(self):
        super(TestMultiDict, self).setUp()
        self.v_new = ('a', 'new', 'value')
        self.k_new = 'new'
        self.v_overwrite = ('overwrite', 'a', 'value')
        self.d_update = {'quick': ('monkey', 'eats', 'banana'),
                         'a': ('frisbee', 'fly', 'away')}
