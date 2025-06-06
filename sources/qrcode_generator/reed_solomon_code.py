"""Implement Reed-Solomon codes as used in QR codes."""

from .gf256 import GF256

def evaluate_polynomial(poly: list[GF256], x: GF256) -> int:

    x_power = GF256.ONE

    r = GF256.ZERO
    for coefficient in poly:
        r += (coefficient * x_power)
        x_power *= x

    return r

def multiply_polynomial(pa: list[GF256], pb: list[GF256]) -> list[GF256]:

    na = len(pa)
    nb = len(pb)

    nz = na + nb - 1

    z = [GF256.ZERO] * nz

    for ia in range(na):
        for ib in range(nb):
            m = pa[ia] * pb[ib]
            z[ia + ib] += pa[ia] * pb[ib]

    # Pop leading zeroes.
    while z and z[0] == GF256.ZERO:
        z.pop(0)

    return z


def calculate_reed_solomon_polynomial(n: int, *, strip: bool) -> list[int]:
    """Determine the n-degree Reed-Solomon polynomial used for QR codes.

    This function reproduces the polynomials given in Annex A of ISO/IEC 18004:2024(en).
    """
    element = GF256.ONE
    poly = [GF256.ONE]
    for k in range(n):
        factor_poly = [GF256.ONE, element]
        poly = multiply_polynomial(poly, factor_poly)
        element *= GF256.ALPHA

    if strip:
        # Strip the first high-order coefficient from the polynomial.
        # The algorithm we use for the remainder calculation assumes that
        # the highest power coefficient is not present.
        popped_coefficient = poly.pop(0)
        if popped_coefficient != GF256.ONE:
            raise RuntimeError(f"Expected to pop value GF256.ONE, but popped {popped_coefficient} instead.")

    return poly


def reed_solomon_code_remainder(data: list[GF256], poly: list[GF256]) -> list[GF256]:
    """Determine remainder of data(x) ** x^n + poly(x)."""

    residual = [GF256.ZERO] * len(poly)

    for d in data:

        m = residual.pop(0) + d  # TODO: or minus?
        residual.append(GF256.ZERO)

        for k, element in enumerate(poly):
            residual[k] -= (m *  element)

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
