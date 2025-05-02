#! /usr/bin/env -S python3 -B

"""Write example QR codes with explicit ECI designators as PNG image files."""

import glob
import itertools
import os
from typing import Optional

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, CharacterEncodingType
from qrcode_generator.lookup_tables import version_specification_table, count_bits_table
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.utilities import save_qrcode_as_png_file, QRCodePngFileDescriptor


def write_eci_data_test(
        *,
        png_filename: str,
        payload: bytes,
        colormap: Optional[str | dict],
        optimize_png: bool) -> QRCodePngFileDescriptor:
    """Write QR code using an ECI designator combined with a specific encoding."""

    for version, level in itertools.product(range(1, 41), reversed(ErrorCorrectionLevel)):
        version_specification = version_specification_table[(version, level)]
        # (20 bits for the ECI designator.)
        # 4 bits for the bytes block intro.
        # k bits for the bytes block count bits.
        bits_available = 8 * version_specification.number_of_data_codewords() - 4 - count_bits_table[EncodingVariant.from_version(version)][CharacterEncodingType.BYTES]
        if 8 * len(payload) <= bits_available:
            break
    else:
        raise RuntimeError("Cannot encode the string with an ECI designator prefix (too big).")

    #version_specification = version_specification_table[(version, level)]
    #print("@@@", version, level, "payload bits", len(payload) *  8, "codewords", 8 * version_specification.number_of_data_codewords())

    de = DataEncoder(EncodingVariant.from_version(version))
    # de.append_eci_designator(899)
    de.append_byte_mode_block(payload)

    qr_canvas = make_qr_code(de, version=version, level=level)

    return save_qrcode_as_png_file(
        png_filename=png_filename,
        canvas=qr_canvas,
        colormap=colormap,
        optimize_png=optimize_png
    )


def main():

    # Remove stale QR code ECI example files.

    for filename in glob.glob("qrcode_data_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)

    # Parameters.

    colormap = 'default'
    optimize_png = True

    for size in (4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 2953):

        payload = bytes(size)

        write_eci_data_test(
            png_filename=f"qrcode_data_{size}_{{VERSION}}{{LEVEL}}p{{PATTERN}}.png",
            payload=payload,
            colormap=colormap,
            optimize_png=optimize_png
        )


if __name__ == "__main__":
    main()
