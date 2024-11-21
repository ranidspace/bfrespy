import io
from ..core import IResData, ResFileLoader


class Buffer(IResData):
    def __init__(self):
        self.stride: int
        self.data: list[bytes]
        self.flags: int
        self.buff_offs: int

    @property
    def size(self):
        return sum([len(x) for x in self.data])

    def load(self, loader: ResFileLoader):
        data_pointer = loader.read_uint32()
        size = loader.read_uint32()
        handle = loader.read_uint32()
        self.stride = loader.read_uint16()
        num_buffering = loader.read_uint16()
        context_pointer = loader.read_uint32()
        data_offs = loader.read_offset()
        with loader.temporary_seek(data_offs):
            data = []
            for i in range(num_buffering):
                data.append(loader.read_bytes(size))
            self.data = data
