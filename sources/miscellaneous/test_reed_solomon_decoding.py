#! /usr/bin/env python3

import random

from qrcode_generator.reed_solomon_code import (calculate_reed_solomon_polynomial, reed_solomon_code_remainder, GF256,
                                                evaluate_polynomial)


def solve_linear_system(lhs, rhs):

    assert len(lhs) == len(rhs)

    n = len(lhs)

    assert all(len(row) == n for row in lhs)

    # Copy the equations.
    # We want to leave the original system of equations untouched.

    lhs = [[coefficient for coefficient in equation] for equation in lhs]
    rhs = [value for value in rhs]

    # *** FORWARD ELIMINATION SWEEP ***
    #
    # Change lhs diagonal to ones and entries below it to zeros.

    for col in range(n):

        # Find first nonzero entry, to be used as a pivot.
        for k in range(col, n):
            if lhs[k][col] != 0:
                break
        else:
            # No usable pivot found.
            return None

        assert lhs[k][col] != 0

        if k != col:
            # Exchange rows, both for the LHS and the RHS
            # print("swapping rows:", k, col)
            lhs[col], lhs[k] = lhs[k], lhs[col]
            rhs[col], rhs[k] = rhs[k], rhs[col]

        assert lhs[col][col] != 0

        # Normalize the current row so the on-diagonal entry becomes 1.
        multiplier = GF256.divide_elements(1, lhs[col][col])
        lhs[col] = [GF256.multiply_elements(multiplier, e) for e in lhs[col]]
        rhs[col] = GF256.multiply_elements(multiplier, rhs[col])

        # Use the pivot to zero the elements below it.

        for k in range(col + 1, n):
            # We will subtract a multiple of row 'col' from row k.
            multiplier = lhs[k][col]
            lhs[k] = [e1 ^ GF256.multiply_elements(multiplier, e2) for (e1, e2) in zip(lhs[k], lhs[col])]
            rhs[k] ^= GF256.multiply_elements(multiplier, rhs[col])

    # *** BACKWARD SUBSTITUTION SWEEP ***
    #
    # Turn the entries above the main diagonal into zero.

    for col in range(n - 1, -1, -1):

        pivot_value = lhs[col][col]
        assert pivot_value == 1

        for k in range(col - 1 , -1, -1):
            rhs[k] ^= GF256.multiply_elements(lhs[k][col], rhs[col])
            lhs[k][col] = 0

    return rhs


def find_error_locations(syndromes, v: int):

    # Set up a linear system for the error locator polynomial coefficients.
    lhs = []
    rhs = []
    for k in range(v):
        lhs.append([syndromes[v + k - kk - 1] for kk in range(v)])
        rhs.append(syndromes[v + k])

    # Solve the error locator polynomial coefficients.
    solution = solve_linear_system(lhs, rhs)
    if solution is None:
        # No solution was found.
        return None

    # The error locator polynomial can now be made.
    error_locator_polynomial = [1] + solution

    # The error locations are the inverse of the roots of the error locator polynomial.
    error_locations = []
    for try_root in range(256):
        value = evaluate_polynomial(error_locator_polynomial, try_root)
        if value == 0:
            inv_root = GF256.divide_elements(1, try_root)
            error_locations.append(GF256.logarithm_table[inv_root - 1])

    assert len(error_locations) == v

    return error_locations


def find_error_magnitudes(syndromes, error_locations):

    lhs = []
    rhs = []

    v = len(error_locations)

    for k in range(1, v + 1):
        lhs.append([GF256.power(2, error_locations[kk] * k) for kk in range(v)])
        rhs.append(syndromes[k])

    solution = solve_linear_system(lhs, rhs)
    if solution is None:
        raise RuntimeError("No solution found.")

    return solution


def correct_codeword(uncorrected_codeword: list[int], k: int) -> list[int]:

    n = len(uncorrected_codeword)

    num_syndromes = n - k

    syndromes = []
    alpha_power = 1
    for j in range(num_syndromes):
        syndrome = 0
        inner_alpha_power = 1
        for coefficient in reversed(uncorrected_codeword):
            syndrome ^= GF256.multiply_elements(coefficient, inner_alpha_power)
            inner_alpha_power = GF256.multiply_elements(inner_alpha_power, alpha_power)
        alpha_power = GF256.multiply_elements(alpha_power, 2) # Multiply alpha_power by alpha.
        syndromes.append(syndrome)

    error_locations_found = None
    v = num_syndromes // 2
    while v != 0:
        error_locations_found = find_error_locations(syndromes, v)
        if error_locations_found is not None:
            break
        v -= 1

    if error_locations_found is None:
        error_locations_found = []

    error_positions_found = [n - 1 - loc for loc in error_locations_found]

    error_magnitudes_found = find_error_magnitudes(syndromes, error_locations_found)

    print("error_magnitudes_found", error_magnitudes_found)

    corrected_codeword = list(uncorrected_codeword)
    for (pos, mag) in zip(error_positions_found, error_magnitudes_found):
        corrected_codeword[pos] ^= mag

    return corrected_codeword


def test_syndrome_decoding(num_errors: int):

    # From version 1-H   :  26 symbols, of which 9 are data symbols and 17 are error correction symbols.
    # From version 40-L  : 149 symbols, of which 119 are data symbols and 30 are error correction symbols.

    code_p =   1  # How many codewords are used for error detection, rather than correction.
    code_c =  26  # Total number of codewords
    code_k =   9  # Number of data keywords
    code_r =   8  # Error correction capacity

    #code_p =   0    # How many codewords are used for error detection, rather than correction.
    #code_c = 149    # Total number of codewords (traditionally this is called 'n' in most sources).
    #code_k = 119    # Number of data keywords
    #code_r =  15    # Error correction capacity (the number of errors that we *want* to correct with this code).

    assert code_c - code_k == 2 * code_r + code_p

    #
    # Initialize the testcase.
    #

    poly = calculate_reed_solomon_polynomial(code_c - code_k, strip=True)

    d_block = list(random.randbytes(code_k))

    e_block = reed_solomon_code_remainder(d_block, poly)

    de_block = d_block + e_block
    print("de_block:", de_block)

    error_positions = random.sample(range(len(de_block)), num_errors)
    print("error positions:", error_positions)

    de_block_errors = [random.randint(1, 255) if k in error_positions else 0 for k in range(len(de_block))]
    print("de_block_errors:", de_block_errors)

    de_block_received = [a ^ b for (a, b) in zip(de_block, de_block_errors)]
    print("de_block_received:", de_block_received)

    de_block_corrected = correct_codeword(de_block_received, code_k)

    assert de_block == de_block_corrected


def main():
    random.seed(123)
    for trial in range(1000):
        num_errors = random.randint(0, 8)
        test_syndrome_decoding(num_errors)
    print("bye!")


if __name__ == "__main__":
    main()
