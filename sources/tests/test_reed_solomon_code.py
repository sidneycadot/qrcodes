#! /usr/bin/env -S python3 -B

"""Test Reed-Solomon code implementation."""

import unittest

from qrcode.reed_solomon.reed_solomon_code import calculate_reed_solomon_polynomial, reed_solomon_code_remainder


class TestReedSolomonCode(unittest.TestCase):

    def test_reed_solomon_example(self):

        data = [
            0b00010000,  # data
            0b00100000,
            0b00001100,
            0b01010110,
            0b01100001,
            0b10000000,
            0b11101100,  # padding
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
            0b10100101,  # error correction codewords
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

        poly = calculate_reed_solomon_polynomial(10, strip=True)

        calc_erc = reed_solomon_code_remainder(data, poly)
        self.assertEqual(calc_erc, erc)

        calc_erc_cat = reed_solomon_code_remainder(data + erc, poly)
        self.assertTrue(all(e == 0 for e in calc_erc_cat))


if __name__ == "__main__":
    unittest.main()
