#! /usr/bin/env python3

"""

GF(8) polynomial is x^8 + x^4 + x^3 + x^2 + 1



"""

exptable = 255 * [None]
logtable = 255 * [None]

element = 1
exponent = 0

while exponent < 255:
    #print(element, exponent)
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



def reed_solomon_code_remainder(data: list[int]):

    residual = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    genpoly  = [exptable[45], exptable[32], exptable[94], exptable[64], exptable[70], exptable[118], exptable[61], exptable[46], exptable[67], exptable[251]]

    for d in data:

        m = residual.pop() ^ d
        residual.insert(0, 0)

        for k in range(10):
            residual[k] ^= multiply_elements(m, genpoly[k])

    return residual

def main():

    data = [
        0b00010000,  # data
        0b00100000,
        0b00001100,
        0b01010110,
        0b01100001,
        0b10000000,
        0b11101100, # padded
        0b00010001,
        0b11101100,
        0b00010001,
        0b11101100,
        0b00010001,
        0b11101100,
        0b00010001,
        0b11101100,
        0b00010001
    ]

    erc = [
        0b10100101, # error correction codewords
        0b00100100,
        0b11010100,
        0b11000001,
        0b11101101,
        0b00110110,
        0b11000111,
        0b10000111,
        0b00101100,
        0b01010101
    ]

    calc_erc = reed_solomon_code_remainder(data)

    print("erc ........ :", " ".join(f"{x:02x}" for x in erc))
    print("calc_erc ... :", " ".join(f"{x:02x}" for x in calc_erc))


if __name__ == "__main__":
    main()
