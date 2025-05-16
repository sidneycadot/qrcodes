"""Enumeration types used for QR code generation."""

from __future__ import annotations

from enum import Enum

class CharacterEncodingType(Enum):
    """The four types of characters encoding used in QR codes."""
    NUMERIC      = 101
    ALPHANUMERIC = 102
    BYTES        = 103
    KANJI        = 104


class DataMaskPattern(Enum):
    """The eight types of XOR masks to scramble QR code symbols."""
    PATTERN0 = 200
    PATTERN1 = 201
    PATTERN2 = 202
    PATTERN3 = 203
    PATTERN4 = 204
    PATTERN5 = 205
    PATTERN6 = 206
    PATTERN7 = 207


class ErrorCorrectionLevel(Enum):
    """The four levels of error correction used in QR codes."""
    L = 301  # Allows recovery of  7% of bad modules.
    M = 302  # Allows recovery of 15% of bad modules.
    Q = 303  # Allows recovery of 25% of bad modules.
    H = 304  # Allows recovery of 30% of bad modules.


class EncodingVariant(Enum):
    """The three variants of data encoding used in QR codes."""
    SMALL  = 401  # versions 1 .. 9
    MEDIUM = 402  # versions 10 .. 26
    LARGE  = 403  # versions 27 .. 40

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
