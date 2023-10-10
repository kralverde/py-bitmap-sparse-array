This code has been transpiled from `js-sparse-array <https://github.com/pgte/js-sparse-array/commit/a489406f6abb5aa4bb7b536b8b73289944bf4343>`_ and has minimal changes. 

Usage
-----

SparseArray implements `MutableSequence`.

We suggest you import the SparseArray as follows:

>>> from sparse_array import SparseArray

Setting and getting
^^^^^^^^^^^^^^^^^^^

>>> sa = SparseArray()
>>> sa[1000000] = 'value'
>>> sa[1000000]
'value'
>>> sa[1]
IndexError()
>>> len(sa)
1000001

Iterating
^^^^^^^^^
You cannot iterate over the `SparseArray` itself. Instead, 3 generators are provided.

>>> sa = SparseArray()
>>> sa[0] = '0'
>>> sa[2] = '2'

`SparseArray.indices()` returns a generator of indices that have values.

>>> list(sa.indices())
[0, 2]

`SparseArray.items()` returns a generator of tuples of indices and values, similar to `Mapping.items()`.

>>> list(sa.items())
[(0, '0'), (2, '2')]

`SparseArray.values()` returns a generator of values with a default value for non-set indices.

>>> list(sa.values())
['0', None, '2']
>>> list(sa.values('default'))
['0', 'default', '2']
