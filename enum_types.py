"""Enumeration types used for QR code generation."""

from enum import Enum, IntEnum


class DataMaskingPattern(IntEnum):
    Pattern0 = 0b000
    Pattern1 = 0b001
    Pattern2 = 0b010
    Pattern3 = 0b011
    Pattern4 = 0b100
    Pattern5 = 0b101
    Pattern6 = 0b110
    Pattern7 = 0b111


class ErrorCorrectionLevel(IntEnum):
    L = 0b01  # Allows recovery of  7% of bad modules.
    M = 0b00  # Allows recovery of 15% of bad modules.
    Q = 0b11  # Allows recovery of 25% of bad modules.
    H = 0b10  # Allows recovery of 30% of bad modules.


class EncodingVariant(Enum):
    SMALL  = 1  # versions 1 .. 9
    MEDIUM = 2  # versions 10 .. 26
    LARGE  = 3  # versions 27 .. 40
