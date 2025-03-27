#! /usr/bin/env -S python3 -B

"""An example encoder for a version 1-M QR Code symbol.
This example uses numeric mode.
"""

import re
from enum import IntEnum
from PIL import Image, ImageDraw

from enum_types import ErrorCorrectionLevel, DataMaskingPattern
from binary_codes import format_information_code_remainder, version_information_code_remainder
from reed_solomon_code import calculate_reed_solomon_polynomial, reed_solomon_code_remainder
from lookup_tables import data_mask_pattern_functions, version_specifications

class ModuleValue(IntEnum):
    QUIET_ZONE_0          = 10
    FINDER_PATTERN_0      = 20
    FINDER_PATTERN_1      = 21
    SEPARATOR_0           = 30
    TIMING_PATTERN_0      = 40
    TIMING_PATTERN_1      = 41
    ALIGNMENT_PATTERN_0   = 50
    ALIGNMENT_PATTERN_1   = 51
    FORMAT_INFORMATION_0  = 60
    FORMAT_INFORMATION_1  = 61
    VERSION_INFORMATION_0 = 70
    VERSION_INFORMATION_1 = 71
    DATA_ERC_0            = 80
    DATA_ERC_1            = 81
    INDETERMINATE         = 99



render_colormap = {
    ModuleValue.QUIET_ZONE_0          : '#ffffff',
    ModuleValue.FINDER_PATTERN_0      : '#ffffff',
    ModuleValue.FINDER_PATTERN_1      : '#000000',
    ModuleValue.SEPARATOR_0           : '#ffffff',
    ModuleValue.TIMING_PATTERN_0      : '#ffffff',
    ModuleValue.TIMING_PATTERN_1      : '#000000',
    ModuleValue.ALIGNMENT_PATTERN_0   : '#ffffff',
    ModuleValue.ALIGNMENT_PATTERN_1   : '#000000',
    ModuleValue.FORMAT_INFORMATION_0  : '#ffffff',
    ModuleValue.FORMAT_INFORMATION_1  : '#000000',
    ModuleValue.VERSION_INFORMATION_0 : '#ffffff',
    ModuleValue.VERSION_INFORMATION_1 : '#000000',
    ModuleValue.DATA_ERC_0            : '#ffffff',
    ModuleValue.DATA_ERC_1            : '#000000',
    ModuleValue.INDETERMINATE         : '#ff0000'
}


class QRCodeCanvas:

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.modules = bytearray([ModuleValue.INDETERMINATE]) * (width * height)

    def set_module_value(self, i: int, j: int, value: ModuleValue) -> None:
        if not ((0 <= i < self.height) and (0 <= j < self.width)):
            raise ValueError(f"Bad module coordinate (i={i}, j={j}).")
        index = i * self.width + j
        self.modules[index] = value

    def get_module_value(self, i: int, j: int) -> ModuleValue:
        if not ((0 <= i < self.height) and (0 <= j < self.width)):
            raise ValueError(f"Bad module coordinate (i={i}, j={j}).")
        index = i * self.width + j
        return ModuleValue(self.modules[index])

    def render_as_image(self, magnification: int = 1) -> None:
        im = Image.new('RGB', (self.width * magnification, self.height * magnification))
        draw = ImageDraw.Draw(im)

        for i in range(self.height):
            for j in range(self.width):
                value = self.get_module_value(i, j)
                color = render_colormap[value]
                draw.rectangle((j * magnification, i * magnification, (j + 1) * magnification - 1, (i + 1) * magnification - 1), color)

        return im

def get_alignment_positions(version: int) -> list[int]:

    positions = []

    if version > 1:

        num = (version+14) // 7

        first = 6
        last = 21 + 4 * (version - 1) - 7

        delta = last - first
        steps = num - 1

        # Find the smallest even integer greater than or equal to delta / steps.
        # This is the step size of all but the first step.
        stepsize = 0
        while not (stepsize * steps >= delta):
            stepsize += 2

        first_stepsize = delta - (steps - 1) * stepsize

        assert first_stepsize > 0
        assert first_stepsize % 2 == 0

        positions.append(6)
        positions.append(positions[-1] + first_stepsize)
        while len(positions) != num:
            positions.append(positions[-1] + stepsize)

    return positions

class QRCodeDrawer:

    def __init__(self, version: int, include_quiet_zone: bool):

        if not (1 <= version <= 40):
            raise ValueError(f"Bad QR code version: {version}.")

        self.version = version
        self.quiet_zone_margin = 4 if include_quiet_zone else 0
        self.width = 21 + 4 * (version - 1)
        self.height = 21 + 4 * (version - 1)

        canvas_width = self.width + 2 * self.quiet_zone_margin
        canvas_height = self.height + 2 * self.quiet_zone_margin

        self.canvas = QRCodeCanvas(canvas_width, canvas_height)

    def set_module_value(self, i: int, j: int, value: ModuleValue) -> None:
        self.canvas.set_module_value(i + self.quiet_zone_margin, j + self.quiet_zone_margin, value)

    def get_module_value(self, i: int, j: int) -> ModuleValue:
        return self.canvas.get_module_value(i + self.quiet_zone_margin, j + self.quiet_zone_margin)

    def place_quiet_zone(self) -> None:
        for i in range(self.quiet_zone_margin):
            for j in range(self.width + 2 * self.quiet_zone_margin):
                self.set_module_value(i - self.quiet_zone_margin, j - self.quiet_zone_margin, ModuleValue.QUIET_ZONE_0)
                self.set_module_value(i + self.height           , j - self.quiet_zone_margin, ModuleValue.QUIET_ZONE_0)

        for i in range(self.height + 2 * self.quiet_zone_margin):
            for j in range(self.quiet_zone_margin):
                self.set_module_value(i - self.quiet_zone_margin, j - self.quiet_zone_margin, ModuleValue.QUIET_ZONE_0)
                self.set_module_value(i - self.quiet_zone_margin, j + self.width            , ModuleValue.QUIET_ZONE_0)

    def place_finder_pattern(self, i: int, j: int) -> None:
        for di in range(7):
            for dj in range(7):
                flag = di in (0, 6) or dj in (0, 6) or (di in (2, 3, 4) and dj in (2, 3, 4))
                value = ModuleValue.FINDER_PATTERN_1 if flag else ModuleValue.FINDER_PATTERN_0
                self.set_module_value(i + di, j + dj, value)

    def place_finder_patterns(self) -> None:
        # Place the three finder patterns in the top-left, top-right, and bottom-left corners.
        self.place_finder_pattern(0, 0)
        self.place_finder_pattern(0, self.width - 7)
        self.place_finder_pattern(self.height - 7, 0)

    def place_separators(self):
        for k in range(8):
            # Top-left
            self.set_module_value(k, 7, ModuleValue.SEPARATOR_0)
            self.set_module_value(7, k, ModuleValue.SEPARATOR_0)
            # Top-right
            self.set_module_value(k, self.width - 8, ModuleValue.SEPARATOR_0)
            self.set_module_value(7, self.width - 8 + k, ModuleValue.SEPARATOR_0)
            # Bottom-right
            self.set_module_value(self.height - 8 + k, 7, ModuleValue.SEPARATOR_0)
            self.set_module_value(self.height - 8, k, ModuleValue.SEPARATOR_0)

    def place_alignment_pattern(self, i: int, j: int) -> None:
        for di in (-2, -1, 0, +1, +2):
            for dj in (-2, -1, 0, +1, +2):
                flag = di in (-2, +2) or dj in (-2, +2) or (di == 0 and dj == 0)
                value = ModuleValue.ALIGNMENT_PATTERN_1 if flag else ModuleValue.ALIGNMENT_PATTERN_0
                self.set_module_value(i + di, j + dj, value)

    def place_alignment_patterns(self) -> None:

        positions = get_alignment_positions(self.version)
        num = len(positions)

        for v in range(num):
            for h in range(num):
                if (h == 0 and v == 0) or (h == 0 and v == num - 1) or (h == num - 1 and v == 0):
                    continue
                self.place_alignment_pattern(positions[v], positions[h])

    def place_timing_patterns(self):
        # Regular QR code has a horizontal and a vertical timing code.
        for i in range(8, self.height - 8):
            self.set_module_value(i, 6, ModuleValue.TIMING_PATTERN_1 if i % 2 == 0 else ModuleValue.TIMING_PATTERN_0)
        for j in range(8, self.width - 8):
            self.set_module_value(6, j, ModuleValue.TIMING_PATTERN_1 if j % 2 == 0 else ModuleValue.TIMING_PATTERN_0)

    def place_format_information_regions(self, level: ErrorCorrectionLevel, pattern: DataMaskingPattern):

        format_data_bits = (level << 3) | pattern
        format_ecc_bits = format_information_code_remainder(format_data_bits)

        format_bits = (format_data_bits << 10) | format_ecc_bits

        # XOR the result with a fixed pattern.
        format_bits ^= 0b101010000010010

        W = self.width
        H = self.height

        copies = [
            [(0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (7, 8), (8, 8), (8, 7), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1), (8, 0)],
            [(8, W-1), (8, W-2), (8, W-3), (8, W-4), (8, W-5), (8, W-6), (8, W-7), (8, W-8), (H-7, 8), (H-6, 8), (H-5, 8), (H-4, 8), (H-3, 8), (H-2, 8), (H-1, 8)]
        ]

        # Set the single module that is always on.
        self.set_module_value(H-8, 8, ModuleValue.FORMAT_INFORMATION_1)

        for k in range(15):
            fbit = ((format_bits >> k) & 1) != 0
            for copy in copies:
                (i, j) = copy[k]
                self.set_module_value(i, j, ModuleValue.FORMAT_INFORMATION_1 if fbit else ModuleValue.FORMAT_INFORMATION_0)

    def place_version_information_regions(self):
        if self.version >= 7:

            version_bits = version_information_code_remainder(self.version) | (self.version << 12)

            for k in range(18):
                vbit = (version_bits >> k) & 1 == 0
                self.set_module_value(self.height - 11 + k % 3, k // 3, ModuleValue.VERSION_INFORMATION_1 if vbit else ModuleValue.VERSION_INFORMATION_0)
                self.set_module_value(k // 3, self.width - 11 + k % 3, ModuleValue.VERSION_INFORMATION_1 if vbit else ModuleValue.VERSION_INFORMATION_0)

    def get_indeterminate_positions(self):
        positions = []
        assert self.width % 2 == 1
        for h_outer in range((self.width - 1) // 2):
            # Note: the last three h_outer walks are to the left of the vertical timing pattern, the
            # other ones are to the right of the vertical timing pattern.
            for v in range(self.height):
                i = (self.height - 1 - v) if h_outer % 2 == 0 else v
                for h_inner in range(2):
                    h = h_outer * 2 + h_inner
                    j = (self.width - 1 - h)
                    if j <= 6: # Skip vertical timing pattern.
                        j -= 1
                    value = self.get_module_value(i, j)
                    if value == ModuleValue.INDETERMINATE:
                        position = (i, j)
                        positions.append(position)
        return positions

    def apply_data_masking_pattern(self, pattern, positions):
        pattern_function = data_mask_pattern_functions[pattern]
        for (i, j) in positions:
            value = self.get_module_value(i, j)
            assert value in (ModuleValue.DATA_ERC_0, ModuleValue.DATA_ERC_1)
            # Invert if the pattern condition is True
            if pattern_function(i, j):
                value = ModuleValue.DATA_ERC_1 if value == ModuleValue.DATA_ERC_0 else ModuleValue.DATA_ERC_0
                self.set_module_value(i, j, value)

    def render_as_image(self, magnification: int = 1) -> None:
        return self.canvas.render_as_image(magnification)

    def count_indeterminate(self):
        count = 0
        for i in range(self.height):
            for j in range(self.width):
                value = self.get_module_value2(i, j)
                if value == ModuleValue.INDETERMINATE:
                    count += 1
        return count


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

class DataEncoder:

    def __init__(self, version: int):

        if not (1 <= version <= 40):
            raise ValueError(f"Bad QR code version: {version}.")

        self.version = version
        self.bits = []

    def append_bits(self, s: str) -> None:
        for c in s:
            if c == '0':
                self.bits.append(0)
            elif c == '1':
                self.bits.append(1)
            else:
                raise ValueError()

    def append_integer_value(self, value: int, numbits: int) -> None:
        mask = 1 << (numbits - 1)
        while mask != 0:
            bit = 1 if (value & mask) != 0 else 0
            self.bits.append(bit)
            mask >>= 1

    def append_numeric_mode_block(self, s: str) -> None:
        if re.fullmatch("[0-9]*", s) is None:
            raise ValueError()

        self.append_integer_value(1, 4)  # Numeric mode block follows.

        count_bits = numeric_mode_character_count_bits(self.version)

        self.append_integer_value(len(s), count_bits)

        idx = 0
        while idx != len(s):
            blocksize = min(3, len(s) - idx)
            if blocksize == 1:
                numbits = 4
            elif blocksize == 2:
                numbits = 7
            elif blocksize == 3:
                numbits = 10
            else:
                raise RuntimeError()
            self.append_integer_value(int(s[idx:idx + blocksize]), numbits)
            idx += blocksize

    def append_alphanumeric_mode_block(self, s: str) -> None:
        raise NotImplementedError()

    def append_byte_mode_block(self, b: bytes) -> None:

        self.append_integer_value(4, 4)  # Byte mode block follows.

        count_bits = byte_mode_character_count_bits(self.version)

        self.append_integer_value(len(b), count_bits)

        for value in b:
            self.append_integer_value(value, 8)

    def append_kanji_mode_block(self, s: str) -> None:
        raise NotImplementedError()

    def append_terminator(self):
        self.append_integer_value(0, 4)

    def append_padding_bits(self):
        while len(self.bits) % 8 != 0:
            self.bits.append(0)

    def get_words(self):

        if len(self.bits) % 8 != 0:
            raise RuntimeError("Number of bits is not a multiple of 8.")

        idx = 0
        words = []
        while idx != len(self.bits):
            word = int("".join(map(str, self.bits[idx:idx+8])), 2)
            words.append(word)
            idx += 8

        return words


def main():

    # This follows appendix I of the standard.

    # We want to encode the data string "01234567" in numeric mode.
    # Numeric mode data, where each symbol is a decimal digit 0-9, works by encoding groups of 3
    # digits (0..999) as a 10-bit number. The final group, if it is 2 digits, will be converted as 7 bits. If it is 1 digit: 4 bits.

    # 012    0000001100   (10 bits, value 12)
    # 345    0101011001   (10 bits, value 345)
    # 67     1000011      (7 bits, value 67)

    # Character count indicator is 10 bits for version 1-M.
    #
    # The character count is 8: 0000001000
    #
    # We also add a data-terminator to the end (4 bits: 0000).
    #
    # So we arrive at: 0001-0000001000-0000001100-0101011001-1000011-0000
    #
    # Which is:
    #
    # 000100000010000000001100010101100110000110000
    #
    # Divide in 8-bit groups, adding padding zeros to fill out a multiple of 8 bits.
    # We end up with 6 bytes.
    #
    # 00010000 00100000 00001100 01010110 01100001 10000000
    #
    # We add PAD codewords. For version 1-M, 16 data codewords must be present, so we need to add 10 Pad codewords.
    # Padding codewords are alternatingly 11101100 / 00010001.
    #
    # This yields the following 16 codewords:
    #
    # 00010000 00100000 00001100 01010110 01100001 10000000 11101100 00010001
    # 11101100 00010001 11101100 00010001 11101100 00010001 11101100 00010001
    #
    # Now we add 10 Reed-Solomon codewords, for error protection, ending up with 26 codewords:
    #
    # 00010000 00100000 00001100 01010110 01100001 10000000 11101100 00010001
    # 11101100 00010001 11101100 00010001 11101100 00010001 11101100 00010001
    # 10100101 00100100 11010100 11000001 11101101 00110110 11000111 10000111
    # 00101100 01010101
    #
    # No interleaving is required here (what is interleaving ???)
    #
    # Place finder patterns.
    # Place separators.
    # Place timing patterns.

    magnification = 1

    version = 5
    level = ErrorCorrectionLevel.L

    version_specification = version_specifications[(version, level)]

    block_specification = version_specification.block_specification

    for pattern in DataMaskingPattern:

        qr = QRCodeDrawer(version, True)
        qr.place_quiet_zone()
        qr.place_finder_patterns()
        qr.place_separators()
        qr.place_timing_patterns()
        qr.place_alignment_patterns()
        qr.place_format_information_regions(level, pattern)
        qr.place_version_information_regions()

        de = DataEncoder(version)

        #de.append_numeric_mode_block("01234567")
        #de.append_byte_mode_block('⛄ Snowman'.encode())
        #de.append_byte_mode_block('Hallo Petra!'.encode())
        #de.append_byte_mode_block(b"http://www.jigsaw.nl")
        de.append_byte_mode_block(b"https://www.jigsaw.nl/")
        de.append_terminator()
        de.append_padding_bits()

        data = de.get_words()

        print("unpadded data length:", len(data))

        assert len(data) <= version_specification.total_number_of_codewords - version_specification.number_of_error_correcting_codewords

        pad_word = 0b11101100
        while len(data) != version_specification.total_number_of_codewords - version_specification.number_of_error_correcting_codewords:
            data.append(pad_word)
            pad_word ^= 0b11111101

        datablocks = []

        idx = 0
        for (count, (code_c, code_k, code_r)) in version_specification.block_specification:
            poly = calculate_reed_solomon_polynomial(code_c - code_k, strip=True)
            for rep in range(count):
                # Encode 'code_k' words to 'code_c' words, by adding error correction.

                datablock = data[idx:idx+code_k]
                idx += code_k
                erc = reed_solomon_code_remainder(datablock, poly)
                datablock.extend(erc)
                datablocks.append(datablock)

        assert idx == version_specification.total_number_of_codewords - version_specification.number_of_error_correcting_codewords

        assert sum(len(db) for db in datablocks) == version_specification.total_number_of_codewords

        data = []
        k = 0
        while len(data) != version_specification.total_number_of_codewords:
            if len(datablocks[k]) != 0:
                data.append(datablocks[k].pop(0))
            k = (k + 1) % len(datablocks)

        positions = qr.get_indeterminate_positions()

        databits = []
        for d in data:
            mask = 0x80
            while mask != 0:
                bit = (d & mask) != 0
                databits.append(bit)
                mask >>= 1

        assert len(databits) <= len(positions)

        # Add padding.
        while len(databits) < len(positions):
            databits.append(0)

        print("num positions:", len(positions))
        print("num databits:", len(databits))

        assert len(positions) == len(databits)

        for (position, databit) in zip(positions, databits):
            qr.set_module_value(*position, ModuleValue.DATA_ERC_1 if databit else ModuleValue.DATA_ERC_0)

        qr.apply_data_masking_pattern(pattern, positions)

        im = qr.render_as_image(magnification)

        filename = f"v{version}_{pattern}.png"
        print(f"Saving {filename} ...")
        im.save(filename)


if __name__ == "__main__":
    main()
