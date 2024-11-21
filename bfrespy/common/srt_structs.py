from dataclasses import dataclass
from enum import IntEnum


class TexSrtMode(IntEnum):
    ModeMaya = 0
    Mode3dsMax = 1
    ModeSoftimage = 2


@dataclass
class Srt2D:
    scaling: tuple[float, float]
    rotation: float
    translation: tuple[float, float]


@dataclass
class Srt3D:
    scaling: tuple[float, float, float]
    rotation: tuple[float, float, float]
    translation: tuple[float, float, float]


@dataclass
class TexSrt:
    mode: TexSrtMode
    scaling: tuple[float, float]
    rotation: float
    translation: tuple[float, float]
