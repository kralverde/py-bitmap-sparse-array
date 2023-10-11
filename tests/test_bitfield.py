from bitmap_sparse_array import SparseArray

def test_bitfield():
    sa = SparseArray()
    assert sa.bit_field() == b''
    sa[0] = 0
    assert sa.bit_field() == bytes([0b1])
    sa[1] = 1
    assert sa.bit_field() == bytes([0b11])
    sa[6] = 6
    assert sa.bit_field() == bytes([0b1000011])
    sa[7] = 7
    assert sa.bit_field() == bytes([0b11000011])
    sa[8] = 8
    assert sa.bit_field() == bytes([0b11000011, 0b1])
    sa[10] = 10
    assert sa.bit_field() == bytes([0b11000011, 0b101])
    sa[15] = 15
    assert sa.bit_field() == bytes([0b11000011, 0b10000101])
    sa[16] = 16
    assert sa.bit_field() == bytes([0b11000011, 0b10000101, 0b1])
