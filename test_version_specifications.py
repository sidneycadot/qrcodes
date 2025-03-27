#! /usr/bin/env -S python3 -B

from lookup_tables import version_specifications

for (key, vspec) in version_specifications.items():

	print(key)
	assert key == (vspec.version, vspec.error_correction_level)

	assert vspec.total_number_of_codewords == sum(count * c for (count, (c, k, r)) in vspec.block_specification)
	assert vspec.total_number_of_codewords == vspec.number_of_error_correcting_codewords + sum(count * k for (count, (c, k, r)) in vspec.block_specification)
