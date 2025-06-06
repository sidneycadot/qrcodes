import textwrap

from qrcode_generator.binary_codes import format_information_code_remainder, version_information_code_remainder
from qrcode_generator.enum_types import EncodingVariant, CharacterEncodingType
from qrcode_generator.lookup_tables import error_correction_level_encoding, data_masking_pattern_encoding, data_mask_pattern_function_table, \
    version_specification_table, count_bits_table
from qrcode_generator.qr_code import QRCodeDrawer
from qrcode_generator.reed_solomon.gf256 import GF256
from qrcode_generator.reed_solomon.reed_solomon_code import calculate_reed_solomon_polynomial
from qrcode_generator.reed_solomon.reed_solomon_decoder import correct_reed_solomon_codeword


def weight(value: int) -> int:
    result = 0
    while value != 0:
        result += (value & 1)
        value >>= 1
    return result


def hamming_distance(a: int, b: int) -> int:
    return weight(a ^ b)


def make_testcase_oralb():
    oralb = """
    #######.#.#.##.##.#.#.#######
    #.....#.#...#.####..#.#.....#
    #.###.#.##..##.##..##.#.###.#
    #.###.#...##.##..##.#.#.###.#
    #.###.#...#.#.....#...#.###.#
    #.....#.##..#.##..#.#.#.....#
    #######.#.#eeeeeee#.#.#######
    ........#.#eeeeeee###........
    ..###.#.#.#eeeeeee#.####..###
    #...#..##.#eeeeeee#..##.#..##
    .##.####...eeeeeee.##.....#..
    ...###.####eeeeeee##..#####..
    ##...##....eeeeeee#.##..#.##.
    #......####eeeeeee.##.#.##..#
    .#.#..###..eeeeeee.#...#..#.#
    #.#.#..#.##eeeeeee##.####.###
    ##.##.##.#.eeeeeee#..#.#.....
    ####.....#.eeeeeee##.###.#.#.
    #.#.#.#..##eeeeeee...#....#..
    #.#..#.##..eeeeeee.##.#.##.##
    #.##..#....eeeeeee#.#####..##
    ........#..eeeeeee###...##..#
    #######...#eeeeeee.##.#.####.
    #.....#.......#...###...##.##
    #.###.#.#..#######.######....
    #.###.#.########.##.###.##...
    #.###.#.##.####.###..####.##.
    #.....#..#..#.#..##..#.#.#..#
    #######...##..#..##.#.####...
    """

    lines = [line.strip() for line in textwrap.dedent(oralb.strip()).splitlines()]
    pixels = [ [(c == '#') for c in line] for line in lines]

    return pixels


def make_testcase_lego():
    lego = """
    #######.#.#.#.#.#.#######
    #.....#..#####..#.#.....#
    #.###.#.###..##...#.###.#
    #.###.#.###.#####.#.###.#
    #.###.#.#..##..##.#.###.#
    #.....#.#.##.#....#.....#
    #######.#.#.#.#.#########
    ........#.#.#.###........
    ####..#.#.##..####..###.#
    #.#.#.....#.##..#..#...#.
    ###...#..###.....#.##....
    ###....####.##.##.#..##..
    .##...##.#######.##.#.###
    .#.###...#....#######...#
    .###..###.#..#...###..###
    #.##...#.#.#..####...#..#
    .....##...#..#..#########
    ........######..#...#...#
    #######..#..#...#.#.#####
    #.....#..##.#..##...#...#
    #.###.#....#..#.#####...#
    #.###.#.##.##.##.##.#.###
    #.###.#.#####..#.#######.
    #.....#.####.#.#.##.#.#..
    #######.##...##....######
    """

    lines = [line.strip() for line in textwrap.dedent(lego.strip()).splitlines()]
    pixels = [ [(c == '#') for c in line] for line in lines]

    return pixels


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


def decode_pixels(pixels):
    height = len(pixels)
    print(f"input height {height}")
    if not all(len(line) == height for line in pixels):
        raise RuntimeError("2D pixel array is not square.")

    width = height
    print(f"input width {width}")

    if not (width % 4 == 1):
        raise RuntimeError("Unexpected width.")

    version = (width - 17) // 4
    if not (1 <= version <= 40):
        raise RuntimeError("Unexpected version.")

    print(f"version: {version}")

    qr = QRCodeDrawer(version, include_quiet_zone=False)

    # Get format bits.

    # Get the single fixed "dark module" above and to the right of the bottom-left finder pattern (7.9.1).
    fixed_format_module = pixels[height - 8][8]
    print("fixed_format_module", fixed_format_module)
    assert fixed_format_module == True

    # Get the two format information patterns.
    fa = 0
    fb = 0
    for ((fai, faj), (fbi, fbj)) in qr.format_bit_position_lists:
        fa = 2 * fa + pixels[fai][faj]
        fb = 2 * fb + pixels[fbi][fbj]

    print(f"fa before XOR: 0b{fa:015b}")
    print(f"fb before XOR: 0b{fb:015b}")

    fa ^= 0b101010000010010
    fb ^= 0b101010000010010

    print(f"fa after XOR: 0b{fa:015b}")
    print(f"fb after XOR: 0b{fb:015b}")

    distances = []
    for k in range(32):
        nominal = (k << 10) | format_information_code_remainder(k)

        fa_dist = hamming_distance(fa, nominal)
        fb_dist = hamming_distance(fb, nominal)
        print(fa_dist, fb_dist)

        distances.append(fa_dist + fb_dist)

    min_distance = min(distances)

    print("min distance for format information:", min_distance)

    best = [k for k in range(32) if distances[k] == min_distance]
    if len(best) != 1:
        raise RuntimeError()

    format_information = best[0]

    print(f"format information: {format_information}")

    error_correction_level_decoding_map = dict(map(reversed, error_correction_level_encoding.items()))
    data_masking_pattern_decoding_map = dict(map(reversed, data_masking_pattern_encoding.items()))
    level_encoding = format_information >> 3
    pattern_encoding = format_information & 7

    level = error_correction_level_decoding_map[level_encoding]
    pattern = data_masking_pattern_decoding_map[pattern_encoding]

    print("Extracted level:", level)
    print("Extracted pattern:", pattern)

    if version >= 7:
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

        print("min distance for version information:", min_distance)

        best = [1 + k for k in range(40) if distances[k] == min_distance]
        if len(best) != 1:
            raise RuntimeError()

        version_information = best[0]

        print("version information:", version_information)

        if version_information != version:
            raise RuntimeError()

    # Get the data and error correction bits.
    # Apply the data mask pattern at the same time.

    pattern_function = data_mask_pattern_function_table[pattern]

    bitstream = [pixels[i][j] ^ pattern_function(i, j) for (i, j) in qr.data_and_error_correction_positions]

    bitstream = list(map(int, bitstream))

    # Chop padding bits.
    num_chop = len(bitstream) % 8
    if num_chop != 0:
        assert all(bit == 0 for bit in bitstream[-num_chop:])
        bitstream = bitstream[:-num_chop]

    assert len(bitstream) % 8 == 0

    # Bits to bytes.
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

    print("octets:", octets)

    version_specification = version_specification_table[(version, level)]

    assert len(octets) == version_specification.total_number_of_codewords

    num_blocks = sum(count for (count, (code_c, code_k, code_r)) in version_specification.block_specification)

    print("number of code blocks:", num_blocks)

    block_data_length = []
    block_error_length = []
    for (count, (code_c, code_k, code_r)) in version_specification.block_specification:
        for k in range(count):
            block_data_length.append(code_k)
            block_error_length.append(code_c - code_k)

    print("block data length expected:", block_data_length)
    print("block error length expected:", block_error_length)

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

    # Verify and/or correct the data polynomials.
    idx = 0
    for (count, (code_c, code_k, code_r)) in version_specification.block_specification:
        poly = calculate_reed_solomon_polynomial(code_c - code_k, strip=True)
        for k in range(count):
            de_block = d_blocks[idx] + e_blocks[idx]

            de_block_corrected = correct_reed_solomon_codeword(de_block[::-1], code_k)
            de_block_corrected = de_block_corrected[::-1]

            if de_block == de_block_corrected:
                print("No correction necessary!")
            else:
                corr = sum(a != b for (a, b) in zip(de_block, de_block_corrected))
                print(f"Corrected {corr} error symbols:")
                print("  Corrected from:", de_block)
                print("  Corrected to:", de_block_corrected)

            d_blocks[idx] = de_block_corrected[:code_k]
            e_blocks[idx] = de_block_corrected[code_k:]

            idx += 1

    data = []
    for d_block in d_blocks:
        data.extend(d_block)

    data = [x.value for x in data]

    print("number of data octets:", len(data))

    # Turn it into a bit-stream:
    decoder = BitstreamDecoder()
    for octet in data:
        for bit in (7, 6, 5, 4, 3, 2, 1, 0):
            decoder.append((octet >> bit) & 1)

    variant = EncodingVariant.from_version(version)

    print("bits in decoder:", decoder.available())
    print(decoder.bits)

    while True:
        if decoder.available() >= 4:
            directive = decoder.pop_bits(4)
            print("directive", directive)
            if directive == 0b0000: # Terminator
                print("found terminator.")
                while decoder.available() >= 8:
                    octet = decoder.pop_bits(8)
                    print(f"post-terminator octet: 0x{octet:02x}")
                print("bits left:", decoder.bits)
                break
            elif directive == 0b0100:  # Bytes mode.
                number_of_count_bits = count_bits_table[variant][CharacterEncodingType.BYTES]
                if decoder.available() >= number_of_count_bits:
                    count = decoder.pop_bits(number_of_count_bits)
                    if decoder.available() >= count * 8:
                        octets = []
                        for k in range(count):
                            octet = decoder.pop_bits(8)
                            octets.append(octet)
                        octet_string = bytes(octets).decode('utf_8')
                        print(f"Read {count} bytes: {octets} {octet_string!r}")
                    else:
                        raise RuntimeError("Not enough bits.")
                else:
                    raise RuntimeError("Cannot read count.")
            elif directive == 0b1001:  # FNC1 indicator, second position.
                b1 = decoder.pop_bits(8)
                print("FNC1, second position directive:", b1)
            elif directive == 0b0111:  # ECI designator.
                b1 = decoder.pop_bits(8)
                assert b1 <= 127
                print("ECI directive:", b1)
            else:
                raise RuntimeError(f"Bad directive value {directive}.")
        else:
            print(f"No more decoding blocks, only {decoder.available()} bits available.")
            break


def main():
    #pixels = make_testcase_oralb()
    pixels = make_testcase_lego()

    decode_pixels(pixels)


if __name__ == "__main__":
    main()
