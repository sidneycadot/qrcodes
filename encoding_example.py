#! /usr/bin/env -S python3 -B

"""Generate QR Code examples."""

from enum import IntEnum
from PIL import Image, ImageDraw

from enum_types import ErrorCorrectionLevel, DataMaskingPattern
from binary_codes import format_information_code_remainder, version_information_code_remainder
from reed_solomon_code import calculate_reed_solomon_polynomial, reed_solomon_code_remainder
from lookup_tables import alignment_pattern_positions, data_mask_pattern_functions, version_specifications
from data_encoder import DataEncoder

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
    FORMAT_INFORMATION_INDETERMINATE  = 69 # Placeholder
    VERSION_INFORMATION_0             = 70
    VERSION_INFORMATION_1             = 71
    VERSION_INFORMATION_INDETERMINATE = 79 # Placeholder
    DATA_ERC_0                        = 80
    DATA_ERC_1                        = 81
    INDETERMINATE                     = 99


render_colormap1 = {
    ModuleValue.QUIET_ZONE_0                      : '#ffffff',
    ModuleValue.FINDER_PATTERN_0                  : '#ffcccc',
    ModuleValue.FINDER_PATTERN_1                  : '#ff0000',
    ModuleValue.SEPARATOR_0                       : '#ffffff',
    ModuleValue.TIMING_PATTERN_0                  : '#ffcccc',
    ModuleValue.TIMING_PATTERN_1                  : '#ff0000',
    ModuleValue.ALIGNMENT_PATTERN_0               : '#ffcccc',
    ModuleValue.ALIGNMENT_PATTERN_1               : '#ff0000',
    ModuleValue.FORMAT_INFORMATION_0              : '#ccffcc',
    ModuleValue.FORMAT_INFORMATION_1              : '#00bb00',
    ModuleValue.FORMAT_INFORMATION_INDETERMINATE  : '#ccffcc',
    ModuleValue.VERSION_INFORMATION_0             : '#ddddff',
    ModuleValue.VERSION_INFORMATION_1             : '#0000ff',
    ModuleValue.VERSION_INFORMATION_INDETERMINATE : '#ddddff',
    ModuleValue.DATA_ERC_0                        : '#ffffff',
    ModuleValue.DATA_ERC_1                        : '#000000',
    ModuleValue.INDETERMINATE                     : '#ff0000'
}

render_colormap2 = {
    ModuleValue.QUIET_ZONE_0                      : '#ffffff',
    ModuleValue.FINDER_PATTERN_0                  : '#ffffff',
    ModuleValue.FINDER_PATTERN_1                  : '#000000',
    ModuleValue.SEPARATOR_0                       : '#ffffff',
    ModuleValue.TIMING_PATTERN_0                  : '#ffffff',
    ModuleValue.TIMING_PATTERN_1                  : '#000000',
    ModuleValue.ALIGNMENT_PATTERN_0               : '#ffffff',
    ModuleValue.ALIGNMENT_PATTERN_1               : '#000000',
    ModuleValue.FORMAT_INFORMATION_0              : '#ffffff',
    ModuleValue.FORMAT_INFORMATION_1              : '#000000',
    ModuleValue.FORMAT_INFORMATION_INDETERMINATE : '#ffffff',
    ModuleValue.VERSION_INFORMATION_0             : '#ffffff',
    ModuleValue.VERSION_INFORMATION_1             : '#000000',
    ModuleValue.VERSION_INFORMATION_INDETERMINATE : '#ffffff',
    ModuleValue.DATA_ERC_0                        : '#ffffff',
    ModuleValue.DATA_ERC_1                        : '#000000',
    ModuleValue.INDETERMINATE                     : '#ffffff'
}

render_colormap = render_colormap1


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

    def render_as_image(self, magnification: int = 1) -> Image.Image:
        im = Image.new('RGB', (self.width * magnification, self.height * magnification))
        draw = ImageDraw.Draw(im)

        for i in range(self.height):
            for j in range(self.width):
                value = self.get_module_value(i, j)
                color = render_colormap[value]
                draw.rectangle((j * magnification, i * magnification, (j + 1) * magnification - 1, (i + 1) * magnification - 1), color)

        return im

def enumerate_bits(value: int, num_bits: int):
    """Enumerate the bits in value, starting from the MSB and going down to the LSB."""
    assert 0 <= value < (1 << num_bits)
    mask = 1 << (num_bits - 1)
    while mask != 0:
        yield (value & mask) != 0
        mask >>= 1


class QRCodeDrawer:

    def __init__(self, version: int, include_quiet_zone: bool):

        if not (1 <= version <= 40):
            raise ValueError(f"Bad QR code version: {version}.")

        self.version = version
        self.quiet_zone_margin = 4 if include_quiet_zone else 0
        self.width = 21 + 4 * (version - 1)
        self.height = 21 + 4 * (version - 1)

        W = self.width
        H = self.height

        self.format_bit_position_lists = [
            [(8, 0), (H-1, 8)],
            [(8, 1), (H-2, 8)],
            [(8, 2), (H-3, 8)],
            [(8, 3), (H-4, 8)],
            [(8, 4), (H-5, 8)],
            [(8, 5), (H-6, 8)],
            [(8, 7), (H-7, 8)],
            [(8, 8), (8, W-8)],
            [(7, 8), (8, W-7)],
            [(5, 8), (8, W-6)],
            [(4, 8), (8, W-5)],
            [(3, 8), (8, W-4)],
            [(2, 8), (8, W-3)],
            [(1, 8), (8, W-2)],
            [(0, 8), (8, W-1)]
        ]

        self.version_bit_position_lists = [
            [(H -  9, 5), (5, W -  9)],
            [(H - 10, 5), (5, W - 10)],
            [(H - 11, 5), (5, W - 11)],
            [(H -  9, 4), (4, W -  9)],
            [(H - 10, 4), (4, W - 10)],
            [(H - 11, 4), (4, W - 11)],
            [(H -  9, 3), (3, W -  9)],
            [(H - 10, 3), (3, W - 10)],
            [(H - 11, 3), (3, W - 11)],
            [(H -  9, 2), (2, W -  9)],
            [(H - 10, 2), (2, W - 10)],
            [(H - 11, 2), (2, W - 11)],
            [(H -  9, 1), (1, W -  9)],
            [(H - 10, 1), (1, W - 10)],
            [(H - 11, 1), (1, W - 11)],
            [(H -  9, 0), (0, W -  9)],
            [(H - 10, 0), (0, W - 10)],
            [(H - 11, 0), (0, W - 11)]
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

def append_pi(de):
    with open("pi_10k.txt", "r") as fi:
        pi_chars = fi.read()
    de.append_alphanumeric_mode_block(pi_chars[:2])
    de.append_numeric_mode_block(pi_chars[2:7081])

def append_html(de):
    with open("sidney.html", "r") as fi:
        html = fi.read()
    html = "data:text/html," + html
    de.append_byte_mode_block(html.encode())

def append_vcard(de):
    with open("sidney.vcard", "r") as fi:
        vcard = fi.read()
    de.append_byte_mode_block(vcard.encode())

def append_geo_position(de):
    # Supported by iOS
    #de.append_byte_mode_block(b"geo:37.91334,15.33897")
    de.append_byte_mode_block(b"geo:37.364722,14.334722")

def append_mailto(de):
    # Supported by iOS
    de.append_byte_mode_block(b"mailto:sidney@jigsaw.nl")

def append_kanji(de):
    de.append_kanji_mode_block('点茗')

def append_kanji_test(de):
    de.append_byte_mode_block(b'Japanese characters in Kanji block: ')
    de.append_kanji_mode_block('点茗')
    de.append_byte_mode_block(b'\nJapanese characters in byte block (UTF-8 bytes): ' + '点茗'.encode('utf-8') + b'\n')

class QRCodeCapacityError(Exception):
    pass



def main():

    magnification = 32

    for version in (2, ):

        de = DataEncoder(version)

        append_geo_position(de)
        #append_pi(de)
        #append_mailto(de)
        #append_kanji_test(de)

        #de.append_eci_designator(899)
        #de.append_byte_mode_block('Hallo Petra!\n'.encode())
        #append_kanji(de)
        #de.append_byte_mode_block('Hallo Sidney!\n'.encode())
        #de.append_byte_mode_block('Hello ⛄ Snowman!\n'.encode())
        #de.append_numeric_mode_block("01234567")
        #de.append_byte_mode_block(b"http://www.jigsaw.nl?data=sidney")
        #de.append_byte_mode_block(b"https://www.jigsaw.nl/")

        de.append_terminator()
        de.append_padding_bits()

        data = de.get_words()

        for level in (ErrorCorrectionLevel.L, ):



            version_specification = version_specifications[(version, level)]
            block_specification = version_specification.block_specification

            qr = QRCodeDrawer(version, True)
            qr.place_quiet_zone()
            qr.place_finder_patterns()
            qr.place_separators()
            qr.place_timing_patterns()
            qr.place_alignment_patterns()

            # Place a temporary format and version information placeholders.
            # However, We need to put /something/ there to be able to find the symbol's channel bit positions
            # later on in the call to qr.get_indeterminate_positions().
            # After pattern selection, we will fill the actual format and version information.

            qr.place_format_information_placeholders()
            qr.place_version_information_placeholders()

            # ==================== Start of: set DATA/ERC code words.

            # Check if the data will fit in the selected QR code symbol.

            number_of_data_codewords = version_specification.total_number_of_codewords - version_specification.number_of_error_correcting_codewords

            if len(data) > number_of_data_codewords:
                name = f"{version_specification.version}-{version_specification.error_correction_level.name}"
                raise QRCodeCapacityError(f"Cannot fit {len(data)} data words in QR code symbol {name} ({number_of_data_codewords} data words available).")

            # Append padding to data to fill up the QR code capacity, by adding the words
            # 0b11101100, 0b00010001 alternatingly.

            pad_word = 0b11101100
            while len(data) != number_of_data_codewords:
                data.append(pad_word)
                pad_word ^= 0b11111101

            # Split up data in datablocks, and calculate the corresponding error correction blocks.

            dblocks = []
            eblocks = []

            idx = 0
            for (count, (code_c, code_k, code_r)) in version_specification.block_specification:
                # Calculate the Reed-Solomon polynomial corresponding the the number of error correction words.
                poly = calculate_reed_solomon_polynomial(code_c - code_k, strip=True)
                for rep in range(count):

                    dblock = data[idx:idx+code_k]
                    dblocks.append(dblock)

                    eblock = reed_solomon_code_remainder(dblock, poly)
                    eblocks.append(eblock)

                    idx += code_k

            assert idx == version_specification.total_number_of_codewords - version_specification.number_of_error_correcting_codewords
            assert sum(map(len, dblocks)) + sum(map(len, eblocks)) == version_specification.total_number_of_codewords

            # Interleave the data words and error correction words.
            # All data words precede all error correction words.

            channelwords = []

            k = 0
            while sum(map(len, dblocks)) != 0:
                if len(dblocks[k]) != 0:
                    channelwords.append(dblocks[k].pop(0))
                k = (k + 1) % len(dblocks)

            k = 0
            while sum(map(len, eblocks)) != 0:
                if len(eblocks[k]) != 0:
                    channelwords.append(eblocks[k].pop(0))
                k = (k + 1) % len(eblocks)

            # Convert data-words to data-bits.

            channelbits = [channelbit for word in channelwords for channelbit in enumerate_bits(word, 8)]

            # Get the module positions where the data needs to go.

            positions = qr.get_indeterminate_positions()

            assert len(channelbits) <= len(positions)

            # Add padding bits to data-bits if needed.

            num_padding_bits = len(positions) - len(channelbits)
            if num_padding_bits != 0:
                print(f"Adding {num_padding_bits} channel padding bits...")
                channelbits.extend([0] * num_padding_bits)

            #print("num positions:", len(positions))
            #print("num channelbits:", len(channelbits))

            assert len(positions) == len(channelbits)

            # Place the channel bits in the module.

            for ((i, j), channelbit) in zip(positions, channelbits):
                qr.set_module_value(i, j, ModuleValue.DATA_ERC_1 if channelbit else ModuleValue.DATA_ERC_0)

            # ==================== End of: set DATA/ERC code words.

            for pattern in DataMaskingPattern: # (DataMaskingPattern.Pattern0, ):

                qr.apply_data_masking_pattern(pattern, positions)

                qr.place_version_information_placeholders()
                qr.place_format_information_placeholders()

                # Determine score for this pattern, as per the standard.

                # Fill in the definitive version.
                qr.place_version_information_patterns()
                qr.place_format_information_patterns(level, pattern)

                # Determine actual score for this pattern, with format and version information filled in.

                # Capture image.
                im = qr.render_as_image(magnification)

                filename = f"v{version}{level.name}_p{pattern}.png"
                print(f"Saving {filename} ...")
                im.save(filename)

                # Revert to the unmasked data.
                qr.apply_data_masking_pattern(pattern, positions)


if __name__ == "__main__":
    main()
