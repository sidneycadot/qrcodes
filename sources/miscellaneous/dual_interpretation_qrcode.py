
from types import SimpleNamespace
from typing import NamedTuple

from qrcode.enum_types import ErrorCorrectionLevel
from qrcode.lookup_tables import version_specification_table
from qrcode.qr_code import QRCodeDrawer

class CodewordDescriptor(NamedTuple):
    n: int
    k: int
    r: int

#class PixelDescriptor:
#    def __init__(self):
#        self.normal = SimpleNamespace()
#        self.mirror = SimpleNamespace()

def main():

    version = 1
    level = ErrorCorrectionLevel.L

    qr = QRCodeDrawer(version, include_quiet_zone=False)

    #for (i, j) in sorted(qr.data_and_error_correction_positions):
    #    pixel_descriptor = PixelDescriptor()
    #    pixel_descriptor.normal.i = i
    #    pixel_descriptor.normal.j = j
    #    print(pixel_descriptor.normal)

    version_specification = version_specification_table[(version, level)]

    codeword_descriptors = []

    d_blocks = []
    e_blocks = []
    for (count, (code_c, code_k, code_r)) in version_specification.block_specification:
        # Calculate the Reed-Solomon polynomial corresponding to the number of error correction words.
        codeword_descriptor = CodewordDescriptor(code_c, code_k, code_r)
        for repeat_code in range(count):
            codeword_index = len(codeword_descriptors)
            codeword_descriptors.append(codeword_descriptor)
            d_block = []
            e_block = []
            for symbol_index in range(code_c):
                if symbol_index < code_k:
                    symbol_key = (codeword_index, symbol_index)
                    d_block.append(symbol_key)
                else:
                    symbol_key = (codeword_index, symbol_index)
                    e_block.append(symbol_key)
            d_blocks.append(d_block)
            e_blocks.append(e_block)

    channel_words = []

    k = 0
    while sum(map(len, d_blocks)) != 0:
        if len(d_blocks[k]) != 0:
            channel_words.append(d_blocks[k].pop(0))
        k = (k + 1) % len(d_blocks)

    k = 0
    while sum(map(len, e_blocks)) != 0:
        if len(e_blocks[k]) != 0:
            channel_words.append(e_blocks[k].pop(0))
        k = (k + 1) % len(e_blocks)

    # Which code symbol occupies which pixels?
    occupation = {}

    pixel_coordinate_iterator = iter(qr.data_and_error_correction_positions)
    for (codeword_index, symbol_index) in channel_words:
        for bit in range(8):
            (i, j) = next(pixel_coordinate_iterator)
            print('A', codeword_index, symbol_index, i, j)
            key = ('A', codeword_index, symbol_index)
            if key not in occupation:
                occupation[key] = set()
            occupation[key].add((i, j))
            print('B', codeword_index, symbol_index, j, i)
            key = ('B', codeword_index, symbol_index)
            if key not in occupation:
                occupation[key] = set()
            occupation[key].add((j, i))

    print(occupation)

    assignments = {}

    assigned = set()

    prev_assigned = -1
    while True:
        flag = False
        for codeword_index in range(len(codeword_descriptors)):
            for side in ('A', 'B'):
                codeword_descriptor = codeword_descriptors[codeword_index]
                for symbol_index in range(codeword_descriptor.n):
                    key = (side, codeword_index, symbol_index)
                    if not assigned.intersection(occupation[key]):
                        print("assigning:", side, codeword_index, symbol_index)
                        if (side, codeword_index) not in assignments:
                            assignments[(side, codeword_index)] = []
                        assignments[(side, codeword_index)].append(symbol_index)
                        assigned |= occupation[key]
                        flag = True
                        break
        if not flag:
            break

    for side in ('A', 'B'):
        for codeword_index in range(len(codeword_descriptors)):
            print(side, codeword_index, "***", codeword_descriptors[codeword_index], "***",  len(assignments[(side, codeword_index)]), "symbols claimed:", assignments[(side, codeword_index)])


if __name__ == "__main__":
    main()
