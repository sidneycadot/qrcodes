"""QR code canvaa and canvas drawing functionality."""

from enum import IntEnum
from typing import Optional

from enum_types import ErrorCorrectionLevel, DataMaskingPattern
from binary_codes import format_information_code_remainder, version_information_code_remainder
from reed_solomon_code import calculate_reed_solomon_polynomial, reed_solomon_code_remainder
from lookup_tables import alignment_pattern_positions, data_mask_pattern_functions, version_specifications
from data_encoder import DataEncoder


class QRCodeCapacityError(Exception):
    pass


class ModuleValue(IntEnum):
    QUIET_ZONE_0                      = 10
    FINDER_PATTERN_0                  = 20
    FINDER_PATTERN_1                  = 21
    SEPARATOR_0                       = 30
    TIMING_PATTERN_0                  = 40
    TIMING_PATTERN_1                  = 41
    ALIGNMENT_PATTERN_0               = 50
    ALIGNMENT_PATTERN_1               = 51
    FORMAT_INFORMATION_0              = 60
    FORMAT_INFORMATION_1              = 61
    FORMAT_INFORMATION_INDETERMINATE  = 69  # Placeholder, to be filled in later.
    VERSION_INFORMATION_0             = 70
    VERSION_INFORMATION_1             = 71
    VERSION_INFORMATION_INDETERMINATE = 79  # Placeholder, to be filled in later.
    DATA_ERC_0                        = 80
    DATA_ERC_1                        = 81
    INDETERMINATE                     = 99


class QRCodeCanvas:
    """A QRCodeCanvas defines a rectangular array of modules (pixels).

    The QR codes defined by the standard are square, so the width is equal to the height.
    """

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


def enumerate_bits(value: int, num_bits: int):
    """Enumerate the bits in the unsigned integer value as booleans, going from the MSB down to the LSB."""
    assert 0 <= value < (1 << num_bits)
    mask = 1 << (num_bits - 1)
    while mask != 0:
        yield (value & mask) != 0
        mask >>= 1


class QRCodeDrawer:
    """A QRCodeDrawer knows how to draw the different areas in a QR code."""
    def __init__(self, version: int, include_quiet_zone: bool):

        if not (1 <= version <= 40):
            raise ValueError(f"Bad QR code version: {version}.")

        self.version = version
        self.quiet_zone_margin = 4 if include_quiet_zone else 0
        self.width = 17 + 4 * version
        self.height = 17 + 4 * version

        self.format_bit_position_lists = [
            [(8, 0), (self.height - 1, 8)],  # MSB positions
            [(8, 1), (self.height - 2, 8)],
            [(8, 2), (self.height - 3, 8)],
            [(8, 3), (self.height - 4, 8)],
            [(8, 4), (self.height - 5, 8)],
            [(8, 5), (self.height - 6, 8)],
            [(8, 7), (self.height - 7, 8)],
            [(8, 8), (8, self.width - 8)],
            [(7, 8), (8, self.width - 7)],
            [(5, 8), (8, self.width - 6)],
            [(4, 8), (8, self.width - 5)],
            [(3, 8), (8, self.width - 4)],
            [(2, 8), (8, self.width - 3)],
            [(1, 8), (8, self.width - 2)],
            [(0, 8), (8, self.width - 1)]    # LSB positions
        ]

        self.version_bit_position_lists = [
            [(self.height -  9, 5), (5, self.width -  9)],  # MSB positions
            [(self.height - 10, 5), (5, self.width - 10)],
            [(self.height - 11, 5), (5, self.width - 11)],
            [(self.height -  9, 4), (4, self.width -  9)],
            [(self.height - 10, 4), (4, self.width - 10)],
            [(self.height - 11, 4), (4, self.width - 11)],
            [(self.height -  9, 3), (3, self.width -  9)],
            [(self.height - 10, 3), (3, self.width - 10)],
            [(self.height - 11, 3), (3, self.width - 11)],
            [(self.height -  9, 2), (2, self.width -  9)],
            [(self.height - 10, 2), (2, self.width - 10)],
            [(self.height - 11, 2), (2, self.width - 11)],
            [(self.height -  9, 1), (1, self.width -  9)],
            [(self.height - 10, 1), (1, self.width - 10)],
            [(self.height - 11, 1), (1, self.width - 11)],
            [(self.height -  9, 0), (0, self.width -  9)],
            [(self.height - 10, 0), (0, self.width - 10)],
            [(self.height - 11, 0), (0, self.width - 11)]   # LSB positions
        ]

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

        positions = alignment_pattern_positions[self.version]
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

    def place_format_information_placeholders(self):

        # Place the two format information patterns.
        for format_bit_position_list in self.format_bit_position_lists:
            for (i, j) in format_bit_position_list:
                self.set_module_value(i, j, ModuleValue.FORMAT_INFORMATION_INDETERMINATE)

        # Place the single fixed "dark module" above and to the right of the bottom-left finder pattern (7.9.1).
        self.set_module_value(self.height-8, 8, ModuleValue.FORMAT_INFORMATION_INDETERMINATE)

    def place_format_information_patterns(self, level: ErrorCorrectionLevel, pattern: DataMaskingPattern):

        format_data_bits = (level << 3) | pattern

        # Extend the 5-bit formation information with 10 bits of error-correction data.
        format_bits = (format_data_bits << 10) | format_information_code_remainder(format_data_bits)

        # XOR the result with a fixed pattern.
        format_bits ^= 0b101010000010010

        # Place the two format information patterns.
        for (format_bit_position_list, format_bit) in zip(self.format_bit_position_lists, enumerate_bits(format_bits, 15)):
            module_value = ModuleValue.FORMAT_INFORMATION_1 if format_bit else ModuleValue.FORMAT_INFORMATION_0
            for (i, j) in format_bit_position_list:
                self.set_module_value(i, j, module_value)

        # Place the single fixed "dark module" above and to the right of the bottom-left finder pattern (7.9.1).
        self.set_module_value(self.height-8, 8, ModuleValue.FORMAT_INFORMATION_1)

    def place_version_information_placeholders(self):

        # The version information is only present in versions 7..40.
        if not (7 <= self.version <= 40):
            return

        # Place the two version information patterns.
        for version_bit_position_list in self.version_bit_position_lists:
            for (i, j) in version_bit_position_list:
                self.set_module_value(i, j, ModuleValue.VERSION_INFORMATION_INDETERMINATE)

    def place_version_information_patterns(self):

        # The version information is only present in versions 7..40.
        if not (7 <= self.version <= 40):
            return

        # Extend the 6-bit version number with 12 bits of error-correction data.
        version_bits = (self.version << 12) | version_information_code_remainder(self.version)

        # Place the two version information patterns.
        for (version_bit_position_list, version_bit) in zip(self.version_bit_position_lists, enumerate_bits(version_bits, 18)):
            module_value = ModuleValue.VERSION_INFORMATION_1 if version_bit else ModuleValue.VERSION_INFORMATION_0
            for (i, j) in version_bit_position_list:
                self.set_module_value(i, j, module_value)

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
                    if j <= 6:  # Skip vertical timing pattern.
                        j -= 1
                    value = self.get_module_value(i, j)
                    if value == ModuleValue.INDETERMINATE:
                        position = (i, j)
                        positions.append(position)
        return positions

    def apply_data_masking_pattern(self, pattern: DataMaskingPattern, positions: list[tuple[int, int]]) -> None:
        pattern_function = data_mask_pattern_functions[pattern]
        for (i, j) in positions:
            value = self.get_module_value(i, j)
            assert value in (ModuleValue.DATA_ERC_0, ModuleValue.DATA_ERC_1)
            # Invert if the pattern condition is True
            if pattern_function(i, j):
                value = ModuleValue.DATA_ERC_1 if value == ModuleValue.DATA_ERC_0 else ModuleValue.DATA_ERC_0
                self.set_module_value(i, j, value)

    def score(self):
        surplus = 0
        for i in range(self.height):
            for j in range(self.width):
                value = self.get_module_value(i, j) % 10
                assert value in (0, 1)
                surplus += 2 * value - 1
        return abs(surplus)


def make_qr_code(de: DataEncoder, version: int, level: ErrorCorrectionLevel, include_quiet_zone: bool,
                 pattern: Optional[DataMaskingPattern] = None) -> QRCodeCanvas:

    version_specification = version_specifications[(version, level)]

    # Check if the data will fit in the selected QR code version / level.

    number_of_data_codewords = version_specification.number_of_data_codewords()

    data = de.get_words(number_of_data_codewords)

    if data is None:
        name = version_specification.name()
        raise QRCodeCapacityError(f"Cannot fit {len(de.bits)} data bits in QR code symbol {name} ({number_of_data_codewords * 8} data bits available).")

    # Data will fit -- proceed.
    # Split up data in data-blocks, and calculate the corresponding error correction blocks.

    dblocks = []
    eblocks = []

    idx = 0
    for (count, (code_c, code_k, code_r)) in version_specification.block_specification:
        # Calculate the Reed-Solomon polynomial corresponding to the number of error correction words.
        poly = calculate_reed_solomon_polynomial(code_c - code_k, strip=True)
        for k in range(count):
            dblock = data[idx:idx + code_k]
            dblocks.append(dblock)

            eblock = reed_solomon_code_remainder(dblock, poly)
            eblocks.append(eblock)

            idx += code_k

    assert idx == version_specification.total_number_of_codewords - version_specification.number_of_error_correcting_codewords
    assert sum(map(len, dblocks)) + sum(map(len, eblocks)) == version_specification.total_number_of_codewords

    # Interleave the data words and error correction words.
    # All data words will precede all error correction words.

    channel_words = []

    k = 0
    while sum(map(len, dblocks)) != 0:
        if len(dblocks[k]) != 0:
            channel_words.append(dblocks[k].pop(0))
        k = (k + 1) % len(dblocks)

    k = 0
    while sum(map(len, eblocks)) != 0:
        if len(eblocks[k]) != 0:
            channel_words.append(eblocks[k].pop(0))
        k = (k + 1) % len(eblocks)

    # Convert data-words to data-bits.

    channel_bits = [channel_bit for word in channel_words for channel_bit in enumerate_bits(word, 8)]

    # We prepared the channel bits. Now prepare the QR code symbol.

    qr = QRCodeDrawer(version, include_quiet_zone)
    qr.place_quiet_zone()
    qr.place_finder_patterns()
    qr.place_separators()
    qr.place_timing_patterns()
    qr.place_alignment_patterns()

    # Place temporary format and version information placeholders.
    # We need to put /something/ there to be able to find the symbol's available
    # channel bit positions later on in the call to qr.get_indeterminate_positions().
    # After pattern selection, we will fill the actual format and version information.

    qr.place_format_information_placeholders()
    qr.place_version_information_placeholders()

    # Get the module positions where the data needs to go.

    positions = qr.get_indeterminate_positions()

    assert len(channel_bits) <= len(positions)

    # Add padding bits to data-bits if needed.

    num_padding_bits = len(positions) - len(channel_bits)
    if num_padding_bits != 0:
        channel_bits.extend([False] * num_padding_bits)

    assert len(positions) == len(channel_bits)

    # Place the channel bits in the QR code symbol.

    for ((i, j), channel_bit) in zip(positions, channel_bits):
        qr.set_module_value(i, j, ModuleValue.DATA_ERC_1 if channel_bit else ModuleValue.DATA_ERC_0)

    # Now for masking.
    # If a pattern is given as a parameter, we will use that. Otherwise, we'll determine
    # the best pattern based on a score (TODO: implement scoring function described by the standard).

    if pattern is None:

        score_pattern_tuple_list = []

        for test_pattern in DataMaskingPattern:
            qr.place_version_information_patterns()
            qr.place_format_information_patterns(level, test_pattern)

            # Apply data mask pattern
            qr.apply_data_masking_pattern(test_pattern, positions)

            score = qr.score()
            score_pattern_tuple_list.append((score, test_pattern))

            # Un-apply data mask pattern
            qr.apply_data_masking_pattern(test_pattern, positions)

        score_pattern_tuple_list.sort(key=lambda score_pattern_tuple: score_pattern_tuple[0])

        for (score, test_pattern) in score_pattern_tuple_list:
            print(f"{score:3d} {test_pattern.name}")

        # Select pattern that yields the lowest score.
        pattern = score_pattern_tuple_list[0][1]

    print(f"Applying data mask pattern {pattern.name}.")

    qr.apply_data_masking_pattern(pattern, positions)

    qr.place_version_information_patterns()
    qr.place_format_information_patterns(level, pattern)

    return qr.canvas
