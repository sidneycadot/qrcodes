"""QR code data encoder.

The data payload of QR codes consists of a bitstream containing typed sequences as described in the standard.

Each type sequence starts with a 4-bit indicator.

Four sequence types encode string data; they are followed by a character count, and finally the character data:

0001 Numeric data;      alphabet is any of the 10 characters "0123456789".
0010 Alphanumeric data; alphabet is any of the 45 characters "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:".
0100 Byte data;         alphabet is 8-bit bytes, normally interpreted as UTF-8 by phones.
1000 Kanji data;        alphabet is Kanji characters encoded in 13 bits each.

The message is ended by a four-bit terminator sequence (if space allows). It doesn't have any follow-up bits.

0000 terminator symbol; This should be the last typed sequence. It may be omitted if the QR code symbol
                        doesn't have space for it.
"""

from enum import Enum
from typing import Optional

from .enum_types import EncodingVariant
from .kanji_encode import kanji_character_value


class Encoding(Enum):
    NUMERIC = 1
    ALPHANUMERIC = 2
    BYTES = 3
    KANJI = 4


# Map of numeric characters to their integer representation.
numeric_characters = "0123456789"
numeric_character_map = dict((c, index) for (index, c) in enumerate(numeric_characters))

# Map of alphanumeric characters to their integer representation.
alphanumeric_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
alphanumeric_character_map = dict((c, index) for (index, c) in enumerate(alphanumeric_characters))


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
        """Append unsigned integer value to the encoded bits."""
        if not (numbits > 0):
            raise ValueError("Number of bits must be positive.")

        if not (0 <= value < (1 << numbits)):
            raise ValueError("The value passed cannot be represented in the number of bits available.")

        mask = 1 << (numbits - 1)
        while mask != 0:
            bit = 1 if (value & mask) != 0 else 0
            self.bits.append(bit)
            mask >>= 1

    def append_structured_append_marker(self, index: int, count: int, parity_data: int) -> None:
        """Append Structured Append marker."""

        if not (0 <= index <= 15):
            raise ValueError()

        if not (1 <= count <= 16):
            raise ValueError()

        if not (0 <= parity_data <= 255):
            raise ValueError()

        # Append the Structured Append Marker intro.
        self.append_integer_value(0b0011, 4)

        # Append the index.
        self.append_integer_value(index, 4)

        # Append the count, offset by one.
        self.append_integer_value(count - 1, 4)

        # Append the parity data (content XOR checksum).
        self.append_integer_value(parity_data, 8)

    def append_eci_designator(self, value: int) -> None:
        """Append Extended Channel Interpretation (ECI) block."""

        if not (0 <= value <= 999999):
            raise ValueError(f"Bad ECI designator value ({value}).")

        # Append the ECI designator intro.
        self.append_integer_value(0b0111, 4)

        # Append the ECI designator value.
        if value <= 127:
            self.append_integer_value(value, 8)
        elif value <= 16383:
            self.append_integer_value(0x8000 | value, 16)
        else:
            self.append_integer_value(0xc00000 | value, 24)

    def append_numeric_mode_block(self, s: str) -> None:

        # Verify that all characters in the string can be represented as numeric characters.
        if not all(c in numeric_character_map for c in s):
            raise ValueError("Not all characters can be represented in numeric mode.")

        # Verify that it is possible to represent the character count.
        if not (len(s) < (1 << self.numeric_mode_count_bits)):
            raise ValueError("Numeric string too long.")

        # Append the numeric mode block intro.
        self.append_integer_value(0b0001, 4)

        # Append the numeric mode block character count.
        self.append_integer_value(len(s), self.numeric_mode_count_bits)

        # Append the numeric character data, in chunks of 1, 2, or 3 characters.
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
            raise ValueError("Not all characters can be represented in alphanumeric mode.")

        # Verify that it is possible to represent the character count.
        if not (len(s) < (1 << self.alphanumeric_mode_count_bits)):
            raise ValueError("Alphanumeric string too long.")

        # Append the alphanumeric mode block intro.
        self.append_integer_value(0b0010, 4)

        # Append the alphanumeric mode block character count.
        self.append_integer_value(len(s), self.alphanumeric_mode_count_bits)

        # Append the alphanumeric character data, in chunks of 1 or 2 characters.
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
                raise ValueError("Not all characters can be represented in kanji mode.")
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

    def get_words(self, number_of_data_codewords: int) -> Optional[list[int]]:
        """Convert the DataEncoder's data bits to a list of 8-bit words for further processing.

        First, a check is made to see if the data bits currently stored in the DataEncoder
        will fit in the 'number_of_data_codewords' specified. If not, None is returned.

        Next, a number of zero padding bits is determined. This includes the four-bit terminator
        (if there is room for it) and padding bits to get the total number of bits up to a multiple
        of eight bits.

        Next, the bits are converted to 8-bit words.

        Finally, two alternating words (0xec, 0x11) are added as world-level padding, to pad
        the word list to contain 'number_of_data_codewords' words, if necessary.

        The resulting list of 8-bit words is returned.
        """

        number_of_data_encoding_bits = len(self.bits)
        number_of_data_bits_available = number_of_data_codewords * 8

        if number_of_data_encoding_bits > number_of_data_bits_available:
            return None  # The data cannot fit, even without a terminator.

        # The Standard prescribes a terminator pattern consisting of four zero-bits,
        # followed by padding zero-bits to bring the number of bits to a multiple of 8.
        # However, if there is no room for the terminator, the Standard says the
        # terminator pattern can be omitted.

        slack = number_of_data_bits_available - number_of_data_encoding_bits

        zero_padding_bits = min(slack, (slack - 4) % 8 + 4)

        # Convert bits, including zero padding bits, to words.

        assert (len(self.bits) + zero_padding_bits) % 8 == 0

        words = []

        mask = 0b10000000
        value = 0
        for bit in self.bits + bytes(zero_padding_bits):
            if bit != 0:
                value |= mask

            if mask == 0b00000001:
                words.append(value)
                value = 0
                mask = 0b10000000
            else:
                mask >>= 1

        # Append padding to data to fill up the QR code data capacity by adding the words
        # (0b11101100, 0b00010001) repeatedly.

        pad_word = 0b11101100
        while len(words) != number_of_data_codewords:
            words.append(pad_word)
            pad_word ^= 0b11111101

        return words
