import io
from .core import IResData
from ..binary_io import BinaryReader

class ResFile(IResData):
    def __init__(self, raw: io.BytesIO):
        self.is_platform_switch: bool
        if (self.is_switch_binary(raw)):
            from ..switch.core import ResFileSwitchLoader 
            with ResFileSwitchLoader(self, raw) as loader:
                loader.execute()
        else:
            raise NotImplementedError(
                "Sorry, WiiU files aren't supported yet")
    
    def is_switch_binary(self, raw):
        with BinaryReader(raw) as reader:
            reader.endianness = '<'

            reader.seek(4, io.SEEK_SET)
            padding_check = reader.read_uint32()
            reader.seek(0, io.SEEK_SET)
            
            return padding_check == 0x20202020
        
    def set_version_info(self, version):
        self.version_major = version >> 24
        self.version_major2 = version >> 16 & 0xFF
        self.version_minor = version >> 8 & 0xFF
        self.version_minor2 = version & 0xFF

    def load(self, loader):
        self.is_platform_switch = loader.is_switch
        if (loader.is_switch):
            from bfrespy.switch import ResFileParser
            from bfrespy.switch.core import ResFileSwitchLoader
            ResFileParser.load(loader, self)