import io
from abc import ABC, abstractmethod
from .binary_io import BinaryReader


class IResData(ABC):
    @abstractmethod
    def load(self, loader):
        """Loads raw data from the loader data stream into instances"""
        pass


class ResFileLoader(BinaryReader):
    def __init__(self, res_file, stream: io.BufferedReader,
                 leave_open=False, res_data=None):
        super().__init__(stream, leave_open)
        self.res_file = res_file
        self._data_map = {}
        self.is_switch: bool
        if (res_data):
            self.importable_file = res_data

    # Internal Methods

    def import_section(self, raw=None, res_data=None, res_file=None):
        if raw and res_data and res_file:
            platform_switch = False

            with BinaryReader(raw) as reader:
                reader.seek(24, io.SEEK_SET)
                platform_switch = reader.read_uint32 != 0

            if (platform_switch):
                from .switch import ResFileSwitchLoader
                with ResFileSwitchLoader(res_file, raw, res_data) as reader:
                    reader.import_section()
        else:
            self.read_imported_file_header()

            if isinstance(Shape, self.importable_file):
                shape_offs = self.read_uint32()
                vtx_buff_offs = self.read_uint32()

                self.seek(shape_offs, io.SEEK_SET)
                self.importable_file.load(self)

                self.seek(vtx_buff_offs, io.SEEK_SET)
                buffer = VertexBuffer()
                buffer.load(self)
                self.importable_file.vtx_buffer = buffer
            else:
                self.importable_file.load(self)

    def read_imported_file_header(self):
        self.endianness = '>'
        self.seek(8, io.SEEK_SET)
        self.res_file.version = self.read_uint32()
        self.res_file.set_version_info(self.res_file.version)

    def read_byte_order(self):
        self.endianness = '>'
        bom = self.__byte_order[self.read_uint16()]
        self.endianness = bom

    __byte_order = {
        0xFEFF: '>',
        0xFFFE: '<',
    }

    def execute(self):
        self.res_file.load(self)

    def load(self, T, use_offset=True):
        if (not use_offset):
            return self.__read_res_data(T)
        offset = self.read_offset()
        if (offset == 0):
            return T()
        with self.temporary_seek(offset, io.SEEK_SET):
            return self.__read_res_data(T)

    def load_custom(self, T, callback, *args, offset=None):
        offset = (offset
                  if offset is not None
                  else self.read_offset())
        if (offset == 0):
            return T()
        with (self.temporary_seek(offset, io.SEEK_SET)):
            return callback(*args)

    def load_dict(self, T):
        from .common import ResDict

        offset = self.read_offset()
        if (offset == 0):
            return ResDict()

        with self.temporary_seek(offset, io.SEEK_SET):
            dict = ResDict()
            dict.load(T, self)
            return dict

    def load_list(self, T, count, offset=None):
        list_ = []
        offset = offset if offset else self.read_offset()
        if (offset == 0 or count == 0):
            return []
        with self.temporary_seek(offset, io.SEEK_SET):
            while count > 0:
                list_.append(self.__read_res_data(T))
                count -= 1
            return list_

    def load_string(self, encoding=None):
        """Reads and returns a str instance from the following offset or None
        if the read offset is 0.
        """
        offset = self.read_offset()
        if (offset == 0):
            return None
        # TODO implement string cache
        with self.temporary_seek(offset, io.SEEK_SET):
            return self.read_string(encoding)

    def load_strings(self, count, encoding=None):
        """Reads and returns count of str from the following offset.
        """
        offsets = self.read_offsets(count)
        names = [None] * len(offsets)
        with self.temporary_seek():
            for i, offset in enumerate(offsets):
                if (offset == 0):
                    continue

                # TODO implement string cache
                self.seek(offset, io.SEEK_SET)
                names[i] = self.read_string(encoding)
            return names

    def load_dict_values(self, T: IResData, dict_offs=None, values_offs=None):
        """Reads and returns a ResDict instance with elements of type T from
        the following offset or returns an empty instance if the
        read offset is 0.
        """
        from .common import ResDict
        if not (dict_offs or values_offs):
            values_offs = self.read_offset()
            dict_offs = self.read_offset()
        if (dict_offs == 0):
            return ResDict()
        with self.temporary_seek(dict_offs, io.SEEK_SET):
            dict_ = ResDict()
            dict_.load(T, self)

            keys = list(dict_.keys())
            values = self.load_list(T, len(dict_), values_offs)

            dict_.clear()
            for i in range(len(keys)):
                dict_.append(keys[i], values[i])
            return dict_

    def load_relocation_table(self, offset):
        from .rlt import RelocationTable
        with self.temporary_seek(offset, io.SEEK_SET):
            self.relocation_table = self.__read_res_data(RelocationTable)

    def read_size(self):
        return self.read_uint32()

    def read_string(self, encoding):
        return self.read_null_string(encoding)

    def check_signature(self, valid_signature):
        """Reads a BFRES signature consisting of 4 ASCII characters encoded as
        a UInt32 and checks for validity.
        """
        signature = self.read_raw_string(4, 'ascii')
        if (signature != valid_signature):
            print(f"Invalid signature, expected '{valid_signature}' but got "
                  f"'{signature}' at position {self.tell()}.")

    def read_offset(self):
        """Reads a BFRES offset which is relative to itself,
        and returns the absolute address."""
        offset = self.read_uint32()
        return (0
                if offset == 0
                else self.tell() - 4 + offset
                )

    def read_offsets(self, count) -> list[int]:
        values = [] * count
        for i in count:
            values.append(self.read_offset())
        return values

    def read_bit32_bools(self, count) -> list[bool]:
        booleans = [None] * count
        if (count == 0):
            return booleans
        idx = 0
        while (idx < count):
            value = self.read_uint32()
            for i in range(32):
                if (count <= idx):
                    break
                booleans[idx] = (value & 0x1) != 0
                value >>= 1

                idx += 1
        return booleans

    # Private Methods

    def __read_res_data(self, T):
        offset = self.tell()
        instance = T()
        instance.load(self)

        existing_instance = self._data_map.get(offset)
        if existing_instance:
            return existing_instance
        else:
            self._data_map[offset] = instance
            return instance

# Byte/Uint32 Extensions


def _decode(byte, first_bit, bits):
    """Returns a int instance represented by the given number of bits,
    starting at the first_bit.
    """
    return ((byte >> first_bit) & ((1 << bits) - 1))


def _enable_bit(byte, index):
    return byte | (1 << index)


def _encode(byte, value, first_bit, bits):
    value = int(value)
    mask = (((1 << bits) - 1) << first_bit)
    byte &= ~mask
    value = (value << first_bit) & mask
    return (byte | value)


def _disable_bit(byte, index):
    return byte & ~(1 << index)


def _get_bit(byte, index):
    """Returns a value indicating whether the bit at the index in the current
    Byte is enabled or disabled.
    """
    return (byte & (1 << index)) != 0


def _set_bit(byte, index: int, enable: bool):
    """Returns the current Byte with the bit at the index enabled or disabled,
    according to enable."""
    if (enable):
        return _enable_bit(byte, index)
    else:
        return _disable_bit(byte, index)
