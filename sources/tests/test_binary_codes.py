#! /usr/bin/env -S python3 -B

"""Test binary codes used for the format and version information as described and tabulated in the standard."""

import unittest

from qrcode.binary_codes import format_information_code_remainder, version_information_code_remainder


class TestBinaryCodes(unittest.TestCase):

    def test_format_information_code_table(self):

        # From the standard, Table C.1.
        #
        # This table describes a (15, 5) BCH code with generator polynomial:
        #
        #     G(x) = x**10 + x**8 + x**5 + x**4 + x**2 + x + 1
        #
        # The generator polynomial can be expressed as a binary number 0b10100110111.
        #
        # The input is a 5-bit number.
        #
        # Note: After concatenating the remainder, the resulting 15-bit number should be XOR'ed
        # with 0b101010000010010 (for QR Code symbols) or 0b100010001000101 (for Micro QR Code symbols).

        format_information_lookup_table = {
            0b00000: 0b0000000000,
            0b00001: 0b0100110111,
            0b00010: 0b1001101110,
            0b00011: 0b1101011001,
            0b00100: 0b0111101011,
            0b00101: 0b0011011100,
            0b00110: 0b1110000101,
            0b00111: 0b1010110010,
            0b01000: 0b1111010110,
            0b01001: 0b1011100001,
            0b01010: 0b0110111000,
            0b01011: 0b0010001111,
            0b01100: 0b1000111101,
            0b01101: 0b1100001010,
            0b01110: 0b0001010011,
            0b01111: 0b0101100100,
            0b10000: 0b1010011011,
            0b10001: 0b1110101100,
            0b10010: 0b0011110101,
            0b10011: 0b0111000010,
            0b10100: 0b1101110000,
            0b10101: 0b1001000111,
            0b10110: 0b0100011110,
            0b10111: 0b0000101001,
            0b11000: 0b0101001101,
            0b11001: 0b0001111010,
            0b11010: 0b1100100011,
            0b11011: 0b1000010100,
            0b11100: 0b0010100110,
            0b11101: 0b0110010001,
            0b11110: 0b1011001000,
            0b11111: 0b1111111111
        }

        for (key, value) in format_information_lookup_table.items():
            residual = format_information_code_remainder(key)
            self.assertEqual(value, residual)

    def test_version_information_code_table(self):

        # From the standard, Table D.1.
        #
        # This table describes a (18, 6) Golay code with generator polynomial:
        #
        #     G(x) = x**12 + x**11 + x**10 + x**9 + x**8 + x**5 + x**2 + 1
        #
        # The generator polynomial can be expressed as a binary number 0b1111100100101.
        #
        # The input is a 6-bit number ranging from 7 to 40 (QR code versions 1-6 do not have the version area).

        version_information_lookup_table = {
            7: 0b000111110010010100,
            8: 0b001000010110111100,
            9: 0b001001101010011001,
            10: 0b001010010011010011,
            11: 0b001011101111110110,
            12: 0b001100011101100010,
            13: 0b001101100001000111,
            14: 0b001110011000001101,
            15: 0b001111100100101000,
            16: 0b010000101101111000,
            17: 0b010001010001011101,
            18: 0b010010101000010111,
            19: 0b010011010100110010,
            20: 0b010100100110100110,
            21: 0b010101011010000011,
            22: 0b010110100011001001,
            23: 0b010111011111101100,
            24: 0b011000111011000100,
            25: 0b011001000111100001,
            26: 0b011010111110101011,
            27: 0b011011000010001110,
            28: 0b011100110000011010,
            29: 0b011101001100111111,
            30: 0b011110110101110101,
            31: 0b011111001001010000,
            32: 0b100000100111010101,
            33: 0b100001011011110000,
            34: 0b100010100010111010,
            35: 0b100011011110011111,
            36: 0b100100101100001011,
            37: 0b100101010000101110,
            38: 0b100110101001100100,
            39: 0b100111010101000001,
            40: 0b101000110001101001
        }

        for (key, value) in version_information_lookup_table.items():
            residual = version_information_code_remainder(key)
            key_residual_concatenation = key << 12 | residual
            self.assertEqual(value, key_residual_concatenation)


if __name__ == "__main__":
    unittest.main()
