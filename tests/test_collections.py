from bitmap_sparse_array import SparseArray

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
    for i, val in enumerate(sa.values()):
        assert str(i) == val
    assert i == 99

def test_map():
    global sa
    def mapping(element):
        assert element
    map(mapping, sa.values())

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

def test_iters_and_remove():
    x = SparseArray(range(100))
    assert len(x) == 100
    for i, v in enumerate(x.values()):
        assert i == v
    for i, (ii, iv) in enumerate(x.items()):
        assert i == ii
        assert i == iv
    for i, ii in enumerate(x.indices()):
        assert i == ii

    assert x.index(50) == 50
    try:
        x.index(200)
    except ValueError:
        pass
    else:
        assert False

    x.remove(50)

    try:
        x.index(50)
    except ValueError:
        pass
    else:
        assert False

    assert len(x) == 100
    for i, v in enumerate(x.values()):
        if i == 50:
            assert v is None
        else:
            assert i == v
    assert i == 99
    for i, (ii, iv) in enumerate(x.items()):
        m_i = i
        assert ii != 50
        if i >= 50:
            m_i += 1
        assert m_i == ii
        assert m_i == iv
    assert i == 98
    for i, ii in enumerate(x.indices()):
        m_i = i
        assert ii != 50
        if i >= 50:
            m_i += 1
        assert m_i == ii
    assert i == 98

    for _, value in [value for value in x.items()]:
        x.remove(value)

    assert len(x) == 0

def test_null_value():
    x = SparseArray()
    x[1] = None
    assert x.get(1, 'not null') is None
