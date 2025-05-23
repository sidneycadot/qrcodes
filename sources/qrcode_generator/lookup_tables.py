"""Lookup tables for QR code generation."""

from typing import NamedTuple

from .enum_types import ErrorCorrectionLevel, DataMaskPattern, EncodingVariant, CharacterEncodingType

# The encoding of the error correction level as specified in Table 12 of ISO/IEC 18004:2024(en).

error_correction_level_encoding = {
    ErrorCorrectionLevel.L: 0b01,
    ErrorCorrectionLevel.M: 0b00,
    ErrorCorrectionLevel.Q: 0b11,
    ErrorCorrectionLevel.H: 0b10
}

# The number of bits in the character count that follows the 4-bit mode indicator as specified in Table 3 of ISO/IEC 18004:2024(en).

count_bits_table = {
    EncodingVariant.SMALL: {
        CharacterEncodingType.NUMERIC: 10,
        CharacterEncodingType.ALPHANUMERIC: 9,
        CharacterEncodingType.BYTES: 8,
        CharacterEncodingType.KANJI: 8
    },
    EncodingVariant.MEDIUM: {
        CharacterEncodingType.NUMERIC: 12,
        CharacterEncodingType.ALPHANUMERIC: 11,
        CharacterEncodingType.BYTES: 16,
        CharacterEncodingType.KANJI: 10
    },
    EncodingVariant.LARGE: {
        CharacterEncodingType.NUMERIC: 14,
        CharacterEncodingType.ALPHANUMERIC: 13,
        CharacterEncodingType.BYTES: 16,
        CharacterEncodingType.KANJI: 12
    }
}

# QR Code version specifications as given in Table 9 of ISO/IEC 18004:2024(en).
#
# Among other things, these specify the Reed-Solomon codes used in each of the 160 QR code formats
# described by the standard (40 versions, with 4 error correction levels per version).


class VersionSpecification(NamedTuple):
    """Represent version-specific information."""
    version: int
    error_correction_level: ErrorCorrectionLevel
    total_number_of_codewords: int
    number_of_error_correcting_codewords: int
    p: int
    block_specification: list[tuple[int, tuple[int, int, int]]]

    def name(self) -> str:
        return f"{self.version}-{self.error_correction_level.name}"

    def number_of_data_codewords(self) -> int:
        return self.total_number_of_codewords - self.number_of_error_correcting_codewords


version_specification_table = {

    (version_specification.version, version_specification.error_correction_level) : version_specification for version_specification in [

        VersionSpecification( 1, ErrorCorrectionLevel.L,   26,    7, 3, [ (  1, ( 26,  19,  2))                        ]),
        VersionSpecification( 1, ErrorCorrectionLevel.M,   26,   10, 2, [ (  1, ( 26,  16,  4))                        ]),
        VersionSpecification( 1, ErrorCorrectionLevel.Q,   26,   13, 1, [ (  1, ( 26,  13,  6))                        ]),
        VersionSpecification( 1, ErrorCorrectionLevel.H,   26,   17, 1, [ (  1, ( 26,   9,  8))                        ]),

        VersionSpecification( 2, ErrorCorrectionLevel.L,   44,   10, 2, [ (  1, ( 44,  34,  4))                        ]),
        VersionSpecification( 2, ErrorCorrectionLevel.M,   44,   16, 0, [ (  1, ( 44,  28,  8))                        ]),
        VersionSpecification( 2, ErrorCorrectionLevel.Q,   44,   22, 0, [ (  1, ( 44,  22, 11))                        ]),
        VersionSpecification( 2, ErrorCorrectionLevel.H,   44,   28, 0, [ (  1, ( 44,  16, 14))                        ]),

        VersionSpecification( 3, ErrorCorrectionLevel.L,   70,   15, 1, [ (  1, ( 70,  55,  7))                        ]),
        VersionSpecification( 3, ErrorCorrectionLevel.M,   70,   26, 0, [ (  1, ( 70,  44, 13))                        ]),
        VersionSpecification( 3, ErrorCorrectionLevel.Q,   70,   36, 0, [ (  2, ( 35,  17,  9))                        ]),
        VersionSpecification( 3, ErrorCorrectionLevel.H,   70,   44, 0, [ (  2, ( 35,  13, 11))                        ]),

        VersionSpecification( 4, ErrorCorrectionLevel.L,  100,   20, 0, [ (  1, (100,  80, 10))                        ]),
        VersionSpecification( 4, ErrorCorrectionLevel.M,  100,   36, 0, [ (  2, ( 50,  32,  9))                        ]),
        VersionSpecification( 4, ErrorCorrectionLevel.Q,  100,   52, 0, [ (  2, ( 50,  24, 13))                        ]),
        VersionSpecification( 4, ErrorCorrectionLevel.H,  100,   64, 0, [ (  4, ( 25,   9,  8))                        ]),

        VersionSpecification( 5, ErrorCorrectionLevel.L,  134,   26, 0, [ (  1, (134, 108, 13))                        ]),
        VersionSpecification( 5, ErrorCorrectionLevel.M,  134,   48, 0, [ (  2, ( 67,  43, 12))                        ]),
        VersionSpecification( 5, ErrorCorrectionLevel.Q,  134,   72, 0, [ (  2, ( 33,  15,  9)), (  2, ( 34,  16,  9)) ]),
        VersionSpecification( 5, ErrorCorrectionLevel.H,  134,   88, 0, [ (  2, ( 33,  11, 11)), (  2, ( 34,  12, 11)) ]),

        VersionSpecification( 6, ErrorCorrectionLevel.L,  172,   36, 0, [ (  2, ( 86,  68,  9))                        ]),
        VersionSpecification( 6, ErrorCorrectionLevel.M,  172,   64, 0, [ (  4, ( 43,  27,  8))                        ]),
        VersionSpecification( 6, ErrorCorrectionLevel.Q,  172,   96, 0, [ (  4, ( 43,  19, 12))                        ]),
        VersionSpecification( 6, ErrorCorrectionLevel.H,  172,  112, 0, [ (  4, ( 43,  15, 14))                        ]),

        VersionSpecification( 7, ErrorCorrectionLevel.L,  196,   40, 0, [ (  2, ( 98,  78, 10))                        ]),
        VersionSpecification( 7, ErrorCorrectionLevel.M,  196,   72, 0, [ (  4, ( 49,  31,  9))                        ]),
        VersionSpecification( 7, ErrorCorrectionLevel.Q,  196,  108, 0, [ (  2, ( 32,  14,  9)), (  4, ( 33,  15,  9)) ]),
        VersionSpecification( 7, ErrorCorrectionLevel.H,  196,  130, 0, [ (  4, ( 39,  13, 13)), (  1, ( 40,  14, 13)) ]),

        VersionSpecification( 8, ErrorCorrectionLevel.L,  242,   48, 0, [ (  2, (121,  97, 12))                        ]),
        VersionSpecification( 8, ErrorCorrectionLevel.M,  242,   88, 0, [ (  2, ( 60,  38, 11)), (  2, ( 61,  39, 11)) ]),
        VersionSpecification( 8, ErrorCorrectionLevel.Q,  242,  132, 0, [ (  4, ( 40,  18, 11)), (  2, ( 41,  19, 11)) ]),
        VersionSpecification( 8, ErrorCorrectionLevel.H,  242,  156, 0, [ (  4, ( 40,  14, 13)), (  2, ( 41,  15, 13)) ]),

        VersionSpecification( 9, ErrorCorrectionLevel.L,  292,   60, 0, [ (  2, (146, 116, 15))                        ]),
        VersionSpecification( 9, ErrorCorrectionLevel.M,  292,  110, 0, [ (  3, ( 58,  36, 11)), (  2, ( 59,  37, 11)) ]),
        VersionSpecification( 9, ErrorCorrectionLevel.Q,  292,  160, 0, [ (  4, ( 36,  16, 10)), (  4, ( 37,  17, 10)) ]),
        VersionSpecification( 9, ErrorCorrectionLevel.H,  292,  192, 0, [ (  4, ( 36,  12, 12)), (  4, ( 37,  13, 12)) ]),

        VersionSpecification(10, ErrorCorrectionLevel.L,  346,   72, 0, [ (  2, ( 86,  68,  9)), (  2, ( 87,  69,  9)) ]),
        VersionSpecification(10, ErrorCorrectionLevel.M,  346,  130, 0, [ (  4, ( 69,  43, 13)), (  1, ( 70,  44, 13)) ]),
        VersionSpecification(10, ErrorCorrectionLevel.Q,  346,  192, 0, [ (  6, ( 43,  19, 12)), (  2, ( 44,  20, 12)) ]),
        VersionSpecification(10, ErrorCorrectionLevel.H,  346,  224, 0, [ (  6, ( 43,  15, 14)), (  2, ( 44,  16, 14)) ]),

        VersionSpecification(11, ErrorCorrectionLevel.L,  404,   80, 0, [ (  4, (101,  81, 10))                        ]),
        VersionSpecification(11, ErrorCorrectionLevel.M,  404,  150, 0, [ (  1, ( 80,  50, 15)), (  4, ( 81,  51, 15)) ]),
        VersionSpecification(11, ErrorCorrectionLevel.Q,  404,  224, 0, [ (  4, ( 50,  22, 14)), (  4, ( 51,  23, 14)) ]),
        VersionSpecification(11, ErrorCorrectionLevel.H,  404,  264, 0, [ (  3, ( 36,  12, 12)), (  8, ( 37,  13, 12)) ]),

        VersionSpecification(12, ErrorCorrectionLevel.L,  466,   96, 0, [ (  2, (116,  92, 12)), (  2, (117,  93, 12)) ]),
        VersionSpecification(12, ErrorCorrectionLevel.M,  466,  176, 0, [ (  6, ( 58,  36, 11)), (  2, ( 59,  37, 11)) ]),
        VersionSpecification(12, ErrorCorrectionLevel.Q,  466,  260, 0, [ (  4, ( 46,  20, 13)), (  6, ( 47,  21, 13)) ]),
        VersionSpecification(12, ErrorCorrectionLevel.H,  466,  308, 0, [ (  7, ( 42,  14, 14)), (  4, ( 43,  15, 14)) ]),

        VersionSpecification(13, ErrorCorrectionLevel.L,  532,  104, 0, [ (  4, (133, 107, 13))                        ]),
        VersionSpecification(13, ErrorCorrectionLevel.M,  532,  198, 0, [ (  8, ( 59,  37, 11)), (  1, ( 60,  38, 11)) ]),
        VersionSpecification(13, ErrorCorrectionLevel.Q,  532,  288, 0, [ (  8, ( 44,  20, 12)), (  4, ( 45,  21, 12)) ]),
        VersionSpecification(13, ErrorCorrectionLevel.H,  532,  352, 0, [ ( 12, ( 33,  11, 11)), (  4, ( 34,  12, 11)) ]),

        VersionSpecification(14, ErrorCorrectionLevel.L,  581,  120, 0, [ (  3, (145, 115, 15)), (  1, (146, 116, 15)) ]),
        VersionSpecification(14, ErrorCorrectionLevel.M,  581,  216, 0, [ (  4, ( 64,  40, 12)), (  5, ( 65,  41, 12)) ]),
        VersionSpecification(14, ErrorCorrectionLevel.Q,  581,  320, 0, [ ( 11, ( 36,  16, 10)), (  5, ( 37,  17, 10)) ]),
        VersionSpecification(14, ErrorCorrectionLevel.H,  581,  384, 0, [ ( 11, ( 36,  12, 12)), (  5, ( 37,  13, 12)) ]),

        VersionSpecification(15, ErrorCorrectionLevel.L,  655,  132, 0, [ (  5, (109,  87, 11)), (  1, (110,  88, 11)) ]),
        VersionSpecification(15, ErrorCorrectionLevel.M,  655,  240, 0, [ (  5, ( 65,  41, 12)), (  5, ( 66,  42, 12)) ]),
        VersionSpecification(15, ErrorCorrectionLevel.Q,  655,  360, 0, [ (  5, ( 54,  24, 15)), (  7, ( 55,  25, 15)) ]),
        VersionSpecification(15, ErrorCorrectionLevel.H,  655,  432, 0, [ ( 11, ( 36,  12, 12)), (  7, ( 37,  13, 12)) ]),

        VersionSpecification(16, ErrorCorrectionLevel.L,  733,  144, 0, [ (  5, (122,  98, 12)), (  1, (123,  99, 12)) ]),
        VersionSpecification(16, ErrorCorrectionLevel.M,  733,  280, 0, [ (  7, ( 73,  45, 14)), (  3, ( 74,  46, 14)) ]),
        VersionSpecification(16, ErrorCorrectionLevel.Q,  733,  408, 0, [ ( 15, ( 43,  19, 12)), (  2, ( 44,  20, 12)) ]),
        VersionSpecification(16, ErrorCorrectionLevel.H,  733,  480, 0, [ (  3, ( 45,  15, 15)), ( 13, ( 46,  16, 15)) ]),

        VersionSpecification(17, ErrorCorrectionLevel.L,  815,  168, 0, [ (  1, (135, 107, 14)), (  5, (136, 108, 14)) ]),
        VersionSpecification(17, ErrorCorrectionLevel.M,  815,  308, 0, [ ( 10, ( 74,  46, 14)), (  1, ( 75,  47, 14)) ]),
        VersionSpecification(17, ErrorCorrectionLevel.Q,  815,  448, 0, [ (  1, ( 50,  22, 14)), ( 15, ( 51,  23, 14)) ]),
        VersionSpecification(17, ErrorCorrectionLevel.H,  815,  532, 0, [ (  2, ( 42,  14, 14)), ( 17, ( 43,  15, 14)) ]),

        VersionSpecification(18, ErrorCorrectionLevel.L,  901,  180, 0, [ (  5, (150, 120, 15)), (  1, (151, 121, 15)) ]),
        VersionSpecification(18, ErrorCorrectionLevel.M,  901,  338, 0, [ (  9, ( 69,  43, 13)), (  4, ( 70,  44, 13)) ]),
        VersionSpecification(18, ErrorCorrectionLevel.Q,  901,  504, 0, [ ( 17, ( 50,  22, 14)), (  1, ( 51,  23, 14)) ]),
        VersionSpecification(18, ErrorCorrectionLevel.H,  901,  588, 0, [ (  2, ( 42,  14, 14)), ( 19, ( 43,  15, 14)) ]),

        VersionSpecification(19, ErrorCorrectionLevel.L,  991,  196, 0, [ (  3, (141, 113, 14)), (  4, (142, 114, 14)) ]),
        VersionSpecification(19, ErrorCorrectionLevel.M,  991,  364, 0, [ (  3, ( 70,  44, 13)), ( 11, ( 71,  45, 13)) ]),
        VersionSpecification(19, ErrorCorrectionLevel.Q,  991,  546, 0, [ ( 17, ( 47,  21, 13)), (  4, ( 48,  22, 13)) ]),
        VersionSpecification(19, ErrorCorrectionLevel.H,  991,  650, 0, [ (  9, ( 39,  13, 13)), ( 16, ( 40,  14, 13)) ]),

        VersionSpecification(20, ErrorCorrectionLevel.L, 1085,  224, 0, [ (  3, (135, 107, 14)), (  5, (136, 108, 14)) ]),
        VersionSpecification(20, ErrorCorrectionLevel.M, 1085,  416, 0, [ (  3, ( 67,  41, 13)), ( 13, ( 68,  42, 13)) ]),
        VersionSpecification(20, ErrorCorrectionLevel.Q, 1085,  600, 0, [ ( 15, ( 54,  24, 15)), (  5, ( 55,  25, 15)) ]),
        VersionSpecification(20, ErrorCorrectionLevel.H, 1085,  700, 0, [ ( 15, ( 43,  15, 14)), ( 10, ( 44,  16, 14)) ]),

        VersionSpecification(21, ErrorCorrectionLevel.L, 1156,  224, 0, [ (  4, (144, 116, 14)), (  4, (145, 117, 14)) ]),
        VersionSpecification(21, ErrorCorrectionLevel.M, 1156,  442, 0, [ ( 17, ( 68,  42, 13))                        ]),
        VersionSpecification(21, ErrorCorrectionLevel.Q, 1156,  644, 0, [ ( 17, ( 50,  22, 14)), (  6, ( 51,  23, 14)) ]),
        VersionSpecification(21, ErrorCorrectionLevel.H, 1156,  750, 0, [ ( 19, ( 46,  16, 15)), (  6, ( 47,  17, 15)) ]),

        VersionSpecification(22, ErrorCorrectionLevel.L, 1258,  252, 0, [ (  2, (139, 111, 14)), (  7, (140, 112, 14)) ]),
        VersionSpecification(22, ErrorCorrectionLevel.M, 1258,  476, 0, [ ( 17, ( 74,  46, 14)),                       ]),
        VersionSpecification(22, ErrorCorrectionLevel.Q, 1258,  690, 0, [ (  7, ( 54,  24, 15)), ( 16, ( 55,  25, 15)) ]),
        VersionSpecification(22, ErrorCorrectionLevel.H, 1258,  816, 0, [ ( 34, ( 37,  13, 12))                        ]),

        VersionSpecification(23, ErrorCorrectionLevel.L, 1364,  270, 0, [ (  4, (151, 121, 15)), (  5, (152, 122, 15)) ]),
        VersionSpecification(23, ErrorCorrectionLevel.M, 1364,  504, 0, [ (  4, ( 75,  47, 14)), ( 14, ( 76,  48, 14)) ]),
        VersionSpecification(23, ErrorCorrectionLevel.Q, 1364,  750, 0, [ ( 11, ( 54,  24, 15)), ( 14, ( 55,  25, 15)) ]),
        VersionSpecification(23, ErrorCorrectionLevel.H, 1364,  900, 0, [ ( 16, ( 45,  15, 15)), ( 14, ( 46,  16, 15)) ]),

        VersionSpecification(24, ErrorCorrectionLevel.L, 1474,  300, 0, [ (  6, (147, 117, 15)), (  4, (148, 118, 15)) ]),
        VersionSpecification(24, ErrorCorrectionLevel.M, 1474,  560, 0, [ (  6, ( 73,  45, 14)), ( 14, ( 74,  46, 14)) ]),
        VersionSpecification(24, ErrorCorrectionLevel.Q, 1474,  810, 0, [ ( 11, ( 54,  24, 15)), ( 16, ( 55,  25, 15)) ]),
        VersionSpecification(24, ErrorCorrectionLevel.H, 1474,  960, 0, [ ( 30, ( 46,  16, 15)), (  2, ( 47,  17, 15)) ]),

        VersionSpecification(25, ErrorCorrectionLevel.L, 1588,  312, 0, [ (  8, (132, 106, 13)), (  4, (133, 107, 13)) ]),
        VersionSpecification(25, ErrorCorrectionLevel.M, 1588,  588, 0, [ (  8, ( 75,  47, 14)), ( 13, ( 76,  48, 14)) ]),
        VersionSpecification(25, ErrorCorrectionLevel.Q, 1588,  870, 0, [ (  7, ( 54,  24, 15)), ( 22, ( 55,  25, 15)) ]),
        VersionSpecification(25, ErrorCorrectionLevel.H, 1588, 1050, 0, [ ( 22, ( 45,  15, 15)), ( 13, ( 46,  16, 15)) ]),

        VersionSpecification(26, ErrorCorrectionLevel.L, 1706,  336, 0, [ ( 10, (142, 114, 14)), (  2, (143, 115, 14)) ]),
        VersionSpecification(26, ErrorCorrectionLevel.M, 1706,  644, 0, [ ( 19, ( 74,  46, 14)), (  4, ( 75,  47, 14)) ]),
        VersionSpecification(26, ErrorCorrectionLevel.Q, 1706,  952, 0, [ ( 28, ( 50,  22, 14)), (  6, ( 51,  23, 14)) ]),
        VersionSpecification(26, ErrorCorrectionLevel.H, 1706, 1110, 0, [ ( 33, ( 46,  16, 15)), (  4, ( 47,  17, 15)) ]),

        VersionSpecification(27, ErrorCorrectionLevel.L, 1828,  360, 0, [ (  8, (152, 122, 15)), (  4, (153, 123, 15)) ]),
        VersionSpecification(27, ErrorCorrectionLevel.M, 1828,  700, 0, [ ( 22, ( 73,  45, 14)), (  3, ( 74,  46, 14)) ]),
        VersionSpecification(27, ErrorCorrectionLevel.Q, 1828, 1020, 0, [ (  8, ( 53,  23, 15)), ( 26, ( 54,  24, 15)) ]),
        VersionSpecification(27, ErrorCorrectionLevel.H, 1828, 1200, 0, [ ( 12, ( 45,  15, 15)), ( 28, ( 46,  16, 15)) ]),

        VersionSpecification(28, ErrorCorrectionLevel.L, 1921,  390, 0, [ (  3, (147, 117, 15)), ( 10, (148, 118, 15)) ]),
        VersionSpecification(28, ErrorCorrectionLevel.M, 1921,  728, 0, [ (  3, ( 73,  45, 14)), ( 23, ( 74,  46, 14)) ]),
        VersionSpecification(28, ErrorCorrectionLevel.Q, 1921, 1050, 0, [ (  4, ( 54,  24, 15)), ( 31, ( 55,  25, 15)) ]),
        VersionSpecification(28, ErrorCorrectionLevel.H, 1921, 1260, 0, [ ( 11, ( 45,  15, 15)), ( 31, ( 46,  16, 15)) ]),

        VersionSpecification(29, ErrorCorrectionLevel.L, 2051,  420, 0, [ (  7, (146, 116, 15)), (  7, (147, 117, 15)) ]),
        VersionSpecification(29, ErrorCorrectionLevel.M, 2051,  784, 0, [ ( 21, ( 73,  45, 14)), (  7, ( 74,  46, 14)) ]),
        VersionSpecification(29, ErrorCorrectionLevel.Q, 2051, 1140, 0, [ (  1, ( 53,  23, 15)), ( 37, ( 54,  24, 15)) ]),
        VersionSpecification(29, ErrorCorrectionLevel.H, 2051, 1350, 0, [ ( 19, ( 45,  15, 15)), ( 26, ( 46,  16, 15)) ]),

        VersionSpecification(30, ErrorCorrectionLevel.L, 2185,  450, 0, [ (  5, (145, 115, 15)), ( 10, (146, 116, 15)) ]),
        VersionSpecification(30, ErrorCorrectionLevel.M, 2185,  812, 0, [ ( 19, ( 75,  47, 14)), ( 10, ( 76,  48, 14)) ]),
        VersionSpecification(30, ErrorCorrectionLevel.Q, 2185, 1200, 0, [ ( 15, ( 54,  24, 15)), ( 25, ( 55,  25, 15)) ]),
        VersionSpecification(30, ErrorCorrectionLevel.H, 2185, 1440, 0, [ ( 23, ( 45,  15, 15)), ( 25, ( 46,  16, 15)) ]),

        VersionSpecification(31, ErrorCorrectionLevel.L, 2323,  480, 0, [ ( 13, (145, 115, 15)), (  3, (146, 116, 15)) ]),
        VersionSpecification(31, ErrorCorrectionLevel.M, 2323,  868, 0, [ (  2, ( 74,  46, 14)), ( 29, ( 75,  47, 14)) ]),
        VersionSpecification(31, ErrorCorrectionLevel.Q, 2323, 1290, 0, [ ( 42, ( 54,  24, 15)), (  1, ( 55,  25, 15)) ]),
        VersionSpecification(31, ErrorCorrectionLevel.H, 2323, 1530, 0, [ ( 23, ( 45,  15, 15)), ( 28, ( 46,  16, 15)) ]),

        VersionSpecification(32, ErrorCorrectionLevel.L, 2465,  510, 0, [ ( 17, (145, 115, 15))                        ]),
        VersionSpecification(32, ErrorCorrectionLevel.M, 2465,  924, 0, [ ( 10, ( 74,  46, 14)), ( 23, ( 75,  47, 14)) ]),
        VersionSpecification(32, ErrorCorrectionLevel.Q, 2465, 1350, 0, [ ( 10, ( 54,  24, 15)), ( 35, ( 55,  25, 15)) ]),
        VersionSpecification(32, ErrorCorrectionLevel.H, 2465, 1620, 0, [ ( 19, ( 45,  15, 15)), ( 35, ( 46,  16, 15)) ]),

        VersionSpecification(33, ErrorCorrectionLevel.L, 2611,  540, 0, [ ( 17, (145, 115, 15)), (  1, (146, 116, 15)) ]),
        VersionSpecification(33, ErrorCorrectionLevel.M, 2611,  980, 0, [ ( 14, ( 74,  46, 14)), ( 21, ( 75,  47, 14)) ]),
        VersionSpecification(33, ErrorCorrectionLevel.Q, 2611, 1440, 0, [ ( 29, ( 54,  24, 15)), ( 19, ( 55,  25, 15)) ]),
        VersionSpecification(33, ErrorCorrectionLevel.H, 2611, 1710, 0, [ ( 11, ( 45,  15, 15)), ( 46, ( 46,  16, 15)) ]),

        VersionSpecification(34, ErrorCorrectionLevel.L, 2761,  570, 0, [ ( 13, (145, 115, 15)), (  6, (146, 116, 15)) ]),
        VersionSpecification(34, ErrorCorrectionLevel.M, 2761, 1036, 0, [ ( 14, ( 74,  46, 14)), ( 23, ( 75,  47, 14)) ]),
        VersionSpecification(34, ErrorCorrectionLevel.Q, 2761, 1530, 0, [ ( 44, ( 54,  24, 15)), (  7, ( 55,  25, 15)) ]),
        VersionSpecification(34, ErrorCorrectionLevel.H, 2761, 1800, 0, [ ( 59, ( 46,  16, 15)), (  1, ( 47,  17, 15)) ]),

        VersionSpecification(35, ErrorCorrectionLevel.L, 2876,  570, 0, [ ( 12, (151, 121, 15)), (  7, (152, 122, 15)) ]),
        VersionSpecification(35, ErrorCorrectionLevel.M, 2876, 1064, 0, [ ( 12, ( 75,  47, 14)), ( 26, ( 76,  48, 14)) ]),
        VersionSpecification(35, ErrorCorrectionLevel.Q, 2876, 1590, 0, [ ( 39, ( 54,  24, 15)), ( 14, ( 55,  25, 15)) ]),
        VersionSpecification(35, ErrorCorrectionLevel.H, 2876, 1890, 0, [ ( 22, ( 45,  15, 15)), ( 41, ( 46,  16, 15)) ]),

        VersionSpecification(36, ErrorCorrectionLevel.L, 3034,  600, 0, [ (  6, (151, 121, 15)), ( 14, (152, 122, 15)) ]),
        VersionSpecification(36, ErrorCorrectionLevel.M, 3034, 1120, 0, [ (  6, ( 75,  47, 14)), ( 34, ( 76,  48, 14)) ]),
        VersionSpecification(36, ErrorCorrectionLevel.Q, 3034, 1680, 0, [ ( 46, ( 54,  24, 15)), ( 10, ( 55,  25, 15)) ]),
        VersionSpecification(36, ErrorCorrectionLevel.H, 3034, 1980, 0, [ (  2, ( 45,  15, 15)), ( 64, ( 46,  16, 15)) ]),

        VersionSpecification(37, ErrorCorrectionLevel.L, 3196,  630, 0, [ ( 17, (152, 122, 15)), (  4, (153, 123, 15)) ]),
        VersionSpecification(37, ErrorCorrectionLevel.M, 3196, 1204, 0, [ ( 29, ( 74,  46, 14)), ( 14, ( 75,  47, 14)) ]),
        VersionSpecification(37, ErrorCorrectionLevel.Q, 3196, 1770, 0, [ ( 49, ( 54,  24, 15)), ( 10, ( 55,  25, 15)) ]),
        VersionSpecification(37, ErrorCorrectionLevel.H, 3196, 2100, 0, [ ( 24, ( 45,  15, 15)), ( 46, ( 46,  16, 15)) ]),

        VersionSpecification(38, ErrorCorrectionLevel.L, 3362,  660, 0, [ (  4, (152, 122, 15)), ( 18, (153, 123, 15)) ]),
        VersionSpecification(38, ErrorCorrectionLevel.M, 3362, 1260, 0, [ ( 13, ( 74,  46, 14)), ( 32, ( 75,  47, 14)) ]),
        VersionSpecification(38, ErrorCorrectionLevel.Q, 3362, 1860, 0, [ ( 48, ( 54,  24, 15)), ( 14, ( 55,  25, 15)) ]),
        VersionSpecification(38, ErrorCorrectionLevel.H, 3362, 2220, 0, [ ( 42, ( 45,  15, 15)), ( 32, ( 46,  16, 15)) ]),

        VersionSpecification(39, ErrorCorrectionLevel.L, 3532,  720, 0, [ ( 20, (147, 117, 15)), (  4, (148, 118, 15)) ]),
        VersionSpecification(39, ErrorCorrectionLevel.M, 3532, 1316, 0, [ ( 40, ( 75,  47, 14)), (  7, ( 76,  48, 14)) ]),
        VersionSpecification(39, ErrorCorrectionLevel.Q, 3532, 1950, 0, [ ( 43, ( 54,  24, 15)), ( 22, ( 55,  25, 15)) ]),
        VersionSpecification(39, ErrorCorrectionLevel.H, 3532, 2310, 0, [ ( 10, ( 45,  15, 15)), ( 67, ( 46,  16, 15)) ]),

        VersionSpecification(40, ErrorCorrectionLevel.L, 3706,  750, 0, [ ( 19, (148, 118, 15)), (  6, (149, 119, 15)) ]),
        VersionSpecification(40, ErrorCorrectionLevel.M, 3706, 1372, 0, [ ( 18, ( 75,  47, 14)), ( 31, ( 76,  48, 14)) ]),
        VersionSpecification(40, ErrorCorrectionLevel.Q, 3706, 2040, 0, [ ( 34, ( 54,  24, 15)), ( 34, ( 55,  25, 15)) ]),
        VersionSpecification(40, ErrorCorrectionLevel.H, 3706, 2430, 0, [ ( 20, ( 45,  15, 15)), ( 61, ( 46,  16, 15)) ])
    ]
}

# Data mask pattern definitions as given in Table 10 of ISO/IEC 18004:2024(en).

data_masking_pattern_encoding = {
    DataMaskPattern.PATTERN0: 0,
    DataMaskPattern.PATTERN1: 1,
    DataMaskPattern.PATTERN2: 2,
    DataMaskPattern.PATTERN3: 3,
    DataMaskPattern.PATTERN4: 4,
    DataMaskPattern.PATTERN5: 5,
    DataMaskPattern.PATTERN6: 6,
    DataMaskPattern.PATTERN7: 7
}

data_mask_pattern_function_table = {
    DataMaskPattern.PATTERN0: lambda i, j: (i + j) % 2 == 0,
    DataMaskPattern.PATTERN1: lambda i, j: i % 2 == 0,
    DataMaskPattern.PATTERN2: lambda i, j: j % 3 == 0,
    DataMaskPattern.PATTERN3: lambda i, j: (i + j) % 3 == 0,
    DataMaskPattern.PATTERN4: lambda i, j: ((i // 2) + (j // 3)) % 2 == 0,
    DataMaskPattern.PATTERN5: lambda i, j: (i * j) % 2 + (i * j) % 3 == 0,
    DataMaskPattern.PATTERN6: lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0,
    DataMaskPattern.PATTERN7: lambda i, j: ((i + j) % 2 + (i * j) % 3) % 2 == 0
}

# Alignment pattern positions QR codes as specified in Table E.1 of ISO/IEC 18004:2024(en).
#
# They specify both horizontal and vertical center positions of the 5x5 alignment
# patterns present in regular QR codes. The top-left, top-right, and bottom-left
# alignment patterns are omitted, as they would clash with the three finder patterns.
#
# QR Code version 1 is exceptional, as it has no alignment patterns at all.
#
# For versions 2..40, we observe the following:
#
# (1) The first and last positions are predictable. They are fixed relative to the
#     edges of the QR code.
#
#     first_position = 6
#     last_position  = 10 + 4 * version
#
# (2) The number of positions occupied is predictable:
#
#     num_positions = 2 + floor(version / 7)
#
#    Note that the standard does not explicitly guarantee this.
#    The pattern is easily deduced from the table.
#
# (3) The first step (i.e., the difference between the first and second position)
#     can differ from all other steps. All steps but the first are identical.
#
#     The standard documents these two facts, but it does not specify how
#     to derive the two step-sizes given the version number.
#
#     There appears to be no simple relation to derive the first and
#     non-first step-sizes from the version number that works in all cases.
#
# Given the lack of an algorithmic description of how to obtain the alignment pattern positions
# from the version number, we will use a lookup table instead.

alignment_pattern_position_table: dict[int, list[int]] = {
     1: [],
     2: [6, 18],
     3: [6, 22],
     4: [6, 26],
     5: [6, 30],
     6: [6, 34],
     7: [6, 22, 38],
     8: [6, 24, 42],
     9: [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66],
    15: [6, 26, 48, 70],
    16: [6, 26, 50, 74],
    17: [6, 30, 54, 78],
    18: [6, 30, 56, 82],
    19: [6, 30, 58, 86],
    20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94],
    22: [6, 26, 50, 74, 98],
    23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106],
    25: [6, 32, 58, 84, 110],
    26: [6, 30, 58, 86, 114],
    27: [6, 34, 62, 90, 118],
    28: [6, 26, 50, 74, 98, 122],
    29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130],
    31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138],
    33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146],
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154],
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162],
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170]
}
