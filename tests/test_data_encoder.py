#! /usr/bin/env -S python3 -B
from data_encoder import DataEncoder
#from enum_types import ErrorCorrectionLevel
#from lookup_tables import version_specifications
from optimal_encoding import find_optimal_string_encoding, EncodingVariant

filename = "pi_10k.txt"
with open(filename, "r") as fi:
	plaintext = fi.read()

plaintext = plaintext[:7081]

for variant in (EncodingVariant.LARGE, ):

	solutions = find_optimal_string_encoding(plaintext, variant)
	if len(solutions) == 0:
		raise RuntimeError()
	solution = solutions[0]

	bitcount = solution.bitcount()
	print(variant, bitcount)

	de = DataEncoder(variant)

	solution.render(de)
