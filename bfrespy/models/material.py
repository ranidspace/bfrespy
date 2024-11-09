import math
from enum import IntEnum, auto

from .. import core, gx2
from ..common import (ResDict, ResString, TextureRef, UserData,
                      Srt2D, Srt3D, TexSrt, TexSrtMode)


class Material(core.IResData):
    """Represents an FMAT subsection of a Model subfile, storing information
    on with which textures and how technically a surface is drawn.
    """
    _signature = "FMAT"

    def __init__(self):

        self.name = ""
        self.flags = MaterialFlags.Visible

        self.shader_assign = ShaderAssign()

        self.renderinfos: ResDict[RenderInfo] = ResDict()
        self.texture_refs: list[TextureRef] = []
        self.samplers: ResDict[Sampler] = ResDict()
        self.userdata: ResDict[UserData] = ResDict()
        self.shader_params: ResDict[ShaderParam] = ResDict()

        self.shaderparamdata = bytearray()
        self.volatileflags = bytearray()

        self.render_state: RenderState
        self.renderinfo_size: int

        self.texture_slot_array: list[int]
        self.sampler_slot_array: list[int]
        self.param_idxs: list[int]

    @property
    def visible(self):
        return MaterialFlags in self.flags

    @visible.setter
    def visible(self, value):
        if value:
            self.flags |= MaterialFlags.Visible
        else:
            self.flags = MaterialFlags.None_

    def __fill_slots(self, count):
        slots = []
        for i in range(count):
            slots[i] = -1
        return slots

    def load(self, loader: core.ResFileLoader):
        loader.check_signature(self._signature)
        if (loader.is_switch):
            from ..switch.model import MaterialParser
            MaterialParser.load(loader, self)
        else:
            self.name = loader.load_string()
            self.flags = MaterialFlags(loader.read_uint32())
            idx = loader.read_uint16()
            num_renderinfo = loader.read_uint16()
            num_sampler = loader.read_byte()
            num_tex_ref = loader.read_byte()
            num_shader_param = loader.read_uint16()
            num_shader_paramVolatile = loader.read_uint16()
            siz_param_source = loader.read_uint16()
            siz_param_raw = loader.read_uint16()
            num_user_data = loader.read_uint16()
            self.renderinfos = loader.load_dict(RenderInfo)
            self.render_state = loader.load(RenderState)
            self.shader_assign = loader.load(ShaderAssign)
            self.texture_refs = loader.load_list(TextureRef, num_tex_ref)
            ofs_sample_list = loader.read_offset()  # Only use dict.
            self.samplers = loader.load_dict(Sampler)
            ofs_shader_param_list = loader.read_offset()  # Only use dict.
            self.shader_params = loader.load_dict(ShaderParam)
            self.shaderparamdata = loader.load_custom(bytes,
                                                      loader.read_bytes,
                                                      siz_param_source)
            self.userdata = loader.load_dict(UserData)
            self.volatileflags = loader.load_custom(bytearray,
                                                    loader.read_bytes,
                                                    math.ceil(num_shader_param / 8.0))
            user_pointer = loader.read_uint32()

        self.__read_shader_params(self.shaderparamdata,
                                  '<' if loader.is_switch else '>')

    def __read_shader_params(self, data: bytes, endianness: str):
        if (data == None):
            return
        # XXX this could be done with just a temporary reader and relocation?
        import io
        from ..binary_io import BinaryReader
        with BinaryReader(io.BytesIO(data)) as reader:
            reader.endianness = endianness
            for param in self.shader_params.values():
                reader.seek(param.data_offs, io.SEEK_SET)
                param.data_value = self.__read_param_data(param.type, reader)

    def __read_param_data(self, type_, reader: core.BinaryReader):
        match (type_):
            case ShaderParamType.Bool: return reader.read_bool()
            case ShaderParamType.Bool2: return reader.read_bools(2)
            case ShaderParamType.Bool3: return reader.read_bools(3)
            case ShaderParamType.Bool4: return reader.read_bools(4)
            case ShaderParamType.Float: return reader.read_single()
            case ShaderParamType.Float2: return reader.read_singles(2)
            case ShaderParamType.Float2x2: return reader.read_singles(2 * 2)
            case ShaderParamType.Float2x3: return reader.read_singles(2 * 3)
            case ShaderParamType.Float2x4: return reader.read_singles(2 * 4)
            case ShaderParamType.Float3: return reader.read_singles(3)
            case ShaderParamType.Float3x2: return reader.read_singles(3 * 2)
            case ShaderParamType.Float3x3: return reader.read_singles(3 * 3)
            case ShaderParamType.Float3x4: return reader.read_singles(3 * 4)
            case ShaderParamType.Float4: return reader.read_singles(4)
            case ShaderParamType.Float4x2: return reader.read_singles(4 * 2)
            case ShaderParamType.Float4x3: return reader.read_singles(4 * 3)
            case ShaderParamType.Float4x4: return reader.read_singles(4 * 4)
            case ShaderParamType.Int: return reader.read_int32()
            case ShaderParamType.Int2: return reader.read_int32s(2)
            case ShaderParamType.Int3: return reader.read_int32s(3)
            case ShaderParamType.Int4: return reader.read_int32s(4)
            case ShaderParamType.UInt: return reader.read_int32()
            case ShaderParamType.UInt2: return reader.read_int32s(2)
            case ShaderParamType.UInt3: return reader.read_int32s(3)
            case ShaderParamType.UInt4: return reader.read_int32s(4)
            case ShaderParamType.Reserved2: return reader.read_bytes(2)
            case ShaderParamType.Reserved3: return reader.read_bytes(3)
            case ShaderParamType.Reserved4: return reader.read_bytes(4)
            case ShaderParamType.Srt2D:
                return Srt2D(reader.read_vector2f(),
                             reader.read_single(),
                             reader.read_vector2f())
            case ShaderParamType.Srt3D:
                return Srt3D(reader.read_vector3f(),
                             reader.read_vector3f(),
                             reader.read_vector3f(),
                             )
            case ShaderParamType.TexSrt | ShaderParamType.TexSrtEx:
                return TexSrt(TexSrtMode(reader.read_int32()),
                              reader.read_vector2f(),
                              reader.read_single(),
                              reader.read_vector2f())
        return 0


class MaterialFlags(IntEnum):
    # uint32
    None_ = 0
    Visible = 1


class ShaderAssign(core.IResData):
    def __init__(self):
        self.shader_archive_name = ""
        self.shading_model_name = ""
        self.revision = 0
        self.attrib_assigns: ResDict[ResString] = ResDict()
        self.sampler_assigns: ResDict[ResString] = ResDict()
        self.shader_options: ResDict[ResString] = ResDict()

    @property
    def shader_options_list(self):
        strings = []
        for option in self.shader_options:
            strings.append(self.ResStringDisplay(option.key, option.value))
        return strings

    @shader_options_list.setter
    def shader_options_list(self, value):
        self.shader_options.clear()
        for option in value:
            self.shader_options.append(option.name, option.value)

    class ResStringDisplay:
        def __init__(self, name=None, value=None):
            self.name = name
            self.value = value

    def load(self, loader: core.ResFileLoader):
        self.shader_archive_name = loader.load_string()
        self.shading_model_name = loader.load_string()

        if (loader.is_switch):
            self.attrib_assigns = loader.load_dict_values(ResString)
            self.sampler_assigns = loader.load_dict_values(ResString)
            self.shader_options = loader.load_dict_values(ResString)
            self.revision = loader.read_uint32()
            num_attrib_assign = loader.read_byte()
            num_sampler_assign = loader.read_byte()
            num_shader_option = loader.read_uint16()
        else:
            self.revision = loader.read_uint32()
            num_attrib_assign = loader.read_byte()
            num_sampler_assign = loader.read_byte()
            num_shader_option = loader.read_uint16()
            self.attrib_assigns = loader.load_dict(ResString)
            self.sampler_assigns = loader.load_dict(ResString)
            self.shader_options = loader.load_dict(ResString)


class RenderInfo(core.IResData):
    """Represents a render info in a FMAT section storing uniform parameters
    required to render the UserData"""

    def __init__(self):
        self.__value: object
        self.type: RenderInfoType

        self.name = ""
        self.set_value([])

    @property
    def data(self):
        return self.__value

    @data.setter
    def data(self, value):
        self.__value = value

    def get_value(self, value) -> list[object]:
        """Gets the stored value as an array."""
        if (self.__value == None):
            return []
        return list(self.__value)

    def get_value_strings(self, value) -> list[str]:
        if (self.__value == None or self.type != RenderInfoType.String):
            return []
        return list(self.__value)

    def set_value(self, value):
        if len(value) == 0 or isinstance(value[0], int):
            self.type = RenderInfoType.Int32
        elif isinstance(value[0], float):
            self.type = RenderInfoType.Single
        elif isinstance(value[0], str):
            self.type = RenderInfoType.String
        self.__value = value

    def load(self, loader: core.ResFileLoader):
        if (loader.is_switch):
            self.name = loader.load_string()
            data_offs = loader.read_offset()
            count = loader.read_uint16()
            self.type = RenderInfoType(loader.read_byte())
            loader.seek(5)

            match (self.type):
                case RenderInfoType.Int32:
                    self._value = loader.load_custom(
                        list, loader.read_int32s, count, data_offs
                    )
                case RenderInfoType.Single:
                    self._value = loader.load_custom(
                        list, loader.read_singles, count, data_offs
                    )
                case RenderInfoType.String:
                    if (data_offs == 0):  # Some games have empty data offset and no strings
                        self._value = []
                    else:
                        self._value = loader.load_custom(
                            list, loader.load_strings, count, data_offs
                        )
        else:
            count = loader.read_uint16()
            self.type = RenderInfoType(loader.read_byte())
            loader.seek(1)
            self.name = loader.load_string()
            match (self.type):
                case RenderInfoType.Int32:
                    self._value = loader.read_int32s(count)
                case RenderInfoType.Single:
                    self._value = loader.read_singles(count)
                case RenderInfoType.String:
                    self._value = loader.load_strings(count)

    def read_data(self, loader: core.ResFileLoader, typ: IntEnum, count):
        self.type = typ
        match (self.type):
            case RenderInfoType.Int32:
                self.__value = loader.read_int32s(count)
            case RenderInfoType.Single:
                self.__value = loader.read_singles(count)
            case RenderInfoType.String:
                self.__value = loader.load_strings(count)


class RenderInfoType(IntEnum):
    """Represents the data type of elements of the RenderInfo value array."""
    # byte
    Int32 = 0
    Single = 1
    String = 2


class RenderState(core.IResData):
    """Represents GX2 GPU configuration to determine how polygons are
    rendered.
    """

    def __init__(self):
        self.flags_mode = RenderStateFlagsMode.Opaque
        self.flags_blend_mode = RenderStateFlagsBlendMode.None_

        # TODO I think this is wii U only


class RenderStateFlagsMode(IntEnum):
    # uint32
    Custom = 0
    Opaque = 1
    AlphaMask = 2
    Translucent = 3


class RenderStateFlagsBlendMode(IntEnum):
    # uint32
    None_ = 0
    Color = 1
    Logical = 2


class ShaderParam(core.IResData):
    """Represents a parameter value in a UserData section, passing data to
    shader variables"""

    def __init__(self):
        self.data_value: object
        self.callback_pointer: int
        self.use_padding: bool
        self.padding_length: int

        self.name = ""
        self.type = ShaderParamType.Float
        self.data_offs = 0
        self.depended_idx = 0
        self.depend_idx = 0

    @property
    def data_size(self):
        """The size of the value in bytes."""
        if (int(self.type) <= int(ShaderParamType.Float4x4)):
            return 4 * (self.type.value & 0x03) + 1
        if (int(self.type) <= int(ShaderParamType.Float4x4)):
            cols = (int(self.type) & 0x03) + 1
            rows = (int(self.type) - int(ShaderParamType.Reserved2) >> 2) + 2
            return 4 * cols * rows

        # XXX Figure this out
        match self.type:
            case ShaderParamType.Srt2D:
                return 20
            case ShaderParamType.Srt3D:
                return 36
            case ShaderParamType.TexSrt:
                return 24
            case ShaderParamType.TexSrtEx:
                return 28
        raise ValueError(
            f"Cannot retrieve size of unknown {self.type.name}")

    def load(self, loader: core.ResFileLoader):
        if (loader.is_switch):
            self.callback_pointer = loader.read_uint64()
            self.name = loader.load_string()
            self.type = ShaderParamType(loader.read_byte())
            siz_data = loader.read_byte()
            self.data_offs = loader.read_uint16()
            self.offset = loader.read_uint16()  # Uniform variable offset
            self.depended_idx = loader.read_uint16()
            self.depend_idx = loader.read_uint16()
            padding2 = loader.read_uint32()  # Uniform variable offset.
        else:
            self.type = ShaderParamType(loader.read_byte())
            siz_data = loader.read_byte()

            if (siz_data != self.data_size and siz_data > self.data_size):
                self.use_padding = True
                self.padding_length = siz_data - self.data_size

            self.data_offs = loader.read_uint16()
            self.offset = loader.read_int32()  # Uniform variable offset.
            if (loader.res_file.version >= 0x03040000):
                self.callback_pointer = loader.read_uint32()
                self.depended_idx = loader.read_uint16()
                self.depend_idx = loader.read_uint16()
            elif (loader.res_file.version >= 0x03030000
                  and loader.res_file.version < 0x03040000):
                self.callback_pointer = loader.read_uint32()
                self.depended_idx = loader.read_uint16()
                self.depend_idx = loader.read_uint16()
                fmat_offset = loader.read_uint32()  # Why does this have this????
            self.name = loader.load_string()


class ShaderParamType(IntEnum):
    # byte

    # The value is a single Boolean.
    Bool = 0

    # The value is a Vector2Bool.
    Bool2 = auto()

    # The value is a Vector3Bool.
    Bool3 = auto()

    # The value is a Vector4Bool.
    Bool4 = auto()

    # The value is a single Int32.
    Int = auto()

    # The value is a Vector2.
    Int2 = auto()

    # The value is a Vector3.
    Int3 = auto()

    # The value is a Vector4.
    Int4 = auto()

    # The value is a single UInt32.
    UInt = auto()

    # The value is a Vector2U.
    UInt2 = auto()

    # The value is a Vector3U.
    UInt3 = auto()

    # The value is a Vector4U.
    UInt4 = auto()

    # The value is a single Single.
    Float = auto()

    # The value is a Vector2F.
    Float2 = auto()

    # The value is a Vector3F.
    Float3 = auto()

    # The value is a Vector4F.
    Float4 = auto()

    # An invalid type for ShaderParam values, only used for internal computations.
    Reserved2 = auto()

    # The value is a Matrix2.
    Float2x2 = auto()

    # The value is a Matrix2x3.
    Float2x3 = auto()

    # The value is a Matrix2x4.
    Float2x4 = auto()

    # An invalid type for ShaderParam values, only used for internal computations.
    Reserved3 = auto()

    # The value is a Matrix3x2.
    Float3x2 = auto()

    # The value is a Matrix3.
    Float3x3 = auto()

    # The value is a Matrix3x4.
    Float3x4 = auto()

    # An invalid type for ShaderParam values, only used for internal computations.
    Reserved4 = auto()

    # The value is a Single.
    Float4x2 = auto()

    # The value is a Matrix4x3.
    Float4x3 = auto()

    # The value is a Matrix4.
    Float4x4 = auto()

    # The value is a Srt2D.
    Srt2D = auto()

    # The value is a Srt3D.
    Srt3D = auto()

    # The value is a TexSrt.
    TexSrt = auto()

    # The value is a TexSrtEx.
    TexSrtEx = auto()


class Sampler(core.IResData):
    def __init__(self):
        self.tex_sampler: TexSampler
        self.name: str

    def load(self, loader: core.ResFileLoader):
        if (loader.is_switch):
            from ..switch import model
            sampler = model.SamplerSwitch()
            sampler.load(loader)
            self.tex_sampler = sampler.to_tex_sampler()
        else:
            self.tex_sampler = TexSampler(loader.read_int32s(3))
            handle = loader.read_uint32()
            self.name = loader.load_string()
            idx = loader.read_byte()
            loader.seek(3)

    class MaxAnisotropic(IntEnum):
        # byte
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

# Included in GX2, and not Material


class TexSampler:
    """Represents a GX2 texture sampler controlling how a texture is sampled
    and drawn onto a surface."""
    __CLAMP_X_BIT = 0
    __CLAMP_X_BITS = 3
    __CLAMP_Y_BIT = 3
    __CLAMP_Y_BITS = 3
    __CLAMP_Z_BIT = 6
    __CLAMP_Z_BITS = 3
    __XY_MAG_FILTER_BIT = 9
    __XY_MAG_FILTER_BITS = 2
    __XY_MIN_FILTER_BIT = 12
    __XY_MIN_FILTER_BITS = 2
    __Z_FILTER_BIT = 15
    __Z_FILTER_BITS = 2
    __MIP_FILTER_BIT = 17
    __MIP_FILTER_BITS = 2
    __MAX_ANISOTROPIC_RATIO_BIT = 19
    __MAX_ANISOTROPIC_RATIO_BITS = 3
    __BORDER_TYPE_BIT = 22
    __BORDER_TYPE_BITS = 2
    __DEPTH_COMPARE_FUNC_BIT = 26
    __DEPTH_COMPARE_FUNC_BITS = 3

    __MIN_LOD_BIT = 0
    __MIN_LOD_BITS = 10
    __MAX_LOD_BIT = 10
    __MAX_LOD_BITS = 10
    __LOD_BIAS_BIT = 20
    __LOD_BIAS_BITS = 12

    __DEPTH_COMPARE_BIT = 30

    def __init__(self, values=None):
        self.__filter_flags: int
        if values:
            self.values = values
        else:
            self.values = [33559049, 851968, 2147483648]

            self.clamp_x = gx2.GX2TexClamp.Wrap
            self.clamp_y = gx2.GX2TexClamp.Wrap
            self.clamp_z = gx2.GX2TexClamp.Clamp
            self.mag_filter = gx2.GX2TexXYFilterType.Bilinear
            self.min_filter = gx2.GX2TexXYFilterType.Bilinear
            self.z_filter = gx2.GX2TexZFilterType.Linear
            self.mip_filter = gx2.GX2TexMipFilterType.Linear
            self.max_anisotropic_ratio = gx2.GX2TexAnisoRatio.Ratio_1_1
            self.border_type = gx2.GX2TexBorderType.ClearBlack
            self.depth_compare_func = gx2.GX2CompareFunction.Never
            self.lod_bias = 0
            self.min_lod = 0
            self.max_lod = 13

    @property
    def clamp_x(self):
        return gx2.GX2TexClamp(
            core._decode(self.values[0],
                         self.__CLAMP_X_BIT,
                         self.__CLAMP_X_BITS))

    @clamp_x.setter
    def clamp_x(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__CLAMP_X_BIT,
                                      self.__CLAMP_X_BITS)

    @property
    def clamp_y(self):
        return gx2.GX2TexClamp(
            core._decode(self.values[0],
                         self.__CLAMP_Y_BIT,
                         self.__CLAMP_Y_BITS))

    @clamp_y.setter
    def clamp_y(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__CLAMP_Y_BIT,
                                      self.__CLAMP_Y_BITS)

    @property
    def clamp_z(self):
        return gx2.GX2TexClamp(
            core._decode(self.values[0],
                         self.__CLAMP_Z_BIT,
                         self.__CLAMP_Z_BITS))

    @clamp_z.setter
    def clamp_z(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__CLAMP_Z_BIT,
                                      self.__CLAMP_Z_BITS)

    @property
    def mag_filter(self):
        return gx2.GX2TexXYFilterType(
            core._decode(self.values[0],
                         self.__XY_MAG_FILTER_BIT,
                         self.__XY_MAG_FILTER_BITS))

    @mag_filter.setter
    def mag_filter(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__XY_MAG_FILTER_BIT,
                                      self.__XY_MAG_FILTER_BITS)

    @property
    def min_filter(self):
        return gx2.GX2TexXYFilterType(
            core._decode(self.values[0],
                         self.__XY_MIN_FILTER_BIT,
                         self.__XY_MIN_FILTER_BITS))

    @min_filter.setter
    def min_filter(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__XY_MIN_FILTER_BIT,
                                      self.__XY_MIN_FILTER_BITS)

    @property
    def z_filter(self):
        return gx2.GX2TexZFilterType(
            core._decode(self.values[0],
                         self.__Z_FILTER_BIT,
                         self.__Z_FILTER_BITS))

    @z_filter.setter
    def z_filter(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__Z_FILTER_BIT,
                                      self.__Z_FILTER_BITS)

    @property
    def mip_filter(self):
        return gx2.GX2TexMipFilterType(
            core._decode(self.values[0],
                         self.__MIP_FILTER_BIT,
                         self.__MIP_FILTER_BITS))

    @mip_filter.setter
    def mip_filter(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__MIP_FILTER_BIT,
                                      self.__MIP_FILTER_BITS)

    @property
    def max_anisotropic_ratio(self):
        return gx2.GX2TexAnisoRatio(
            core._decode(self.values[0],
                         self.__MAX_ANISOTROPIC_RATIO_BIT,
                         self.__MAX_ANISOTROPIC_RATIO_BITS))

    @max_anisotropic_ratio.setter
    def max_anisotropic_ratio(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__MAX_ANISOTROPIC_RATIO_BIT,
                                      self.__MAX_ANISOTROPIC_RATIO_BITS)

    @property
    def border_type(self):
        return gx2.GX2TexBorderType(
            core._decode(self.values[0],
                         self.__BORDER_TYPE_BIT,
                         self.__BORDER_TYPE_BITS))

    @border_type.setter
    def border_type(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__BORDER_TYPE_BIT,
                                      self.__BORDER_TYPE_BITS)

    @property
    def depth_compare_func(self):
        return gx2.GX2CompareFunction(
            core._decode(self.values[0],
                         self.__DEPTH_COMPARE_FUNC_BIT,
                         self.__DEPTH_COMPARE_FUNC_BITS))

    @depth_compare_func.setter
    def depth_compare_func(self, value):
        self.values[0] = core._encode(self.values[0],
                                      value,
                                      self.__DEPTH_COMPARE_FUNC_BIT,
                                      self.__DEPTH_COMPARE_FUNC_BITS)

    @property
    def min_lod(self):
        return self.__usingle_4x6_to_single(
            core._decode(self.values[1],
                         self.__MIN_LOD_BIT,
                         self.__MIN_LOD_BITS))

    @min_lod.setter
    def min_lod(self, value):
        self.values[1] = core._encode(self.values[1],
                                      self.__single_to_usingle4x6(value),
                                      self.__MIN_LOD_BIT,
                                      self.__MIN_LOD_BITS)

    @property
    def max_lod(self):
        return self.__usingle_4x6_to_single(
            core._decode(self.values[1],
                         self.__MAX_LOD_BIT,
                         self.__MAX_LOD_BITS))

    @max_lod.setter
    def max_lod(self, value):
        self.values[1] = core._encode(self.values[1],
                                      self.__single_to_usingle4x6(value),
                                      self.__MAX_LOD_BIT,
                                      self.__MAX_LOD_BITS)

    @property
    def lod_bias(self):
        return self.__single_5x6_to_single(
            core._decode(self.values[1],
                         self.__LOD_BIAS_BIT,
                         self.__LOD_BIAS_BITS))

    @lod_bias.setter
    def lod_bias(self, value):
        self.values[1] = core._encode(self.values[1],
                                      self.__single_to_single5x6(value),
                                      self.__LOD_BIAS_BIT,
                                      self.__LOD_BIAS_BITS)

    @property
    def depth_compare_enabled(self):
        return core._get_bit(self.values[2], self.__DEPTH_COMPARE_BIT)

    @depth_compare_enabled.setter
    def depth_compare_enabled(self, value: bool):
        self.values[2] = core._set_bit(self.values[2],
                                       self.__DEPTH_COMPARE_BIT,
                                       value)

    # Private Methods

    def __single_5x6_to_single(self, value: int):
        signed = (value << 20) & 0xFFFFFFFF  # XXX no idea if this is right
        return (signed >> 20) / float(64)

    def __usingle_4x6_to_single(self, value: int):
        return value / float(64)

    def __single_to_single5x6(self, value: float):
        if (value <= -32):
            return 32 * 64
        elif (value >= 31.984375):
            return 31.984375 * 64
        return value * 64

    def __single_to_usingle4x6(self, value: float):
        if (value <= 0):
            return 0
        elif (value >= 13):
            return 13 * 64
        return int(value * 64)
