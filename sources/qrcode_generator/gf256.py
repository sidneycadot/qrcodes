"""Implement GF(256) as used in Reed-Solomon codes."""

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
    The GF(8) polynomial is: x^8 + x^4 + x^3 + x^2 + 1.

    Elements are represented as integers between 0 and 255 (inclusive).

    Addition and subtraction of elements corresponds to a bitwise XOR.

    Multiplication is implemented by the 'multiply_elements' method.
    """

    exponents_table, logarithm_table = make_gf256_multiplication_tables()

    @staticmethod
    def multiply_elements(a, b):
        if (a == 0) or (b == 0):
            return 0
        log_a = GF256.logarithm_table[a - 1]
        log_b = GF256.logarithm_table[b - 1]
        log_ab = (log_a + log_b) % 255

        return GF256.exponents_table[log_ab]

    @staticmethod
    def divide_elements(a, b):
        if b == 0:
            raise ZeroDivisionError()
        if a == 0:
            return 0

        log_a = GF256.logarithm_table[a - 1]
        log_b = GF256.logarithm_table[b - 1]
        log_ab = (log_a - log_b) % 255

        return GF256.exponents_table[log_ab]

    @staticmethod
    def power(a, k):
        assert a != 0
        assert k >= 0

        log_a = GF256.logarithm_table[a - 1]
        log_ak = (log_a * k) % 255

        return GF256.exponents_table[log_ak]
