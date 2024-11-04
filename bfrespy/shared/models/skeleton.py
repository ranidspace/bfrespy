from enum import IntFlag
from ..core import IResData, ResFileLoader
from ..common import ResDict, UserData


class Bone(IResData):

    def __init__(self):
        self._flags: int
        self.name = ""
        self.userdata = ResDict()
        self.parent_index = -1
        self.smooth_mtx_index = -1
        self.rigid_mtx_index = -1
        self.billboard_index = -1

        self.scale = (1, 1, 1)
        self.rotation = (0, 0, 0, 0)
        self.position = (0, 0, 0)

        self.flags = BoneFlags.Visible
        self.flags_rotation = BoneFlagsRotation.EulerXYZ
        self.flags_billboard = BoneFlagsBillboard.None_
        self.flags_transform = BoneFlagsTransform.None_
        self.flags_transform_cumulative = BoneFlagsTransformCumulative.None_

    _flagsMask = 0b00000000_00000000_00000000_00000001
    _flagsMaskRotate = 0b00000000_00000000_01110000_00000000
    _flagsMaskBillboard = 0b00000000_00000111_00000000_00000000
    _flagsMaskTransform = 0b00001111_00000000_00000000_00000000
    _flagsMaskTransformCumulative = 0b11110000_00000000_00000000_00000000

    # Properties

    @property
    def visible(self):
        return BoneFlags.Visible in self.flags

    @visible.setter
    def visible(self, value):
        if (value):
            self.flags |= BoneFlags.Visible
        else:
            self.flags &= BoneFlags.Visible

    @property
    def bone_flags(self):
        return BoneFlags(self._flags & self._flagsMask)

    @bone_flags.setter
    def bone_flags(self, value):
        self._flags = self._flags & ~self._flagsMask | int(value)

    @property
    def bone_flags_rotation(self):
        return BoneFlagsRotation(self._flags & self._flagsMaskRotate)

    @bone_flags_rotation.setter
    def bone_flags_rotation(self, value):
        self._flags = self._flags & ~self._flagsMaskRotate | int(value)

    @property
    def bone_flags_billboard(self):
        return BoneFlagsBillboard(self._flags & self._flagsMaskBillboard)

    @bone_flags_billboard.setter
    def bone_flags_billboard(self, value):
        self._flags = self._flags & ~self._flagsMaskBillboard | int(value)

    @property
    def bone_flags_transform(self):
        return BoneFlagsTransform(self._flags & self._flagsMaskTransform)

    @bone_flags_transform.setter
    def bone_flags_transform(self, value):
        self._flags = self._flags & ~self._flagsMaskTransform | int(value)

    @property
    def bone_flags_transform_cumulative(self):
        return BoneFlagsTransformCumulative(self._flags & self._flagsMaskTransformCumulative)

    @bone_flags_transform_cumulative.setter
    def bone_flags_transform_cumulative(self, value):
        self._flags = self._flags & ~self._flagsMaskTransformCumulative | int(
            value)

    @property
    def userdata_list(self):
        return self.userdata.values()

    # Methods

    def load(self, loader: ResFileLoader):
        if (loader.is_switch):
            self.name = loader.load_string()
            self.userdata = loader.load_dict_values(UserData)
            if (loader.res_file.version_major2 > 9):
                loader.seek(8)

            if (loader.res_file.version_major2 == 8
                    or loader.res_file.version_major2 == 9):
                loader.seek(16)

            idx = loader.read_uint16()
            self.parent_index = loader.read_uint16()
            self.smooth_mtx_index = loader.read_uint16()
            self.rigid_mtx_index = loader.read_uint16()
            self.billboard_index = loader.read_uint16()
            num_user_data = loader.read_uint16()
            _flags = loader.read_uint32()
            self.scale = loader.read_vector3f()
            self.rotation = loader.read_vector4f()
            self.position = loader.read_vector3f()
        else:
            self.name = loader.load_string()
            idx = loader.read_uint16()
            self.parent_index = loader.read_uint16()
            self.smooth_mtx_index = loader.read_uint16()
            self.rigid_mtx_index = loader.read_uint16()
            self.billboard_index = loader.read_uint16()
            num_user_data = loader.read_uint16()
            _flags = loader.read_uint32()
            self.scale = loader.read_vector3f()
            self.rotation = loader.read_vector4f()
            self.position = loader.read_vector3f()
            self.userdata = loader.load_dict(UserData)

            if (loader.res_file.version < 0x03040000):
                self.inverse_mtx = loader.read_matrix_3x4()


class BoneFlags(IntFlag):
    Visible = 1


class BoneFlagsRotation(IntFlag):
    Quaternion = 0
    EulerXYZ = 1 << 12


class BoneFlagsBillboard(IntFlag):
    """Represents the possible transformations for bones to handle them as billboards."""
    # No transformation is applied.
    None_ = 0

    # Transforms of the child are applied.
    Child = 1 << 16

    # Transforms the Z axis parallel to the camera.
    WorldViewVector = 2 << 16

    # Transforms the Z axis parallel to the direction of the camera.
    WorldViewPoint = 3 << 16

    # Transforms the Y axis parallel to the camera up vector,
    # and the Z parallel to the camera up-vector.
    ScreenViewVector = 4 << 16

    # Transforms the Y axis parallel to the camera up vector, and the
    # Z axis parallel to the direction of the camera.
    ScreenViewPoint = 5 << 16

    # Transforms the Z axis parallel to the camera by
    # rotating only the Y axis.
    YAxisViewVector = 6 << 16

    # Transforms the Z axis parallel to the direction of the camera
    # by rotating only the Y axis.
    YAxisViewPoint = 7 << 16


class BoneFlagsTransform(IntFlag):
    None_ = 0
    ScaleUniform = 1 << 24,
    ScaleVolumeOne = 1 << 25
    RotateZero = 1 << 26
    TranslateZero = 1 << 27
    ScaleOne = ScaleUniform | ScaleVolumeOne
    RotateTranslateZero = RotateZero | TranslateZero
    Identity = ScaleOne | RotateZero | TranslateZero


class BoneFlagsTransformCumulative(IntFlag):
    None_ = 0
    ScaleUniform = 1 << 28
    ScaleVolumeOne = 1 << 29
    RotateZero = 1 << 30
    TranslateZero = 1 << 31
    ScaleOne = ScaleVolumeOne | ScaleUniform
    RotateTranslateZero = RotateZero | TranslateZero
    Identity = ScaleOne | RotateZero | TranslateZero


class Skeleton(IResData):
    _signature = "FSKL"
    _flagsScalingMask = 0b00000000_00000000_00000011_00000000
    _flagsRotationMask = 0b00000000_00000000_01110000_00000000

    def __init__(self):
        self._flags: int
        self.num_smooth_mtxs: int
        self.num_rigid_mtxs: int
        self.user_indices: list

        self.mtx_to_bone_list = []
        self.inverse_model_mtxs = []
        self.bones = ResDict()
        self.flags_rotation = SkeletonFlagRotation.EulerXYZ
        self.flags_scaling = SkeletonFlagScaling.Maya

    # Properties

    @property
    def flags_scaling(self):
        return SkeletonFlagScaling(self._flags & self._flagsScalingMask)

    @flags_scaling.setter
    def flags_scaling(self, value):
        self._flags = self._flags & ~self._flagsScalingMask | int(value)

    @property
    def flags_rotation(self):
        return SkeletonFlagScaling(self._flags & self._flagsRotationMask)

    @flags_rotation.setter
    def flags_rotation(self, value):
        self._flags = self._flags & ~self._flagsRotationMask | int(value)

    @property
    def bonelist(self):
        self.bones.values()

    def get_smooth_indices(self):
        indices = []
        for bone in self.bones.values():
            if (bone.smooth_mtx_index != 1):
                indices.add(bone.smooth_mtx_index)
        return indices

    def get_rigid_indices(self):
        indices = []
        for bone in self.bones.values():
            if (bone.rigid_mtx_index != 1):
                indices.add(bone.rigid_mtx_index)
        return indices

    # Methods

    def load(self, loader: ResFileLoader):
        loader.check_signature(self._signature)
        if (loader.is_switch):
            if (loader.res_file.version_major2 >= 9):
                self._flags = loader.read_uint32()
            else:
                loader.load_header_block()

            bone_dict_offs = loader.read_offset()
            bone_array_offs = loader.read_offset()
            self.bones = loader.load_dict_values(
                Bone, bone_dict_offs, bone_array_offs
            )
            mtx_to_bone_list_offs = loader.read_offset()
            inverse_model_mtx_offs = loader.read_offset()

            if (loader.res_file.version_major2 == 8):
                loader.seek(16)
            if (loader.res_file.version_major2 >= 9):
                loader.seek(8)

            user_pointer = loader.read_int64()
            if (loader.res_file.version_major2 < 9):
                self._flags = loader.read_uint32()
            num_bone = loader.read_uint16()
            self.num_smooth_mtxs = loader.read_uint16()
            self.num_rigid_mtxs = loader.read_uint16()
            loader.seek(6)

            self.user_indices = loader.load_custom(
                list, loader.read_uint16s,
                num_bone,
                offset=user_pointer
            )

            self.mtx_to_bone_list = (
                loader.load_custom(
                    list, loader.read_uint16s,
                    self.num_smooth_mtxs + self.num_rigid_mtxs,
                    offset=mtx_to_bone_list_offs
                )
            )
            self.inverse_model_mtxs = (
                loader.load_custom(
                    list, loader.read_matrix_3x4s,
                    self.num_smooth_mtxs,
                    offset=inverse_model_mtx_offs
                )
            )


class SkeletonFlagScaling(IntFlag):
    None_ = 0
    Standard = 1 << 8
    Maya = 2 << 8
    Softimage = 3 << 8


class SkeletonFlagRotation(IntFlag):
    Quaternion = 0
    EulerXYZ = 1 << 12
