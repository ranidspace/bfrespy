from ..shared import ResFile
from .core import ResFileSwitchLoader

class ResFileParser:
    def load(loader: ResFileSwitchLoader, res_file: ResFile):
        loader.check_signature("FRES")
        padding = loader.read_uint32()
        res_file.version = loader.read_uint32()
        res_file.set_version_info(res_file.version)
        res_file.endianness = loader.read_byte_order()
        res_file.alignment = loader.read_byte()
        res_file.target_addr_size = loader.read_byte();  #Thanks MasterF0X for pointing out the layout of the these
        offset_to_filename = loader.read_uint32()
        res_file.flag = loader.read_uint16()
        res_file.block_offs = loader.read_uint16()
        relocation_table_offset = loader.read_uint32()
        siz_file = loader.read_uint32()
        res_file.name = loader.load_string()
        model_offs = loader.read_offset()
        model_dict_offs = loader.read_offset()
        if (loader.res_file.version_major2 >= 9):
            loader.read_bytes(32);  #reserved
        # TODO Finish the rest of the header, the rest of this is the source
        # code from the original c# library 
        '''res_file.SkeletalAnims = loader.LoadDictValues<SkeletalAnim>()
        res_file.MaterialAnims = loader.LoadDictValues<MaterialAnim>()
        res_file.BoneVisibilityAnims = loader.LoadDictValues<VisibilityAnim>()
        res_file.ShapeAnims = loader.LoadDictValues<ShapeAnim>()
        res_file.SceneAnims = loader.LoadDictValues<SceneAnim>()
        res_file.MemoryPool = loader.Load<MemoryPool>()
        res_file.BufferInfo = loader.Load<BufferInfo>()

        if (loader.ResFile.VersionMajor2 >= 10)
             #Peek at external flags
            byte PeekFlags()
                with (loader.TemporarySeek(0xee, SeekOrigin.Begin)):
                    return loader.read_byte()

            var flag = (ResFile.ExternalFlags)PeekFlags()
            if (flag.HasFlag(ResFile.ExternalFlags.HoldsExternalStrings))
                long externalFileOffset = loader.read_offset()
                var externalFileDict = loader.LoadDict<ResString>()

                using (loader.TemporarySeek(externalFileOffset, SeekOrigin.Begin))
                    StringCache.Strings.Clear()
                    foreach (var str in externalFileDict.Keys)
                        long stringID = loader.ReadInt64()
                        StringCache.Strings.Add(stringID, str)
                return
             #GPU section for TOTK
            if (flag.HasFlag(ResFile.ExternalFlags.HasExternalGPU))
                using (loader.TemporarySeek(sizFile, SeekOrigin.Begin))
                    uint gpuDataOffset = loader.read_uint32()
                    uint gpuBufferSize = loader.read_uint32()

                    res_file.BufferInfo = new BufferInfo()
                    BufferInfo.BufferOffset = sizFile + 288

        res_file.ExternalFiles = loader.LoadDictValues<ExternalFile>()
        long padding1 = loader.ReadInt64()
        res_file.StringTable = loader.Load<StringTable>()
        uint StringPoolSize = loader.read_uint32()
        ushort numModel = loader.read_uint16()

         #Read models after buffer data
        res_file.Models = loader.LoadDictValues<Model>(modelDictOffset, modelOffset)

        if (loader.ResFile.VersionMajor2 >= 9)
             #Count for 2 new sections
            ushort unkCount = loader.read_uint16()
            ushort unk2Count = loader.read_uint16()

            if (unkCount != 0) throw new System.Exception("unk1 has section!")
            if (unk2Count != 0) throw new System.Exception("unk2 has section!")

        ushort numSkeletalAnim = loader.read_uint16()
        ushort numMaterialAnim = loader.read_uint16()
        ushort numBoneVisibilityAnim = loader.read_uint16()
        ushort numShapeAnim = loader.read_uint16()
        ushort numSceneAnim = loader.read_uint16()
        ushort numExternalFile = loader.read_uint16()
        res_file.ExternalFlag = (ResFile.ExternalFlags)loader.read_byte()
        byte reserve10 = loader.read_byte()

        uint padding3 = loader.read_uint32()

        if (reserve10 == 1 || res_file.ExternalFlag != 0)
            res_file.DataAlignmentOverride = 0x1000

        res_file.Textures = new ResDict<TextureShared>()
        foreach (var ext in res_file.ExternalFiles) {
            if (ext.Key.Contains(".bntx")) 
                BntxFile bntx = new BntxFile(new MemoryStream(ext.Value.Data))
                ext.Value.LoadedFileData = bntx
                foreach (var tex in bntx.Textures)
                    res_file.Textures.Add(tex.Name, new SwitchTexture(bntx, tex))

        res_file.TexPatternAnims = new ResDict<MaterialAnim>()
        res_file.MatVisibilityAnims = new ResDict<MaterialAnim>()
        res_file.ShaderParamAnims = new ResDict<MaterialAnim>()
        res_file.ColorAnims = new ResDict<MaterialAnim>()
        res_file.TexSrtAnims = new ResDict<MaterialAnim>()

         #Split material animations into shader, texture, and visual animation lists
        foreach (var anim in res_file.MaterialAnims.Values)
            if (anim.Name.Contains("_ftp"))
                res_file.TexPatternAnims.Add(anim.Name, anim)
            else if(anim.Name.Contains("_fts"))
                res_file.ShaderParamAnims.Add(anim.Name, anim)
            else if (anim.Name.Contains("_fcl"))
                res_file.ColorAnims.Add(anim.Name, anim)
            else if (anim.Name.Contains("_fst"))
                res_file.TexSrtAnims.Add(anim.Name, anim)
            else if (anim.Name.Contains("_fvt"))
                res_file.MatVisibilityAnims.Add(anim.Name, anim)
            else if (anim.MaterialAnimDataList != null && anim.MaterialAnimDataList.Any(x => x.VisibilyCount > 0))
                res_file.MatVisibilityAnims.Add(anim.Name, anim)
            else if (anim.MaterialAnimDataList != null && anim.MaterialAnimDataList.Any(x => x.TexturePatternCount > 0))
                res_file.TexPatternAnims.Add(anim.Name, anim)
            else
                res_file.ShaderParamAnims.Add(anim.Name, anim)'''