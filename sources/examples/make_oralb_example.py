#! /usr/bin/env -S python3 -B

"""Reproduce the QR code found on a commercial toothbrush blister."""

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render.utilities import save_qrcode_as_png_file


def main():

    version = 3
    pattern = DataMaskingPattern.PATTERN2
    level = ErrorCorrectionLevel.H

    include_quiet_zone = True

    mode = 'RGB'
    colormap = 'color'
    optimize_png = True

    png_filename = "qrcode_oralb.png"

    de = DataEncoder(EncodingVariant.from_version(version)).append_eci_designator(26).append_byte_mode_block("https://qrco.de/bb8b9t".encode('utf_8'))

    canvas = make_qr_code(de, version=version, level=level, include_quiet_zone=include_quiet_zone, pattern=pattern)

    save_qrcode_as_png_file(png_filename=png_filename, canvas=canvas, mode=mode, colormap=colormap, optimize_png=optimize_png)


if __name__ == "__main__":
    main()
