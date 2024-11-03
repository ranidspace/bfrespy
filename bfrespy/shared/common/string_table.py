import io
from ..core import IResData, ResFileLoader

class StringTable(IResData):
    def __init__(self):
        self.strings = []
    
    def load(self, loader: ResFileLoader):
        self.strings.clear()
        if loader.is_switch:
            loader.seek(-0x14, io.SEEK_CUR)
            signature = loader.read_uint32()
            block_offs = loader.read_uint32()
            block_size = loader.read_uint64()
            string_count = loader.read_uint32()

            for i in range(string_count):
                size = loader.read_uint16()
                self.strings.append(loader.read_null_string())
                loader.align(2)