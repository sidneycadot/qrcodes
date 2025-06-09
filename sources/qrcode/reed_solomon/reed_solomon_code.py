"""Implement Reed-Solomon codes as used in QR codes."""

from qrcode.reed_solomon.gf256 import GF256


def multiply_polynomial(pa: list[GF256], pb: list[GF256]) -> list[GF256]:

    na = len(pa)
    nb = len(pb)

    nz = na + nb - 1

    z = [GF256.ZERO] * nz

    for ia in range(na):
        for ib in range(nb):
            z[ia + ib] += pa[ia] * pb[ib]

    # Pop leading zeroes.
    while z and z[0] == GF256.ZERO:
        z.pop(0)

    return z


def calculate_reed_solomon_polynomial(n: int, *, strip: bool) -> list[int]:
    """Determine the n-degree Reed-Solomon generator polynomial used for QR codes.

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
        # The 'reed_solomon_code_remainder' routine defined below assumes that the highest power coefficient is not present.
        popped_coefficient = poly.pop(0)
        if popped_coefficient != GF256.ONE:
            raise RuntimeError(f"Expected to pop value GF256.ONE, but popped {popped_coefficient} instead.")

    return poly


def reed_solomon_code_remainder(data: list[GF256], poly: list[GF256]) -> list[GF256]:
    """Determine remainder of data(x) ** x^n + poly(x)."""

    residual = [GF256.ZERO] * len(poly)

    for d in data:

        m = residual.pop(0) + d
        residual.append(GF256.ZERO)

        for k, element in enumerate(poly):
            residual[k] -= (m *  element)

    return residual
