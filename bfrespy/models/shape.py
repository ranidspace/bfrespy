from dataclasses import dataclass
from enum import IntFlag, IntEnum

from bfrespy.core import IResData, ResFileLoader
from bfrespy.common import ResDict, Buffer
from bfrespy.gx2 import GX2PrimitiveType, GX2IndexFormat
from bfrespy.switch.memory_pool import MemoryPool, BufferSize, BufferInfo
from . import VertexBuffer


class Shape(IResData):
    _signature = "FSHP"

    def __init__(self):
        self.name = ""
        self.flags = ShapeFlags.HasVertexBuffer
        self.material_idx = 0
        self.bone_idx = 0
        self.vtx_buff_idx = 0
        self.radius_array = []
        self.bounding_radius_list: list[tuple[float]] = []
        self.vtx_skin_count = 0
        self.target_attrib_count = 0
        self.meshes: list[Mesh] = []
        self.skin_bone_idxs = []
        self.key_shapes: ResDict[KeyShape] = ResDict()
        self.submesh_boundings: list[Bounding] = []
        self.submesh_bounding_nodes: list[BoundingNode] = []
        self.submesh_bounding_idxs = []
        self.vtx_buffer = VertexBuffer()

    @property
    def has_vtx_buffer(self):
        return ShapeFlags.HasVertexBuffer in self.flags

    @has_vtx_buffer.setter
    def has_vtx_buffer(self, value):
        if (value):
            self.flags |= ShapeFlags.HasVertexBuffer
        else:
            self.flags &= ShapeFlags.HasVertexBuffer

    @property
    def submesh_boundary_consistent(self):
        return ShapeFlags.SubMeshBoundaryConsistent in self.flags

    @has_vtx_buffer.setter
    def has_vtx_buffer(self, value):
        if (value):
            self.flags |= ShapeFlags.SubMeshBoundaryConsistent
        else:
            self.flags &= ShapeFlags.SubMeshBoundaryConsistent

    def load(self, loader: ResFileLoader):
        loader.check_signature(self._signature)
        if (loader.is_switch):
            from bfrespy.switch.model import ShapeParser
            ShapeParser.read(loader, self)


class Mesh(IResData):
    def __init__(self):
        self.primitive_type = GX2PrimitiveType.Triangles
        self.index_format = GX2IndexFormat.UInt16
        self.submeshes = []
        self.index_buffer = Buffer()
        self.mempool = MemoryPool()

    @property
    def index_count(self):
        element_count = 0
        format_size = self.format_size
        for i in range(len(self.index_buffer.data)):
            buffering_size = len(self.index_buffer.data[i])
            if (buffering_size % format_size != 0):
                raise ValueError(
                    f"Cannot form complete indices from {self.index_buffer}.")
            element_count += buffering_size / format_size
        return element_count

    @property
    def data(self):
        return self.index_buffer.data[0]

    @property
    def format_size(self):
        match (self.index_format):
            case (GX2IndexFormat.UInt16
                  | GX2IndexFormat.UInt16LittleEndian):
                return 2
            case (GX2IndexFormat.UInt32
                  | GX2IndexFormat.UInt32LittleEndian):
                return 4
            case _:
                raise ValueError(f"Invalid GX2IndexFormat \
                                 {self.index_format.name}.")

    def load(self, loader: ResFileLoader):
        if (loader.is_switch):
            submesh_array_offs = loader.read_offset()
            self.mempool = loader.load(MemoryPool)
            buffer = loader.read_offset()
            buffer_size = loader.load(BufferSize)
            face_buff_offs = loader.read_uint32()
            self.primitive_type = self.primitive_type_list[
                self.SwitchPrimitiveType(loader.read_uint32())
            ]
            self.index_format = self.index_list[
                self.SwitchIndexFormat(loader.read_uint32())
            ]
            index_count = loader.read_uint32()
            self.first_vtx = loader.read_uint32()
            num_submesh = loader.read_uint16()
            padding = loader.read_uint16()
            self.submeshes = loader.load_list(
                SubMesh, num_submesh, offset=submesh_array_offs
            )
            data_offs = int(BufferInfo.buff_offs) + face_buff_offs

            self.index_buffer = Buffer()
            self.index_buffer.flags = buffer_size.flags
            self.index_buffer.data = [[]]
            self.index_buffer.data[0] = loader.load_custom(
                list, loader.read_bytes, buffer_size.size, offset=data_offs
            )

    class SwitchIndexFormat(IntEnum):
        UnsignedByte = 0
        UInt16 = 1
        UInt32 = 2

    class SwitchPrimitiveType(IntEnum):
        Points = 0x00
        Lines = 0x01
        LineStrip = 0x02
        Triangles = 0x03
        TriangleStrip = 0x04
        LinesAdjacency = 0x05
        LineStripAdjacency = 0x06
        TrianglesAdjacency = 0x07
        TriangleStripAdjacency = 0x08
        Patches = 0x09

    index_list = {
        SwitchIndexFormat.UInt16: GX2IndexFormat.UInt16LittleEndian,
        SwitchIndexFormat.UInt32: GX2IndexFormat.UInt32LittleEndian,
        SwitchIndexFormat.UnsignedByte: GX2IndexFormat.UInt16LittleEndian,
    }

    primitive_type_list = {
        SwitchPrimitiveType.Triangles: GX2PrimitiveType.Triangles,
        SwitchPrimitiveType.TrianglesAdjacency: GX2PrimitiveType.TrianglesAdjacency,
        SwitchPrimitiveType.TriangleStrip: GX2PrimitiveType.TriangleStripAdjacency,
        SwitchPrimitiveType.TriangleStripAdjacency: GX2PrimitiveType.TriangleStripAdjacency,
        SwitchPrimitiveType.Lines: GX2PrimitiveType.Lines,
        SwitchPrimitiveType.LinesAdjacency: GX2PrimitiveType.LinesAdjacency,
        SwitchPrimitiveType.LineStrip: GX2PrimitiveType.LineStrip,
        SwitchPrimitiveType.LineStripAdjacency: GX2PrimitiveType.LineStripAdjacency,
        SwitchPrimitiveType.Points: GX2PrimitiveType.Points,
    }


class SubMesh(IResData):
    def __init__(self):
        self.offset: int
        self.count: int

    def load(self, loader: ResFileLoader):
        self.offset = loader.read_uint32()
        self.count = loader.read_uint32()


class KeyShape(IResData):
    def __init__(self):
        self.target_attrib_idx: list
        self.target_attrib_idx_offs: list

    def load(self, loader: ResFileLoader):
        self.target_attrib_idx = loader.read_bytes(20)
        self.target_attrib_idx_offs = loader.read_bytes(4)


class BoundingNode(IResData):
    def __init__(self):
        self.left_child_idx: int
        self.next_sibling: int
        self.right_child_idx: int
        self.unk: int
        self.submesh_idx: int
        self.submesh_cnt: int

    def load(self, loader: ResFileLoader):
        self.left_child_idx = loader.read_uint16()
        self.next_sibling = loader.read_uint16()
        self.right_child_idx = loader.read_uint16()
        self.unk = loader.read_uint16()
        self.submesh_idx = loader.read_uint16()
        self.submesh_cnt = loader.read_uint16()


@dataclass
class Bounding:
    center: tuple
    extent: tuple


class ShapeFlags(IntFlag):
    HasVertexBuffer = 1 << 1
    SubMeshBoundaryConsistent = 1 << 2
