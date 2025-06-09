"""A QR code decoder prototype."""

from qrcode_generator.binary_codes import format_information_code_remainder, version_information_code_remainder
from qrcode_generator.data_encoder import alphanumeric_characters
from qrcode_generator.enum_types import EncodingVariant, CharacterEncodingType
from qrcode_generator.lookup_tables import error_correction_level_encoding, data_masking_pattern_encoding, data_mask_pattern_function_table, \
    version_specification_table, count_bits_table
from qrcode_generator.qr_code import QRCodeDrawer
from qrcode_generator.reed_solomon.gf256 import GF256
from qrcode_generator.reed_solomon.reed_solomon_decoder import correct_reed_solomon_codeword


def weight(value: int) -> int:
    result = 0
    while value != 0:
        result += (value & 1)
        value >>= 1
    return result


def hamming_distance(a: int, b: int) -> int:
    return weight(a ^ b)


class DecodingError(Exception):
    pass


class BitstreamDecoder:
    def __init__(self):
        self.bits = []

    def append(self, bit: int) -> None:
        self.bits.append(bit)

    def available(self) -> int:
        return len(self.bits)

    def pop_bits(self, numbits: int) -> int:
        if numbits > len(self.bits):
            raise ValueError()
        value = 0
        while numbits != 0:
            bit = self.bits.pop(0)
            value = value * 2 + bit
            numbits -= 1
        return value


def extract_format_information(pixels, qr):
    # First, verify the single fixed "dark module" above and to the right of the bottom-left finder pattern (7.9.1).
    fixed_format_module = pixels[qr.height - 8][8]
    if fixed_format_module:
        print("Fixed format module is 1 - good!")
    else:
        print("Fixed format module is 0 - bad!")

    # Get the two format information patterns:
    # 'fa' comes from the top-left corner.
    # 'fb' comes from the secondary copy in the bottom-left and top-right corner.

    fa = 0
    fb = 0
    for ((fai, faj), (fbi, fbj)) in qr.format_bit_position_lists:
        fa = 2 * fa + pixels[fai][faj]
        fb = 2 * fb + pixels[fbi][fbj]

    # Apply XOR pattern to get the BCH codewords.
    fa ^= 0b101010000010010
    fb ^= 0b101010000010010

    # Select a format information codeword. Here, we deviate from the standard; we will
    # take into consideration *all* 30 bits simultaneously.

    distances = []
    for k in range(32):
        nominal = (k << 10) | format_information_code_remainder(k)

        fa_dist = hamming_distance(fa, nominal)
        fb_dist = hamming_distance(fb, nominal)
        # print(fa_dist, fb_dist)

        distances.append(fa_dist + fb_dist)

    min_distance = min(distances)

    print("Minimum distance for format information:", min_distance)

    best = [k for k in range(32) if distances[k] == min_distance]
    if len(best) != 1:
        raise DecodingError("No unique best format info.")

    format_information = best[0]

    print(f"Format information extracted: {format_information}")

    error_correction_level_decoding_map = dict(map(reversed, error_correction_level_encoding.items()))
    data_masking_pattern_decoding_map = dict(map(reversed, data_masking_pattern_encoding.items()))

    level_encoding = format_information >> 3
    pattern_encoding = format_information & 7

    level = error_correction_level_decoding_map[level_encoding]
    pattern = data_masking_pattern_decoding_map[pattern_encoding]

    return (level, pattern)


def extract_version_information(pixels, qr):

    # Get the two version information patterns.
    va = 0
    vb = 0
    for ((vai, vaj), (vbi, vbj)) in qr.version_bit_position_lists:
        va = 2 * va + pixels[vai][vaj]
        vb = 2 * vb + pixels[vbi][vbj]

    distances = []
    for k in range(1, 41):
        nominal = (k << 12) | version_information_code_remainder(k)

        va_dist = hamming_distance(va, nominal)
        vb_dist = hamming_distance(vb, nominal)

        distances.append(va_dist + vb_dist)

    min_distance = min(distances)

    print("Minimum distance for version information:", min_distance)

    best = [1 + k for k in range(40) if distances[k] == min_distance]
    if len(best) != 1:
        raise DecodingError("No unique best version info.")

    version_information = best[0]

    return version_information


def decode_pixels(pixels: list[list[bool]]) -> str:
    """Decode a square array of pixels as a QR code."""

    height = len(pixels)
    print(f"Input height: {height}")
    if not all(len(line) == height for line in pixels):
        raise DecodingError("2D pixel array is not square.")

    width = height
    print(f"Input width: {width}")

    width_ok = (width % 4 == 1) and (21 <= width <= 177)
    if not width_ok:
        raise DecodingError(f"Unsupported pixel array size {width}.")

    version = (width - 1) // 4 - 4
    assert (1 <= version <= 40)

    print(f"QR code version: {version}")

    # We make a QR code drawer to get access to the pixel positions of several features.
    qr = QRCodeDrawer(version, include_quiet_zone=False)

    # Extract format information bits.
    (level, pattern) = extract_format_information(pixels, qr)

    print("Format information: level =", level)
    print("Format information: data mask pattern =", pattern)

    if version < 7:
        print("This QR code version does not have version information areas.")
    else:
        version_information_extracted = extract_version_information()
        print("Version information extracted from pixels:", version_information_extracted)

        if version_information_extracted != version:
            print(f"WARNING: version mismatch (pixel size: {version} version area: {version_information_extracted}")

    # Get the data and error correction bits.
    # Apply the data mask pattern at the same time.

    pattern_function = data_mask_pattern_function_table[pattern]

    bitstream = [pixels[i][j] ^ pattern_function(i, j) for (i, j) in qr.data_and_error_correction_positions]

    bitstream = list(map(int, bitstream))

    # Chop padding bits.
    num_chop = len(bitstream) % 8
    if num_chop != 0:
        print("Dropping padding bits (normally all zero):", bitstream[-num_chop:])
        bitstream = bitstream[:-num_chop]

    assert len(bitstream) % 8 == 0

    # Convert bits to bytes.
    num_octets = len(bitstream) // 8
    octets = []
    index = 0
    for k in range(num_octets):
        octet = 0
        for bit in (7, 6, 5, 4, 3, 2, 1, 0):
            if bitstream[index]:
                octet |= (1 << bit)
            index += 1
        octets.append(octet)

    print("Extracted octets before error correction: ", ", ".join("0x{:02x}".format(octet) for octet in octets))

    version_specification = version_specification_table[(version, level)]
    print("Version_specification", version_specification)

    assert len(octets) == version_specification.total_number_of_codewords

    num_blocks = sum(count for (count, (code_c, code_k, code_r)) in version_specification.block_specification)

    print("Number of Reed-Solomon codewords to process:", num_blocks)

    block_data_length = []
    block_error_length = []
    for (count, (code_c, code_k, code_r)) in version_specification.block_specification:
        for k in range(count):
            block_data_length.append(code_k)
            block_error_length.append(code_c - code_k)

    print("Block data length expected:", block_data_length)
    print("Block error length expected:", block_error_length)

    num_data_words = sum(block_data_length)
    num_error_correction_words = sum(block_error_length)

    idx = 0

    # De-interleave data blocks.

    d_blocks = [[] for k in range(num_blocks)]

    k = 0
    while sum(map(len, d_blocks)) != num_data_words:
        if len(d_blocks[k]) < block_data_length[k]:
            d_blocks[k].append(GF256(octets[idx]))
            idx += 1
        k = (k + 1) % num_blocks

    # De-interleave error correction blocks.

    e_blocks = [[] for k in range(num_blocks)]

    k = 0
    while sum(map(len, e_blocks)) != num_error_correction_words:
        if len(e_blocks[k]) < block_error_length[k]:
            e_blocks[k].append(GF256(octets[idx]))
            idx += 1
        k = (k + 1) % num_blocks

    assert idx == len(octets)
    assert len(d_blocks) == len(e_blocks)

    # Correct the data+error codewords using the correct Reed-Solomon code.
    idx = 0
    for (count, (code_c, code_k, code_r)) in version_specification.block_specification:

        for k in range(count):

            de_block = d_blocks[idx] + e_blocks[idx]

            de_block_corrected = correct_reed_solomon_codeword(de_block[::-1], code_k)
            if de_block_corrected is None:
                print("Unable to correct codeword.")
                raise DecodingError("Cannot correct a Reed-Solomon codeword.")

            de_block_corrected = de_block_corrected[::-1]

            if de_block == de_block_corrected:
                print("No correction necessary.")
            else:
                corr = sum(a != b for (a, b) in zip(de_block, de_block_corrected))
                print(f"Corrected {corr} bad symbols:")
                print("  Corrected from ...... :", de_block)
                print("  Corrected to ........ :", de_block_corrected)

                d_blocks[idx] = de_block_corrected[:code_k]
                e_blocks[idx] = de_block_corrected[code_k:]

            idx += 1

    # Concatenate the GF256 byte values from the data blocks.

    data = []
    for d_block in d_blocks:
        data.extend(d_block)

    data = [x.value for x in data]

    print("Number of data octets after error correction:", len(data))

    # Make a bit-stream from the data bytes.

    decoder = BitstreamDecoder()
    for octet in data:
        for bit in (7, 6, 5, 4, 3, 2, 1, 0):
            decoder.append((octet >> bit) & 1)

    variant = EncodingVariant.from_version(version)

    print("Number of data bits after error correction:", decoder.available())

    # Decode data bits.

    byte_mode_encoding = 'utf_8'

    decoded_strings = []
    while True:
        if decoder.available() >= 4:
            directive = decoder.pop_bits(4)
            print(f"Found bitstream directive : {directive:04b}")
            if directive == 0b0000: # Terminator
                print("  Data terminator (0000) found.")
                octets = []
                while decoder.available() >= 8:
                    octet = decoder.pop_bits(8)
                    octets.append(octet)
                print("  Post-terminator octets: ", ", ".join("0x{:02x}".format(octet) for octet in octets))
                print("  Bits left:", decoder.bits)
                break
            elif directive == 0b0010:  # Alphanumeric mode segment.
                number_of_count_bits = count_bits_table[variant][CharacterEncodingType.ALPHANUMERIC]
                if decoder.available() < number_of_count_bits:
                    raise DecodingError("Cannot read count for alphanumeric-mode segment.")

                count = decoder.pop_bits(number_of_count_bits)

                needed_bits = (count // 2) * 11 + (count % 2) * 6
                if decoder.available() < needed_bits:
                    raise DecodingError("Not enough bits available to read alphanumeric-mode segment.")

                characters = []
                while count >= 2:
                    bits = decoder.pop_bits(11)
                    assert 0 <= bits < 45 * 45
                    characters.append(alphanumeric_characters[bits // 45])
                    characters.append(alphanumeric_characters[bits % 45])
                    count -= 2
                while count >= 1:
                    bits = decoder.pop_bits(6)
                    assert 0 <= bits < 45
                    characters.append(alphanumeric_characters[bits])
                    count -= 1
                decoded_string = "".join(characters)
                print(f"  Read {len(decoded_string)} alphanumeric characters: {decoded_string!r}")
                decoded_strings.append(decoded_string)

            elif directive == 0b0100:  # Byte mode.
                number_of_count_bits = count_bits_table[variant][CharacterEncodingType.BYTES]
                if decoder.available() < number_of_count_bits:
                    raise DecodingError("Cannot read count for byte-mode segment.")

                count = decoder.pop_bits(number_of_count_bits)
                needed_bits = count * 8
                if decoder.available() < needed_bits:
                    raise DecodingError("Not enough bits available to read byte-mode segment.")

                octets = []
                for k in range(count):
                    octet = decoder.pop_bits(8)
                    octets.append(octet)
                decoded_string = bytes(octets).decode(byte_mode_encoding)
                print(f"  Read {count} octets: ", ", ".join("0x{:02x}".format(octet) for octet in octets))
                print(f"  String interpretation ({byte_mode_encoding}): {decoded_string!r}")
                decoded_strings.append(decoded_string)

            elif directive == 0b0111:  # ECI designator.
                b1 = decoder.pop_bits(8)
                if b1 & 0x10000000 == 0b00000000:
                    # The most significant bit is 0.
                    # Values 000000 to 000127 can be represented using a single byte.
                    eci = b1
                elif b1 & 0b11000000 == 0b10000000:
                    # The two most significant bits are 10.
                    # Values 000000 to 016383 can be represented using two bytes.
                    b1 &= 0b00111111
                    b2 = decoder.pop_bits(8)
                    eci = b1 * 256 + b2
                elif b1 & 0b11100000 == 0b11000000:
                    # The three most significant bits are 110.
                    # Values 000000 to 999999 can be represented using three bytes.
                    b1 &= 0b00011111
                    b2 = decoder.pop_bits(8)
                    b3 = decoder.pop_bits(8)
                    eci = b1 * 65536 + b2 * 256 + b3
                else:
                    raise DecodingError("Bad ECI field format.")

                if not (0 <= eci <= 999999):
                    raise DecodingError(f"Bad ECI field value: {eci}.")

                if eci == 26:
                    print(f"  ECI value {eci} -- switching to UTF-8 for byte-mode segment decoding.")
                    byte_mode_encoding = 'utf_8'
                else:
                    print(f"  ECI value {eci} -- currently ignored.")

            else:
                raise NotImplementedError(f"Bitstream directive not implemented: 0b{directive:04b}.")
        else:
            print(f"No more decoding blocks, only {decoder.available()} bits available.")
            break

    decoded_string = "".join(decoded_strings)
    print(f"Decoding done. Decoded string: {decoded_string!r}")

    return decoded_string
