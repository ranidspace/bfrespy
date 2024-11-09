from ..core import IResData, ResFileLoader


class MemoryPool(IResData):
    __size = 288

    def __init__(self):
        pool_array = bytearray()

    def load(self, loader):
        pass
        # nothing?


class BufferSize(IResData):
    def __init__(self):
        self.size: int
        self.flags: int

    def load(self, loader: ResFileLoader):
        self.size = loader.read_uint32()
        self.flags = loader.read_uint32()
        loader.seek(40)


class BufferInfo(IResData):
    buff_offs = None
    vtx_buffer_data: list[bytearray] = None
    index_buffer_data: list[bytearray] = None
    unk = 34

    @classmethod
    def load(cls, loader: ResFileLoader):
        cls.unk = loader.read_uint32()
        size = loader.read_uint32()
        cls.buff_offs = loader.read_int64()
        padding = loader.read_bytes(16)
