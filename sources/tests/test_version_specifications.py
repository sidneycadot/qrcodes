#! /usr/bin/env -S python3 -B

"""Test version specification table entries."""

import unittest

from qrcode.lookup_tables import version_specification_table


class TestVersionSpecificationsTable(unittest.TestCase):

    def test_version_specification_properties(self):

        for (key, vspec) in version_specification_table.items():

            self.assertEqual(key, (vspec.version, vspec.error_correction_level))

            self.assertEqual(vspec.total_number_of_codewords,
                             sum(count * c for (count, (c, k, r)) in vspec.block_specification))

            self.assertEqual(vspec.total_number_of_codewords,
                             vspec.number_of_error_correcting_codewords +
                             sum(count * k for (count, (c, k, r)) in vspec.block_specification)
                             )

            self.assertEqual(len(set(r for (count, (c, k, r)) in vspec.block_specification)), 1)

            for (count, (c, k, r)) in vspec.block_specification:
                self.assertEqual(c - k, 2 * r + vspec.p)


if __name__ == "__main__":
    unittest.main()
