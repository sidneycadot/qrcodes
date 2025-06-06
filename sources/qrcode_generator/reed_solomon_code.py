"""Implement Reed-Solomon codes as used in QR codes."""

from .gf256 import GF256

def evaluate_polynomial(poly: list[int], x: int) -> int:

    x_power = 1

    r = 0
    for coefficient in poly:
        r ^= GF256.multiply_elements(coefficient, x_power)
        x_power = GF256.multiply_elements(x_power, x)

    return r

def multiply_polynomial(pa: list[int], pb: list[int]) -> list[int]:

    na = len(pa)
    nb = len(pb)

    nz = na + nb - 1

    z = [0] * nz

    for ia in range(na):
        for ib in range(nb):
            z[ia + ib] ^= GF256.multiply_elements(pa[ia], pb[ib])

    # Pop leading zeroes.
    while z and z[0] == 0:
        z.pop(0)

    return z


def calculate_reed_solomon_polynomial(n: int, *, strip: bool) -> list[int]:
    """Determine the n-degree Reed-Solomon polynomial used for QR codes.

    This function reproduces the polynomials given in Annex A of ISO/IEC 18004:2024(en).
    """
    element = 1
    poly = [1]
    for k in range(n):
        factor_poly = [1, element]
        poly = multiply_polynomial(poly, factor_poly)
        element <<= 1
        if element & 0b100000000:
            element ^= 0b100011101

    if strip:
        # Strip the first high-order coefficient from the polynomial.
        # The algorithm we use for the remainder calculation assumes that
        # the highest power coefficient is not present.
        popped_coefficient = poly.pop(0)
        if popped_coefficient != 1:
            raise RuntimeError()

    return poly


def reed_solomon_code_remainder(data: list[int], poly: list[int]) -> list[int]:
    """Determine remainder of data(x) ** x^n + poly(x)."""

    residual = [0] * len(poly)

    for d in data:

        m = residual.pop(0) ^ d
        residual.append(0)

        for k, element in enumerate(poly):
            residual[k] ^= GF256.multiply_elements(m, element)

    return residual


def poly_string(poly: list[int], prepend_prefix_term: bool) -> str:
    """Represent a GF256 polynomial as a string."""
    terms = []

    n = len(poly)

    if prepend_prefix_term:
        term = (0, n)
        terms.append(term)

    for (k, c) in enumerate(poly):
        if c != 0:
            term = (GF256.logarithm_table[c - 1], n - k - 1)
            terms.append(term)

    term_strings = []

    for (alpha_exponent, x_exponent) in terms:
        factors = []
        if alpha_exponent == 0:
            pass
        elif alpha_exponent == 1:
            factors.append("α")
        else:
            factors.append(f"α^{alpha_exponent}")
        if x_exponent == 0:
            pass
        elif x_exponent == 1:
            factors.append("x")
        else:
            factors.append(f"x^{x_exponent}")
        if len(factors) == 0:
            term_strings.append("1")
        else:
            term_strings.append("*".join(factors))

    if len(term_strings) == 0:
        expr_str = "0"
    else:
        expr_str = " + ".join(term_strings)

    return expr_str
