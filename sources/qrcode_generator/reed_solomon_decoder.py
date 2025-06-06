"""Reed-Solomon decoder."""

from typing import Optional

from qrcode_generator.gf256 import GF256
from qrcode_generator.reed_solomon_code import evaluate_polynomial


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
            if lhs[k][col] != GF256.ZERO:
                break
        else:
            # No usable pivot found.
            return None

        assert lhs[k][col] != GF256.ZERO

        if k != col:
            # Exchange rows, both for the LHS and the RHS
            # print("swapping rows:", k, col)
            lhs[col], lhs[k] = lhs[k], lhs[col]
            rhs[col], rhs[k] = rhs[k], rhs[col]

        assert lhs[col][col] != GF256(0)

        # Normalize the current row so the on-diagonal entry becomes 1.
        multiplier = GF256(1) / lhs[col][col]
        lhs[col] = [(multiplier * e) for e in lhs[col]]
        rhs[col] = multiplier * rhs[col]

        # Use the pivot to zero the elements below it.

        for k in range(col + 1, n):
            # We will subtract a multiple of row 'col' from row k.
            multiplier = lhs[k][col]
            lhs[k] = [e1 - (multiplier * e2) for (e1, e2) in zip(lhs[k], lhs[col])]
            rhs[k] -= (multiplier * rhs[col])

    # *** BACKWARD SUBSTITUTION SWEEP ***
    #
    # Turn the entries above the main diagonal into zero.

    for col in range(n - 1, -1, -1):

        pivot_value = lhs[col][col]
        assert pivot_value == GF256.ONE

        for k in range(col - 1 , -1, -1):
            rhs[k] -= (lhs[k][col] * rhs[col])
            lhs[k][col] = GF256.ZERO

    return rhs


def find_error_locations_inverse(syndromes: list[GF256], v: int):
    """Find the error locations, based on the 'inverse' form of the error location polynomial, Λ(x)."""

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
    error_locator_polynomial = [GF256(1)] + solution
    #print("error_locator_polynomial Λ(x)", error_locator_polynomial)

    # The error locations are the inverse of the roots of the error locator polynomial.
    error_locations = []
    for root_value in range(256):
        try_root = GF256(root_value)
        value = evaluate_polynomial(error_locator_polynomial, try_root)
        if value == GF256.ZERO:
            inv_root = GF256.ONE / try_root
            error_locations.append(GF256.log(inv_root))

    #assert len(error_locations) == v

    return error_locations


def find_error_locations_direct(syndromes: list[GF256], v: int):
    """Find the error locations, based on the 'direct' form of the error location polynomial, σ(x)."""

    # Set up a linear system for the error locator polynomial coefficients.
    lhs = []
    rhs = []
    for k in range(v):
        lhs.append([syndromes[k +kk] for kk in range(v)])
        rhs.append(syndromes[v + k])

    # Solve the error locator polynomial coefficients.
    solution = solve_linear_system(lhs, rhs)
    if solution is None:
        # No solution was found.
        return None

    # The error locator polynomial can now be made.
    error_locator_polynomial = solution + [GF256(1)]
    #print("error_locator_polynomial σ(x)", error_locator_polynomial)

    # The error locations are the roots of the error locator polynomial.
    error_locations = []
    for root_value in range(256):
        try_root = GF256(root_value)
        value = evaluate_polynomial(error_locator_polynomial, try_root)
        if value == GF256.ZERO:
            error_locations.append(GF256.logarithm_table[try_root.value - 1])

    #assert len(error_locations) == v

    return error_locations


def find_error_magnitudes(syndromes, error_locations):

    lhs = []
    rhs = []

    v = len(error_locations)

    for k in range(1, v + 1):
        lhs.append([GF256.ALPHA ** (error_locations[kk] * k) for kk in range(v)])
        rhs.append(syndromes[k])

    solution = solve_linear_system(lhs, rhs)
    if solution is None:
        raise RuntimeError("No solution found.")

    return solution


def correct_codeword(uncorrected_codeword: list[GF256], k: int) -> Optional[list[GF256]]:
    """Correct a received reed-solomon codeword."""
    n = len(uncorrected_codeword)

    num_syndromes = n - k

    syndromes = []
    alpha_power = GF256.ONE
    for j in range(num_syndromes):
        syndrome = GF256.ZERO
        inner_alpha_power = GF256.ONE
        for coefficient in uncorrected_codeword:
            syndrome += (coefficient * inner_alpha_power)
            inner_alpha_power *= alpha_power
        alpha_power *= GF256.ALPHA
        syndromes.append(syndrome)

    if all(syndrome == GF256(0) for syndrome in syndromes):
        return uncorrected_codeword

    error_locations = None
    v = num_syndromes // 2
    while v != 0:
        error_locations = find_error_locations_inverse(syndromes, v)
        if error_locations is not None:
            break
        v -= 1

    if error_locations is None:
        # Unable to decode.
        return None

    error_magnitudes = find_error_magnitudes(syndromes, error_locations)

    corrected_codeword = uncorrected_codeword.copy()
    for (error_location, error_magnitude) in zip(error_locations, error_magnitudes):
        corrected_codeword[error_location] -= error_magnitude

    return corrected_codeword
