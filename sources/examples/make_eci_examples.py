#! /usr/bin/env -S python3 -B

"""Write example QR codes with explicit ECI designators as PNG image files."""

import glob
import os
from typing import Optional

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render_pil import render_qrcode_as_pil_image
from qrcode_generator.utilities import optimize_png


def write_eci_test(
        filename: str, *,
        payload: str,
        encoding: str,
        eci_designator_value: int,
        version: int,
        level: ErrorCorrectionLevel,
        colormap: Optional[str | dict] = None,
        post_optimize: bool = False) -> None:
    """Write QR code using an ECI designator combined with a specific encoding."""

    de = DataEncoder(EncodingVariant.from_version(version))
    de.append_eci_designator(eci_designator_value),
    de.append_byte_mode_block(payload.encode(encoding))

    qr_canvas = make_qr_code(de, version, level)
    im = render_qrcode_as_pil_image(qr_canvas, colormap=colormap)
    print(f"Saving {filename} ...")
    im.save(filename)
    if post_optimize:
        optimize_png(filename)


def main():

    # Remove stale QR code example files.

    for filename in glob.glob("qrcode_eci_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)

    colormap = 'color'
    post_optimize = True

    level = ErrorCorrectionLevel.H

    version = 10

    write_eci_test(
        filename="qrcode_eci_cp437_eci_0.png",
        payload="This is a 'codepage 437' encoded text, using ECI designator value 0. Here's a greek lowercase sigma: 'σ'.",
        encoding="cp437",
        eci_designator_value = 0,
        version=10,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_iso8859_1_eci_1.png",
        payload="This is an ISO-6659-1 encoded text, using ECI designator value 1. Here's a copyright sign: '©'.",
        encoding="iso-8859-1",
        eci_designator_value = 1,
        version=9,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_cp437_eci_2.png",
        payload="This is a 'codepage 437' encoded text, using ECI designator value 2. Here's a greek lowercase sigma: 'σ'.",
        encoding="cp437",
        eci_designator_value = 2,
        version=10,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_iso8859_1_eci_3.png",
        payload="This is an ISO-6659-1 encoded text, using ECI designator value 3. Here's a copyright sign: '©'.",
        encoding="iso-8859-1",
        eci_designator_value = 3,
        version=9,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_utf8_eci_26.png",
        payload="This is a UTF-8 encoded text, using ECI designator value 26.",
        encoding="utf_8",
        eci_designator_value = 26,
        version=7,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_ascii_eci_27.png",
        payload="This is an ASCII encoded text, using ECI designator value 27.",
        encoding="ascii",
        eci_designator_value = 27,
        version=7,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_utf16be_eci_25.png",
        payload="This is a UTF-16 (big endian) encoded text, using ECI designator value 25.",
        encoding="utf_16_be",
        eci_designator_value = 25,
        version=12,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_utf16le_eci_33.png",
        payload="This is a UTF-16 (little endian) encoded text, using ECI designator value 33.",
        encoding="utf_16_le",
        eci_designator_value = 33,
        version=12,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_utf32be_eci_34.png",
        payload="This is a UTF-32 (big endian) encoded text, using ECI designator value 34.",
        encoding="utf_32_be",
        eci_designator_value=34,
        version=18,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_utf32le_eci_35.png",
        payload="This is a UTF-32 (little endian) encoded text, using ECI designator value 35.",
        encoding="utf_32_le",
        eci_designator_value=35,
        version=18,
        level=level,
        colormap=colormap,
        post_optimize=post_optimize
    )

if __name__ == "__main__":
    main()
