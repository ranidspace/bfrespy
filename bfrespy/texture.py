from . import core
from .common import UserData


class TextureShared(core.IResData):
    def __init__(self):
        self.name: str
        self.path: str
        self.width: int
        self.height: int
        self.depth: int
        self.mipcount: int
        self.array_length: int
        self.userdata: UserData

    def get_swizzled_data(self, arraylevel=None, miplevel=None):
        return None

    def load(self, loader: core.IResData):
        pass
