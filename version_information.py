#! /usr/bin/env python3

def poly_division(datapoly: int, databits: int, data_direction: bool, poly: int, polybits: int, residual_direction: bool, inshift_value: bool, bit_compare: bool) -> int:

    residual_mask = (1 << polybits) - 1

    if inshift_value:
        inshift_mask = 1 if residual_direction else 1 << (polybits - 1)
    else:
        inshift_mask = 0

    residual = 0
    for k in range(databits):
        index = k if data_direction else databits - 1 - k
        datamask = 1 << index
        bit = (datapoly & datamask) != 0

        if residual_direction:
            residual = (residual << 1) & residual_mask
            residual |= inshift_mask
        else:
            residual = (residual >> 1) & residual_mask
            residual |= inshift_mask

        if bit == bit_compare:
            residual ^= poly

    return residual

poly = 0b0100110111

for data_direction in (False, True):
    for residual_direction in (False, True):
        for bit_compare in (False, True):
            for inshift_value in (False, True):

                residual = poly_division(0, 5, data_direction, poly, 10, residual_direction, inshift_value, bit_compare)
                if residual != 0b0000000000:
                    continue

                residual = poly_division(1, 5, data_direction, poly, 10, residual_direction, inshift_value, bit_compare)
                if residual != 0b0100110111:
                    continue

                residual = poly_division(2, 5, data_direction, poly, 10, residual_direction, inshift_value, bit_compare)
                if residual != 0b1001101110:
                    continue

                residual = poly_division(3, 5, data_direction, poly, 10, residual_direction, inshift_value, bit_compare)
                if residual != 0b1101011001:
                    continue

                residual = poly_division(4, 5, data_direction, poly, 10, residual_direction, inshift_value, bit_compare)
                if residual != 0b0111101011:
                    continue

                #residual = poly_division(4, 5, data_direction, poly, 10, residual_direction, inshift_value, bit_compare)
                #if residual != 0b0111101011:
                #    continue

                print("good:", data_direction, residual_direction, bit_compare, inshift_value)

