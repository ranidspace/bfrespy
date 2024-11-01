import io
from bfrespy.shared.core import ResFileLoader, IResData
from ..shared.res_file import ResFile

class ResFileSwitchLoader(ResFileLoader):
    def __init__(self, res_file: ResFile, 
                 raw: io.BytesIO, 
                 res_data: IResData = None):
        super().__init__(res_file, raw, res_data)
        self.endianness = '<'
        self.is_switch = True

    # TODO load_custom if needed https://github.com/KillzXGaming/BfresLibrary/blob/6f387692bbbddefce278716313cd714a2cdaa95d/BfresLibrary/Switch/Core/ResFileLoader.cs#L80

    def read_offset(self):
        """Reads a BFRES offset which is relative to itself, and returns the absolute address"""
        # XXX Im pretty sure this is to do with relocation tables but the
        # the line in BfresLibrary is return "offset == 0 ? 0 : offset"
        #
        # Rewrite when relocation tables are implemented I guess?
        offset = self.read_uint64()
        return 0 if offset == 0 else offset
    
    def readsize(self):
        return self.read_uint64()
    
    def load_header_block(self):
        offset = self.read_uint32()
        size = self.read_uint64()

    def load_string(self, encoding = None) -> str:
        offset = self.read_offset()
        if (offset == 0):
            return None
        # TODO Implement String Cache
        if (offset < 0 or offset > len(self.raw.getbuffer())):
            return ""
        with self.TemporarySeek(self, offset, io.SEEK_SET) as reader:
            return self.read_string(encoding)
        
    def load_strings(self, count, encoding = None):
        offsets = self.read_uint64s(count)
        names: list[str] = [None] * len(offsets)
        with self.TemporarySeek(self):
            for i, offset in enumerate(offsets):
                if offset == 0:
                    continue
                # XXX Implement String Cache again
                else:
                    self.seek(offset)
                    names[i] = self.read_string(encoding)

    def read_string(self, encoding = None):
        size = self.read_uint16()
        return self.read_null_string(encoding)


        
