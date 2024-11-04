from enum import IntEnum
from ...shared.core import IResData, ResFileLoader


class SamplerSwitch(IResData):
    __FLAGS_SHRINK_MASK = 0b00000000_00110000
    __FLAGS_EXPAND_MASK = 0b00000000_00001100
    __FLAGS_MIPMAP_MASK = 0b00000000_00000011

    def __init__(self):
        self.wrapmode_u = self.TexClamp.Repeat
        self.wrapmode_v = self.TexClamp.Repeat
        self.wrapmode_w = self.TexClamp.Clamp
        self.compare_func = self.CompareFunction.Never
        self.border_colour_type = self.TexBorderType.White
        self.anisotropic = self.MaxAnisotropic.Ratio_1_1
        self.lod_bias = 0
        self.min_lod = 0
        self.max_lod = 13
        self.__filter_flags = 42

    # Properties

    @property
    def shrink_xy(self):
        return self.ShrinkFilterModes(self.__filter_flags
                                      & self.__FLAGS_SHRINK_MASK)

    @shrink_xy.setter
    def shrink_xy(self, value):
        self.__filter_flags = (self.__filter_flags
                               & ~self.__FLAGS_SHRINK_MASK
                               | int(value))

    @property
    def expand_xy(self):
        return self.ExpandFilterModes(self.__filter_flags
                                      & self.__FLAGS_EXPAND_MASK)

    @expand_xy.setter
    def expand_xy(self, value):
        self.__filter_flags = (self.__filter_flags
                               & ~self.__FLAGS_EXPAND_MASK
                               | int(value))

    @property
    def mipmap(self):
        return self.MipFilterModes(self.__filter_flags
                                   & self.__FLAGS_MIPMAP_MASK)

    @mipmap.setter
    def mipmap(self, value):
        self.__filter_flags = (self.__filter_flags
                               & ~self.__FLAGS_MIPMAP_MASK
                               | int(value))

    # Methods

    # byte

    class MaxAnisotropic(IntEnum):
        Ratio_1_1 = 0x1
        Ratio_2_1 = 0x2
        Ratio_4_1 = 0x4
        Ratio_8_1 = 0x8
        Ratio_16_1 = 0x10

    # uint16
    class MipFilterModes(IntEnum):
        None_ = 0
        Points = 1
        Linear = 2

    # uint16
    class ExpandFilterModes(IntEnum):
        Points = 1 << 2
        Linear = 2 << 2

    # uint16
    class ShrinkFilterModes(IntEnum):
        Points = 1 << 4
        Linear = 2 << 4

    # byte
    class CompareFunction(IntEnum):
        """Represents compare functions used for depth and stencil tests."""
        Never = 0
        Less = 1
        Equal = 2
        LessOrEqual = 3
        Greater = 4
        NotEqual = 5
        GreaterOrEqual = 6
        Always = 7

    # byte
    class TexBorderType(IntEnum):
        """Represents type of border color to use."""
        White = 0
        Transparent = 1
        Opaque = 2

    # sbyte
    class TexClamp(IntEnum):
        """Represents how to treat texture coordinates outside of the
        normalized coordinate texture range.
        """
        Repeat = 0
        Mirror = 1
        Clamp = 2
        ClampToEdge = 3
        MirrorOnce = 4
        MirrorOnceClampToEdge = 5
