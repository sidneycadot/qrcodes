#! /usr/bin/env puthon3

from collections import Counter

from qrcode.binary_codes import format_information_code_remainder


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
    counter = Counter()
    for bits in range(32768):
        rbits = reverse(bits, 15)
        (bw, bs) = find_best(bits)
        (rbw, rbs) = find_best(rbits)

        if bw <= 3 and rbw == 0 and len(rbs) == 1:
            print(bits, bw, bs, "***", rbits, rbw, rbs)
        counter[(bw, len(bs), rbw, len(rbs))] += 1
    print(counter)


if __name__ == "__main__":
    main()

# 9237 3 [28] *** 21522 0 [0]
#
# 0: 101010000010010
#
# mirror:
#
#  010010000010101
#  010010010110100
# ----------------
#  000000010100001


#
# (3, 1, 3, 1): 6132,  Ambiguous
# (3, 1, 2, 1): 1656,  Ambiguous
# (2, 1, 3, 1): 1656,  Ambiguous
# (2, 1, 2, 1): 252,   Ambiguous
# (1, 1, 3, 1): 168,   Ambiguous
# (3, 1, 1, 1): 168,   Ambiguous
# (1, 1, 2, 1): 78,    Ambiguous
# (2, 1, 1, 1): 78,    Ambiguous
# (0, 1, 3, 1): 26,    Ambiguous
# (3, 1, 0, 1): 26,    Ambiguous
