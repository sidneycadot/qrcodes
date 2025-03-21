#! /usr/bin/env -S python3 -B

from lookup_tables import format_information_lookup_table, version_information_lookup_table

def format_information_code_remainder(data: int) -> int:

    residual = 0b0000000000
    rmask_hi = 0b1000000000
    rmask_lo = 0b0111111111
    genpoly  = 0b0100110111

    dmask = 0b10000

    while dmask != 0:

        databit = (data & dmask) != 0
        dmask >>= 1

        residual_bit = (residual & rmask_hi) != 0
        residual = (residual & rmask_lo) << 1

        if databit ^ residual_bit:
            residual ^= genpoly

    return residual

def version_information_code_remainder(data: int) -> int:

    residual = 0b000000000000
    rmask_hi = 0b100000000000
    rmask_lo = 0b011111111111
    genpoly  = 0b111100100101

    dmask = 0b100000

    while dmask != 0:

        databit = (data & dmask) != 0
        dmask >>= 1

        residual_bit = (residual & rmask_hi) != 0
        residual = (residual & rmask_lo) << 1

        if databit ^ residual_bit:
            residual ^= genpoly

    return residual

def main():

    for (key, value) in format_information_lookup_table.items():
        residual = format_information_code_remainder(key)
        assert residual == value

    for (key, value) in version_information_lookup_table.items():
        residual = version_information_code_remainder(key)
        assert (key << 12) | residual == value

if __name__ == "__main__":
    main()
