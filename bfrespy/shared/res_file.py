import io
from .core import IResData

class ResFile(IResData):
    def __init__(self, raw: io.BytesIO):
        if (self.is_switch_binary(raw)):
            from ..switch.core import ResFileSwitchLoader 
            with ResFileSwitchLoader(self, raw) as loader:
                loader
        else:
            raise NotImplementedError("Sorry, WiiU files aren't supported yet")