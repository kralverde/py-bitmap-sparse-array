from sparse_array import SparseArray

def test_creation():
    global sa
    sa = SparseArray()

def test_appending():
    global sa
    sa = SparseArray([1])
    assert sa.bit_field() == bytes([0b1])

    sa = SparseArray()
    for i in range(100):
        sa.append(str(i))
        assert sa[i] == str(i)
    
def test_length():
    global sa
    assert len(sa) == 100

def test_iter():
    global sa
    for i, val in enumerate(sa.iter_values_over_range_with_none()):
        assert str(i) == val
    assert i == 99

def test_map():
    global sa
    def mapping(element):
        assert element
    map(mapping, sa.iter_values_over_range_with_none())

def test_find():
    global sa
    i = sa.index('1')
    assert i == 1

def test_not_find():
    global sa
    try:
        i = sa.index('1000')
    except ValueError:
        return
    assert False

def test_unsets():
    global sa
    for i in range(100):
        del sa[i]
        for j in range(i + 1, 100):
            assert sa[j] == str(j)

def test_unsets_rev():
    x = list(range(100))
    for i in range(99, -1, -1):
        del x[i]
        for j in range(i):
            assert j < i
            assert x[j] == j

    sa = SparseArray(range(100))
    for i in range(99, -1, -1):
        del sa[i]
        try:
            sa[i]
        except IndexError:
            pass
        else:
            assert False
        for j in range(i):
            assert j < i
            assert sa[j] == j

def test_insert():
    x = list(range(100))
    sa = SparseArray[int](x)

    x.insert(50, 1000)
    sa.insert(50, 1000)

    assert len(x) == len(sa)

    for i1, i2 in zip(x, sa.iter_values_over_range_with_none()):
        assert i1 == i2
    