
Performance Benchmarks
======================

These historical benchmark graphs were produced with `vbench
<http://github.com/wesm/vbench>`__.

The ``pandas_vb_common`` setup script can be found here_

.. _here: https://github.com/wesm/pandas/tree/master/vb_suite

Produced on a machine with

  - Intel Core i7 950 processor
  - (K)ubuntu Linux 12.10
  - Python 2.7.2 64-bit (Enthought Python Distribution 7.1-2)
  - NumPy 1.6.1

frame_ctor
----------

series_ctor_from_dict
~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/series_ctor_from_dict.txt

frame_ctor_nested_dict_int64
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/frame_ctor_nested_dict_int64.txt

frame_ctor_nested_dict
~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/frame_ctor_nested_dict.txt

frame_ctor_list_of_dict
~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/frame_ctor_list_of_dict.txt

frame_methods
-------------

frame_fancy_lookup
~~~~~~~~~~~~~~~~~~
.. include:: vbench/frame_fancy_lookup.txt

frame_fancy_lookup_all
~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/frame_fancy_lookup_all.txt

groupby
-------

groupby_multi_cython
~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/groupby_multi_cython.txt

groupby_multi_python
~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/groupby_multi_python.txt

groupby_multi_series_op
~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/groupby_multi_series_op.txt

groupby_series_simple_cython
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/groupby_series_simple_cython.txt

index_object
------------

index_datetime_union
~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/index_datetime_union.txt

index_datetime_intersection
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/index_datetime_intersection.txt

indexing
--------

dataframe_getitem_scalar
~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/dataframe_getitem_scalar.txt

indexing_dataframe_boolean_rows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/indexing_dataframe_boolean_rows.txt

series_getitem_scalar
~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/series_getitem_scalar.txt

dataframe_get_value
~~~~~~~~~~~~~~~~~~~
.. include:: vbench/dataframe_get_value.txt

datamatrix_getitem_scalar
~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/datamatrix_getitem_scalar.txt

indexing_dataframe_boolean_rows_object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/indexing_dataframe_boolean_rows_object.txt

join_merge
----------

join_dataframe_index_single_key_bigger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/join_dataframe_index_single_key_bigger.txt

append_frame_single_mixed
~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/append_frame_single_mixed.txt

join_dataframe_index_multi
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/join_dataframe_index_multi.txt

series_align_int64_index
~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/series_align_int64_index.txt

join_dataframe_index_single_key_small
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/join_dataframe_index_single_key_small.txt

append_frame_single_homogenous
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/append_frame_single_homogenous.txt

series_align_left_monotonic
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/series_align_left_monotonic.txt

miscellaneous
-------------

misc_cache_readonly
~~~~~~~~~~~~~~~~~~~
.. include:: vbench/misc_cache_readonly.txt

panel_ctor
----------

panel_from_dict_two_different_indexes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/panel_from_dict_two_different_indexes.txt

panel_from_dict_equiv_indexes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/panel_from_dict_equiv_indexes.txt

panel_from_dict_same_index
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/panel_from_dict_same_index.txt

panel_from_dict_all_different_indexes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/panel_from_dict_all_different_indexes.txt

reindex
-------

reindex_fillna_pad
~~~~~~~~~~~~~~~~~~
.. include:: vbench/reindex_fillna_pad.txt

reindex_frame_level_reindex
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/reindex_frame_level_reindex.txt

reindex_daterange_pad
~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/reindex_daterange_pad.txt

reindex_fillna_backfill
~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/reindex_fillna_backfill.txt

reindex_daterange_backfill
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/reindex_daterange_backfill.txt

reindex_multiindex
~~~~~~~~~~~~~~~~~~
.. include:: vbench/reindex_multiindex.txt

dataframe_reindex_daterange
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/dataframe_reindex_daterange.txt

frame_drop_duplicates
~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/frame_drop_duplicates.txt

reindex_frame_level_align
~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/reindex_frame_level_align.txt

dataframe_reindex_columns
~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/dataframe_reindex_columns.txt

frame_sort_index_by_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/frame_sort_index_by_columns.txt

sparse
------

sparse_series_to_frame
~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/sparse_series_to_frame.txt

stat_ops
--------

stat_ops_series_std
~~~~~~~~~~~~~~~~~~~
.. include:: vbench/stat_ops_series_std.txt

stat_ops_level_frame_sum
~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/stat_ops_level_frame_sum.txt

stat_ops_level_series_sum_multiple
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/stat_ops_level_series_sum_multiple.txt

stat_ops_level_frame_sum_multiple
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/stat_ops_level_frame_sum_multiple.txt

stat_ops_level_series_sum
~~~~~~~~~~~~~~~~~~~~~~~~~
.. include:: vbench/stat_ops_level_series_sum.txt

