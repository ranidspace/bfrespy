from enum import IntEnum
from ... import core
from ...models import TexSampler
from ... import gx2


class SamplerSwitch(core.IResData):
    __FLAGS_SHRINK_MASK = 0b00000000_00110000
    __FLAGS_EXPAND_MASK = 0b00000000_00001100
    __FLAGS_MIPMAP_MASK = 0b00000000_00000011

    def __init__(self):
        self.wrapmode_u = self.TexClamp.Repeat
        self.wrapmode_v = self.TexClamp.Repeat
        self.wrapmode_w = self.TexClamp.Clamp
        self.compare_func = self.CompareFunction.Never
        self.border_color_type = self.TexBorderType.White
        self.anisotropic = self.MaxAnisotropic.Ratio_1_1
        self.lod_bias = 0.0
        self.min_lod = 0.0
        self.max_lod = 13.0
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

    def to_tex_sampler(self):
        sampler = TexSampler()
        sampler.__filter_flags = self.__filter_flags

        if (self.wrapmode_u in self.clamp_modes):
            sampler.clamp_x = self.clamp_modes[self.wrapmode_u]
        if (self.wrapmode_v in self.clamp_modes):
            sampler.clamp_y = self.clamp_modes[self.wrapmode_v]
        if (self.wrapmode_w in self.clamp_modes):
            sampler.clamp_z = self.clamp_modes[self.wrapmode_w]
        if (self.anisotropic in self.anisotropic_modes):
            sampler.max_anisotropic_ratio = self.anisotropic_modes[self.anisotropic]
        if (self.compare_func in self.compare_modes):
            sampler.depth_compare_func = self.compare_modes[self.compare_func]
        if (self.border_color_type in self.border_modes):
            sampler.border_type = self.border_modes[self.border_color_type]

        if (self.mipmap in self.mip_filters):
            sampler.mip_filter = self.mip_filters[self.mipmap]
        if (self.expand_xy in self.expand_filters):
            sampler.mag_filter = self.expand_filters[self.expand_xy]
        if (self.shrink_xy in self.shrink_filters):
            sampler.min_filter = self.shrink_filters[self.shrink_xy]

        sampler.max_lod = self.max_lod
        sampler.min_lod = self.min_lod
        sampler.lod_bias = self.lod_bias

        return sampler

    def load(self, loader: core.ResFileLoader):
        self.wrapmode_u = self.TexClamp(loader.read_byte())
        self.wrapmode_v = self.TexClamp(loader.read_byte())
        self.wrapmode_w = self.TexClamp(loader.read_byte())
        self.compare_func = self.CompareFunction(loader.read_byte())
        self.border_color_type = self.TexBorderType(loader.read_byte())
        self.anisotropic = self.MaxAnisotropic(loader.read_byte())
        self.__filter_flags = loader.read_uint16()
        self.min_lod = loader.read_single()
        self.max_lod = loader.read_single()
        self.lod_bias = loader.read_single()
        loader.seek(12)

    class MaxAnisotropic(IntEnum):
        # byte
        Ratio_1_1 = 0x1
        Ratio_2_1 = 0x2
        Ratio_4_1 = 0x4
        Ratio_8_1 = 0x8
        Ratio_16_1 = 0x10

    class MipFilterModes(IntEnum):
        # uint16
        None_ = 0
        Points = 1
        Linear = 2

    class ExpandFilterModes(IntEnum):
        # uint16
        Points = 1 << 2
        Linear = 2 << 2

    class ShrinkFilterModes(IntEnum):
        # uint16
        Points = 1 << 4
        Linear = 2 << 4

    class CompareFunction(IntEnum):
        """Represents compare functions used for depth and stencil tests."""
        # byte
        Never = 0
        Less = 1
        Equal = 2
        LessOrEqual = 3
        Greater = 4
        NotEqual = 5
        GreaterOrEqual = 6
        Always = 7

    class TexBorderType(IntEnum):

        """Represents type of border color to use."""
        # byte
        White = 0
        Transparent = 1
        Opaque = 2

    class TexClamp(IntEnum):
        """Represents how to treat texture coordinates outside of the
        normalized coordinate texture range.
        """
        # sbyte
        Repeat = 0
        Mirror = 1
        Clamp = 2
        ClampToEdge = 3
        MirrorOnce = 4
        MirrorOnceClampToEdge = 5

    expand_filters = {
        ExpandFilterModes.Linear: gx2.GX2TexXYFilterType.Bilinear,
        ExpandFilterModes.Points: gx2.GX2TexXYFilterType.Point,
    }

    shrink_filters = {
        ShrinkFilterModes.Linear: gx2.GX2TexXYFilterType.Bilinear,
        ShrinkFilterModes.Points: gx2.GX2TexXYFilterType.Point,
    }

    mip_filters = {
        MipFilterModes.Linear: gx2.GX2TexMipFilterType.Linear,
        MipFilterModes.Points: gx2.GX2TexMipFilterType.Point,
        MipFilterModes.None_: gx2.GX2TexMipFilterType.NoMip,
    }

    border_modes = {
        TexBorderType.Opaque: gx2.GX2TexBorderType.SolidBlack,
        TexBorderType.White: gx2.GX2TexBorderType.SolidWhite,
        TexBorderType.Transparent: gx2.GX2TexBorderType.ClearBlack,
    }

    compare_modes = {
        CompareFunction.Always: gx2.GX2CompareFunction.Always,
        CompareFunction.Equal: gx2.GX2CompareFunction.Equal,
        CompareFunction.Greater: gx2.GX2CompareFunction.Greater,
        CompareFunction.GreaterOrEqual: gx2.GX2CompareFunction.GreaterOrEqual,
        CompareFunction.Less: gx2.GX2CompareFunction.Less,
        CompareFunction.LessOrEqual: gx2.GX2CompareFunction.LessOrEqual,
        CompareFunction.Never: gx2.GX2CompareFunction.Never,
        CompareFunction.NotEqual: gx2.GX2CompareFunction.NotEqual,
    }

    clamp_modes = {
        TexClamp.Repeat: gx2.GX2TexClamp.Wrap,
        TexClamp.Mirror: gx2.GX2TexClamp.Mirror,
        TexClamp.MirrorOnce: gx2.GX2TexClamp.MirrorOnce,
        TexClamp.MirrorOnceClampToEdge: gx2.GX2TexClamp.MirrorOnceBorder,
        TexClamp.Clamp: gx2.GX2TexClamp.Clamp,
        TexClamp.ClampToEdge: gx2.GX2TexClamp.ClampBorder,
    }

    anisotropic_modes = {
        MaxAnisotropic.Ratio_1_1: gx2.GX2TexAnisoRatio.Ratio_1_1,
        MaxAnisotropic.Ratio_2_1: gx2.GX2TexAnisoRatio.Ratio_2_1,
        MaxAnisotropic.Ratio_4_1: gx2.GX2TexAnisoRatio.Ratio_4_1,
        MaxAnisotropic.Ratio_8_1: gx2.GX2TexAnisoRatio.Ratio_8_1,
        MaxAnisotropic.Ratio_16_1: gx2.GX2TexAnisoRatio.Ratio_16_1,
    }
