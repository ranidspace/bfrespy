from enum import IntFlag
from .core import IResData, ResFileLoader


class BoneAnimData:
    def __init__(self, loader: ResFileLoader, flags):
        self.flags = 0  # Never in files.
        self.scale = (loader.read_vector3f()
                      if BoneAnimFlagsBase.scale in flags
                      else (0, 0, 0))


class BoneAnim():
    pass


class BoneAnimFlagsBase(IntFlag):
    """Represents if initial values exist for the corresponding transformation
    in the base animation data.
    """
    # Initial scaling values exist.
    scale = 1 << 3
    # Initial rotation values exist.
    rotate = 1 << 4
    # Initial translation values exist.
    translate = 1 << 5


class BoneAnimsFlagCurve(IntFlag):
    # Curve animating the X component of a bone's scale.
    ScaleX = 1 << 6
    # Curve animating the Y component of a bone's scale.
    ScaleY = 1 << 7
    # Curve animating the Z component of a bone's scale.
    ScaleZ = 1 << 8
    # Curve animating the X component of a bone's rotation.
    RotateX = 1 << 9
    # Curve animating the Y component of a bone's rotation.
    RotateY = 1 << 10
    # Curve animating the Z component of a bone's rotation.
    RotateZ = 1 << 11
    # Curve animating the W component of a bone's rotation.
    RotateW = 1 << 12
    # Curve animating the X component of a bone's translation.
    TranslateX = 1 << 13
    # Curve animating the Y component of a bone's translation.
    TranslateY = 1 << 14
    # Curve animating the Z component of a bone's translation.
    TranslateZ = 1 << 15


class BoneAnimFlagsTransform(IntFlag):
    SegmentScaleCompensate = 1 << 23
    ScaleUniform = 1 << 24
    ScaleVolumeOne = 1 << 25
    RotateZero = 1 << 26
    TranslateZero = 1 << 27
    ScaleOne = ScaleVolumeOne | ScaleUniform
    RotateTranslateZero = RotateZero | TranslateZero
    Identity = ScaleOne | RotateZero | TranslateZero


class SkeletonAnim():
    pass
