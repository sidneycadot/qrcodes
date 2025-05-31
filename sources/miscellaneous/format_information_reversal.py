#! /usr/bin/env -S python3 -B

from qrcode_generator.binary_codes import format_information_code_remainder

def bit_reverse(value: int, num_bits: int) -> int:
    assert 0 <= value < (1 << num_bits)
    r = 0
    for k in range(num_bits):
        r = (r * 2) + (value % 2)
        value //= 2
    return r

def weight(value: int) -> int:
    r = 0
    while value != 0:
        r += (value % 2)
        value //= 2
    return r

masked_format_bits = []

for format_data_bits in range(32):
    # Extend the 5-bit formation information with 10 bits of error-correction data.
    format_bits = (format_data_bits << 10) | format_information_code_remainder(format_data_bits)
    # XOR the result with a fixed pattern.
    format_bits ^= 0b101010000010010
    masked_format_bits.append(format_bits)

for format_data_bits in range(32):
    format_bits = masked_format_bits[format_data_bits]
    reversed_format_bits = bit_reverse(format_bits, 15)
    best_match = []
    best_distance = None
    for k in range(32):
        distance = weight(reversed_format_bits ^ masked_format_bits[k])
        if best_distance is None or distance < best_distance:
            best_matches = [k]
            best_distance = distance
        elif best_distance == distance:
            best_matches.append(k)

    print(f"0b{format_data_bits:05b} -- forward 0b{format_bits:015b} -- reversed 0b{reversed_format_bits:015b} -- reverse match distance {best_distance:2d} for entries {best_matches}")
