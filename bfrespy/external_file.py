import io
from . import core


class ExternalFile(core.IResData):
    def __init__(self):
        self.data: bytes
        self.loaded_file_data: object

    def get_stream(self, writeable=False):
        return io.BytesIO(self.data)

    def load(self, loader: core.ResFileLoader):
        offs_data = loader.read_offset()
        siz_data = loader.read_size()
        self.data = loader.load_custom(
            bytes, loader.read_bytes, siz_data, offset=offs_data
        )
