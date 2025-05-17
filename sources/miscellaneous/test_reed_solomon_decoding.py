#! /usr/bin/env python3

import random

from qrcode_generator.reed_solomon_code import calculate_reed_solomon_polynomial, reed_solomon_code_remainder

# From version 1-H   :  26 symbols, of which 9 are data symbols and 17 are error correction symbols.
# From version 40-L  : 149 symbols, of which 119 are data symbols and 30 are error correction symbols.

print("hello")

code_c =  26 # total number of codewords
code_k =   9 # number of data keywords

poly = calculate_reed_solomon_polynomial(code_c - code_k, strip=True)

random.seed(123)

d_block = list(random.randbytes(code_k))

e_block = reed_solomon_code_remainder(d_block, poly)

de_block = d_block + e_block
print("de_block:", de_block)

num_errors = 1
error_positions = random.sample(range(len(de_block)), num_errors)
print("error positions:", error_positions)

de_block_errors = [random.randint(1, 255) if k in error_positions else 0 for k in range(len(de_block))]
print("de_block_errors:", de_block_errors)

de_block_received = [a ^ b for (a, b) in zip(de_block, de_block_errors)]
print("de_block_received:", de_block_received)

check = reed_solomon_code_remainder(de_block_received, poly)

print("check:", check)
