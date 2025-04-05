#! /usr/bin/env -S python3 -B

"""Test version specification table entries."""

import unittest

from qrcode_generator.lookup_tables import version_specifications


class TestVersionSpecificationsTable(unittest.TestCase):

    def test_version_specification_properties(self):

        for (key, vspec) in version_specifications.items():

            self.assertEqual(key, (vspec.version, vspec.error_correction_level))

            self.assertEqual(vspec.total_number_of_codewords,
                             sum(count * c for (count, (c, k, r)) in vspec.block_specification))

            self.assertEqual(vspec.total_number_of_codewords,
                             vspec.number_of_error_correcting_codewords +
                             sum(count * k for (count, (c, k, r)) in vspec.block_specification)
                             )

            self.assertEqual(len(set(r for (count, (c, k, r)) in vspec.block_specification)), 1)


if __name__ == "__main__":
    unittest.main()
