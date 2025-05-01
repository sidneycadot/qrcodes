#! /usr/bin/env -S python3 -B

"""Reproduce the QR code found on a commercial toothbrush blister."""

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render_pil import render_qrcode_as_pil_image
from qrcode_generator.utilities import optimize_png


def main():

    version = 3
    pattern = DataMaskingPattern.PATTERN2
    level = ErrorCorrectionLevel.H

    include_quiet_zone = True

    mode = 'RGB'
    colormap = 'color'
    post_optimize = True

    filename = "qrcode_oralb.png"

    de = DataEncoder(EncodingVariant.from_version(version))
    de.append_eci_designator(26)  # Declare UTF-8 encoding.
    de.append_byte_mode_block(b"https://qrco.de/bb8b9t")

    qr_canvas = make_qr_code(de, version, level, include_quiet_zone=include_quiet_zone, pattern=pattern)

    im = render_qrcode_as_pil_image(qr_canvas, mode=mode, colormap=colormap)
    im.save(filename)
    if post_optimize:
        optimize_png(filename)


if __name__ == "__main__":
    main()
