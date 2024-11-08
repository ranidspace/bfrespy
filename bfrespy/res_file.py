import io
import struct
from enum import IntFlag
from .core import IResData


class ResFile(IResData):
    """Represents a NintendoWare for Cafe (NW4F) graphics data archive file."""

    def __init__(self, stream: io.BufferedReader):
        """Initializes a new instance of the ResFile class from a stream"""
        self.version: int
        self.version_major: int
        self.version_major2: int
        self.version_minor: int
        self.version_minor2: int
        self.external_flag: self.ExternalFlags

        self.alignment = 0xC
        self.data_alignment_override = 0

        self.is_platform_switch: bool

        if (self.is_switch_binary(stream)):
            from bfrespy.switch.core import ResFileSwitchLoader

            with ResFileSwitchLoader(self, stream) as loader:
                loader.execute()
        else:
            raise NotImplementedError(
                "Sorry, WiiU files aren't supported yet")

    # Public Methods

    def is_switch_binary(self, stream):

        stream.seek(4, io.SEEK_SET)
        padding_check = struct.unpack('<I', stream.read(4))[0]
        stream.seek(0, io.SEEK_SET)

        return padding_check == 0x20202020

    # Properties

    @property
    def data_alignment(self):
        if (self.is_platform_switch):
            return (1 << int(self.alignment))
        else:
            return self.alignment

    @data_alignment.setter
    def data_alignment(self, value):
        if (self.is_platform_switch):
            self.alignment = int(value >> 7)
        else:
            self.alignment = int(value)

    @property
    def version_full(self):
        return f'{self.version_major}{self.version_major2}'\
            f'{self.version_minor}{self.version_minor2}'

    # Internal Methods

    def set_version_info(self, version):
        self.version_major = version >> 24
        self.version_major2 = version >> 16 & 0xFF
        self.version_minor = version >> 8 & 0xFF
        self.version_minor2 = version & 0xFF

    # Enums

    class ExternalFlags(IntFlag):
        is_external_model_uninitalized = 1 << 0
        has_external_string = 1 << 1
        holds_external_strings = 1 << 2
        has_external_gpu = 1 << 3

        mesh_codec_resave = 1 << 7

    def has_flag(self, value, flag):
        return value & flag == flag

    # Methods

    def load(self, loader):
        self.is_platform_switch = loader.is_switch
        if (loader.is_switch):
            from bfrespy import switch
            switch.ResFileParser.load(loader, self)
