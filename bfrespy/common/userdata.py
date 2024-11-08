from bfrespy.core import IResData, ResFileLoader
from enum import IntEnum


class UserData(IResData):
    def __init__(self):
        self._value: object
        self.type: UserDataType

        self.name = ""
        self.set_value([])

    def get_data(self):
        return self._value

    def set_value(self, value):
        self.type = UserDataType.Int32
        self._value = value

    def load(self, loader: ResFileLoader):
        if (loader.is_switch):
            self.name = loader.load_string()
            data_offs = loader.read_offset()
            count = 0
            if (loader.res_file.version_major2 <= 2
                    and loader.res_file.version_major2 == 0):

                reserved = loader.read_raw_string(8)
                count = loader.read_uint32()
                self.type = loader.read_uint32()
            else:
                count - loader.read_uint32()
                self.type = UserDataType(loader.read_byte())
                reserved = loader.read_raw_string(43)

            match self.type:
                case UserDataType.Byte:
                    self._value = loader.load_custom(
                        list, loader.read_sbytes, count, offset=data_offs
                    )
                case UserDataType.Int32:
                    self._value = loader.load_custom(
                        list, loader.read_int32s, count, offset=data_offs
                    )
                case UserDataType.Single:
                    self._value = loader.load_custom(
                        list, loader.read_singles, count, offset=data_offs
                    )
                case UserDataType.String:
                    self._value = loader.load_custom(
                        list, loader.load_strings,
                        count, "utf-8", offset=data_offs
                    )
                case UserDataType.WString:
                    self._value = loader.load_custom(
                        list, loader.load_strings,
                        count, "utf-16", offset=data_offs
                    )
        else:
            self.name = loader.load_string()
            count = loader.read_uint16()
            self.type = UserDataType(loader.read_byte())
            loader.seek(1)
            match self.type:
                case UserDataType.Byte:
                    self._value = loader.read_bytes(count)
                case UserDataType.Int32:
                    self._value = loader.read_int32s(count)
                case UserDataType.Single:
                    self._value = loader.read_singles(count)
                case UserDataType.String:
                    self._value = loader.load_strings(count, "utf-8")
                case UserDataType.WString:
                    self._value = loader.load_strings(count, "utf-16")


class UserDataType(IntEnum):
    Int32 = 0
    Single = 1
    String = 2
    WString = 3
    Byte = 4
