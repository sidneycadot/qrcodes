#! /usr/bin/env -S python3 -B

"""An example encoder for a version 1-M QR Code symbol.
This example uses numeric mode.
"""

from enum import IntEnum
from PIL import Image, ImageDraw

from binary_codes import format_information_code_remainder, version_information_code_remainder
from reed_solomon_code import calculate_reed_solomon_polynomial, reed_solomon_code_remainder


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


render_colormap = {
    ModuleValue.QUIET_ZONE_0          : '#ffffff',
    ModuleValue.FINDER_PATTERN_0      : '#ffffff',
    ModuleValue.FINDER_PATTERN_1      : '#000000',
    ModuleValue.SEPARATOR_0           : '#ffffff',
    ModuleValue.TIMING_PATTERN_0      : '#ffffff',
    ModuleValue.TIMING_PATTERN_1      : '#000000',
    ModuleValue.ALIGNMENT_PATTERN_0   : 'yellow',
    ModuleValue.ALIGNMENT_PATTERN_1   : 'orange',
    ModuleValue.FORMAT_INFORMATION_0  : '#ffffff',
    ModuleValue.FORMAT_INFORMATION_1  : '#000000',
    ModuleValue.VERSION_INFORMATION_0 : '#00cc00',
    ModuleValue.VERSION_INFORMATION_1 : '#00ff00',
    ModuleValue.DATA_ERC_0            : '#ffffff',
    ModuleValue.DATA_ERC_1            : '#000000',
    ModuleValue.INDETERMINATE         : '#ff0000'
}


class QRCodeCanvas:

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.modules = bytearray([ModuleValue.INDETERMINATE]) * (width * height)

    def set_module_value(self, x: int, y: int, value: ModuleValue):
        if not ((0 <= x < self.width) and (0 <= y < self.height)):
            raise ValueError(f"Bad coordinate ({x}, {y}).")
        index = x + y * self.width
        self.modules[index] = value

    def get_module_value(self, x: int, y: int) -> ModuleValue:
        if not ((0 <= x < self.width) and (0 <= y < self.height)):
            raise ValueError(f"Bad coordinate ({x}, {y}).")
        index = x + y * self.width
        return ModuleValue(self.modules[index])

    def render_as_image(self, filename: str, *, magnification: int = 1) -> None:
        im = Image.new('RGB', (self.width * magnification, self.height * magnification))
        draw = ImageDraw.Draw(im)

        for y in range(self.height):
            for x in range(self.width):
                value = self.get_module_value(x, y)
                color = render_colormap[value]
                draw.rectangle((x * magnification, y * magnification, (x + 1) * magnification - 1, (y + 1) * magnification - 1), color)

        im.save(filename)

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

    def set_module_value(self, x: int, y: int, value: ModuleValue):
        self.canvas.set_module_value(x + self.quiet_zone_margin, y + self.quiet_zone_margin, value)

    def get_module_value(self, x: int, y: int) -> ModuleValue:
        return self.canvas.get_module_value(x + self.quiet_zone_margin, y + self.quiet_zone_margin)

    def place_quiet_zone(self) -> None:
        for x in range(self.width + 2 * self.quiet_zone_margin):
            for y in range(self.quiet_zone_margin):
                self.set_module_value(x - self.quiet_zone_margin, y - self.quiet_zone_margin, ModuleValue.QUIET_ZONE_0)
                self.set_module_value(x - self.quiet_zone_margin, y + self.height           , ModuleValue.QUIET_ZONE_0)

        for y in range(self.height + 2 * self.quiet_zone_margin):
            for x in range(self.quiet_zone_margin):
                self.set_module_value(x - self.quiet_zone_margin, y - self.quiet_zone_margin, ModuleValue.QUIET_ZONE_0)
                self.set_module_value(x + self.width            , y - self.quiet_zone_margin, ModuleValue.QUIET_ZONE_0)

    def place_finder_pattern(self, x: int, y: int) -> None:
        for dx in range(7):
            for dy in range(7):
                flag = dx in (0, 6) or dy in (0, 6) or (dx in (2, 3, 4) and dy in (2, 3, 4))
                value = ModuleValue.FINDER_PATTERN_1 if flag else ModuleValue.FINDER_PATTERN_0
                self.set_module_value(x + dx, y + dy, value)

    def place_finder_patterns(self) -> None:
        # Place the three finder patterns in the top-left, top-right, and bottom-left corners.
        self.place_finder_pattern(0, 0)
        self.place_finder_pattern(self.width - 7, 0)
        self.place_finder_pattern(0, self.height - 7)

    def place_separators(self):
        for k in range(8):
            # Top-left
            self.set_module_value(7, k, ModuleValue.SEPARATOR_0)
            self.set_module_value(k, 7, ModuleValue.SEPARATOR_0)
            # Top-right
            self.set_module_value(self.width - 8, k, ModuleValue.SEPARATOR_0)
            self.set_module_value(self.width - 8 + k, 7, ModuleValue.SEPARATOR_0)
            # Bottom-right
            self.set_module_value(7, self.height - 8 + k, ModuleValue.SEPARATOR_0)
            self.set_module_value(k, self.height - 8, ModuleValue.SEPARATOR_0)

    def place_alignment_pattern(self, x: int, y: int) -> None:
        for dx in (-2, -1, 0, +1, +2):
            for dy in (-2, -1, 0, +1, +2):
                flag = dx in (-2, +2) or dy in (-2, +2) or (dx == 0 and dy == 0)
                value = ModuleValue.ALIGNMENT_PATTERN_1 if flag else ModuleValue.ALIGNMENT_PATTERN_0
                self.set_module_value(x + dx, y + dy, value)

    def place_alignment_patterns(self) -> None:

        positions = get_alignment_positions(self.version)
        num = len(positions)

        for v in range(num):
            for h in range(num):
                if (h == 0 and v == 0) or (h == 0 and v == num - 1) or (h == num - 1 and v == 0):
                    continue
                self.place_alignment_pattern(positions[h], positions[v])

    def place_timing_patterns(self):
        # Regular QR code has a horizontal and a vertical timing code.
        for y in range(8, self.height - 8):
            self.set_module_value(6, y, ModuleValue.TIMING_PATTERN_1 if y % 2 == 0 else ModuleValue.TIMING_PATTERN_0)
        for x in range(8, self.width - 8):
            self.set_module_value(x, 6, ModuleValue.TIMING_PATTERN_1 if x % 2 == 0 else ModuleValue.TIMING_PATTERN_0)

    def place_format_information_regions(self):

        level = ErrorCorrectionLevel.M
        pattern = DataMaskingPattern.Pattern2

        format_data_bits = (level << 3) | pattern
        print("@@@@", level, pattern, bin(format_data_bits))
        format_ecc_bits = format_information_code_remainder(format_data_bits)

        format_bits = (format_data_bits << 10) | format_ecc_bits

        # Don't forget to XOR the info with a fixed pattern!
        format_bits ^= 0b101010000010010

        #print("format bits: 0b{:015b}".format(format_bits))

        W = self.width
        H = self.height

        copies = [
            [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8), (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)],
            [(W-1, 8), (W-2, 8), (W-3, 8), (W-4, 8), (W-5, 8), (W-6, 8), (W-7, 8), (W-8, 8), (8, H-7), (8, H-6), (8, H-5), (8, H-4), (8, H-3), (8, H-2), (8, H-1)]
        ]

        # Set the single module.
        self.set_module_value(8, H-8, ModuleValue.FORMAT_INFORMATION_1)

        for k in range(15):
            fbit = ((format_bits >> k) & 1) != 0
            for copy in copies:
                (x, y) = copy[k]
                self.set_module_value(x, y, ModuleValue.FORMAT_INFORMATION_1 if fbit else ModuleValue.FORMAT_INFORMATION_0)

    def place_version_information_regions(self):
        if self.version >= 7:

            version_bits = version_information_code_remainder(self.version) | (self.version << 12)

            for k in range(18):
                vbit = (version_bits >> k) & 1 == 0
                self.set_module_value(k // 3, self.height - 11 + k % 3, ModuleValue.VERSION_INFORMATION_1 if vbit else ModuleValue.VERSION_INFORMATION_0)
                self.set_module_value(self.width - 11 + k % 3, k // 3, ModuleValue.VERSION_INFORMATION_1 if vbit else ModuleValue.VERSION_INFORMATION_0)

    def get_indeterminate_positions(self):
        positions = []
        assert self.width % 2 == 1
        for h_outer in range((self.width - 1) // 2):
            # Note: the last three h_outer walks are to the left of the vertical timing pattern, the
            # other ones are to the right of the vertical timing pattern.
            for v in range(self.height):
                y = (self.height - 1 - v) if h_outer % 2 == 0 else v
                for h_inner in range(2):
                    h = h_outer * 2 + h_inner
                    x = (self.width - 1 - h)
                    if x <= 6: # Skip vertical timing pattern.
                        x -= 1
                    #print("==>", h_outer, h_inner, "h", h, "v", v, "x", x, "y", y)
                    value = self.get_module_value(x, y)
                    if value == ModuleValue.INDETERMINATE:
                        position = (x, y)
                        positions.append(position)
        return positions

    def apply_data_masking_pattern(self, pattern, positions):
        if pattern != DataMaskingPattern.Pattern2:
            raise RuntimeError()
        for (x, y) in positions:
            value = self.get_module_value(x, y)
            assert value in (ModuleValue.DATA_ERC_0, ModuleValue.DATA_ERC_1)
            # Invert if the pattern condition is True
            if x % 3 == 0:
                value = ModuleValue.DATA_ERC_1 if value == ModuleValue.DATA_ERC_0 else ModuleValue.DATA_ERC_0
                self.set_module_value(x, y, value)

    def render_as_image(self, filename: str, *, magnification: int = 1) -> None:
        self.canvas.render_as_image(filename, magnification = magnification)

    def count_indeterminate(self):
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                value = self.get_module_value(x, y)
                if value == ModuleValue.INDETERMINATE:
                    count += 1
        return count


class DataEncoder:
    def __init__(self):
        self.bits = []
    def add_bits(self, s: str):
        for c in s:
            if c == '0':
                self.bits.append(0)
            if c == '1':
                self.bits.append(1)

    def add_error_correction_words(self, n: int):
        # Convert data to 8-bit words.
        assert len(self.bits) % 8 == 0
        idx = 0
        data = []
        while idx != len(self.bits):
            word = int("".join(map(str, self.bits[idx:idx+8])), 2)
            data.append(word)
            idx += 8

        poly = calculate_reed_solomon_polynomial(n, strip=True)

        erc = reed_solomon_code_remainder(data, poly)

        for w in erc:
            self.add_bits("{:08b}".format(w))

        idx = 0
        data = []
        while idx != len(self.bits):
            word = "".join(map(str, self.bits[idx:idx+8]))
            print(word)
            idx += 8


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

    render_versions = (
        (1, 32),
        (2, 16),
        (3, 16),
        (7,  8),
        (14, 8),
        (40, 4)
    )

    magnification = 20

    for version in (1, ):
    #for version in range(1, 41):
        #print(f"Generating version {version} QR code...")
        qr = QRCodeDrawer(version, True)
        qr.place_quiet_zone()
        qr.place_finder_patterns()
        qr.place_separators()
        qr.place_timing_patterns()
        qr.place_alignment_patterns()
        qr.place_format_information_regions()
        qr.place_version_information_regions()

        de = DataEncoder()

        de.add_bits("0001")
        de.add_bits("0000001000")

        de.add_bits("0000001100")
        de.add_bits("0101011001")
        de.add_bits("1000011")

        while len(de.bits) % 8 != 0:
            de.add_bits("0")

        padding = 0
        while len(de.bits) // 8 != 16:
            if padding == 0:
                de.add_bits("11101100")
            else:
                de.add_bits("00010001")
            padding = 1 - padding

        de.add_error_correction_words(10)

        positions = qr.get_indeterminate_positions()

        assert len(positions) == len(de.bits)

        for (p, b) in zip(positions, de.bits):
            qr.set_module_value(*p, ModuleValue.DATA_ERC_1 if b else ModuleValue.DATA_ERC_0)

        qr.apply_data_masking_pattern(DataMaskingPattern.Pattern2, positions)


        qr.render_as_image(f"v{version}.png", magnification=magnification)



if __name__ == "__main__":
    main()
