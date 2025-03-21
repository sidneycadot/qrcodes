#! /usr/bin/env python3

import math
import numpy as np

from lookup_tables import alignment_pattern_positions
from fractions import Fraction

def get_alignment_positions(version: int) -> list[int]:

    positions = []

    if version > 1:

        num = (version+14) // 7

        first = 6
        last = 14 + 4 * (version - 1)

        delta = last - first
        steps = num - 1

        # Find the smallest even integer greater than or equal to (delta / steps).
        # This is the step size of all but the first step.

        nonfirst_stepsize = ((delta + steps * 2 - 1) // (steps * 2)) * 2
        first_stepsize = delta - (steps - 1) * nonfirst_stepsize

        assert first_stepsize > 0
        assert first_stepsize % 2 == 0

        # We start at index 6, then we make a single step of size 'first_stepsize',
        # then we make subsequent steps of size 'nonfirst_stepsize'.

        positions.append(6)
        positions.append(positions[-1] + first_stepsize)
        while len(positions) != num:
            positions.append(positions[-1] + nonfirst_stepsize)

        assert positions[0] == first
        assert positions[-1] == last

    return positions

for (version, reference_positions) in alignment_pattern_positions.items():

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

    A_nonfirst = math.floor(ideal_stepsize / 2) * 2
    B_nonfirst = math.ceil(ideal_stepsize / 2) * 2

    A_first = delta - (num_steps - 1) * A_nonfirst
    B_first = delta - (num_steps - 1) * B_nonfirst

    A_spec = (A_first, A_nonfirst)
    B_spec = (B_first, B_nonfirst)

    if A_spec == B_spec:
        continue

    #assert A_spec != B_spec

    if R_spec == A_spec == B_spec:
        choice = " = "
    elif R_spec == A_spec:
        choice = "(A)"
    elif R_spec == B_spec:
        choice = "(B)"
    else:
        choice = " ? "

    #opt1_steps = np.asarray([opt1_first] + (num_steps - 1 ) * [opt1], dtype=np.float64)
    #opt2_steps = np.asarray([opt2_first] + (num_steps - 1 ) * [opt2], dtype=np.float64)

    print(f"version {version:2} first {first_position} last {last_position:3} delta {delta:3} R {R_spec} ; A {A_spec} {choice} B {B_spec} [{A_spec[0]-A_spec[1]} {B_spec[1]-B_spec[0]}]")
    #last_prop = round(delta / num_steps / 2) * 2

    #assert laststep % 2 == 0

    #assert np.all(steps[1:] ==steps[-1])
    #assert np.sum(steps) == delta
    #assert len(positions) == num_positions
    #assert positions[0] == first
    #assert positions[-1] == last
