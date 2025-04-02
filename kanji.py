"""Support for Kanji character encoding.

This implements the encoding algorithm as described in Section 7.4.6 of ISO/IEC 18004:2015(E).
"""

from typing import Optional


def kanji_character_value(c: str) -> Optional[int]:
    """Give the encoding of a character as a 13-bit integer value."""

    if len(c) != 1:
        raise ValueError("Expected a single character.")

    try:
        encoded_character = c.encode('shift-jis')
    except UnicodeEncodeError:
        # The given character is unrepresentable in the shift-jis encoding.
        return None

    value = int.from_bytes(encoded_character, byteorder='big')
    if 0x8140 <= value <= 0x9ffc:
        value -= 0x8140
    elif 0xe040 <= value <= 0xebbf:
        value -= 0xc140
    else:
        return None

    msb = value // 256
    lsb = value % 256
    value = msb * 0xc0 + lsb

    return value
