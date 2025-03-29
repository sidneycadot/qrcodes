"""QR code data encoder.

The data payload of QR codes consists of a bitstream containing typed sequences as described in the standard.

Each sequence starts with a 4-bit indicator. It is often followed by a character count, and finally the character data.

0000 terminator symbol. This should be the last typed sequence. 

0001 Numeric data; alphabet is any of the 10 characters "0123456789".
0010 Alphanumeric data; alphabet is any of the 45 characters "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:".
0100 Byte data
1000 Kanji data

"""

numeric_character_map = {
    '0' : 0,
    '1' : 1,
    '2' : 2,
    '3' : 3,
    '4' : 4,
    '5' : 5,
    '6' : 6,
    '7' : 7,
    '8' : 8,
    '9' : 9
}

alphanumeric_character_map = {
    '0' :  0,
    '1' :  1,
    '2' :  2,
    '3' :  3,
    '4' :  4,
    '5' :  5,
    '6' :  6,
    '7' :  7,
    '8' :  8,
    '9' :  9,
    'A' : 10,
    'B' : 11,
    'C' : 12,
    'D' : 13,
    'E' : 14,
    'F' : 15,
    'G' : 16,
    'H' : 17,
    'I' : 18,
    'J' : 19,
    'K' : 20,
    'L' : 21,
    'M' : 22,
    'N' : 23,
    'O' : 24,
    'P' : 25,
    'Q' : 26,
    'R' : 27,
    'S' : 28,
    'T' : 29,
    'U' : 30,
    'V' : 31,
    'W' : 32,
    'X' : 33,
    'Y' : 34,
    'Z' : 35,
    ' ' : 36,
    '$' : 37,
    '%' : 38,
    '*' : 39,
    '+' : 40,
    '-' : 41,
    '.' : 42,
    '/' : 43,
    ':' : 44
}

def numeric_mode_character_count_bits(version: int) -> int:
    if (1 <= version <= 9):
        return 10
    if (10 <= version <= 26):
        return 12
    if (27 <= version <= 40):
        return 14
    raise ValueError()

def alphanumeric_mode_character_count_bits(version: int) -> int:
    if (1 <= version <= 9):
        return 9
    if (10 <= version <= 26):
        return 11
    if (27 <= version <= 40):
        return 13
    raise ValueError()

def byte_mode_character_count_bits(version: int) -> int:
    if (1 <= version <= 9):
        return 8
    if (10 <= version <= 26):
        return 16
    if (27 <= version <= 40):
        return 16
    raise ValueError()

def kanji_mode_character_count_bits(version: int) -> int:
    if (1 <= version <= 9):
        return 8
    if (10 <= version <= 26):
        return 10
    if (27 <= version <= 40):
        return 12
    raise ValueError()


class DataEncoder:

    def __init__(self, version: int):

        if not (1 <= version <= 40):
            raise ValueError(f"Bad QR code version: {version}.")

        self.version = version
        self.bits = bytearray()

    def append_integer_value(self, value: int, numbits: int) -> None:

        assert 0 <= value < (1 << numbits)

        mask = 1 << (numbits - 1)
        while mask != 0:
            bit = 1 if (value & mask) != 0 else 0
            self.bits.append(bit)
            mask >>= 1

    def append_numeric_mode_block(self, s: str) -> None:

        # Verify that all characters can be represented as numeric characters.
        if not all(c in numeric_character_map for c in s):
            raise ValueError()

        # Append the numeric mode block intro.
        self.append_integer_value(0b0001, 4)

        # Append the numeric mode block character count.
        count_bits = numeric_mode_character_count_bits(self.version)
        self.append_integer_value(len(s), count_bits)

        # Append the numeric character data.
        idx = 0
        while idx != len(s):
            blocksize = min(3, len(s) - idx)
            numbits = 1 + 3 * blocksize

            chunk_value = 0
            while blocksize != 0:
                character_value = numeric_character_map[s[idx]]
                chunk_value = chunk_value * 10 + character_value
                idx += 1
                blocksize -= 1

            self.append_integer_value(chunk_value, numbits)

    def append_alphanumeric_mode_block(self, s: str) -> None:

        # Verify that all characters can be represented as alphanumeric characters.
        if not all(c in alphanumeric_character_map for c in s):
            raise ValueError()

        # Append the alphanumeric mode block intro.
        self.append_integer_value(0b0010, 4)

        # Append the alphanumeric mode block character count.
        count_bits = alphanumeric_mode_character_count_bits(self.version)
        self.append_integer_value(len(s), count_bits)

        # Append the alphanumeric character data.
        idx = 0
        while idx != len(s):
            blocksize = min(2, len(s) - idx)
            numbits = 1 + 5 * blocksize

            chunk_value = 0
            while blocksize != 0:
                character_value = alphanumeric_character_map[s[idx]]
                chunk_value = chunk_value * 45 + character_value
                idx += 1
                blocksize -= 1

            self.append_integer_value(chunk_value, numbits)

    def append_byte_mode_block(self, b: bytes) -> None:

        # Append the byte mode block intro.
        self.append_integer_value(0b0100, 4)

        # Append the byte mode block character count.
        count_bits = byte_mode_character_count_bits(self.version)
        self.append_integer_value(len(b), count_bits)

        # Append the byte data.
        for value in b:
            self.append_integer_value(value, 8)

    def append_kanji_mode_block(self, s: str) -> None:

        # Append the kanji mode block intro.
        self.append_integer_value(0b1000, 4)

        # Append the kanji mode block character count.
        count_bits = kanji_mode_character_count_bits(self.version)
        self.append_integer_value(len(s), count_bits)

        # Append the kanji character data (not yet implemented).
        for c in s:
            value = int.from_bytes(c.encode('shift-jis'), byteorder='big')
            if (0x8140 <= value <= 0x9ffc):
                value -= 0x8140
            elif (0xe040 <= value <= 0xebbf):
                value -= 0xc140
            else:
                raise ValueError()

            msb = value // 256
            lsb = value % 256
            value = msb * 0xc0 + lsb

            assert 0 <= value <= 8191

            self.append_integer_value(value, 13)

    def append_eci_designator(self, value: int) -> None:
        if (0 <= value <= 127):
            self.append_integer_value(value, 8)
        elif (0 <= value <= 16383):
            self.append_integer_value(0x8000 | value, 16)
        elif (0 <= value <= 999999):
            self.append_integer_value(0xc00000 | value, 24)
        else:
            raise ValueError()

    def append_terminator(self) -> None:
        # Append the terminator pattern.
        self.append_integer_value(0b0000, 4)

    def append_padding_bits(self) -> None:
        # Append zero bits as needed to make the number of bits a multiple of 8 bits.
        while len(self.bits) % 8 != 0:
            self.bits.append(0)

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

