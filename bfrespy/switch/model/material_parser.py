import io
from bfrespy.switch.core import ResFileSwitchLoader
from bfrespy import core
from bfrespy import models
from bfrespy.common import ResDict, ResString, UserData
import bfrespy.binary_io


class MaterialParser:
    @staticmethod
    def load(loader: ResFileSwitchLoader, mat: models.Material):
        if (loader.res_file.version_major2 >= 9):
            mat.flags = models.MaterialFlags(loader.read_uint32())
        else:
            (loader.load_header_block())

        mat.name = loader.load_string()
        if (loader.res_file.version_major2 >= 10):
            MaterialParserV10.load(loader, mat)
            return
        # TODO the rest


class MaterialParserV10:
    @classmethod
    def load(cls, loader: ResFileSwitchLoader, mat: models.Material):
        info = loader.load(cls.ShaderInfo)
        texture_array_offs = loader.read_int64()
        texture_name_array = loader.read_int64()
        sampler_array_offs = loader.read_int64()
        mat.samplers = loader.load_dict_values(models.Sampler)
        # Next is table data
        renderinfo_data_table = loader.read_int64()
        renderinfo_counter_table = loader.read_int64()
        renderinfo_data_offs = loader.read_int64()  # offsets as shorts
        source_param_offs = loader.read_int64()
        # 0xFFFF a bunch per param. Set at runtime??
        source_param_idxs = loader.read_int64()
        loader.read_uint64()  # reserved
        mat.userdata = loader.load_dict_values(UserData)
        volatile_flags_offs = loader.read_int64()
        user_pointer = loader.read_int64()
        sampler_slot_array_offs = loader.read_int64()
        tex_slot_array_offs = loader.read_int64()
        idx = loader.read_uint16()
        num_sampler = loader.read_byte()
        num_texture_ref = loader.read_byte()
        loader.read_uint16()  # reserved
        num_user_data = loader.read_uint16()
        renderinfo_data_size = loader.read_uint16()
        user_shading_model_option_ubo_size = loader.read_uint16()  # Set at runtime?
        loader.read_uint32()  # padding

        mat.renderinfo_size = renderinfo_data_size

        pos = loader.tell()

        textures = loader.load_custom(
            list, loader.load_strings, num_texture_ref, offset=texture_name_array)

        mat.texture_refs = []

        if (textures != None):
            for tex in textures:
                mat.texture_refs.append(models.material.TextureRef(name=tex))

        # Add names to the value as switch does not store any
        for sampler in mat.samplers.nodes():
            sampler.value.name = sampler.key

        mat.texture_slot_array = loader.load_custom(
            list, loader.read_int64s, num_texture_ref, offset=sampler_slot_array_offs
        )
        mat.sampler_slot_array = loader.load_custom(
            list, loader.read_int64s, num_sampler, offset=tex_slot_array_offs)

        if (info != None and info.shader_assign != None):
            mat.shader_assign = models.material.ShaderAssign()
            mat.shader_assign.shader_archive_name = info.shader_assign.shader_archive_name,
            mat.shader_assign.shading_model_name = info.shader_assign.shading_model_name,
            mat.shaderparamdata = loader.load_custom(
                list, loader.read_bytes,
                info.shader_assign.shader_param_size, offset=source_param_offs
            )
            mat.param_idxs = loader.load_custom(
                list, loader.read_int32s,
                len(info.shader_assign.shader_params),
                offset=source_param_idxs
            )

            cls.read_renderinfo(loader, info, mat, renderinfo_counter_table,
                                renderinfo_data_offs, renderinfo_data_table)
            cls.read_shader_params(loader, info, mat)

            cls.load_attribute_assign(info, mat)
            cls.load_sampler_assign(info, mat)
            cls.load_shader_options(info, mat)

            loader.seek(pos, io.SEEK_SET)

    class ShaderInfo(core.IResData):
        def __init__(self):
            self.shader_assign: MaterialParserV10.ShaderAssignV10

            self.attrib_assigns: list[str]
            self.sampler_assigns: list[str]

            self.option_toggles: list[bool]
            self.option_values: list[str]

            self.option_idxs: list[int]
            self.attrib_assign_idxs: list[int]
            self.sampler_assign_idxs: list[int]
            self.__option_bit_flags: list[int]

        def load(self, loader: core.ResFileLoader):
            self.shader_assign = loader.load(MaterialParserV10.ShaderAssignV10)
            attrib_assign_offs = loader.read_int64()
            attrib_assign_idxs_offs = loader.read_int64()
            sampler_assign_offs = loader.read_int64()
            sampler_assign_idxs_offs = loader.read_int64()
            option_choice_toggle_offs = loader.read_uint64()
            option_choice_string_offs = loader.read_uint64()
            option_choice_idx_offs = loader.read_int64()
            loader.read_uint32()  # padding
            num_attrib_assign = loader.read_byte()
            num_sampler_assign = loader.read_byte()
            shader_option_bool_count = loader.read_uint16()
            shader_option_choice_count = loader.read_uint16()
            loader.read_uint16()  # padding
            loader.read_uint32()  # padding

            num_bitflags = int(1 + shader_option_bool_count / 64)

            self.attrib_assigns = loader.load_custom(
                list, loader.load_strings,
                num_attrib_assign, offset=attrib_assign_offs
            )
            self.sampler_assigns = loader.load_custom(
                list, loader.load_strings,
                num_sampler_assign, offset=sampler_assign_offs
            )
            self.__option_bit_flags = loader.load_custom(
                list, loader.read_int64s,
                num_bitflags, offset=option_choice_toggle_offs
            )
            if (self.shader_assign != None):
                self.option_idxs = self.__read_short_idxs(
                    loader, option_choice_idx_offs,
                    shader_option_choice_count,
                    len(self.shader_assign.options)
                )
                self.attrib_assign_idxs = self.__read_byte_idxs(
                    loader, attrib_assign_idxs_offs,
                    num_attrib_assign,
                    len(self.shader_assign.attrib_assign)
                )
                self.sampler_assign_idxs = self.__read_byte_idxs(
                    loader, sampler_assign_idxs_offs,
                    num_sampler_assign,
                    len(self.shader_assign.sampler_assign)
                )

                num_choice_vals = shader_option_choice_count - shader_option_bool_count
                self.option_values = loader.load_custom(
                    list, loader.load_strings,
                    num_choice_vals, offset=option_choice_string_offs
                )

                self.__setup_options_bools(shader_option_bool_count)

        def __read_byte_idxs(
                self, loader: core.ResFileLoader,
                offset, used_count, total_count):
            if (offset == 0):
                return []
            with loader.temporary_seek(offset, io.SEEK_SET):
                used_idxs = loader.read_sbytes(used_count)
                return loader.read_sbytes(total_count)

        def __read_short_idxs(
                self, loader: core.ResFileLoader,
                offset, used_count, total_count):
            if (offset == 0):
                return []
            with loader.temporary_seek(offset, io.SEEK_SET):
                used_idxs = loader.read_int16s(used_count)
                return loader.read_int16s(total_count)

        def __setup_options_bools(self, count):
            self.option_toggles = []
            if (count == 0):
                return
            flags = self.__option_bit_flags
            idx = 0
            for i in range(count):
                if (i != 0 and i % 64 == 0):
                    idx += 1
                self.option_toggles.append(
                    (self.__option_bit_flags[idx] & (1 << i)) != 0
                )

    class ShaderAssignV10(core.IResData):
        def __init__(self):
            self.renderinfos = ResDict()
            self.shader_params = ResDict()
            self.attrib_assign = ResDict()
            self.sampler_assign = ResDict()
            self.options = ResDict()

            self.shader_archive_name: str
            self.shading_model_name: str

            self.shader_param_offs: int
            self.renderinfo_list_offs: int

            self.shader_param_size: int

            self.renderinfo_count: int
            self.param_count: int
            self.parent_material: models.Material

        def load(self, loader: core.ResFileLoader):
            self.shader_archive_name = loader.load_string()
            self.shading_model_name = loader.load_string()

            # List of names + type. Data in material section
            self.renderinfo_list_offs = loader.read_uint64()
            self.renderinfos = loader.load_dict(ResString)
            # List of names + type. Data in material section
            self.shader_param_offs = loader.read_uint64()
            self.shader_params = loader.load_dict(ResString)
            self.attrib_assign = loader.load_dict(ResString)
            self.sampler_assign = loader.load_dict(ResString)
            self.options = loader.load_dict(ResString)
            self.renderinfo_count = loader.read_uint16()
            self.param_count = loader.read_uint16()
            self.shader_param_size = loader.read_uint16()
            loader.read_uint16()  # padding
            loader.read_uint64()  # padding

        def __hash__(self):
            hash_ = 0
            hash_ += hash(self.shader_archive_name)
            hash_ += hash(self.shading_model_name)

            for renderInfo in self.parent_material.renderinfos.values():
                hash_ += hash(renderInfo.name)
                hash_ += renderInfo.Type.GetHashCode()
            for p in self.parent_material.shader_params.values():
                hash_ += hash(p.name)
                hash_ += hash(p.data_offs)
                hash_ += hash(p.type)
            for op in self.options:
                hash_ += hash(op)
            for att in self.attrib_assign:
                hash_ += hash(att)
            for samp in self.sampler_assign:
                hash_ += hash(samp)

            return hash_

    @staticmethod
    def read_renderinfo(loader: ResFileSwitchLoader, info: ShaderInfo,
                        mat: models.Material, renderinfo_counter_table,
                        renderinfo_data_offs, renderinfo_data_table):
        for i in range(len(info.shader_assign.renderinfos)):
            renderinfo = models.material.RenderInfo()

            # Info table
            loader.seek(info.shader_assign.renderinfo_list_offs
                        + i * 16, io.SEEK_SET)
            renderinfo.name = loader.load_string()
            renderinfo.type = models.material.RenderInfoType(
                loader.read_byte())

            # Counter table
            loader.seek(renderinfo_counter_table + i * 2, io.SEEK_SET)
            count = loader.read_uint16()

            # Offset table
            loader.seek(renderinfo_data_offs + i * 2, io.SEEK_SET)
            data_offs = loader.read_uint16()

            # Raw data table
            loader.seek(renderinfo_data_table + data_offs, io.SEEK_SET)
            renderinfo.read_data(loader, renderinfo.type, count)

            mat.renderinfos.append(renderinfo.name, renderinfo)

    @staticmethod
    def read_shader_params(loader: ResFileSwitchLoader, info: ShaderInfo,
                           mat: models.Material):
        for i in range(len(info.shader_assign.shader_params)):
            param = models.material.ShaderParam()

            loader.seek(info.shader_assign.shader_param_offs
                        + i * 24, io.SEEK_SET)
            pad0 = loader.read_uint64()  # padding
            param.name = loader.load_string()  # name offset
            param.data_offs = loader.read_uint16()  # padding
            param.type = models.material.ShaderParamType(
                loader.read_uint16())  # type
            pad2 = loader.read_uint32()  # padding

            mat.shader_params.append(param.name, param)

    @staticmethod
    def load_attribute_assign(info: ShaderInfo, mat: models.Material):
        for i in range(len(info.shader_assign.attrib_assign)):
            idx = (info.attrib_assign_idxs[i]
                   if len(info.attrib_assign_idxs) > 0
                   else i)
            value = ("<Default Value>"
                     if idx == -1
                     else info.attrib_assigns[idx])
            key = info.shader_assign.attrib_assign.get_key(i)

            mat.shader_assign.attrib_assigns.append(key, value)

    @staticmethod
    def load_sampler_assign(info: ShaderInfo, mat: models.Material):
        for i in range(len(info.shader_assign.sampler_assign)):
            idx = (info.sampler_assign_idxs[i]
                   if len(info.sampler_assign_idxs) > 0
                   else i)
            value = ("<default value>"
                     if idx == -1
                     else info.sampler_assigns[idx])
            key = info.shader_assign.sampler_assign.get_key(i)

            mat.shader_assign.sampler_assigns.append(key, value)

    @staticmethod
    def load_shader_options(info: ShaderInfo, mat: models.Material):
        # Find target option
        choices = []
        for i in range(len(info.option_toggles)):
            choices.append("true" if info.option_toggles[i] else "false")
        if (info.option_values != None):
            choices.extend(info.option_values)

        for i in range(len(info.shader_assign.options)):
            idx = (info.option_idxs[i]
                   if len(info.option_idxs) > 0
                   else i)
            value = ("<default value>"
                     if idx == -1
                     else choices[idx])
            key = info.shader_assign.options.get_key(i)

            mat.shader_assign.shader_options.append(key, value)
