#! /usr/bin/env python3

import random

from qrcode_generator.reed_solomon.gf256 import GF256
from qrcode_generator.reed_solomon.reed_solomon_code import calculate_reed_solomon_polynomial, reed_solomon_code_remainder
from qrcode_generator.reed_solomon.reed_solomon_decoder import correct_reed_solomon_codeword


def test_syndrome_decoding(noisy: bool=False):

    # From version 1-H  :  26 symbols, of which   9 are data symbols and 17 are error correction symbols.
    # From version 40-L : 149 symbols, of which 119 are data symbols and 30 are error correction symbols.

    use_big_code = True
    if use_big_code:
        code_p =   0  # How many codewords are used for error detection, rather than correction.
        code_c = 149  # Total number of codewords (traditionally this is called 'n' in most sources).
        code_k = 119  # Number of data keywords.
        code_r =  15  # Error correction capacity (the number of errors that we *want* to correct with this code).
    else:
        code_p =   1  # How many codewords are used for error detection, rather than correction.
        code_c =  26  # Total number of codewords (traditionally this is called 'n' in most sources).
        code_k =   9  # Number of data keywords.
        code_r =   8  # Error correction capacity (the number of errors that we *want* to correct with this code).

    assert code_c - code_k == 2 * code_r + code_p

    # Initialize the testcase.

    poly = calculate_reed_solomon_polynomial(code_c - code_k, strip=True)

    d_block = list(map(GF256, random.randbytes(code_k)))

    e_block = reed_solomon_code_remainder(d_block, poly)

    de_block = d_block + e_block
    if noisy:
        print("de_block ................ :", de_block)

    num_errors = random.randint(0, code_r)
    if noisy:
        print("num_errors .............. :", num_errors)

    error_positions = random.sample(range(len(de_block)), num_errors)
    if noisy:
        print("error positions ......... :", error_positions)

    de_block_errors = [GF256(random.randint(1, 255)) if k in error_positions else GF256.ZERO for k in range(len(de_block))]
    if noisy:
        print("de_block_errors ......... :", de_block_errors)

    de_block_received = [a - b for (a, b) in zip(de_block, de_block_errors)]
    if noisy:
        print("de_block_received ....... :", de_block_received)

    # Try to decode the received Reed-Solomon codeword.
    #
    # The 'correct_codeword' routine expects the lowest-order coefficient (i.e., the coefficient of x**0) to be the
    # first element of the codeword. However, the convention in the rest of the QR code codebase is the other way around.
    # For that reason, we reverse the uncorrected codeword passed to 'correct_codeword', and we reverse the corrected
    # codeword passed back to us.
    de_block_corrected = correct_reed_solomon_codeword(de_block_received[::-1], code_k)

    if de_block_corrected is None:
        raise RuntimeError("Unable to correct errors.")

    de_block_corrected = de_block_corrected[::-1]

    if noisy:
        print("de_block_corrected ...... :", de_block_corrected)
    if de_block_corrected != de_block:
        raise RuntimeError("Incorrectly decoded errors.")


def main():
    for trial in range(1000):
        print("trial:", trial)
        random.seed(trial)
        test_syndrome_decoding(False)
    print("bye!")


if __name__ == "__main__":
    main()
