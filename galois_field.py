#! /usr/bin/env python3

"""

GF(8) polynomial is x^8 + x^4 + x^3 + x^2 + 1

"""

exptable = 255 * [None]
logtable = 255 * [None]

element = 1
exponent = 0

while exponent < 255:
    print(element, exponent)
    exptable[exponent] = element
    logtable[element - 1] = exponent
    element <<= 1
    if element & 0b100000000:
        element ^= 0b100011101
    exponent += 1

def add_elements(a, b):
    return a ^ b

def multiply_elements(a, b):
    if (a == 0) or (b == 0):
        return 0
    log_a = logtable[a - 1]
    log_b = logtable[b - 1]

    log_ab = (log_a + log_b) % 255

    return exptable[log_ab]
