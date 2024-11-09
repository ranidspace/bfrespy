from ..core import IResData, ResFileLoader


class ResString(IResData):
    """Represents a String which is stored in a ResFile"""

    def __init__(self, value=None, encoding=None):
        if (value):
            if isinstance(value, str):
                self.encoding = encoding
                self.string = value
            elif isinstance(value, ResString):
                self.string = value.string
                self.encoding = value.encoding
        else:
            self.string: str
            self.encoding: str

    def to_string(self):
        return self.string

    def load(self, loader: ResFileLoader):
        if (loader.is_switch):
            self.string = loader.load_string(self.encoding)
        else:
            self.string = loader.read_string(self.encoding)

    def save(saver):
        # TODO
        pass
