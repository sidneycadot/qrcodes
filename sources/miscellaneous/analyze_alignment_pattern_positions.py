#! /usr/bin/env -S python3 -B

import math
from fractions import Fraction

from qrcode_generator.lookup_tables import alignment_pattern_position_table


def analyze_alignment_pattern_positions():

    for (version, reference_positions) in alignment_pattern_position_table.items():

        if version == 1:
            # Version 1 is special; ignore it.
            continue

        R_nonfirst = (reference_positions[-1] - reference_positions[-2])
        R_first    = (reference_positions[ 1] - reference_positions[ 0])

        R_spec = (R_first, R_nonfirst)

        first_position = 6
        last_position = 10 + 4 * version
        num_positions = 2 + version // 7

        delta = last_position - first_position
        num_steps = num_positions - 1

        ideal_stepsize = Fraction(delta, num_steps)
        ideal_positions = [first_position + k * ideal_stepsize for k in range(num_positions)]

        A_nonfirst = math.floor(ideal_stepsize / 2) * 2
        B_nonfirst = math.ceil (ideal_stepsize / 2) * 2

        A_first = delta - (num_steps - 1) * A_nonfirst
        B_first = delta - (num_steps - 1) * B_nonfirst

        A_spec = (A_first, A_nonfirst)
        B_spec = (B_first, B_nonfirst)

        if A_spec == B_spec:
            # Choices A and B are identical.
            continue

        A_pos = [6, 6 + A_first]
        B_pos = [6, 6 + B_first]

        while len(A_pos) < len(ideal_positions):
            A_pos.append(A_pos[-1] + A_nonfirst)
            B_pos.append(B_pos[-1] + B_nonfirst)

        if R_spec == A_spec == B_spec:
            choice = "A/B"
        elif R_spec == A_spec:
            choice = " A "
        elif R_spec == B_spec:
            choice = " B "
        else:
            choice = " ? "

        A_quality = sum( abs(ap - ip)**2 + 0.0 for (ap, ip) in zip(A_pos, ideal_positions))
        B_quality = sum( abs(bp - ip)**2 + 0.0 for (bp, ip) in zip(B_pos, ideal_positions))

        print(f"version {version:2} first {first_position} last {last_position:3} delta {delta:3} R {R_spec} ; A {A_spec}  B {B_spec} choice {choice} Aq {A_quality} Bq {B_quality}")


def main():
    analyze_alignment_pattern_positions()


if __name__ == "__main__":
    main()
