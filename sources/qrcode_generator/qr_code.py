"""QR code canvas and canvas drawing functionality."""

from enum import IntEnum
from typing import Optional

from .auxiliary import calculate_qrcode_capacity, enumerate_bits
from .enum_types import ErrorCorrectionLevel, DataMaskingPattern
from .binary_codes import format_information_code_remainder, version_information_code_remainder
from .lookup_tables import alignment_pattern_position_table, data_mask_pattern_function_table, error_correction_level_encoding, \
    data_masking_pattern_encoding
from .data_encoder import DataEncoder


class QRCodeCapacityError(Exception):
    pass


class ModuleValue(IntEnum):
    """Values for the modules (pixels) that make up the content of the QRCodeCanvas.

    These are hex values with the high nibble denoting the function of the module,
    and the low nibble denoting the value:

    0x0 == 0b0000   value 0 (light)
    0x1 == 0b0001   value 1 (dark)
    0xe == 0b1110   indeterminate (rendered as 0, light).

    Bit 0 is useful to see if a module is light (0) or dark (1).
    Indeterminate modules are rendered as light (0).
    """
    INDETERMINATE                     = 0x0e  # Module/pixel unset; defaults to 0 (light).
    QUIET_ZONE_0                      = 0x10
    FINDER_PATTERN_0                  = 0x20
    FINDER_PATTERN_1                  = 0x21
    SEPARATOR_0                       = 0x30
    TIMING_PATTERN_0                  = 0x40
    TIMING_PATTERN_1                  = 0x41
    ALIGNMENT_PATTERN_0               = 0x50
    ALIGNMENT_PATTERN_1               = 0x51
    FORMAT_INFORMATION_0              = 0x60
    FORMAT_INFORMATION_1              = 0x61
    FORMAT_INFORMATION_INDETERMINATE  = 0x6e  # Placeholder, to be filled in later. Defaults to 0 (light).
    VERSION_INFORMATION_0             = 0x70
    VERSION_INFORMATION_1             = 0x71
    VERSION_INFORMATION_INDETERMINATE = 0x7e  # Placeholder, to be filled in later. Defaults to 0 (light).
    DATA_ERC_0                        = 0x80
    DATA_ERC_1                        = 0x81
    DATA_ERC_INDETERMINATE            = 0x8e  # Placeholder, to be filled in later. Defaults to 0 (light).


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


class QRCodeDrawer:
    """A QRCodeDrawer knows how to draw the different areas in a QR code."""
    def __init__(self, version: int, *, include_quiet_zone: Optional[bool] = None):

        if not (1 <= version <= 40):
            raise ValueError(f"Bad QR code version: {version}.")

        if include_quiet_zone is None:
            # By default, the quiet zone (border) is enabled.
            include_quiet_zone = True

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

        # Fill in QR code canvas, except:
        # - format information
        # - version information
        # - data and error correction words

        self.place_quiet_zone()
        self.place_finder_patterns()
        self.place_separators()
        self.place_timing_patterns()
        self.place_alignment_patterns()

        # Place temporary format and version information placeholders.
        # We need to put /something/ there to be able to find the symbol's available
        # channel bit positions later on in the call to qr.get_indeterminate_positions().
        # After pattern selection, we will fill the actual format and version information.

        self.place_format_information_placeholders()
        self.place_version_information_placeholders()

        # Mark the module positions where the data and error correction bits needs to go, and
        # remember their positions.

        self.data_and_error_correction_positions = self.mark_data_and_error_correction_positions()

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

        positions = alignment_pattern_position_table[self.version]
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

        level_encoding = error_correction_level_encoding[level]
        pattern_encoding = data_masking_pattern_encoding[pattern]

        format_data_bits = (level_encoding << 3) | pattern_encoding

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

        # The version information is only present in versions 7 and higher,
        if not (self.version >= 7):
            return

        # Place the two version information patterns.
        for version_bit_position_list in self.version_bit_position_lists:
            for (i, j) in version_bit_position_list:
                self.set_module_value(i, j, ModuleValue.VERSION_INFORMATION_INDETERMINATE)

    def place_version_information_patterns(self):

        # The version information is only present in versions 7 and higher.
        if not (self.version >= 7):
            return

        # Extend the 6-bit version number with 12 bits of error-correction data.
        version_bits = (self.version << 12) | version_information_code_remainder(self.version)

        # Place the two version information patterns.
        for (version_bit_position_list, version_bit) in zip(self.version_bit_position_lists, enumerate_bits(version_bits, 18)):
            module_value = ModuleValue.VERSION_INFORMATION_1 if version_bit else ModuleValue.VERSION_INFORMATION_0
            for (i, j) in version_bit_position_list:
                self.set_module_value(i, j, module_value)

    def mark_data_and_error_correction_positions(self) -> list[tuple[int, int]]:
        """Traverse modules for data/error correction bits, and return those that are currently INDETERMINATE.

        The order in which the modules are visited (and, hence, the order in which the positions are returned)
        reflects the placement of data and error correction bits in the final QR code.

        The h_outer loop below samples two neighboring columns. Note that a QR code has an odd number of
        columns; but there is a full column covered by the vertical timing pattern (j==6) which is not usable
        for data.

        """
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
                    if j <= 6:  # Skip the vertical timing pattern line at j==6.
                        j -= 1
                    value = self.get_module_value(i, j)
                    if value == ModuleValue.INDETERMINATE:
                        self.set_module_value(i, j, ModuleValue.DATA_ERC_INDETERMINATE)
                        position = (i, j)
                        positions.append(position)

        assert len(positions) == calculate_qrcode_capacity(self.version)

        return positions

    def erase_data_and_error_correction_bits(self) -> None:
        """Useful for some low-level tests."""
        for (i, j) in self.data_and_error_correction_positions:
            self.set_module_value(i, j, ModuleValue.DATA_ERC_0)

    def place_data_and_error_correction_bits(self, de: DataEncoder, level: ErrorCorrectionLevel) -> None:

        channel_bits = de.get_channel_bits(self.version, level)
        if channel_bits is None:
            raise QRCodeCapacityError("Unable to fit the data in the selected QR code symbol.")

        assert len(self.data_and_error_correction_positions) == len(channel_bits)

        # Place the channel bits in the QR code symbol.
        for ((i, j), channel_bit) in zip(self.data_and_error_correction_positions, channel_bits):
            self.set_module_value(i, j, ModuleValue.DATA_ERC_1 if channel_bit else ModuleValue.DATA_ERC_0)

    def apply_data_masking_pattern(self, pattern: DataMaskingPattern) -> None:
        pattern_function = data_mask_pattern_function_table[pattern]
        for (i, j) in self.data_and_error_correction_positions:
            value = self.get_module_value(i, j)
            assert value in (ModuleValue.DATA_ERC_0, ModuleValue.DATA_ERC_1)
            # Invert if the pattern condition is True.
            if pattern_function(i, j):
                value = ModuleValue.DATA_ERC_1 if value == ModuleValue.DATA_ERC_0 else ModuleValue.DATA_ERC_0
                self.set_module_value(i, j, value)

    def score(self):
        """Determine a QR code's score. A higher score corresponds to more undesirable features.

        The score is used to select a data masking pattern.

        The description of the score algorithm in the standard is not very clear;
        the implementation below reflects our best understanding of it.
          However, the data mask pattern choice made based on the current score implementation
        do not currently reproduce the choice that we see in the seven QR code examples given
        in the standard, so something is not right (either in the algorithm implemented
        here, or in the standard).
        """

        # Contribution 1: consecutive same-color runs, horizontally and vertically.

        points = 0

        for i in range(self.height):
            previous_value = None
            consecutive = 0
            for j in range(self.width):
                value = self.get_module_value(i, j) % 2
                if value == previous_value:
                    consecutive += 1
                    if consecutive == 5:
                        points += 3
                    elif consecutive > 5:
                        points += 1
                else:
                    consecutive = 1
                    previous_value = value

        for j in range(self.width):
            previous_value = None
            consecutive = 0
            for i in range(self.height):
                value = self.get_module_value(i, j) % 2
                if value == previous_value:
                    consecutive += 1
                    if consecutive == 5:
                        points += 3
                    elif consecutive > 5:
                        points += 1
                else:
                    consecutive = 1
                    previous_value = value

        contribution_1 = points

        # Contribution 2: 2x2 blocks of the same color.

        num_blocks = 0
        for i in range(self.height - 1):
            for j in range(self.width - 1):
                value00 = self.get_module_value(i + 0, j + 0) % 2
                value01 = self.get_module_value(i + 0, j + 1) % 2
                value10 = self.get_module_value(i + 1, j + 0) % 2
                value11 = self.get_module_value(i + 1, j + 1) % 2

                if value00 == value01 == value10 == value11:
                    num_blocks += 1

        contribution_2 = 3 * num_blocks

        # Contribution 3: 1011101 with preceding or following 4 white pixels.

        occurrences = 0
        pattern = bytes([1, 0, 1, 1, 1, 0, 1])
        b = bytearray()

        for i in range(self.height):
            b.clear()
            #b.append(0)
            #b.append(0)
            #b.append(0)
            #b.append(0)
            for j in range(self.width):
                value = self.get_module_value(i, j) % 2
                b.append(value)
            #b.append(0)
            #b.append(0)
            #b.append(0)
            #b.append(0)

            #assert len(b) == self.width + 8

            idx = 0
            while True:
                idx = b.find(pattern, idx)
                if idx == -1:
                    break
                #before = all(b[idx-k-1] == 0 for k in range(4))
                #after = all(b[idx+7+k] == 0 for k in range(4))
                #if before or after:
                occurrences += 1
                idx += 1

        for j in range(self.width):
            b.clear()
            for i in range(self.height):
                value = self.get_module_value(i, j) % 2
                b.append(value)

            #assert len(b) == self.height + 8

            idx = 0
            while True:
                idx = b.find(pattern, idx)
                if idx == -1:
                    break
                # before = all(b[idx-k-1] == 0 for k in range(4))
                # after = all(b[idx+7+k] == 0 for k in range(4))
                # if before or after:
                occurrences += 1
                idx += 1

        contribution_3 = 40 * occurrences

        # Contribution 4: black/white imbalance.

        count_ones = 0
        for i in range(self.height):
            for j in range(self.width):
                value = self.get_module_value(i, j) % 2
                if value == 1:
                    count_ones += 1

        # 0..5: 0
        # 5..10: 10
        # 10..15: 20
        # etc.
        deviation_percentage = abs(count_ones / (self.height * self.width) * 100.0 - 50.0)
        k = round(deviation_percentage // 5.0)

        contribution_4 = 10 * k

        return contribution_1 + contribution_2 + contribution_3 + contribution_4


def make_qr_code(
            de: DataEncoder, version: int, level: ErrorCorrectionLevel,
            *,
            include_quiet_zone: Optional[bool] = None,
            pattern: Optional[DataMaskingPattern] = None
        ) -> QRCodeCanvas:

    # Prepare the selected QR code symbol and fill it with the data.

    qr = QRCodeDrawer(version, include_quiet_zone=include_quiet_zone)

    # Note: this may raise a QRCodeCapacityError.
    qr.place_data_and_error_correction_bits(de, level)

    # Handle data pattern masking.
    #
    # If a pattern is given as a parameter, we will use that.
    # Otherwise, we'll determine the best pattern based on a score.

    if pattern is None:

        score_pattern_tuple_list = []

        for test_pattern in DataMaskingPattern:

            standard_compliant = True
            if standard_compliant:
                # The standard prescribes that the version and format information should
                # be left empty when scoring the patterns.
                qr.place_version_information_placeholders()
                qr.place_format_information_placeholders()
            else:
                # A more sensible, but not standard-compliant approach is to fill the
                # version and format information before scoring, since it is all known at
                # this point.
                qr.place_version_information_patterns()
                qr.place_format_information_patterns(level, test_pattern)

            # Apply the data mask test pattern.
            qr.apply_data_masking_pattern(test_pattern)

            # Calculate and record the score for this test pattern.
            score = qr.score()
            score_pattern_tuple_list.append((score, test_pattern))

            # Un-apply the data mask test pattern.
            qr.apply_data_masking_pattern(test_pattern)

        # Sort the test patterns by score.
        score_pattern_tuple_list.sort(key=lambda score_pattern_tuple: score_pattern_tuple[0])

        # As a debugging aid, print the scores for the different test patterns.
        for (score, test_pattern) in score_pattern_tuple_list:
            print(f"{score:3d} {test_pattern.name}")

        # Select the test pattern that yields the lowest score.
        pattern = score_pattern_tuple_list[0][1]

    # Apply the selected data masking pattern.
    print(f"Applying data mask pattern {pattern.name}.")
    qr.apply_data_masking_pattern(pattern)

    # Fill in the definitive version and format information.
    qr.place_version_information_patterns()
    qr.place_format_information_patterns(level, pattern)

    return qr.canvas
