import io
from abc import ABC, abstractmethod
from ..binary_io import BinaryReader


class IResData(ABC):
    @abstractmethod
    def load(self, loader):
        """Loads raw data from the loader data stream into instances"""
        pass

class ResFileLoader(BinaryReader):
    def __init__(self, 
                 res_file, 
                 stream: io.BufferedReader,
                 leave_open = False, 
                 res_data: IResData = None
                 ):
        super().__init__(stream, leave_open)
        self.res_file = res_file
        self._data_map = {}
        self.is_switch: bool
        if (res_data):
            self.importable_file = res_data
    
    # Internal Methods

    def import_section(self,
                       raw = None,
                       res_data: IResData = None,
                       res_file = None,
                       ):
        if raw and res_data and res_file:
            platform_switch = False
            
            with BinaryReader(raw) as reader:
                reader.seek(24, io.SEEK_SET)
                platform_switch = reader.read_uint32 != 0
            
            if (platform_switch):
                from ..switch import ResFileSwitchLoader
                with ResFileSwitchLoader(res_file, raw, res_data) as reader:
                    reader.import_section()
        else:
            self.read_imported_file_header()

            if type(self.importable_file) is Shape:
                shape_offset = self.read_uint32()
                vertex_buff_offs = self.read_uint32()

                self.seek(shape_offset, io.SEEK_SET)
                self.importable_file.load(self)

                self.seek(vertex_buff_offs, io.SEEK_SET)
                buffer = VertexBuffer()
                buffer.load(self)
                self.importable_file.vertex_buffer = buffer
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
    
    def load(self, T, use_offset = True):
        if (not use_offset):
            return self.__read_res_data(T)
        offset = self.read_offset()
        if (offset == 0):
            return T()
        with self.TemporarySeek(self, offset, io.SEEK_SET):
            return self.__read_res_data(T)
        

    def load_custom(self, T, callback, arg, offset = None):
        offset = (offset 
                  if offset is not None 
                  else self.read_offset())
        if (offset == 0):
            return T()
        with (self.TemporarySeek(self, offset, io.SEEK_SET)):
            return callback(arg)

    def load_dict(self):
        from .common import ResDict
        offset = self.read_offset()
        if (offset == 0):
            return ResDict()
        with self.TemporarySeek(self):
            dict = ResDict()
            dict.load()
            return dict
    
    def load_list(self, T, count, offset = None):
        list_ = []
        offset = offset if offset else self.read_offset()
        if (offset == 0 or count == 0):
            return []
        with self.TemporarySeek(self, offset):
            while count > 0:
                list_.append(self.__read_res_data(T))
                count -= 1
            return list_
    
    def load_string(self, encoding = None):
        """Reads and returns a str instance from the following offset or None
        if the read offset is 0.
        """
        offset = self.read_offset()
        if (offset == 0):
            return None
        # TODO implement string cache
        with self.TemporarySeek(self, offset, io.SEEK_SET):
            return self.read_string(encoding)
        
    def load_dict_values(self, T: IResData,
                         dict_offset = None, 
                         values_offset = None):
        """Reads and returns a ResDict instance with elements of type T from
        the following offset or returns an empty instance if the
        read offset is 0.
        """
        from .common import ResDict
        if not (dict_offset or values_offset):
            values_offset = self.read_offset()
            dict_offset = self.read_offset()
        if (dict_offset == 0):
            return ResDict()
        with self.TemporarySeek(self, dict_offset, io.SEEK_SET):
            dict_ = ResDict()
            dict_.load(self)

            keys = list(dict_.keys())
            values = self.load_list(T, len(dict_), values_offset)

            dict_.clear()
            for i in range(len(keys)):
                dict_.add(keys[i], values[i])
            return dict_

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
            print(f"Invalid signature, expected '{valid_signature}' but got\
                   '{signature}' at position {self.tell()}.")



    def read_offset(self):
        """Reads a BFRES offset which is relative to itself,
        and returns the absolute address."""
        offset = self.read_uint32
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
                return T(existing_instance)
        else:
            self._data_map[offset] = instance
            return instance