"""Reed-Solomon decoder.

Decoding a (possibly garbled) Reed-Solomon codeword is a five-step process:

(1) Calculate the syndrome values S[j] for 0 <= k < (n - k).

    If the Syndromes are all zero, the word is accepted as-is.
    No error occurred during transmission.

(2) Find the location of the error(s).

    Several methods exist; we implement the simplest one here, that expresses the error locator
    values X[j] as roots of a so-called 'error locator polynomial', which is called σ(x).

    Note: There is an alternative form of the error locator polynomial, called Λ(x),
    which has the INVERSES of the locator values X[j] as its roots.

    (2a) The coefficients of σ(x) are determined by solving a linear system of equations.
    (2b) The roots of σ(x) are found by trying each possible value of x in succession.

    A way of doing this that aims to minimize the operation count is "Chien search".

    Alternative algorithms:
    - Berlekamp-Massey.
    - Euclidean GCD

(3) Find the magnitude of the error(s).

    Several methods exist; we implement the simplest one here, that finds the error magnitudes
    as solutions of a linear system of equations.

    Alternative algorithms:
    - Fossey

(4) Correct the error.
"""

from typing import Optional

from qrcode_generator.reed_solomon.gf256 import GF256
from qrcode_generator.reed_solomon.gf256_polynomial import GF256Polynomial


def solve_linear_system(lhs, rhs):
    """Solve a linear system A.x == b over GF(256)."""

    assert len(lhs) == len(rhs)

    n = len(lhs)

    assert all(len(row) == n for row in lhs)

    # Copy the equations.
    # We want to leave the original system of equations untouched.

    lhs = [[coefficient for coefficient in equation] for equation in lhs]
    rhs = [value for value in rhs]

    # Forward sweep: Change diagonal of LHS to ones and entries below it to zeros.

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

        assert lhs[col][col] != GF256.ZERO

        # Normalize the current row so the on-diagonal entry becomes 1.
        multiplier = GF256.ONE / lhs[col][col]
        lhs[col] = [(multiplier * e) for e in lhs[col]]
        rhs[col] = multiplier * rhs[col]

        # Use the pivot to zero the elements below it.

        for k in range(col + 1, n):
            # We will subtract a multiple of row 'col' from row k.
            multiplier = lhs[k][col]
            lhs[k] = [e1 - (multiplier * e2) for (e1, e2) in zip(lhs[k], lhs[col])]
            rhs[k] -= (multiplier * rhs[col])

    # Backward sweep: Turn the entries above the main diagonal of LHS into zero.

    for col in range(n - 1, -1, -1):

        pivot_value = lhs[col][col]
        assert pivot_value == GF256.ONE

        for k in range(col - 1 , -1, -1):
            rhs[k] -= (lhs[k][col] * rhs[col])
            lhs[k][col] = GF256.ZERO

    # We have turned the system of equations into an equivalent system where the LHS is the identiry matrix.
    # Therefore, the RHS is now equal to the solution of the system.

    return rhs


def find_error_locations_direct(syndromes: list[GF256], n: int, v: int):
    """Find the error locations, based on the 'direct' form of the error location polynomial, σ(x)."""

    # Set up a linear system for the error locator polynomial coefficients.
    lhs = []
    rhs = []
    for k in range(v):
        lhs.append([syndromes[k + kk] for kk in range(v)])
        rhs.append(syndromes[v + k])

    # Solve the error locator polynomial coefficients.
    solution = solve_linear_system(lhs, rhs)
    if solution is None:
        # No solution was found.
        return None

    # The error locator polynomial can now be made.
    error_locator_polynomial = GF256Polynomial(solution + [GF256.ONE])
    # print(f"error_locator_polynomial σ(x) = {error_locator_polynomial}")

    error_locations = []
    for location in range(n):
        x = GF256.exp(location)
        value = error_locator_polynomial.evaluate(x)
        if value == GF256.ZERO:
            error_locations.append(location)

    if len(error_locations) < v:
        return None

    return error_locations


def find_error_locations_inverse(syndromes: list[GF256], n: int, v: int):
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
    error_locator_polynomial = GF256Polynomial([GF256.ONE] + solution)
    # print(f"error_locator_polynomial Λ(x) = {error_locator_polynomial}")

    # The error locations are the inverse of the roots of the error locator polynomial.
    error_locations = []
    for location in range(n):
        x = GF256.exp(-location)
        value = error_locator_polynomial.evaluate(x)
        if value == GF256.ZERO:
            error_locations.append(location)

    if len(error_locations) < v:
        return None

    return error_locations


def find_error_magnitudes(syndromes, error_locations):

    lhs = []
    rhs = []

    v = len(error_locations)

    for k in range(1, v + 1):
        lhs.append([GF256.exp(error_locations[kk] * k) for kk in range(v)])
        rhs.append(syndromes[k])

    solution = solve_linear_system(lhs, rhs)
    if solution is None:
        raise RuntimeError("No solution found.")

    return solution


def correct_reed_solomon_codeword(uncorrected_codeword: list[GF256], k: int) -> Optional[list[GF256]]:
    """Correct a received Reed-Solomon codeword that may contain errors.

    If decoding fails, None is returned.
    """

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

    if all(syndrome == GF256.ZERO for syndrome in syndromes):
        # The codeword does not contain errors.
        return uncorrected_codeword

    error_locations = None

    # We need to try the most errors first.
    v = num_syndromes // 2
    while v != 0:
        error_locations = find_error_locations_direct(syndromes, n, v)  # We can use either the 'direct' or 'inverse' method here.
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
