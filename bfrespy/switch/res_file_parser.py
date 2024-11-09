import io
from ..res_file import ResFile
from ..external_file import ExternalFile
from .switchcore import ResFileSwitchLoader
from .memory_pool import MemoryPool, BufferInfo
from ..common import ResString, StringTable, ResDict
from .. import models


class ResFileParser:
    def load(loader: ResFileSwitchLoader, res_file: ResFile):
        # File Header
        loader.check_signature("FRES")
        padding = loader.read_uint32()
        res_file.version = loader.read_uint32()
        res_file.set_version_info(res_file.version)
        res_file.endianness = loader.read_byte_order()
        res_file.alignment = loader.read_byte()
        # Thanks MasterF0X for pointing out the layout of the these
        res_file.target_addr_size = loader.read_byte()
        offset_to_filename = loader.read_uint32()
        res_file.flags = loader.read_uint16()
        res_file.block_offs = loader.read_uint16()
        relocation_table_offs = loader.read_uint32()
        siz_file = loader.read_uint32()

        loader.load_relocation_table(relocation_table_offs)

        # Bfres Header
        res_file.name = loader.load_string()
        model_offs = loader.read_offset()
        model_dict_offs = loader.read_offset()
        if (loader.res_file.version_major2 >= 9):
            loader.read_bytes(32)  # reserved
        # TODO Read These properly
        res_file.skeletal_anims = loader.read_offset()
        res_file.skeletal_anims = loader.read_offset()
        res_file.material_anims = loader.read_offset()
        res_file.material_anims = loader.read_offset()
        res_file.bone_visibility_anims = loader.read_offset()
        res_file.bone_visibility_anims = loader.read_offset()
        res_file.shape_anims = loader.read_offset()
        res_file.shape_anims = loader.read_offset()
        res_file.scene_anims = loader.read_offset()
        res_file.scene_anims = loader.read_offset()
        res_file.mempool = loader.load(MemoryPool)
        res_file.buffer_info = loader.load(BufferInfo)

        if (loader.res_file.version_major2 >= 10):
            # Peek at external flags
            def peek_flags():
                with (loader.temporary_seek(0xee, io.SEEK_SET)):
                    return loader.read_byte()

            flags = peek_flags()
            if (res_file.has_flag(flags,
                                  res_file.ExternalFlags.holds_external_strings)):
                externalFileOffset = loader.read_offset()
                externalFileDict = loader.load_dict(ResString)

                '''with (loader.temporary_seek(externalFileOffset, io.SEEK_SET)):
                    StringCache.Strings.Clear()
                    foreach (var str in externalFileDict.Keys)
                        long stringID = loader.ReadInt64()
                        StringCache.Strings.Add(stringID, str)'''
                return
             # GPU section for TOTK
            if (res_file.has_flag(flags,
                                  res_file.ExternalFlags.has_external_gpu)):
                with (loader.temporary_seek(res_file.siz_file, io.SEEK_SET)):
                    gpuDataOffset = loader.read_uint32()
                    gpuBufferSize = loader.read_uint32()

                    res_file.buffer_info = BufferInfo()
                    res_file.buffer_info.bufffer_offs = siz_file + 288

        res_file.external_files = loader.load_dict_values(ExternalFile)
        padding1 = loader.read_uint64()
        res_file.string_table = loader.load(StringTable)
        res_file.string_pool_size = loader.read_uint32()
        res_file.num_model = loader.read_uint16()

        # Read models after buffer data
        res_file.models = loader.load_dict_values(
            models.Model, model_dict_offs, model_offs)

        if (loader.res_file.version_major2 >= 9):
            # Count for 2 new sections
            unkCount = loader.read_uint16()
            unk2Count = loader.read_uint16()

            if (unkCount != 0):
                raise ValueError("unk1 has section!")
            if (unk2Count != 0):
                raise ValueError("unk2 has section!")

        num_skeletal_anim = loader.read_uint16()
        num_material_anim = loader.read_uint16()
        num_bone_visibility_anim = loader.read_uint16()
        num_shape_anim = loader.read_uint16()
        num_scene_anim = loader.read_uint16()
        num_external_file = loader.read_uint16()
        res_file.external_flag = ResFile.ExternalFlags(loader.read_byte())
        reserve10 = loader.read_byte()

        padding3 = loader.read_uint32()

        if (reserve10 == 1 or res_file.external_flag != 0):
            res_file.data_alignment_override = 0x1000

        # TODO External Files and material animations
        """res_file.textures = ResDict()
        for ext in res_file.external_files:
            if (".bntx" in ext.key):
                bntx = BntxFile(io.BytesIO(ext.value.data))
                ext.Value.LoadedFileData = bntx
                for tex in bntx.textures:
                    res_file.textures.append(
                        tex.Name, SwitchTexture(bntx, tex))

        res_file.tex_pattern_anims = ResDict(MaterialAnim)
        res_file.mat_visibility_anims = ResDict(MaterialAnim)
        res_file.shader_param_anims = ResDict(MaterialAnim)
        res_file.color_anims = ResDict(MaterialAnim)
        res_file.tex_srt_anims = ResDict(MaterialAnim)

        # Split material animations into shader, texture, and visual animation lists
        for anim in res_file.material_anims.values:
            if (anim.name.contains("_ftp")):
                res_file.tex_pattern_anims.append(anim.name, anim)
            elif (anim.name.contains("_fts")):
                res_file.shader_param_anims.append(anim.name, anim)
            elif (anim.name.contains("_fcl")):
                res_file.color_anims.append(anim.name, anim)
            elif (anim.name.contains("_fst")):
                res_file.tex_srt_anims.append(anim.name, anim)
            elif (anim.name.contains("_fvt")):
                res_file.mat_visibility_anims.append(anim.name, anim)
            elif (anim.material_anim_data_list != None and anim.material_anim_data_list.any(x= > x.visibily_count > 0)):
                res_file.mat_visibility_anims.append(anim.name, anim)
            elif (anim.material_anim_data_list != None and anim.material_anim_data_list.any(x= > x.texture_pattern_count > 0)):
                res_file.tex_pattern_anims.append(anim.name, anim)
            else:
                res_file.shader_param_anims.append(anim.name, anim)"""
