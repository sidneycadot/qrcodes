#! /usr/bin/env -S python3 -B

"""Render codes found in the wild."""

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render.utilities import save_qrcode_as_png_file


def render_iso_standard_customer_feedback_code():
    """Render QR code found on the cover of the ISO/IEC 18004:2024 standard."""
    version = 8
    pattern = DataMaskingPattern.PATTERN3
    level = ErrorCorrectionLevel.L

    include_quiet_zone = True

    mode = 'RGB'
    colormap = 'color'
    optimize_png = True

    png_filename = "qrcode_wild_IsoStandard_{VERSION}{LEVEL}p{PATTERN}.png"

    payload = "https://go.iso.org/customer-feedback?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdGQiOiJJU08vSUVDIDE4MDA0OjIwMjQiLCJpc3MiOiJJU08ifQ.4cn-n2MBPD_i_oNu1dZxQbD5j-rZNKq2DTTOqnPaqCY"

    de = DataEncoder(EncodingVariant.from_version(version))
    de.append_byte_mode_block(payload.encode('iso_8859_1'))

    canvas = make_qr_code(
        de,
        version=version,
        level=level,
        include_quiet_zone=include_quiet_zone,
        pattern=pattern
    )

    save_qrcode_as_png_file(
        png_filename=png_filename,
        canvas=canvas, mode=mode,
        colormap=colormap,
        transform=None,
        optimize_png=optimize_png
    )


def render_oralb_package_code():
    """Reproduce the QR code found on a commercial toothbrush blister."""

    version = 3
    pattern = DataMaskingPattern.PATTERN2
    level = ErrorCorrectionLevel.H

    include_quiet_zone = True

    mode = 'RGB'
    colormap = 'color'
    optimize_png = True

    png_filename = "qrcode_wild_OralBPackage_{VERSION}{LEVEL}p{PATTERN}.png"

    payload = "https://qrco.de/bb8b9t"

    de = DataEncoder(EncodingVariant.from_version(version))
    de.append_eci_designator(26)
    de.append_byte_mode_block(payload.encode('utf_8'))

    canvas = make_qr_code(
        de,
        version=version,
        level=level,
        include_quiet_zone=include_quiet_zone,
        pattern=pattern
    )

    save_qrcode_as_png_file(
        png_filename=png_filename,
        canvas=canvas,
        mode=mode,
        colormap=colormap,
        transform="rotate-clockwise",
        optimize_png=optimize_png
    )


def render_lego_bouwplaats_code():
    """Render QR code found in Delft, Lego shop display."""

    version = 2
    pattern = DataMaskingPattern.PATTERN3
    level = ErrorCorrectionLevel.L

    include_quiet_zone = True

    mode = 'RGB'
    colormap = 'default'
    optimize_png = True

    png_filename = "qrcode_wild_LegoBouwplaats_{VERSION}{LEVEL}p{PATTERN}.png"

    payload = "http://debontebouwplaats.nl"

    de = DataEncoder(EncodingVariant.from_version(version))
    de.append_byte_mode_block(payload.encode('iso_8859_1'))

    canvas = make_qr_code(
        de,
        version=version,
        level=level,
        include_quiet_zone=include_quiet_zone,
        pattern=pattern
    )

    save_qrcode_as_png_file(
        png_filename=png_filename,
        canvas=canvas,
        mode=mode,
        colormap=colormap,
        transform="rotate-180",
        optimize_png=optimize_png
    )


def main():
    render_iso_standard_customer_feedback_code()
    render_oralb_package_code()
    render_lego_bouwplaats_code()
    pass


if __name__ == "__main__":
    main()
