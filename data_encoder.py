"""QR code data encoder.

The data payload of QR codes consists of a bitstream containing typed sequences as described in the standard.

Each sequence starts with a 4-bit indicator. It is followed by a character count, and finally the character data.

0000 terminator symbol. This should be the last typed sequence. 

0001 Numeric data;      alphabet is any of the 10 characters "0123456789".
0010 Alphanumeric data; alphabet is any of the 45 characters "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:".
0100 Byte data;         alphabet is 8-bit bytes, normally interpreted as UTF-8 by phones.
1000 Kanji data;        alphabet is Kanji characters encoded in 13 bits each.
"""

from enum import Enum

from enum_types import EncodingVariant
from kanji import kanji_character_value


class Encoding(Enum):
    NUMERIC      = 0b0001
    ALPHANUMERIC = 0b0010
    BYTES        = 0b0100
    KANJI        = 0b1000

# Map of numeric characters to their integer representation.
numeric_character_map = dict(map(reversed, enumerate("0123456789")))

# Map of alphanumeric characters to their integer representation.
alphanumeric_character_map = dict(map(reversed, enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")))


class DataEncoder:

    def __init__(self, variant: EncodingVariant):

        assert isinstance(variant, EncodingVariant)

        if variant == EncodingVariant.SMALL:
            self.numeric_mode_count_bits = 10
            self.alphanumeric_mode_count_bits = 9
            self.byte_mode_count_bits = 8
            self.kanji_mode_count_bits = 8
        elif variant == EncodingVariant.MEDIUM:
            self.numeric_mode_count_bits = 12
            self.alphanumeric_mode_count_bits = 11
            self.byte_mode_count_bits = 16
            self.kanji_mode_count_bits = 10
        else:
            self.numeric_mode_count_bits = 14
            self.alphanumeric_mode_count_bits = 13
            self.byte_mode_count_bits = 16
            self.kanji_mode_count_bits = 12

        self.bits = bytearray()

    def append_integer_value(self, value: int, numbits: int) -> None:

        if not (numbits > 0):
            raise ValueError("Number of bits must be positive.")

        if not (0 <= value < (1 << numbits)):
            raise ValueError("The value passed cannot be represented in the number of bits given.")

        mask = 1 << (numbits - 1)
        while mask != 0:
            bit = 1 if (value & mask) != 0 else 0
            self.bits.append(bit)
            mask >>= 1

    def append_numeric_mode_block(self, s: str) -> None:

        # Verify that all characters in the string can be represented as numeric characters.
        if not all(c in numeric_character_map for c in s):
            raise ValueError("A string was passed containing characters that cannot be represented in numeric mode.")

        # Verify that it is possible to represent the character count.
        if not (len(s) < (1 << self.numeric_mode_count_bits)):
            raise ValueError("Numeric string too long.")

        # Append the numeric mode block intro.
        self.append_integer_value(0b0001, 4)

        # Append the numeric mode block character count.
        self.append_integer_value(len(s), self.numeric_mode_count_bits)

        # Append the numeric character data.
        idx = 0
        while idx != len(s):
            chunk_size = min(3, len(s) - idx)
            numbits = 1 + 3 * chunk_size

            chunk_value = 0
            while chunk_size != 0:
                character_value = numeric_character_map[s[idx]]
                chunk_value = chunk_value * 10 + character_value
                idx += 1
                chunk_size -= 1

            self.append_integer_value(chunk_value, numbits)

    def append_alphanumeric_mode_block(self, s: str) -> None:

        # Verify that all characters in the string can be represented as alphanumeric characters.
        if not all(c in alphanumeric_character_map for c in s):
            raise ValueError("A string was passed containing characters that cannot be represented in alphanumeric mode.")

        # Verify that it is possible to represent the character count.
        if not (len(s) < (1 << self.alphanumeric_mode_count_bits)):
            raise ValueError("Alphanumeric string too long.")

        # Append the alphanumeric mode block intro.
        self.append_integer_value(0b0010, 4)

        # Append the alphanumeric mode block character count.
        self.append_integer_value(len(s), self.alphanumeric_mode_count_bits)

        # Append the alphanumeric character data.
        idx = 0
        while idx != len(s):
            chunk_size = min(2, len(s) - idx)
            numbits = 1 + 5 * chunk_size

            chunk_value = 0
            while chunk_size != 0:
                character_value = alphanumeric_character_map[s[idx]]
                chunk_value = chunk_value * 45 + character_value
                idx += 1
                chunk_size -= 1

            self.append_integer_value(chunk_value, numbits)

    def append_byte_mode_block(self, b: bytes) -> None:

        # Verify that it is possible to represent the byte count.
        if not (len(b) < (1 << self.byte_mode_count_bits)):
            raise ValueError("Byte sequence too long.")

        # Append the byte mode block intro.
        self.append_integer_value(0b0100, 4)

        # Append the byte mode block character count.
        self.append_integer_value(len(b), self.byte_mode_count_bits)

        # Append the byte data.
        for value in b:
            self.append_integer_value(value, 8)

    def append_kanji_mode_block(self, s: str) -> None:

        values = []
        for c in s:
            value = kanji_character_value(c)
            if value is None:
                raise ValueError("A string was passed containing characters that cannot be represented in kanji mode.")
            values.append(value)

        if not (len(values) < (1 << self.kanji_mode_count_bits)):
            raise ValueError("Kanji string too long.")

        # Append the kanji mode block intro.
        self.append_integer_value(0b1000, 4)

        # Append the kanji mode block character count.
        self.append_integer_value(len(values), self.kanji_mode_count_bits)

        # Append the kanji character data.
        for value in values:
            self.append_integer_value(value, 13)

    def append_eci_designator(self, value: int) -> None:
        """Append Extended Channel Interpretation (ECI) block."""

        if not (0 <= value <= 999999):
            raise ValueError("Bad ECI designator.")

        # Append the ECI designator intro.
        self.append_integer_value(0b0111, 4)

        # Append the ECI  designator value.
        if value <= 127:
            self.append_integer_value(value, 8)
        elif value <= 16383:
            self.append_integer_value(0x8000 | value, 16)
        else:
            self.append_integer_value(0xc00000 | value, 24)

    def append_terminator(self) -> None:
        # Append the terminator pattern.
        self.append_integer_value(0b0000, 4)

    def append_padding_bits(self) -> None:
        # Append zero bits as needed to make the number of bits a multiple of 8 bits.
        modulo = len(self.bits) % 8
        if modulo != 0:
            self.append_integer_value(0, 8 - modulo)

    def get_words(self) -> list[int]:

        if len(self.bits) % 8 != 0:
            raise RuntimeError("Number of bits is not a multiple of 8.")

        words = []

        mask = 0b10000000
        value = 0
        for bit in self.bits:
            if bit != 0:
                value |= mask

            if mask == 0b00000001:
                words.append(value)
                value = 0
                mask = 0b10000000
            else:
                mask >>= 1
    
        return words
