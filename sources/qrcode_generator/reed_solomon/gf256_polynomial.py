"""Polynomials over GF(256)."""

from __future__ import annotations

from .gf256 import GF256

class GF256Polynomial:

    def __init__(self, coefficients: list[GF256]):
        self.coefficients = list(coefficients)
        while len(self.coefficients) != 0 and self.coefficients[-1] == GF256.ZERO:
            self.coefficients.pop()

    def __len__(self) -> int:
        return len(self.coefficients)

    def __str__(self) -> str:
        terms = []
        for k, c in enumerate(self.coefficients):
            if k == 0:
                term = f"{c}"
            elif k == 1:
                term =  f"{c}*x"
            else:
                term = f"{c}*x^{k}"
            terms.append(term)
        if len(terms) == 0:
            return "0"
        else:
            return "+".join(term for term in reversed(terms))

    def __lshift__(self, numbits: int) -> GF256Polynomial:
        assert numbits >= 0
        return GF256Polynomial([0] * numbits + self.coefficients)

    def __mod__(self, modulo_poly: GF256Polynomial) -> GF256Polynomial:
        np = len(modulo_poly)
        if np == 0:
            raise ZeroDivisionError()
        r = self.copy()
        while True:
            nr = len(r)
            if nr < np:
                break # Done.
            multiplier = r[-1] * modulo_poly[-1]
            r -= multiplier * (modulo_poly << (nr - np))
        return r

    def copy(self) -> GF256Polynomial:
        return GF256Polynomial(self.coefficients)

    def evaluate(self, x: GF256) -> GF256:
        x_power = GF256.ONE
        r = GF256.ZERO
        for coefficient in self.coefficients:
            r += (coefficient * x_power)
            x_power *= x
        return r
