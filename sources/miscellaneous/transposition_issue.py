#! /usr/bin/env puthon3

from collections import Counter

from qrcode.binary_codes import format_information_code_remainder
from qrcode.lookup_tables import error_correction_level_encoding, data_masking_pattern_encoding


def reverse(n: int, numbits: int) -> int:
    r = 0
    for k in range(numbits):
        r = (r * 2) + (n % 2)
        n //= 2
    return r

def weight(n: int) -> int:
    r = 0
    while n != 0:
        r += (n % 2)
        n //= 2
    return r


def make_format_bits(format_data_bits: int) -> int:
    assert 0 <= format_data_bits <= 31
    format_bits = (format_data_bits << 10) | format_information_code_remainder(format_data_bits)
    # XOR the result with a fixed pattern.
    format_bits ^= 0b101010000010010
    return format_bits


def code_distance():
    counter = Counter()
    for k1 in range(32):
        for k2 in range(32):
            d = weight(make_format_bits(k1) ^ make_format_bits(k2))
            counter[d] += 1
    print(counter)


def find_best(bits: int):
    best_weight = None
    best_solutions = []
    for format_data_bits in range(32):
        format_bits = make_format_bits(format_data_bits)
        w = weight(format_bits ^ bits)
        if best_weight is None or w < best_weight:
            best_weight = w
            best_solutions = [format_data_bits]
        elif w == best_weight:
            best_solutions.append(format_data_bits)
    return (best_weight, best_solutions)


def main():
    solutions = {}
    for bits in range(32768):
        if bits != reverse(bits, 15):
            continue
        if bits & 0b000000010000000 == 0:
            continue
        bw, bs = find_best(bits)
        if len(bs) != 1:
            continue
        bs = bs[0]
        if bs not in solutions:
            solutions[bs] = []
        solutions[bs].append((bw, bits))

    error_correction_level_decoding_map = dict(map(reversed, error_correction_level_encoding.items()))
    data_masking_pattern_decoding_map = dict(map(reversed, data_masking_pattern_encoding.items()))

    for format_information in sorted(solutions.keys()):
        level_encoding = format_information >> 3
        pattern_encoding = format_information & 7

        level = error_correction_level_decoding_map[level_encoding]
        pattern = data_masking_pattern_decoding_map[pattern_encoding]

        print(f"# {format_information}: {level} {pattern}")

        for option in solutions[format_information]:
            print(f"#     {option[0]} --> {option[1]:015b}")

if __name__ == "__main__":
    main()
