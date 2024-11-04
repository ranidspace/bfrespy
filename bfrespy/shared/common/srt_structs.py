from dataclasses import dataclass
from enum import IntEnum


@dataclass
class Srt2D:
    def __init__(self):
        self.scaling: tuple[float]
        self.rotation: tuple[float]
        self.translation: tuple[float]


@dataclass
class Srt3D:
    def __init__(self):
        self.scaling: tuple[float]
        self.rotation: tuple[float]
        self.translation: tuple[float]


class TexSrt:
    def __init__(self):
        self.mode: TexSrtMode
        self.scaling: tuple[float]
        self.rotation: tuple[float]
        self.translation: tuple[float]


class TexSrtMode(IntEnum):
    ModeMaya = 0
    Mode3dsMax = 1
    ModeSoftimage = 2
