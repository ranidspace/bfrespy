from ..core import IResData, ResFileLoader


class Buffer(IResData):
    def __init__(self):
        self.stride: int
        self.data: list[list[int]]
        self.flags: int
        self.buff_offs: int

    @property
    def size(self):
        x = 0
        for i in self.data:
            x += len(i)
        return x

    def load(self, loader: ResFileLoader):
        data_pointer = loader.read_uint32()
        size = loader.read_uint32()
        handle = loader.read_uint32()
        self.stride = loader.read_uint16()
        num_buffering = loader.read_uint16()
        context_pointer = loader.read_uint32()
        data_offs = loader.read_offset()
        with loader.TemporarySeek(data_offs):
            data = []
            for i in range(num_buffering):
                data.append(loader.read_bytes(size))
            self.data = data
