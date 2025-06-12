from qrcode.enum_types import ErrorCorrectionLevel
from qrcode.lookup_tables import version_specification_table
from qrcode.qr_code import QRCodeDrawer


def main():
    version = 7
    level = ErrorCorrectionLevel.H

    version_specification = version_specification_table[(version, level)]

    qr = QRCodeDrawer(version, include_quiet_zone=False)
    print("data/errc positions:", len(qr.data_and_error_correction_positions))

    d_blocks = []
    e_blocks = []
    codeword_index = 0
    for (count, (code_c, code_k, code_r)) in version_specification.block_specification:
        # Calculate the Reed-Solomon polynomial corresponding to the number of error correction words.
        for repeat_code in range(count):
            codeword_index += 1
            d_block = []
            e_block = []
            for symbol_index in range(code_c):
                if symbol_index < code_k:
                    symbol_key = f"W{codeword_index}_D{symbol_index}"
                    d_block.append(symbol_key)
                else:
                    symbol_key = f"W{codeword_index}_E{symbol_index}"
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

    for channel_word in channel_words:
        print("@@@", channel_word)

if __name__ == "__main__":
    main()
