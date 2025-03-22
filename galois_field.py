#! /usr/bin/env python3

"""Implement Reed-Solomon codes as used in QR codes."""

def make_gf8_multiplication_tables():

    exptable = 255 * [0]
    logtable = 255 * [0]

    element = 1
    exponent = 0

    while exponent < 255:
        exptable[exponent] = element
        logtable[element - 1] = exponent
        element <<= 1
        if element & 0b100000000:
            element ^= 0b100011101
        exponent += 1

    return exptable, logtable

class GF8:
    """
    GF(8) generator polynomial is x^8 + x^4 + x^3 + x^2 + 1.

    Elements are represented as integers between 0 and 255 (inclusive).

    Addition and subtraction of elements corresponds to a bitwise XOR.

    Multiplication is implemented by the 'multiply_elements' method.
    """


    exptable, logtable = make_gf8_multiplication_tables()

    @staticmethod
    def multiply_elements(a, b):
        if (a == 0) or (b == 0):
            return 0
        log_a = GF8.logtable[a - 1]
        log_b = GF8.logtable[b - 1]
        log_ab = (log_a + log_b) % 255

        return GF8.exptable[log_ab]

def reed_solomon_code_remainder(data: list[int]):

    genpoly  = [GF8.exptable[251], GF8.exptable[67], GF8.exptable[46], GF8.exptable[61], GF8.exptable[118], GF8.exptable[70], GF8.exptable[64], GF8.exptable[94], GF8.exptable[32], GF8.exptable[45]]

    residual = [0 for g in genpoly]

    for d in data:

        m = residual.pop(0) ^ d
        residual.append(0)

        for k, g in enumerate(genpoly):
            residual[k] ^= GF8.multiply_elements(m, g)

    return residual



def test_reed_solomon_example():

    data = [
        0b00010000,  # data
        0b00100000,
        0b00001100,
        0b01010110,
        0b01100001,
        0b10000000,
        0b11101100, # padded
        0b00010001,
        0b11101100,
        0b00010001,
        0b11101100,
        0b00010001,
        0b11101100,
        0b00010001,
        0b11101100,
        0b00010001
    ]

    erc = [
        0b10100101, # error correction codewords
        0b00100100,
        0b11010100,
        0b11000001,
        0b11101101,
        0b00110110,
        0b11000111,
        0b10000111,
        0b00101100,
        0b01010101
    ]

    calc_erc = reed_solomon_code_remainder(data)
    calc_erc_cat = reed_solomon_code_remainder(data + erc)

    print("erc ............ :", " ".join(f"{x:02x}" for x in erc))
    print("calc_erc ....... :", " ".join(f"{x:02x}" for x in calc_erc))
    print("calc_erc_cat ... :", " ".join(f"{x:02x}" for x in calc_erc_cat))

def calculate_generator_polynomial(n: int):
    pass

def main():
    test_reed_solomon_example()

if __name__ == "__main__":
    main()
