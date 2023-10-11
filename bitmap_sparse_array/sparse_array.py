import sys

from typing import MutableSequence, List, TypeVar, Tuple, Generator, Optional, Iterable, Iterator

BITS_PER_BYTE = 8

def _pop_count(v: int) -> int:
    v = v - ((v >> 1) & 0x55555555)
    v = (v & 0x33333333) + ((v >> 2) & 0x33333333)
    return ((v + (v >> 4) & 0xF0F0F0F) * 0x1010101) >> 24

T = TypeVar('T')
class SparseArray(MutableSequence[T]):
    def __init__(self, initlist: Optional[Iterable[T]]=None) -> None:
        self._bit_arrays = bytearray()
        self._data: List[Tuple[int, T]] = []
        self._length = 0
        self._changed_length = False
        self._changed_data = False
        if initlist:
            self.extend(initlist)

    def _sort_data(self) -> None:
        if self._changed_data:
            self._data.sort(key=lambda x: x[0])
        self._changed_data = False

    def _set_internal_position(self, pos: int, index: int, value: T, needs_sort: bool) -> None:
        elem = (index, value)
        if needs_sort:
            self._sort_data()
            self._data[pos] = elem
        else:
            data_len = len(self._data)
            if data_len > 0:
                if self._data[data_len - 1][0] >= index:
                    self._data.append(elem)
                elif self._data[0][0] <= index:
                    self._data.insert(0, elem)
                else:
                    random_index = round(data_len / 2)
                    self._data.insert(random_index, elem)
            else:
                self._data.append(elem)
            self._changed_data = True
            self._changed_length = True

    def _unset_internal_position(self, pos: int) -> None:
        self._sort_data()
        self._data.pop(pos)

    def _set_bit(self, index: int) -> None:
        byte_pos = self._byte_pos_for(index, False)
        self._bit_arrays[byte_pos] |= (1 << (index - (byte_pos * BITS_PER_BYTE)))

    def _unset_bit(self, index: int) -> None:
        byte_pos = self._byte_pos_for(index, False)
        self._bit_arrays[byte_pos] &= ~(1 << (index - (byte_pos * BITS_PER_BYTE)))

    def _byte_pos_for(self, index: int, no_create: bool) -> int:
        byte_pos = index // BITS_PER_BYTE
        target_length = byte_pos + 1
        while not no_create and len(self._bit_arrays) < target_length:
            self._bit_arrays.append(0)
        return byte_pos

    def _internal_position_for(self, index: int, no_create: bool) -> int:
        byte_pos = self._byte_pos_for(index, no_create)
        if byte_pos >= len(self._bit_arrays):
            return -1
        bite = self._bit_arrays[byte_pos]
        bit_pos = index - byte_pos * BITS_PER_BYTE
        exists = (bite & (1 << bit_pos)) > 0
        if not exists:
            return -1
        previous_pop_count = sum(_pop_count(b) for b in self._bit_arrays[:byte_pos])
        mask = ~(0xffffffff << (bit_pos + 1))
        byte_pop_count = _pop_count(bite & mask)
        array_pos = previous_pop_count + byte_pop_count - 1
        return array_pos

    def __setitem__(self, index: int, item: T) -> None:  # type: ignore[override]
        if not isinstance(index, int):
            raise TypeError(f'SparseArray indices must be integers, not {type(index)}')
        if index < 0:
            index = len(self) + index
        pos = self._internal_position_for(index, False)
        if pos < 0:
            pos = len(self._data)
            self._set_bit(index)
            self._changed_data = True
            needs_sort = False
        else:
            needs_sort = True
        self._set_internal_position(pos, index, item, needs_sort)
        self._changed_length = True

    def __delitem__(self, index: int) -> None:  # type: ignore[override]
        if not isinstance(index, int):
            raise TypeError(f'SparseArray indices must be integers, not {type(index)}')
        if index < 0:
            index = len(self) + index
        pos = self._internal_position_for(index, False)
        if pos >= 0:
            self._unset_internal_position(pos)
            self._unset_bit(index)
            self._changed_length = True
            self._changed_data = True

    def __getitem__(self, index: int) -> T:  # type: ignore[override]
        if not isinstance(index, int):
            raise TypeError(f'SparseArray indices must be integers, not {type(index)}')
        self._sort_data()
        pos = self._internal_position_for(index, True)
        if pos < 0:
            raise IndexError()
        return self._data[pos][1]
    
    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError()
    
    def indices(self) -> Generator[int, None, None]:
        self._sort_data()
        return (x[0] for x in self._data)

    def items(self) -> Generator[Tuple[int, T], None, None]:
        self._sort_data()
        return (x for x in self._data)
        
    def values(self, *, default: Optional[T] = None, start: int = 0, end: Optional[int] = None) -> Generator[Optional[T], None, None]:
        self._sort_data()
        return (self.get(x, default if default is not None else None) for x in range(start, min(end or len(self), len(self))))

    def append(self, value: T) -> None:
        self[len(self)] = value

    def remove(self, value: T) -> None:
        index = self.index(value)
        del self[index]

    def index(self, value: T, start: int = 0, stop: int = sys.maxsize) -> int:
        self._sort_data()
        for d_index, d_value in self._data:
            if d_index < start: 
                continue
            if d_index >= stop: 
                break
            if d_value == value:
                return d_index
        raise ValueError()

    def get(self, index: int, default: Optional[T] = None) -> Optional[T]:
        try:
            return self[index]
        except IndexError:
            return default

    def insert(self, index: int, value: T) -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        self._sort_data()
        if self._changed_length:
            if len(self._data) > 0:
                last = self._data[-1]
                self._length = last[0] + 1
            else:
                self._length = 0
            self._changed_length = False
        return self._length

    def bit_field(self) -> bytes:
        raw_nums = []
        pending_bits_for_resulting_byte = 8
        pending_bits_for_new_byte = 0
        resulting_byte = 0
        new_byte = 0
        pending = self._bit_arrays[:]
        while len(pending) > 0 or pending_bits_for_new_byte > 0:
            if pending_bits_for_new_byte == 0:
                new_byte = pending.pop(0)
                pending_bits_for_new_byte = BITS_PER_BYTE
            
            using_bits = min(pending_bits_for_new_byte, pending_bits_for_resulting_byte)
            mask = ~(0b11111111 << using_bits)
            masked = new_byte & mask
            resulting_byte |= masked << (8 - pending_bits_for_new_byte)
            new_byte = new_byte >> using_bits
            pending_bits_for_new_byte -= using_bits
            pending_bits_for_resulting_byte -= using_bits

            if pending_bits_for_resulting_byte == 0 or (pending_bits_for_new_byte == 0 and len(pending) == 0):
                raw_nums.append(resulting_byte)
                resulting_byte = 0
                pending_bits_for_resulting_byte = 8

        for i in range(len(raw_nums) - 1, 0, -1):
            val = raw_nums[i]
            if val == 0:
                raw_nums.pop()
            else:
                break

        return bytes(raw_nums)
