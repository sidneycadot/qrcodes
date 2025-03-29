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


def multiply_polynomial(pa: list[int], pb: list[int]) -> list[int]:

    na = len(pa)
    nb = len(pb)

    nz = na + nb - 1

    z = [0] * nz

    for ia in range(na):
        for ib in range(nb):
            m = GF8.multiply_elements(pa[ia], pb[ib])
            z[ia + ib] ^= m

    while z[0] == 0:
        z.pop(0)

    return z


def calculate_reed_solomon_polynomial(n: int, *, strip: bool) -> list[int]:
    element = 1
    poly = [1]
    for k in range(n):
        factor_poly = [1, element]
        poly = multiply_polynomial(poly, factor_poly)
        element <<= 1
        if element & 0b100000000:
            element ^= 0b100011101

    if strip:
        # Strip the first alement from the polynomial.
        # The algorithm we use for the remainder calculation assumes the highest
        # power is not present.
        popped_coefficient = poly.pop(0)
        if popped_coefficient != 1:
            raise RuntimeError()

    return poly

def reed_solomon_code_remainder(data: list[int], poly: list[int]) -> list[int]:

    residual = [0 for g in poly]

    for d in data:

        m = residual.pop(0) ^ d
        residual.append(0)

        for k, element in enumerate(poly):
            residual[k] ^= GF8.multiply_elements(m, element)

    return residual


def poly_string(poly: list[int], prepend_prefix_term: bool) -> str:

    terms = []

    n = len(poly)

    if prepend_prefix_term:
        term = (0, n)
        terms.append(term)

    for (k, c) in enumerate(poly):
        if c != 0:
            term = (GF8.logtable[c- 1], n - k - 1)
            terms.append(term)

    term_strings = []

    for (alpha_exponent, x_exponent) in terms:
        factors = []
        if alpha_exponent == 0:
            pass
        elif alpha_exponent == 1:
            factors.append("α")
        else:
            factors.append("α^{}".format(alpha_exponent))
        if x_exponent == 0:
            pass
        elif x_exponent == 1:
            factors.append("x")
        else:
            factors.append("x^{}".format(x_exponent))
        if len(factors) == 0:
            term_strings.append("1")
        else:
            term_strings.append("*".join(factors))

    if len(term_strings) == 0:
        expr_str = "0"
    else:
        expr_str = " + ".join(term_strings)

    return expr_str
