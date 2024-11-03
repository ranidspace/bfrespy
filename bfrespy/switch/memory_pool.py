from ..shared.core import IResData
from ..shared.core import ResFileLoader

class MemoryPool(IResData):
    __size = 288
    def __init__(self):
        pool_array = bytearray()
    
    def load(self, loader):
        pass
        #nothing?

class BufferSize(IResData):
    def __init__(self):
        self.size: int
        self.flags: int
    
    def load(self, loader: ResFileLoader):
        self.size = loader.read_uint32()
        self.flags = loader.read_uint32()
        loader.seek(40)

class BufferInfo(IResData):
    def __init__(self):
        self.buffer_offset: int
        self.vertex_buffer_data: list[bytearray]
        self.index_buffer_data: list[bytearray]
        self.unk: int
    
    def load(self, loader: ResFileLoader):
        self.unk = loader.read_uint32()
        size = loader.read_uint32()
        self.buffer_offset = loader.read_int64()
        padding = loader.read_bytes(16)