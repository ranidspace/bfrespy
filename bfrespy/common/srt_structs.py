from dataclasses import dataclass
from enum import IntEnum


class TexSrtMode(IntEnum):
    ModeMaya = 0
    Mode3dsMax = 1
    ModeSoftimage = 2


@dataclass
class Srt2D:
    scaling: tuple[float]
    rotation: tuple[float]
    translation: tuple[float]


@dataclass
class Srt3D:
    scaling: tuple[float]
    rotation: tuple[float]
    translation: tuple[float]


@dataclass
class TexSrt:
    mode: TexSrtMode
    scaling: tuple[float]
    rotation: tuple[float]
    translation: tuple[float]
