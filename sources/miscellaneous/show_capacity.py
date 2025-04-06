#! /usr/bin/env -S python3 -B

data_module_count = {
     1:   208,
     2:   359,
     3:   567,
     4:   807,
     5:  1079,
     6:  1383,
     7:  1568,
     8:  1936,
     9:  2336,
    10:  2768,
    11:  3232,
    12:  3728,
    13:  4256,
    14:  4651,
    15:  5243,
    16:  5867,
    17:  6523,
    18:  7211,
    19:  7931,
    20:  8683,
    21:  9252,
    22: 10068,
    23: 10916,
    24: 11796,
    25: 12708,
    26: 13652,
    27: 14628,
    28: 15371,
    29: 16411,
    30: 17483,
    31: 18587,
    32: 19723,
    33: 20891,
    34: 22091,
    35: 23008,
    36: 24272,
    37: 25568,
    38: 26896,
    39: 28256,
    40: 29648
}

def calculate_capacity_v1(version: int) -> int:

    size = 17 + 4 * version

    raw_count = size * size

    count = raw_count

    # subtract area of the three finder patterns, including the empty
    # separator modules.

    count -= 3 * (8 * 8)

    # correct for horizontal and vertical timing patterns
    timing_pattern_length = 1 + version * 4
    count -= 2 * timing_pattern_length

    # correct for format patterns
    count -= 2 * 15
    count -= 1  # The one bit that's always one

    # correct for version patterns
    if version >= 7:
        count -= 2 * 18

    # number of alignment patterns
    num_align_side = 0 if version == 1 else (version // 7 + 2)

    # Correct for area taken by alignment patterns
    if num_align_side >= 2:
        count -= (num_align_side * num_align_side - 3) * 25

        # Correct for modules that were already part of the alignment pattern.
        if num_align_side >= 3:
            count += (num_align_side - 2) * 5 * 2

    return count


def calculate_capacity_v2(version: int) -> int:
    """Return the number of modules (pixels) available for storing data and error correction bits."""
    v7 = version // 7

    extra = 0
    if version == 1: extra += 25  # No alignment pattern.
    if version <= 6: extra += 36  # No version information.

    return 16 * version * (8 + version) - 5 * v7 * (18 + 5 * v7) + 3 + extra


def main():
    for version in range(1, 41):

        v0 = data_module_count[version]
        v1 = calculate_capacity_v1(version)
        v2 = calculate_capacity_v2(version)

        print(f"version {version:2d} v0 {v0:5d} v1 {v1:5d} v2 {v2:5d}")
        assert v0 == v1 == v2


if __name__ == "__main__":
    main()
