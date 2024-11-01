""" Code referenced from Syroot/io_scene_bfres licensed unfer MIT"""
import io
import struct

class BinaryReader(io.BufferedReader):
    """A wrapper to read binary data as other formats"""
    def __init__(self, raw):
        self.endianness = '<'
        if (type(raw) == bytes):
            raw = io.BytesIO(raw)
        return super().__init__(raw)

    def align(self, alignment):
        self.seek(-self.tell() % alignment, io.SEEK_CUR)

    def read_null_string(self, encoding = None) -> str:
        encoding = encoding if encoding != None else 'shift-jis'    # Mostly the same as ascii i dont think there's harm in setting this?
        text = ''
        i = self.read(1)
        while i[0] != 0:
            text += i.decode(encoding) 
            i = self.read(1)
        return text

    # Unsigned

    def read_byte(self) -> int:
        return self.read(1)[0]
    
    def read_bytes(self, count) -> bytes:
        return self.read(count)
    
    def read_uint16(self) -> int:
        return struct.unpack(self.endianness + 'H', self.read(2))[0]

    def read_uint16s(self, count) -> list[int]:
        return struct.unpack(self.endianness + str(int(count)) + 'H', self.read(2 * count))

    def read_uint32(self) -> int:
        return struct.unpack(self.endianness + 'I', self.read(4))[0]

    def read_uint32s(self, count) -> list[int]:
        return struct.unpack(self.endianness + str(int(count)) + 'I', self.read(4 * count))
    
    def read_uint64(self) -> int:  # Switch has 64 bit offsets
        return struct.unpack(self.endianness + 'Q', self.read(8))[0]

    def read_uint64s(self, count) -> int:  # Switch has 64 bit offsets
        return struct.unpack(self.endianness + str(int(count)) + 'Q', self.read(8 * count))
    
    # Signed
    
    def read_int32(self) -> int:
        return struct.unpack(self.endianness + 'i', self.read(4))[0]

    def read_int32s(self, count) -> list[int]:
        return struct.unpack(self.endianness + str(int(count)) + 'i', self.read(4 * count))

    def read_sbyte(self):
        return struct.unpack(self.endianness + 'b', self.read(1))[0]

    def read_sbytes(self, count):
        return struct.unpack(self.endianness + str(int(count)) + 'b', self.read(1 * count))
    
    # Other Formats

    def read_single(self) -> int:
        return struct.unpack(self.endianness + 'f', self.read(4))[0]

    def read_singles(self, count) -> list[int]:
        return struct.unpack(self.endianness + str(int(count)) + 'f', self.read(4 * count))

    def read_raw_string(self, length, encoding = None):
        encoding = encoding if encoding != None else 'shift-jis'
        return self.read(length).decode(encoding)
    
    class TemporarySeek:
        """Temporarily move the pointer to a different location and return it 
        to the correct position when it's closed
        """
        ### XXX There's gotta be a way to do this without having to pass the reader in
        def __init__(self, reader, offset = None, whence = io.SEEK_SET):
            self.offset = offset
            self.whence = whence
            self.reader = reader
            self.curoff = reader.tell()

        def __enter__(self):
            if self.offset != None:
                self.reader.seek(self.offset, self.whence)
        
        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.reader.seek(self.curoff, io.SEEK_SET)


class BinaryWriter:
    def __init__(self, raw):
        self.raw = raw
        self.endianness = '<'  # Little-endian

    def __enter__(self):
        self.writer = io.BufferedWriter(self.raw)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.writer.close()

    def align(self, alignment):
        self.writer.seek(-self.writer.tell() % alignment, io.SEEK_CUR)

    def reserve_offset(self):
        return Offset(self)

    def satisfy_offset(self, offset, value=None):
        offset.satisfy(self, value)

    def seek(self, offset, whence=io.SEEK_SET):
        self.writer.seek(offset, whence)

    def tell(self):
        return self.writer.tell()

    def write_0_string(self, value, encoding='ascii'):
        self.write_raw_string(value, encoding)
        self.write_byte(0)

    def write_byte(self, value):
        self.writer.write(struct.pack('B', value))

    def write_bytes(self, value):
        self.writer.write(value)

    def write_int32(self, value):
        self.writer.write(struct.pack(self.endianness + 'i', value))

    def write_int32s(self, value):
        self.writer.write(struct.pack(self.endianness + str(len(value)) + 'i', *value))

    def write_sbyte(self, value):
        self.writer.write(struct.pack(self.endianness + 'b', value))

    def write_sbytes(self, value):
        self.writer.write(struct.pack(self.endianness + str(len(value)) + 'b', *value))

    def write_single(self, value):
        self.writer.write(struct.pack(self.endianness + 'f', value))

    def write_singles(self, value):
        self.writer.write(struct.pack(self.endianness + str(len(value)) + 'f', *value))

    def write_uint16(self, value):
        self.writer.write(struct.pack(self.endianness + 'H', value))

    def write_uint16s(self, value):
        self.writer.write(struct.pack(self.endianness + str(len(value)) + 'H', *value))

    def write_uint32(self, value):
        self.writer.write(struct.pack(self.endianness + 'I', value))

    def write_uint32s(self, value):
        self.writer.write(struct.pack(self.endianness + str(len(value)) + 'I', *value))

    def write_raw_string(self, value, encoding='ascii'):
        self.writer.write(bytearray(value, encoding))


class Offset:
    def __init__(self, writer):
        # Remember the position of the offset to change it later.
        self.position = writer.tell()
        # Write an empty offset for now.
        self.value = 0
        writer.write_uint32(self.value)

    def satisfy(self, writer, value=None):
        self.value = value if value else writer.tell()
        # Seek back temporarily to the offset position to write the final offset value.
        current_position = writer.tell()
        writer.seek(self.position)
        writer.write_uint32(self.value)
        writer.seek(current_position)

