# pylint: disable-msg=W0612,E1101,W0141
from cStringIO import StringIO
import unittest

from numpy.random import randn
import numpy as np

from pandas.core.index import Index, MultiIndex
from pandas import Panel, DataFrame, Series, notnull, isnull

from pandas.util.testing import (assert_almost_equal,
                                 assert_series_equal,
                                 assert_frame_equal)
import pandas.core.common as com
import pandas.util.testing as tm
from pandas.util.compat import product as cart_product

class TestMultiLevel(unittest.TestCase):

    def setUp(self):
        index = MultiIndex(levels=[['foo', 'bar', 'baz', 'qux'],
                                   ['one', 'two', 'three']],
                           labels=[[0, 0, 0, 1, 1, 2, 2, 3, 3, 3],
                                   [0, 1, 2, 0, 1, 1, 2, 0, 1, 2]],
                           names=['first', 'second'])
        self.frame = DataFrame(np.random.randn(10, 3), index=index,
                               columns=Index(['A', 'B', 'C'], name='exp'))

        self.single_level = MultiIndex(levels=[['foo', 'bar', 'baz', 'qux']],
                                       labels=[[0, 1, 2, 3]],
                                       names=['first'])

        # create test series object
        arrays = [['bar', 'bar', 'baz', 'baz', 'qux', 'qux', 'foo', 'foo'],
                  ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']]
        tuples = zip(*arrays)
        index = MultiIndex.from_tuples(tuples)
        s = Series(randn(8), index=index)
        s[3] = np.NaN
        self.series = s

        tm.N = 100
        self.tdf = tm.makeTimeDataFrame()
        self.ymd = self.tdf.groupby([lambda x: x.year, lambda x: x.month,
                                     lambda x: x.day]).sum()
        self.ymd.index.names = ['year', 'month', 'day']

    def test_append(self):
        a, b = self.frame[:5], self.frame[5:]

        result = a.append(b)
        tm.assert_frame_equal(result, self.frame)

        result = a['A'].append(b['A'])
        tm.assert_series_equal(result, self.frame['A'])

    def test_pickle(self):
        import cPickle
        def _test_roundtrip(frame):
            pickled = cPickle.dumps(frame)
            unpickled = cPickle.loads(pickled)
            assert_frame_equal(frame, unpickled)

        _test_roundtrip(self.frame)
        _test_roundtrip(self.frame.T)
        _test_roundtrip(self.ymd)
        _test_roundtrip(self.ymd.T)

    def test_reindex(self):
        reindexed = self.frame.ix[[('foo', 'one'), ('bar', 'one')]]
        expected = self.frame.ix[[0, 3]]
        assert_frame_equal(reindexed, expected)

    def test_reindex_preserve_levels(self):
        new_index = self.ymd.index[::10]
        chunk = self.ymd.reindex(new_index)
        self.assert_(chunk.index is new_index)

        chunk = self.ymd.ix[new_index]
        self.assert_(chunk.index is new_index)

        ymdT = self.ymd.T
        chunk = ymdT.reindex(columns=new_index)
        self.assert_(chunk.columns is new_index)

        chunk = ymdT.ix[:, new_index]
        self.assert_(chunk.columns is new_index)

    def test_sort_index_preserve_levels(self):
        result = self.frame.sort_index()
        self.assertEquals(result.index.names, self.frame.index.names)

    def test_repr_to_string(self):
        repr(self.frame)
        repr(self.ymd)
        repr(self.frame.T)
        repr(self.ymd.T)

        buf = StringIO()
        self.frame.to_string(buf=buf)
        self.ymd.to_string(buf=buf)
        self.frame.T.to_string(buf=buf)
        self.ymd.T.to_string(buf=buf)

    def test_getitem_simple(self):
        df = self.frame.T

        col = df['foo', 'one']
        assert_almost_equal(col.values, df.values[:, 0])
        self.assertRaises(KeyError, df.__getitem__, ('foo', 'four'))
        self.assertRaises(KeyError, df.__getitem__, 'foobar')

    def test_series_getitem(self):
        s = self.ymd['A']

        result = s[2000, 3]
        result2 = s.ix[2000, 3]
        expected = s[42:65]
        expected.index = expected.index.droplevel(0).droplevel(0)
        assert_series_equal(result, expected)

        result = s[2000, 3, 10]
        expected = s[49]
        self.assertEquals(result, expected)

        # fancy
        result = s.ix[[(2000, 3, 10), (2000, 3, 13)]]
        expected = s[49:51]
        assert_series_equal(result, expected)

        # key error
        self.assertRaises(KeyError, s.__getitem__, (2000, 3, 4))

    def test_series_setitem(self):
        s = self.ymd['A']

        s[2000, 3] = np.nan
        self.assert_(isnull(s[42:65]).all())
        self.assert_(notnull(s[:42]).all())
        self.assert_(notnull(s[65:]).all())

        s[2000, 3, 10] = np.nan
        self.assert_(isnull(s[49]))

    def test_series_slice_partial(self):
        pass

    def test_xs(self):
        xs = self.frame.xs(('bar', 'two'))
        xs2 = self.frame.ix[('bar', 'two')]

        assert_series_equal(xs, xs2)
        assert_almost_equal(xs.values, self.frame.values[4])

    def test_xs_partial(self):
        result = self.frame.xs('foo')
        result2 = self.frame.ix['foo']
        expected = self.frame.T['foo'].T
        assert_frame_equal(result, expected)
        assert_frame_equal(result, result2)

    def test_fancy_2d(self):
        result = self.frame.ix['foo', 'B']
        expected = self.frame.xs('foo')['B']
        assert_series_equal(result, expected)

        ft = self.frame.T
        result = ft.ix['B', 'foo']
        expected = ft.xs('B')['foo']
        assert_series_equal(result, expected)

    def test_get_loc_single_level(self):
        s = Series(np.random.randn(len(self.single_level)),
                   index=self.single_level)
        for k in self.single_level.values:
            s[k]

    def test_getitem_toplevel(self):
        df = self.frame.T

        result = df['foo']
        expected = df.reindex(columns=df.columns[:3])
        expected.columns = expected.columns.droplevel(0)
        assert_frame_equal(result, expected)

        result = df['bar']
        result2 = df.ix[:, 'bar']

        expected = df.reindex(columns=df.columns[3:5])
        expected.columns = expected.columns.droplevel(0)
        assert_frame_equal(result, expected)
        assert_frame_equal(result, result2)

    def test_getitem_int(self):
        levels = [[0, 1], [0, 1, 2]]
        labels = [[0, 0, 0, 1, 1, 1], [0, 1, 2, 0, 1, 2]]
        index = MultiIndex(levels=levels, labels=labels)

        frame = DataFrame(np.random.randn(6, 2), index=index)

        result = frame.ix[1]
        expected = frame[-3:]
        expected.index = expected.index.droplevel(0)
        assert_frame_equal(result, expected)

        # raises exception
        self.assertRaises(KeyError, frame.ix.__getitem__, 3)

        # however this will work
        result = self.frame.ix[2]
        expected = self.frame.xs(self.frame.index[2])
        assert_series_equal(result, expected)

    def test_getitem_partial(self):
        ymd = self.ymd.T
        result = ymd[2000, 2]

        expected = ymd.reindex(columns=ymd.columns[ymd.columns.labels[1] == 1])
        expected.columns = expected.columns.droplevel(0).droplevel(0)
        assert_frame_equal(result, expected)

    def test_setitem_change_dtype(self):
        dft = self.frame.T
        s = dft['foo', 'two']
        dft['foo', 'two'] = s > s.median()
        assert_series_equal(dft['foo', 'two'], s > s.median())
        self.assert_(isinstance(dft._data.blocks[1].items, MultiIndex))

        reindexed = dft.reindex(columns=[('foo', 'two')])
        assert_series_equal(reindexed['foo', 'two'], s > s.median())

    def test_fancy_slice_partial(self):
        result = self.frame.ix['bar':'baz']
        expected = self.frame[3:7]
        assert_frame_equal(result, expected)

        result = self.ymd.ix[(2000,2):(2000,4)]
        lev = self.ymd.index.labels[1]
        expected = self.ymd[(lev >= 1) & (lev <= 3)]
        assert_frame_equal(result, expected)

    def test_sortlevel(self):
        df = self.frame.copy()
        df.index = np.arange(len(df))
        self.assertRaises(Exception, df.sortlevel, 0)

        # axis=1

        # series
        a_sorted = self.frame['A'].sortlevel(0)
        self.assertRaises(Exception,
                          self.frame.delevel()['A'].sortlevel)

        # preserve names
        self.assertEquals(a_sorted.index.names, self.frame.index.names)

    def test_delevel_infer_dtype(self):
        tuples = [tuple for tuple in cart_product(['foo', 'bar'],
                                                  [10, 20], [1.0, 1.1])]
        index = MultiIndex.from_tuples(tuples,
                                       names=['prm0', 'prm1', 'prm2'])
        df = DataFrame(np.random.randn(8,3), columns=['A', 'B', 'C'],
                       index=index)
        deleveled = df.delevel()
        self.assert_(com.is_integer_dtype(deleveled['prm1']))
        self.assert_(com.is_float_dtype(deleveled['prm2']))

    def test_sortlevel_by_name(self):
        self.frame.index.names = ['first', 'second']
        result = self.frame.sortlevel(level='second')
        expected = self.frame.sortlevel(level=1)
        assert_frame_equal(result, expected)

    def test_sortlevel_mixed(self):
        sorted_before = self.frame.sortlevel(1)

        df = self.frame.copy()
        df['foo'] = 'bar'
        sorted_after = df.sortlevel(1)
        assert_frame_equal(sorted_before, sorted_after.drop(['foo'], axis=1))

        dft = self.frame.T
        sorted_before = dft.sortlevel(1, axis=1)
        dft['foo', 'three'] = 'bar'

        sorted_after = dft.sortlevel(1, axis=1)
        assert_frame_equal(sorted_before.drop([('foo', 'three')], axis=1),
                           sorted_after.drop([('foo', 'three')], axis=1))

    def test_count_level(self):
        def _check_counts(frame, axis=0):
            index = frame._get_axis(axis)
            for i in range(index.nlevels):
                result = frame.count(axis=axis, level=i)
                expected = frame.groupby(axis=axis, level=i).count(axis=axis)
                expected = expected.reindex_like(result).astype('i8')
                assert_frame_equal(result, expected)

        self.frame.ix[1, [1, 2]] = np.nan
        self.frame.ix[7, [0, 1]] = np.nan
        self.ymd.ix[1, [1, 2]] = np.nan
        self.ymd.ix[7, [0, 1]] = np.nan

        _check_counts(self.frame)
        _check_counts(self.ymd)
        _check_counts(self.frame.T, axis=1)
        _check_counts(self.ymd.T, axis=1)

        # can't call with level on regular DataFrame
        df = tm.makeTimeDataFrame()
        self.assertRaises(Exception, df.count, level=0)

        self.frame['D'] = 'foo'
        result = self.frame.count(level=0, numeric_only=True)
        assert_almost_equal(result.columns, ['A', 'B', 'C'])

    def test_count_level_series(self):
        index = MultiIndex(levels=[['foo', 'bar', 'baz'],
                                   ['one', 'two', 'three', 'four']],
                           labels=[[0, 0, 0, 2, 2],
                                   [2, 0, 1, 1, 2]])

        s = Series(np.random.randn(len(index)), index=index)

        result = s.count(level=0)
        expected = s.groupby(level=0).count()
        assert_series_equal(result.astype('f8'),
                            expected.reindex(result.index).fillna(0))

        result = s.count(level=1)
        expected = s.groupby(level=1).count()
        assert_series_equal(result.astype('f8'),
                            expected.reindex(result.index).fillna(0))

    def test_count_level_corner(self):
        s = self.frame['A'][:0]
        result = s.count(level=0)
        expected = Series(0, index=s.index.levels[0])
        assert_series_equal(result, expected)

        df = self.frame[:0]
        result = df.count(level=0)
        expected = DataFrame({}, index=s.index.levels[0],
                             columns=df.columns).fillna(0).astype(int)
        assert_frame_equal(result, expected)

    def test_unstack(self):
        # just check that it works for now
        unstacked = self.ymd.unstack()
        unstacked2 = unstacked.unstack()

        # test that ints work
        unstacked = self.ymd.astype(int).unstack()

    def test_stack(self):
        # regular roundtrip
        unstacked = self.ymd.unstack()
        restacked = unstacked.stack()
        assert_frame_equal(restacked, self.ymd)

        unlexsorted = self.ymd.sortlevel(2)

        unstacked = unlexsorted.unstack(2)
        restacked = unstacked.stack()
        assert_frame_equal(restacked.sortlevel(0), self.ymd)

        unlexsorted = unlexsorted[::-1]
        unstacked = unlexsorted.unstack(1)
        restacked = unstacked.stack().swaplevel(1, 2)
        assert_frame_equal(restacked.sortlevel(0), self.ymd)

        unlexsorted = unlexsorted.swaplevel(0, 1)
        unstacked = unlexsorted.unstack(0).swaplevel(0, 1, axis=1)
        restacked = unstacked.stack(0).swaplevel(1, 2)
        assert_frame_equal(restacked.sortlevel(0), self.ymd)

        # columns unsorted
        unstacked = self.ymd.unstack()
        unstacked = unstacked.sort(axis=1, ascending=False)
        restacked = unstacked.stack()
        assert_frame_equal(restacked, self.ymd)

        # more than 2 levels in the columns
        unstacked = self.ymd.unstack(1).unstack(1)

        result = unstacked.stack(1)
        expected = self.ymd.unstack()
        assert_frame_equal(result, expected)

        result = unstacked.stack(2)
        expected = self.ymd.unstack(1)
        assert_frame_equal(result, expected)

        result = unstacked.stack(0)
        expected = self.ymd.stack().unstack(1).unstack(1)
        assert_frame_equal(result, expected)

        # not all levels present in each echelon
        unstacked = self.ymd.unstack(2).ix[:, ::3]
        stacked = unstacked.stack().stack()
        ymd_stacked = self.ymd.stack()
        assert_series_equal(stacked, ymd_stacked.reindex(stacked.index))

        # stack with negative number
        result = self.ymd.unstack(0).stack(-2)
        expected = self.ymd.unstack(0).stack(0)

    def test_stack_mixed_dtype(self):
        df = self.frame.T
        df['foo', 'four'] = 'foo'
        df = df.sortlevel(1, axis=1)

        stacked = df.stack()
        assert_series_equal(stacked['foo'], df['foo'].stack())
        self.assert_(stacked['bar'].dtype == np.float_)

    def test_unstack_bug(self):
        df = DataFrame({'state': ['naive','naive','naive',
                                  'activ','activ','activ'],
                        'exp':['a','b','b','b','a','a'],
                        'barcode':[1,2,3,4,1,3],
                        'v':['hi','hi','bye','bye','bye','peace'],
                        'extra': np.arange(6.)})

        result = df.groupby(['state','exp','barcode','v']).apply(len)
        unstacked = result.unstack()
        restacked = unstacked.stack()
        assert_series_equal(restacked,
                            result.reindex(restacked.index).astype(float))

    def test_stack_unstack_preserve_names(self):
        unstacked = self.frame.unstack()
        self.assertEquals(unstacked.index.name, 'first')
        self.assertEquals(unstacked.columns.names, ['exp', 'second'])

        restacked = unstacked.stack()
        self.assertEquals(restacked.index.names, self.frame.index.names)

    def test_unstack_level_name(self):
        result = self.frame.unstack('second')
        expected = self.frame.unstack(level=1)
        assert_frame_equal(result, expected)

    def test_stack_level_name(self):
        unstacked = self.frame.unstack('second')
        result = unstacked.stack('exp')
        expected = self.frame.unstack().stack(0)
        assert_frame_equal(result, expected)

        result = self.frame.stack('exp')
        expected = self.frame.stack()
        assert_series_equal(result, expected)

    def test_stack_unstack_multiple(self):
        unstacked = self.ymd.unstack(['year', 'month'])
        expected = self.ymd.unstack('year').unstack('month')
        assert_frame_equal(unstacked, expected)
        self.assertEquals(unstacked.columns.names,
                          expected.columns.names)

        # series
        s = self.ymd['A']
        s_unstacked = s.unstack(['year', 'month'])
        assert_frame_equal(s_unstacked, expected['A'])

        restacked = unstacked.stack(['year', 'month'])
        restacked = restacked.swaplevel(0, 1).swaplevel(1, 2)
        restacked = restacked.sortlevel(0)

        assert_frame_equal(restacked, self.ymd)
        self.assertEquals(restacked.index.names, self.ymd.index.names)

        # GH #451
        unstacked = self.ymd.unstack([1, 2])
        expected = self.ymd.unstack(1).unstack(1)
        assert_frame_equal(unstacked, expected)

        unstacked = self.ymd.unstack([2, 1])
        expected = self.ymd.unstack(2).unstack(1)
        assert_frame_equal(unstacked, expected)

    def test_groupby_transform(self):
        s = self.frame['A']
        grouper = s.index.get_level_values(0)

        grouped = s.groupby(grouper)

        applied = grouped.apply(lambda x: x * 2)
        expected = grouped.transform(lambda x: x * 2)
        assert_series_equal(applied.reindex(expected.index), expected)

    def test_join(self):
        a = self.frame.ix[:5, ['A']]
        b = self.frame.ix[2:, ['B', 'C']]

        joined = a.join(b, how='outer').reindex(self.frame.index)
        expected = self.frame.copy()
        expected.values[np.isnan(joined.values)] = np.nan

        self.assert_(not np.isnan(joined.values).all())

        assert_frame_equal(joined, expected)

    def test_swaplevel(self):
        swapped = self.frame['A'].swaplevel(0, 1)
        swapped2 = self.frame['A'].swaplevel('first', 'second')
        self.assert_(not swapped.index.equals(self.frame.index))
        assert_series_equal(swapped, swapped2)

        back = swapped.swaplevel(0, 1)
        back2 = swapped.swaplevel('second', 'first')
        self.assert_(back.index.equals(self.frame.index))
        assert_series_equal(back, back2)

        ft = self.frame.T
        swapped = ft.swaplevel('first', 'second', axis=1)
        exp = self.frame.swaplevel('first', 'second').T
        assert_frame_equal(swapped, exp)

    def test_swaplevel_panel(self):
        panel = Panel({'ItemA' : self.frame,
                       'ItemB' : self.frame * 2})

        result = panel.swaplevel(0, 1, axis='major')
        expected = panel.copy()
        expected.major_axis = expected.major_axis.swaplevel(0, 1)
        tm.assert_panel_equal(result, expected)

    def test_insert_index(self):
        df = self.ymd[:5].T
        df[2000, 1, 10] = df[2000, 1, 7]
        self.assert_(isinstance(df.columns, MultiIndex))
        self.assert_((df[2000, 1, 10] == df[2000, 1, 7]).all())

    def test_alignment(self):
        x = Series(data=[1,2,3],
                   index=MultiIndex.from_tuples([("A", 1), ("A", 2), ("B",3)]))

        y = Series(data=[4,5,6],
                   index=MultiIndex.from_tuples([("Z", 1), ("Z", 2), ("B",3)]))

        res = x - y
        exp_index = x.index.union(y.index)
        exp = x.reindex(exp_index) - y.reindex(exp_index)
        assert_series_equal(res, exp)

        # hit non-monotonic code path
        res = x[::-1] - y[::-1]
        exp_index = x.index.union(y.index)
        exp = x.reindex(exp_index) - y.reindex(exp_index)
        assert_series_equal(res, exp)

    def test_is_lexsorted(self):
        levels = [[0, 1], [0, 1, 2]]

        index = MultiIndex(levels=levels,
                           labels=[[0, 0, 0, 1, 1, 1],
                                   [0, 1, 2, 0, 1, 2]])
        self.assert_(index.is_lexsorted())

        index = MultiIndex(levels=levels,
                           labels=[[0, 0, 0, 1, 1, 1],
                                   [0, 1, 2, 0, 2, 1]])
        self.assert_(not index.is_lexsorted())

        index = MultiIndex(levels=levels,
                           labels=[[0, 0, 1, 0, 1, 1],
                                   [0, 1, 0, 2, 2, 1]])
        self.assert_(not index.is_lexsorted())
        self.assert_(index.lexsort_depth == 0)

    def test_frame_getitem_view(self):
        df = self.frame.T
        df['foo'].values[:] = 0
        self.assert_((df['foo'].values == 0).all())

        # but not if it's mixed-type
        df['foo', 'four'] = 'foo'
        df = df.sortlevel(0, axis=1)
        df['foo']['one'] = 2
        self.assert_((df['foo', 'one'] == 0).all())

    def test_frame_getitem_not_sorted(self):
        df = self.frame.T
        df['foo', 'four'] = 'foo'

        arrays = [np.array(x) for x in zip(*df.columns.get_tuple_index())]

        result = df['foo']
        result2 = df.ix[:, 'foo']
        expected = df.reindex(columns=df.columns[arrays[0] == 'foo'])
        expected.columns = expected.columns.droplevel(0)
        assert_frame_equal(result, expected)
        assert_frame_equal(result2, expected)

        df = df.T
        result = df.xs('foo')
        result2 = df.ix['foo']
        expected = df.reindex(df.index[arrays[0] == 'foo'])
        expected.index = expected.index.droplevel(0)
        assert_frame_equal(result, expected)
        assert_frame_equal(result2, expected)

    def test_series_getitem_not_sorted(self):
        arrays = [['bar', 'bar', 'baz', 'baz', 'qux', 'qux', 'foo', 'foo'],
        ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']]
        tuples = zip(*arrays)
        index = MultiIndex.from_tuples(tuples)
        s = Series(randn(8), index=index)

        arrays = [np.array(x) for x in zip(*index.get_tuple_index())]

        result = s['qux']
        result2 = s.ix['qux']
        expected = s[arrays[0] == 'qux']
        expected.index = expected.index.droplevel(0)
        assert_series_equal(result, expected)
        assert_series_equal(result2, expected)

    AGG_FUNCTIONS = ['sum', 'prod', 'min', 'max', 'median', 'mean', 'skew',
                     'mad', 'std', 'var']

    def test_series_group_min_max(self):
        for op, level, skipna in cart_product(self.AGG_FUNCTIONS,
                                              range(2),
                                              [False, True]):
            grouped = self.series.groupby(level=level)
            aggf = lambda x: getattr(x, op)(skipna=skipna)
            # skipna=True
            leftside = grouped.agg(aggf)
            rightside = getattr(self.series, op)(level=level, skipna=skipna)
            assert_series_equal(leftside, rightside)

    def test_frame_group_ops(self):
        self.frame.ix[1, [1, 2]] = np.nan
        self.frame.ix[7, [0, 1]] = np.nan

        for op, level, axis, skipna in cart_product(self.AGG_FUNCTIONS,
                                                    range(2), range(2),
                                                    [False, True]):
            if axis == 0:
                frame = self.frame
            else:
                frame = self.frame.T

            grouped = frame.groupby(level=level, axis=axis)

            aggf = lambda x: getattr(x, op)(skipna=skipna, axis=axis)
            leftside = grouped.agg(aggf)
            rightside = getattr(frame, op)(level=level, axis=axis,
                                           skipna=skipna)
            assert_frame_equal(leftside, rightside)

    def test_groupby_multilevel(self):
        result = self.ymd.groupby(level=[0, 1]).mean()

        k1 = self.ymd.index.get_level_values(0)
        k2 = self.ymd.index.get_level_values(1)

        expected = self.ymd.groupby([k1, k2]).mean()

        assert_frame_equal(result, expected)
        self.assertEquals(result.index.names, self.ymd.index.names[:2])

        result2 = self.ymd.groupby(level=self.ymd.index.names[:2]).mean()
        assert_frame_equal(result, result2)

    def test_groupby_multilevel_with_transform(self):
        pass

    def test_multilevel_consolidate(self):
        index = MultiIndex.from_tuples([('foo', 'one'), ('foo', 'two'),
                                        ('bar', 'one'), ('bar', 'two')])
        df = DataFrame(np.random.randn(4, 4), index=index, columns=index)
        df['Totals', ''] = df.sum(1)
        df = df.consolidate()

    def test_ix_preserve_names(self):
        result = self.ymd.ix[2000]
        result2 = self.ymd['A'].ix[2000]
        self.assertEquals(result.index.names, self.ymd.index.names[1:])
        self.assertEquals(result2.index.names, self.ymd.index.names[1:])

        result = self.ymd.ix[2000, 2]
        result2 = self.ymd['A'].ix[2000, 2]
        self.assertEquals(result.index.name, self.ymd.index.names[2])
        self.assertEquals(result2.index.name, self.ymd.index.names[2])

    def test_partial_set(self):
        # GH #397
        df = self.ymd.copy()
        exp = self.ymd.copy()
        df.ix[2000, 4] = 0
        exp.ix[2000, 4].values[:] = 0
        assert_frame_equal(df, exp)

        df['A'].ix[2000, 4] = 1
        exp['A'].ix[2000, 4].values[:] = 1
        assert_frame_equal(df, exp)

        df.ix[2000] = 5
        exp.ix[2000].values[:] = 5
        assert_frame_equal(df, exp)

        # this works...for now
        df['A'].ix[14] = 5
        self.assertEquals(df['A'][14], 5)

    def test_unstack_preserve_types(self):
        # GH #403
        self.ymd['E'] = 'foo'
        self.ymd['F'] = 2

        unstacked = self.ymd.unstack('month')
        self.assert_(unstacked['A', 1].dtype == np.float64)
        self.assert_(unstacked['E', 1].dtype == np.object_)
        self.assert_(unstacked['F', 1].dtype == np.float64)

    def test_partial_ix_missing(self):
        result = self.ymd.ix[2000, 0]
        expected = self.ymd.ix[2000]['A']
        assert_series_equal(result, expected)

        # need to put in some work here

        # self.ymd.ix[2000, 0] = 0
        # self.assert_((self.ymd.ix[2000]['A'] == 0).all())

        self.assertRaises(Exception, self.ymd.ix.__getitem__, (2000, 6))
        self.assertRaises(Exception, self.ymd.ix.__getitem__, (2000, 6), 0)

    def test_to_html(self):
        self.ymd.columns.name = 'foo'
        self.ymd.to_html()
        self.ymd.T.to_html()

if __name__ == '__main__':

    # unittest.main()
    import nose
    # nose.runmodule(argv=[__file__,'-vvs','-x', '--pdb-failure'],
    #                exit=False)
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)

