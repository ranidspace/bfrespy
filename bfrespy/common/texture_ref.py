from bfrespy import core
from bfrespy.texture import TextureShared


class TextureRef(core.IResData):
    def __init__(self, name=""):
        self.texture: TextureShared

        self.name = name

    def load(self, loader: core.ResFileLoader):
        name = loader.load_string()
        texture = loader.load(WiiU.Texture)
