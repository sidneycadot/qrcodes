#! /usr/bin/env python3

from enum_types import ErrorCorrectionLevel
from lookup_tables import version_specifications
from optimal_encoding import find_optimal_string_encoding

filename = "pi_10k.txt"
with open(filename, "r") as fi:
	plaintext = fi.read()

plaintext = plaintext[:7081]
print(plaintext)

for level in ErrorCorrectionLevel:
	print(level.name)
	for vspec in version_specifications.values():
		if vspec.error_correction_level != level:
			continue

		version = vspec.version
		data_codewords = vspec.total_number_of_codewords - vspec.number_of_error_correcting_codewords
		name = f"{vspec.version}-{vspec.error_correction_level.name}"
		solutions = find_optimal_string_encoding(plaintext, vspec.version)
		first_solution = solutions[0]
		
		databits = 8 * data_codewords
		if databits >= first_solution.bitcount(version):
			print(name, databits, first_solution.bitcount(version))
			break
