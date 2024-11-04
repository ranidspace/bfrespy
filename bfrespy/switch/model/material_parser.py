import io
from .. import ResFileSwitchLoader
from ...shared import models, core
from ...shared.common import ResDict, ResString


class MaterialParser:
    @staticmethod
    def load(loader: ResFileSwitchLoader, mat: models.Material):
        if (loader.res_file.version_major2 >= 9):
            mat.flags = models.MaterialFlags(loader.read_uint32())
        else:
            (loader.load_header_block())

        mat.name = loader.load_string
        if (loader.res_file.version_major2 >= 10):
            MaterialParserV10.load(loader, mat)
            return
        # TODO the rest


class MaterialParserV10:
    @classmethod
    def load(cls, loader: ResFileSwitchLoader, mat: models.Material):
        info = loader.load(cls.ShaderInfo)

    class ShaderInfo(core.IResData):
        def __init__(self):
            self.shader_assign: MaterialParserV10.ShaderAssignV10

            self.attrib_assigns: list[str]
            self.sampler_assigns: list[str]

            self.option_toggles: list[bool]
            self.option_values: list[str]

            self.option_idxs: list[int]
            self.attrib_assign_idxs: list[int]
            self.sampler_assign_idsx: list[int]
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

            num_bitflags = 1 + shader_option_bool_count / 64

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
                self.sampler_assign_idsx = self.__read_byte_idxs(
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
                return None
            with loader.TemporarySeek(offset, io.SEEK_SET):
                used_idxs = loader.read_sbytes(used_count)
                return loader.read_sbytes(total_count)

        def __read_short_idxs(
                self, loader: core.ResFileLoader,
                offset, used_count, total_count):
            if (offset == 0):
                return None
            with loader.TemporarySeek(offset, io.SEEK_SET):
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
            self.render_infos = ResDict()
            self.shader_params = ResDict()
            self.attrib_assign = ResDict()
            self.sampler_assign = ResDict()
            self.options = ResDict()

            self.shader_archive_name: str
            self.shading_model_name: str

            self.shader_param_offs: int
            self.render_info_list_offs: int

            self.shader_param_size: int

            self.render_info_count: int
            self.param_count: int
            self.parent_material: models.Material

        def load(self, loader: core.ResFileLoader):
            self.shader_archive_name = loader.load_string
            self.shading_model_name = loader.load_string()

            # List of names + type. Data in material section
            self.render_info_list_offs = loader.read_uint64()
            self.render_infos = loader.load_dict(ResString)
            # List of names + type. Data in material section
            self.shader_param_offs = loader.read_uint64()
            self.shader_params = loader.load_dict(ResString)
            self.attrib_assign = loader.load_dict(ResString)
            self.sampler_assign = loader.load_dict(ResString)
            self.options = loader.load_dict(ResString)
            self.render_info_count = loader.read_uint16()
            self.param_count = loader.read_uint16()
            self.shader_param_size = loader.read_uint16()
            loader.read_uint16()  # padding
            loader.read_uint64()  # padding

        def __hash__(self):
            hash_ = 0
            hash_ += hash(self.shader_archive_name)
            hash_ += hash(self.shading_model_name)

            for renderInfo in self.parent_material.render_infos.values():
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
