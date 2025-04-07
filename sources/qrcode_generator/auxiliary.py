"""Auxiliary support functions."""


def enumerate_bits(value: int, num_bits: int):
    """Enumerate the bits in the unsigned integer value as booleans, going from the MSB down to the LSB."""
    assert 0 <= value < (1 << num_bits)
    mask = 1 << (num_bits - 1)
    while mask != 0:
        yield (value & mask) != 0
        mask >>= 1


def calculate_qrcode_capacity(version: int) -> int:
    """Return the number of modules (pixels) available for storing data and error correction bits."""
    v7 = version // 7

    extra = 0
    if version == 1: extra += 25  # No alignment pattern.
    if version <= 6: extra += 36  # No version information.

    return 16 * version * (8 + version) - 5 * v7 * (18 + 5 * v7) + 3 + extra
