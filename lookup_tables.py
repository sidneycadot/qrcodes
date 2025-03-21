"""Alignment pattern positions QR codes.

The alignment pattern positions are copied verbatim from the standard (Table E.1).

They specify both horizontal and vertial center positions of the 5x5 alignment
patterns present in regular QR codes. The top-left, top-right, and bottom-left
alignment patterns are left out, as they would clash with the three finder patterns.

QR Code version 1 is exceptional, as it has no embedded alignment pattern at all.

For versions 2..40, we observe the following:

(1) The first and last positions are predictable. They are fixed relative to the
    edges of the QR code.

    first_position = 6
    last_position  = 10 + 4 * version

(2) The number of positions occupied is predictable:

    num_positions = 2 + floor(version / 7)

    Note that the standard does not explicitly guarantee this.
    The pattern can be observed easily from the table.

(3) The first step (i.e., the difference between the first and second position)
    can differ from all other steps. All steps but the first are identical.

    The standard documents these two facts, but it does not specify how
    to derive the two step sizes given the version number.

    There appears to be no simple relation to derive the first and
    non-first step-sizes from the version number that works in all cases.

Given the lack of an algorithmic description of how to obtain the alignment pattern positions
from the version number, we will use a lookup table instead.
"""

alignment_pattern_positions: dict[int, list[int]] = {
    1: [],
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
    9: [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66],
    15: [6, 26, 48, 70],
    16: [6, 26, 50, 74],
    17: [6, 30, 54, 78],
    18: [6, 30, 56, 82],
    19: [6, 30, 58, 86],
    20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94],
    22: [6, 26, 50, 74, 98],
    23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106],
    25: [6, 32, 58, 84, 110],
    26: [6, 30, 58, 86, 114],
    27: [6, 34, 62, 90, 118],
    28: [6, 26, 50, 74, 98, 122],
    29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130],
    31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138],
    33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146],
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154],
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162],
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170]
}
