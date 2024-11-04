from .. import core
from ... import WiiU
from ...shared import TextureShared


class TextureRef(core.IResData):
    def __init__(self):
        self.texture: TextureShared

        self.name = ""

    def load(self, loader: core.ResFileLoader):
        name = loader.load_string()
        texture = loader.load(WiiU.Texture)
