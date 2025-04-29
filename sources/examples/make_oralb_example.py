#! /usr/bin/env -S python3 -B

"""Write QR code reproducing the QR code as found on a commercial blister as a PNG image file."""

import glob
import os
from typing import Optional

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from qrcode_generator.qr_code import make_qr_code, QRCodeDrawer
from qrcode_generator.render_pil import render_qrcode_as_pil_image, colormap_color
from qrcode_generator.utilities import write_optimal_qrcode, optimize_png


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

    qr = QRCodeDrawer(version, include_quiet_zone=include_quiet_zone)

    # Note: this may raise a QRCodeCapacityError.
    #qr.erase_data_and_error_correction_bits()
    qr.place_data_and_error_correction_bits(de, level)
    # Handle data pattern masking.
    #
    # If a pattern is given as a parameter, we will use that.
    # Otherwise, we'll determine the best pattern based on a score.

    # Apply the selected data masking pattern.
    print(f"Applying data mask pattern {pattern.name}.")
    qr.apply_data_masking_pattern(pattern)

    # Fill in the definitive version and format information.
    qr.place_version_information_patterns()
    qr.place_format_information_patterns(level, pattern)

    im = render_qrcode_as_pil_image(qr.canvas, mode=mode, colormap=colormap)
    im.save(filename)
    if post_optimize:
        optimize_png(filename)


if __name__ == "__main__":
    main()
