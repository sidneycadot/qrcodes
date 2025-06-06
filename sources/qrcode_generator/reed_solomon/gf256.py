"""Implement GF(256) as used in Reed-Solomon codes."""

from __future__ import annotations

def make_gf256_multiplication_tables():

    exponents_table = 255 * [0]
    logarithm_table = 255 * [0]

    element = 1
    exponent = 0

    while exponent < 255:
        exponents_table[exponent] = element
        logarithm_table[element - 1] = exponent
        element <<= 1
        if element & 0b100000000:
            element ^= 0b100011101
        exponent += 1

    assert all(x is not None for x in exponents_table)
    assert all(x is not None for x in logarithm_table)

    return exponents_table, logarithm_table


class GF256:
    """
    The Galois Field of order 256.

    It is constructed using the polynomial p(x) that is irreducible over Z(2):

       p(x) = x^8 + x^4 + x^3 + x^2 + 1.

    The root of this polynomial is denoted as alpha.

    Elements are represented as integers between 0 and 255 (inclusive).

    Addition and subtraction of elements corresponds to a bitwise XOR.

    Multiplication is implemented by the 'multiply_elements' method.
    """

    ZERO  = None  # Will be redefined after the class definition.
    ONE   = None  # Will be redefined after the class definition.
    ALPHA = None  # Will be redefined after the class definition.

    exponents_table, logarithm_table = make_gf256_multiplication_tables()

    def __init__(self, value):
        assert 0 <= value <= 255
        self.value = value

    def __repr__(self) -> str:
        return f"g{self.value}"

    def __eq__(self, other: GF256) -> bool:
        assert isinstance(other, GF256)
        return self.value == other.value

    def __add__(self, other: GF256) -> GF256:
        assert isinstance(other, GF256)
        return GF256(self.value ^ other.value)

    def __sub__(self, other: GF256) -> GF256:
        assert isinstance(other, GF256)
        return GF256(self.value ^ other.value)

    def __mul__(self, other: GF256) -> GF256:
        assert isinstance(other, GF256)
        if (self == GF256.ZERO) or (other == GF256.ZERO):
            return GF256.ZERO
        return GF256.exp(GF256.log(self) + GF256.log(other))

    def __truediv__(self, other: GF256) -> GF256:
        assert isinstance(other, GF256)
        if other == GF256.ZERO:
            raise ZeroDivisionError()
        multiplicative_inverse = other ** (-1)
        return self * multiplicative_inverse

    def __pow__(self, k: int) -> GF256:
        assert isinstance(k, int)
        if self == GF256.ZERO:
            return GF256.ZERO
        return GF256.exp(GF256.log(self) * k)

    @staticmethod
    def log(x: GF256) -> int:
        if x == GF256.ZERO:
            raise ValueError()
        return GF256.logarithm_table[x.value - 1]

    @staticmethod
    def exp(k: int) -> GF256:
        return GF256.exponents_table[k % 255]

GF256.ZERO  = GF256(0)
GF256.ONE   = GF256(1)
GF256.ALPHA = GF256(2)

GF256.exponents_table = [GF256(x) for x in GF256.exponents_table]
