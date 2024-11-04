import io
import struct
from enum import IntFlag
from .core import IResData
from ..binary_io import BinaryReader


class ResFile(IResData):
    def __init__(self, stream: io.BufferedReader):
        self.version: int
        self.version_major: int
        self.version_major2: int
        self.version_minor: int
        self.version_minor2: int

        self.is_platform_switch: bool
        if (self.is_switch_binary(stream)):
            from bfrespy.switch.core import ResFileSwitchLoader

            with ResFileSwitchLoader(self, stream) as loader:
                loader.execute()
        else:
            raise NotImplementedError(
                "Sorry, WiiU files aren't supported yet")

    def is_switch_binary(self, stream):

        stream.seek(4, io.SEEK_SET)
        padding_check = struct.unpack('<I', stream.read(4))[0]
        stream.seek(0, io.SEEK_SET)

        return padding_check == 0x20202020

    def set_version_info(self, version):
        self.version_major = version >> 24
        self.version_major2 = version >> 16 & 0xFF
        self.version_minor = version >> 8 & 0xFF
        self.version_minor2 = version & 0xFF

    class ext_flags(IntFlag):
        is_external_model_uninitalized = 1 << 0
        has_external_string = 1 << 1
        holds_external_strings = 1 << 2
        has_external_gpu = 1 << 3

        mesh_codec_resave = 1 << 7

    def has_flag(self, value, flag):
        return value & flag == flag

    def load(self, loader):
        self.is_platform_switch = loader.is_switch
        if (loader.is_switch):
            from bfrespy.switch import ResFileParser
            from bfrespy.switch.core import ResFileSwitchLoader
            ResFileParser.load(loader, self)
