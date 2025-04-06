"""Enumeration types used for QR code generation."""

from __future__ import annotations

from enum import Enum, IntEnum


class DataMaskingPattern(IntEnum):
    PATTERN0 = 0b000
    PATTERN1 = 0b001
    PATTERN2 = 0b010
    PATTERN3 = 0b011
    PATTERN4 = 0b100
    PATTERN5 = 0b101
    PATTERN6 = 0b110
    PATTERN7 = 0b111


class ErrorCorrectionLevel(IntEnum):
    L = 0b01  # Allows recovery of  7% of bad modules.
    M = 0b00  # Allows recovery of 15% of bad modules.
    Q = 0b11  # Allows recovery of 25% of bad modules.
    H = 0b10  # Allows recovery of 30% of bad modules.


class EncodingVariant(Enum):
    SMALL = 1   # versions 1 .. 9
    MEDIUM = 2  # versions 10 .. 26
    LARGE = 3   # versions 27 .. 40

    @staticmethod
    def from_version(version: int) -> EncodingVariant:
        if not (1 <= version <= 40):
            raise ValueError("Bad QR code version.")
        if version <= 9:
            return EncodingVariant.SMALL
        elif version <= 26:
            return EncodingVariant.MEDIUM
        else:
            return EncodingVariant.LARGE
