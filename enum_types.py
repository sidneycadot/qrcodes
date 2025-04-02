"""Enumeration types used for QR code generation."""

from enum import IntEnum


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
