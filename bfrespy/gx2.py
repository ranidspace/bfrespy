from enum import IntEnum, IntFlag


class GX2AAMode(IntEnum):
    """Represents the AA modes (number of samples) for a surface."""
    Mode1X = 0
    Mode2X = 1
    Mode4X = 2
    Mode8X = 3


class GX2AttribFormat(IntEnum):
    """Represents the format of a vertex attribute entry"""
    Format_8_UNorm = 0x00000000
    # 8 bits (8 x 1)
    Format_8_UInt = 0x00000100
    Format_8_SNorm = 0x00000200
    Format_8_SInt = 0x00000300
    Format_8_UIntToSingle = 0x00000800
    Format_8_SIntToSingle = 0x00000A00
    Format_4_4_UNorm = 0x00000001
    # 8 bits (4 x 2)
    Format_16_UNorm = 0x00000002
    # 16 bits (16 x 1)
    Format_16_UInt = 0x00000102
    Format_16_SNorm = 0x00000202
    Format_16_SInt = 0x00000302
    Format_16_Single = 0x00000803
    Format_16_UIntToSingle = 0x00000802
    Format_16_SIntToSingle = 0x00000A02
    Format_8_8_UNorm = 0x00000004
    # 16 bits (8 x 2)
    Format_8_8_UInt = 0x00000104
    Format_8_8_SNorm = 0x00000204
    Format_8_8_SInt = 0x00000304
    Format_8_8_UIntToSingle = 0x00000804
    Format_8_8_SIntToSingle = 0x00000A04
    Format_32_UInt = 0x00000105
    # 32 bits (32 x 1)
    Format_32_SInt = 0x00000305
    Format_32_Single = 0x00000806
    Format_16_16_UNorm = 0x00000007
    # 32 bits (16 x 2)
    Format_16_16_UInt = 0x00000107
    Format_16_16_SNorm = 0x00000207
    Format_16_16_SInt = 0x00000307
    Format_16_16_Single = 0x00000808
    Format_16_16_UIntToSingle = 0x00000807
    Format_16_16_SIntToSingle = 0x00000A07
    Format_10_11_11_Single = 0x00000809
    # 32 bits (10/11 x 3)
    Format_8_8_8_8_UNorm = 0x0000000A
    # 32 bits (8 x 4)
    Format_8_8_8_8_UInt = 0x0000010A
    Format_8_8_8_8_SNorm = 0x0000020A
    Format_8_8_8_8_SInt = 0x0000030A
    Format_8_8_8_8_UIntToSingle = 0x0000080A
    Format_8_8_8_8_SIntToSingle = 0x00000A0A
    Format_10_10_10_2_UNorm = 0x0000000B
    # 32 bits (10 x 3 + 2)
    Format_10_10_10_2_UInt = 0x0000010B
    Format_10_10_10_2_SNorm = 0x0000020B  # High 2 bits are UNorm
    Format_10_10_10_2_SInt = 0x0000030B
    Format_32_32_UInt = 0x0000010C
    # 64 bits (32 x 2)
    Format_32_32_SInt = 0x0000030C
    Format_32_32_Single = 0x0000080D
    Format_16_16_16_16_UNorm = 0x0000000E
    # 64 bits (16 x 4)
    Format_16_16_16_16_UInt = 0x0000010E
    Format_16_16_16_16_SNorm = 0x0000020E
    Format_16_16_16_16_SInt = 0x0000030E
    Format_16_16_16_16_Single = 0x0000080F
    Format_16_16_16_16_UIntToSingle = 0x0000080E
    Format_16_16_16_16_SIntToSingle = 0x00000A0E
    Format_32_32_32_UInt = 0x00000110
    # 96 bits (32 x 3)
    Format_32_32_32_SInt = 0x00000310
    Format_32_32_32_Single = 0x00000811
    Format_32_32_32_32_UInt = 0x00000112
    # 128 bits (32 x 4){
    Format_32_32_32_32_SInt = 0x00000312
    Format_32_32_32_32_Single = 0x00000813


class GX2BlendCombine(IntEnum):
    """Represents how the terms of the blend function are combined."""
    Add = 0
    SourceMinusDestination = 1
    Minimum = 2
    Maximum = 3
    DestinationMinusSource = 4


class GX2BlendFunction(IntEnum):
    """Represents the factors used in the blend function"""
    Zero = 0
    One = 1
    SourceColor = 2
    OneMinusSourceColor = 3
    SourceAlpha = 4
    OneMinusSourceAlpha = 5
    DestinationAlpha = 6
    OneMinusDestinationAlpha = 7
    DestinationColor = 8
    OneMinusDestinationColor = 9
    SourceAlphaSaturate = 10
    ConstantColor = 13
    OneMinusConstantColor = 14
    Source1Color = 15
    OneMinusSource1Color = 16
    Source1Alpha = 17
    OneMinusSource1Alpha = 18
    ConstantAlpha = 19
    OneMinusConstantAlpha = 20


class GX2CompareFunction(IntEnum):
    """Represents compare functions used for depth and stencil tests."""
    Never = 0
    Less = 1
    Equal = 2
    LessOrEqual = 3
    Greater = 4
    NotEqual = 5
    GreaterOrEqual = 6
    Always = 7


class GX2CompSel(IntEnum):
    """Represents the source channels to map to a color channel in textures."""
    ChannelR = 0
    ChannelG = 1
    ChannelB = 2
    ChannelA = 3
    Always0 = 4
    Always1 = 5


class GX2FrontFaceMode(IntEnum):
    """Represents the vertex order of front-facing polygons."""
    CounterClockwise = 0
    Clockwise = 1


class GX2IndexFormat(IntEnum):
    """Represents the type in which vertex indices are stored."""
    UInt16LittleEndian = 0
    UInt32LittleEndian = 1
    UInt16 = 4
    UInt32 = 9


class GX2LogicOp(IntEnum):
    """Represents the logic op function to perform."""

    Clear = 0x00
    """Black"""

    Set = 0xFF
    """White"""

    Copy = 0xCC
    """Source (Default)"""

    InverseCopy = 0x33
    """~Source"""

    NoOperation = 0xAA
    """Destination"""

    Inverse = 0x55
    """~Destination"""

    And = 0x88
    """Source & Destination"""

    NAnd = 0x77
    """~(Source & Destination)"""

    Or = 0xEE
    """Source | Destination"""

    NOr = 0x11
    """~(Source | Destination)"""

    XOr = 0x66
    """Source ^ Destination"""

    Equivalent = 0x99
    """ ~(Source ^ Destination)"""

    ReverseAnd = 0x44
    """Source & ~Destination"""

    InverseAnd = 0x22
    """~Source & Destination"""

    ReverseOr = 0xDD
    """Source | ~Destination"""

    InverseOr = 0xBB
    """~Source | Destination"""


class GX2PolygonMode(IntEnum):
    """Represents the base primitive used to draw each side of the polygon
    when dual-sided polygon mode is enabled."""
    Point = 0
    Line = 1
    Triangle = 2


class GX2PrimitiveType(IntEnum):
    """Represents the type of primitives to draw."""

    Points = 0x01
    """Requires at least 1 element and 1 more to draw another primitive."""

    Lines = 0x02
    """Requires at least 2 elements and 2 more to draw another primitive."""

    LineStrip = 0x03
    """Requires at least 2 elements and 1 more to draw another primitive."""

    Triangles = 0x04
    """Requires at least 3 elements and 3 more to draw another primitive."""

    TriangleFan = 0x05
    """Requires at least 3 elements and 1 more to draw another primitive."""

    TriangleStrip = 0x06
    """Requires at least 3 elements and 1 more to draw another primitive."""

    LinesAdjacency = 0x0A
    """Requires at least 4 elements and 4 more to draw another primitive."""

    LineStripAdjacency = 0x0B
    """Requires at least 4 elements and 1 more to draw another primitive."""

    TrianglesAdjacency = 0x0C
    """Requires at least 6 elements and 6 more to draw another primitive."""

    TriangleStripAdjacency = 0x0D
    """Requires at least 6 elements and 2 more to draw another primitive."""

    Rects = 0x11
    """Requires at least 3 elements and 3 more to draw another primitive."""

    LineLoop = 0x12
    """Requires at least 2 elements and 1 more to draw another primitive."""

    Quads = 0x13
    """Requires at least 4 elements and 4 more to draw another primitive."""

    QuadStrip = 0x14
    """Requires at least 4 elements and 2 more to draw another primitive."""

    TessellateLines = 0x82
    """Requires at least 2 elements and 2 more to draw another primitive."""

    TessellateLineStrip = 0x83
    """Requires at least 2 elements and 1 more to draw another primitive."""

    TessellateTriangles = 0x84
    """Requires at least 3 elements and 3 more to draw another primitive."""

    TessellateTriangleStrip = 0x86
    """Requires at least 3 elements and 1 more to draw another primitive."""

    TessellateQuads = 0x93
    """Requires at least 4 elements and 4 more to draw another primitive."""

    TessellateQuadStrip = 0x94
    """Requires at least 4 elements and 2 more to draw another primitive."""


class GX2StencilFunction(IntEnum):
    """Represents the stencil function to be performed if stencil tests pass."""
    Keep = 0
    Zero = 1
    Replace = 2
    Increment = 3
    Decrement = 4
    Invert = 5
    IncrementWrap = 6
    DecrementWrap = 7


class GX2SurfaceDim(IntEnum):
    """Represents shapes of a given surface or texture."""
    Dim1D = 0
    Dim2D = 1
    Dim3D = 2
    DimCube = 3
    Dim1DArray = 4
    Dim2DArray = 5
    Dim2DMsaa = 6
    Dim2DMsaaArray = 7


class GX2SurfaceFormat(IntEnum):
    """Represents desired texture, color-buffer, depth-buffer, or scan-buffer formats."""
    Invalid = 0x00000000
    TC_R8_UNorm = 0x00000001
    TC_R8_UInt = 0x00000101
    TC_R8_SNorm = 0x00000201
    TC_R8_SInt = 0x00000301
    T_R4_G4_UNorm = 0x00000002
    TCD_R16_UNorm = 0x00000005
    TC_R16_UInt = 0x00000105
    TC_R16_SNorm = 0x00000205
    TC_R10_G10_B10_A2_SNorm = 0x00000219
    TC_R10_G10_B10_A2_SInt = 0x00000319
    TCS_R8_G8_B8_A8_UNorm = 0x0000001A
    TC_R8_G8_B8_A8_UInt = 0x0000011A
    TC_R8_G8_B8_A8_SNorm = 0x0000021A
    TC_R8_G8_B8_A8_SInt = 0x0000031A
    TCS_R8_G8_B8_A8_SRGB = 0x0000041A
    TCS_A2_B10_G10_R10_UNorm = 0x0000001B
    TC_A2_B10_G10_R10_UInt = 0x0000011B
    D_D32_Float_S8_UInt_X24 = 0x0000081C
    T_R32_Float_X8_X24 = 0x0000081C
    T_X32_G8_UInt_X24 = 0x0000011C
    TC_R32_G32_UInt = 0x0000011D
    TC_R32_G32_SInt = 0x0000031D
    TC_R32_G32_Float = 0x0000081E
    TC_R16_G16_B16_A16_UNorm = 0x0000001F
    TC_R16_G16_B16_A16_UInt = 0x0000011F
    TC_R16_G16_B16_A16_SNorm = 0x0000021F
    TC_R16_G16_B16_A16_SInt = 0x0000031F
    TC_R16_G16_B16_A16_Float = 0x00000820
    TC_R32_G32_B32_A32_UInt = 0x00000122
    TC_R32_G32_B32_A32_SInt = 0x00000322
    TC_R32_G32_B32_A32_Float = 0x00000823
    T_BC1_UNorm = 0x00000031
    T_BC1_SRGB = 0x00000431
    T_BC2_UNorm = 0x00000032
    T_BC2_SRGB = 0x00000432
    T_BC3_UNorm = 0x00000033
    T_BC3_SRGB = 0x00000433
    T_BC4_UNorm = 0x00000034
    T_BC4_SNorm = 0x00000234
    T_BC5_UNorm = 0x00000035
    T_BC5_SNorm = 0x00000235
    T_NV12_UNorm = 0x00000081


class GX2SurfaceUse(IntFlag):
    """Represents Indicates how a given surface may be used. A final TV render
    target is one that will be copied to a TV scan buffer. It needs to be
    designated to handle certain display corner cases (when a HD surface
    must be scaled down to display in NTSC/PAL)."""
    Texture = 1 << 0
    ColorBuffer = 1 << 1
    DepthBuffer = 1 << 2
    ScanBuffer = 1 << 3
    FinalTV = 1 << 31
    ColorBufferTexture = Texture | ColorBuffer
    DepthBufferTexture = Texture | DepthBuffer
    ColorBufferFinalTV = FinalTV | ColorBuffer
    ColorBufferTextureFinalTV = FinalTV | ColorBufferTexture


class GX2TexAnisoRatio(IntEnum):
    """Represents maximum desired anisotropic filter ratios.
    Higher ratios give better image quality, but slower performance.
    """
    Ratio_1_1 = 0
    Ratio_2_1 = 1
    Ratio_4_1 = 2
    Ratio_8_1 = 3
    Ratio_16_1 = 4


class GX2TexBorderType(IntEnum):
    """Represents type of border color to use."""
    ClearBlack = 0
    SolidBlack = 1
    SolidWhite = 2
    UseRegister = 3


class GX2TexClamp(IntEnum):
    """Represents how to treat texture coordinates outside of the normalized coordinate texture range."""
    Wrap = 0
    Mirror = 1
    Clamp = 2
    MirrorOnce = 3
    ClampHalfBorder = 4
    MirrorOnceHalfBorder = 5
    ClampBorder = 6
    MirrorOnceBorder = 7
    ClampToEdge = 8


class GX2TexMipFilterType(IntEnum):
    """Represents desired texture filter options between mip levels."""
    NoMip = 0
    Point = 1
    Linear = 2


class GX2TexXYFilterType(IntEnum):
    """Represents desired texture filter options within a plane."""
    Point = 0
    Bilinear = 1


class GX2TexZFilterType(IntEnum):
    """Represents desired texture filter options between Z planes."""
    UseXY = 0
    Point = 1
    Linear = 2


class GX2TileMode(IntEnum):
    """Represents the desired tiling modes for a surface."""
    Default = 0
    LinearAligned = 1
    Mode1dTiledThin1 = 2
    Mode1dTiledThick = 3
    Mode2dTiledThin1 = 4
    Mode2dTiledThin2 = 5
    Mode2dTiledThin4 = 6
    Mode2dTiledThick = 7
    Mode2bTiledThin1 = 8
    Mode2bTiledThin2 = 9
    Mode2bTiledThin4 = 10
    Mode2bTiledThick = 11
    Mode3dTiledThin1 = 12
    Mode3dTiledThick = 13
    Mode3bTiledThin1 = 14
    Mode3bTiledThick = 15
    LinearSpecial = 16
