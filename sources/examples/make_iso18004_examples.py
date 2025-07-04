#! /usr/bin/env -S python3 -B

"""Generate QR code symbols from the ISO/IEC 18004 standard.

There are currently four editions of the standard:

* ISO/IEC 18004:2000(E)
* ISO/IEC 18004:2006(E)
* ISO/IEC 18004:2015(E)
* ISO/IEC 18004:2024(en)

Each of these contains precisely seven concrete QR code examples:

- Introduction: a QR code symbol encoding the text "QR Code Symbol" as a 1-M symbol.
- The Structured Append Mode section provides an example of a single 4-M QR code symbol
  encoding the string "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
  and also four 1-M symbols that together encode the same string.
- Annex: a QR code symbol encoding the numeric string "01234567" is discussed.

In addition to these, the encoding of the string "ΑΒΓΔΕ" using the ISO/IEC 8859-7
encoding in combination with an ECI designator is discussed, even though no image
of a QR code symbol for this case is present in the standard.
"""

import glob
import os
from typing import Optional

from qrcode.data_encoder import DataEncoder
from qrcode.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskPattern
from qrcode.qr_code import make_qr_code
from qrcode.render.utilities import write_optimal_qrcode, save_qrcode_as_png_file

from examples.utilities.render_html_examples import RenderHtmlExample


def remove_stale_files() -> None:
    """Remove stale QR code files."""

    for filename in glob.glob("qrcode_iso18004_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)


def write_introduction_examples(
        *,
        include_quiet_zone: bool,
        colormap: Optional[str | dict],
        optimize_png: bool) -> list[RenderHtmlExample]:
    """Write the first example of a QR code found in the standard.

    Note that the data masking pattern selected differs between the standard editions:

    - 2000, 2006, 2015 ...... : pattern 5
    - 2024 .................. : pattern 6

    The 2000 edition does not mention what the QR code encodes.

    The 2006 and 2015 editions use this example QR code to showcase the effects of mirroring
    and inversion, and indicate that the symbol encodes the text "QR Code Symbol".

    The 2024 edition incorrectly indicates that the symbol encodes the text "QR code Symbol".

    References:
    - ISO/IEC 18004:2000(E)   Figure 1, Section 7.1, page 5.
    - ISO/IEC 18004:2006(E)   Figure 1, Section 5.2, page 7.
    - ISO/IEC 18004:2015(E)   Figure 1, Section 6.2, page 7.
    - ISO/IEC 18004:2024(en)  Figure 1, Section 5.2, page 6.
    """

    payload = "QR Code Symbol"

    return [
        RenderHtmlExample(
            description=f"Introductory example\n{payload!r}\nISO/IEC 18004:{{2000,2006,2015}}",
            descriptor=write_optimal_qrcode(
                payload=payload,
                png_filename="qrcode_iso18004_2000_2006_2015_QRCodeSymbol_{VERSION}{LEVEL}p{PATTERN}.png",
                include_quiet_zone=include_quiet_zone,
                pattern=DataMaskPattern.PATTERN5,
                version_preference_list=[(1, ErrorCorrectionLevel.M)],
                colormap=colormap,
                optimize_png=optimize_png
            )
        ),
        RenderHtmlExample(
            description=f"Introductory example\n{payload!r}\nISO/IEC 18004:2024",
            descriptor=write_optimal_qrcode(
                payload=payload,
                png_filename="qrcode_iso18004_2024_QRCodeSymbol_{VERSION}{LEVEL}p{PATTERN}.png",
                include_quiet_zone=include_quiet_zone,
                pattern=DataMaskPattern.PATTERN6,
                version_preference_list=[(1, ErrorCorrectionLevel.M)],
                colormap=colormap,
                optimize_png=optimize_png
            )
        )
    ]


def write_explicit_eci_designator_example(
        *,
        include_quiet_zone: bool,
        colormap: Optional[str | dict],
        optimize_png: bool) -> list[RenderHtmlExample]:
    """Represent Greek characters in ISO-8859-7, which corresponds to ECI designator 9.

    This is an example from the standard. The standard just discusses the encoding using
    an ECI designator; it does not show a corresponding QR code symbol.

    Note that the encoding given in the standard is wrong; the string "ΑΒΓΔΕ" encoded
    using iso-8859-7 is 0xc1..0xc5, not 0xa1..0xa5.

    References:
    - ISO/IEC 18004:2000(E)   Section 8.4.1.1, page 19.
    - ISO/IEC 18004:2006(E)   Section 6.4.2.1, page 24.
    - ISO/IEC 18004:2015(E)   Section 7.4.2.2, page 24.
    - ISO/IEC 18004:2024(en)  Section 7.4.3.2, page 22.
    """

    payload = "ΑΒΓΔΕ"
    png_filename = "qrcode_iso18004_2000_2006_2015_2024_ExplicitEciDesignator_{VERSION}{LEVEL}p{PATTERN}.png"

    octets = payload.encode("iso-8859-7")

    de = DataEncoder(EncodingVariant.SMALL).append_eci_designator(9).append_byte_mode_segment(octets)

    qr_canvas = make_qr_code(de, version=1, level=ErrorCorrectionLevel.H, include_quiet_zone=include_quiet_zone)

    return [
        RenderHtmlExample(
            description=f"Explicit ECI designator\n{payload!r}\nISO/IEC 18004:{{2000,2006,2015,2024}}",
            descriptor=save_qrcode_as_png_file(
                png_filename=png_filename,
                canvas=qr_canvas,
                colormap=colormap,
                optimize_png=optimize_png
            )
        )
    ]


def write_structured_append_mode_examples(
        *,
        include_quiet_zone: bool,
        colormap: Optional[str | dict],
        optimize_png: bool) -> list[RenderHtmlExample]:
    """This reproduces the structured append mode example as given in the standard.

    The example shows a 62-character string; first as a single 4-M symbol, then as four 1-M symbols
    using Structured Append Mode.

    The five QR codes are identical for all four editions of the standard.

    References:
    - ISO/IEC 18004:2000(E)   Section 9.1, Figure 22, page 56.
    - ISO/IEC 18004:2006(E)   Section 7.1, Figure 29, page 59.
    - ISO/IEC 18004:2015(E)   Section 8.1, Figure 29, page 60.
    - ISO/IEC 18004:2024(en)  Section 8.1, Figure 29, page 56.
    """

    payload = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    examples = [
        # Reproduces the example where the full payload is encoded in a single QR code.
        # The 62 characters are encoded in a single alphanumeric block.
        RenderHtmlExample(
            description=f"Structured Append Mode example (all data)\n{payload!r}\nISO/IEC 18004:{{2000,2006,2015,2024}}",
            descriptor = write_optimal_qrcode(
                payload=payload,
                png_filename="qrcode_iso18004_2000_2006_2015_2024_StructuredAppendMode_combined_{VERSION}{LEVEL}p{PATTERN}.png",
                include_quiet_zone=include_quiet_zone,
                version_preference_list=[(4, ErrorCorrectionLevel.M)],
                pattern=DataMaskPattern.PATTERN4,
                colormap=colormap,
                optimize_png=optimize_png
            )
        )
    ]

    # Calculate the checksum of the full payload.
    checksum = 0
    for c in payload:
        checksum ^= ord(c)

    structured_append_qrcode_specs = [
        (0, DataMaskPattern.PATTERN0, payload[0:14]),
        (1, DataMaskPattern.PATTERN7, payload[14:30]),
        (2, DataMaskPattern.PATTERN7, payload[30:46]),
        (3, DataMaskPattern.PATTERN3, payload[46:62])
    ]

    for (index, pattern, sub_payload) in structured_append_qrcode_specs:

        de = DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(index, 4, checksum).append_alphanumeric_mode_segment(sub_payload)

        qr_canvas = make_qr_code(de, version=1, level=ErrorCorrectionLevel.M, pattern=pattern, include_quiet_zone=include_quiet_zone)

        png_filename = f"qrcode_iso18004_2000_2006_2015_2024_StructuredAppendMode_split{index}_{{VERSION}}{{LEVEL}}p{{PATTERN}}.png"

        examples.append(
            RenderHtmlExample(
                description=f"Structured Append Mode example (part {index + 1} of 4)\n{sub_payload!r}\nISO/IEC 18004:{{2000,2006,2015,2024}}",
                descriptor=save_qrcode_as_png_file(
                    png_filename=png_filename,
                    canvas=qr_canvas,
                    colormap=colormap,
                    optimize_png=optimize_png
                )
            )
        )

    return examples


def write_annex_examples(
        *,
        include_quiet_zone: bool,
        colormap: Optional[str | dict],
        optimize_png: bool) -> list[RenderHtmlExample]:
    """Write the appendix example of a QR code found in the standard.

    This encodes the numeric string "01234567" as a version 1-M QR code symbol.

    Note that the data masking pattern selected differs between the standard editions:

    - 2000 .................. : pattern 3
    - 2006, 2015, 2024 ...... : pattern 2

    References:
    - ISO/IEC 18004:2000(E)   Figure G.2, Annex G, pages 84--85.
    - ISO/IEC 18004:2006(E)   Figure I.2, Annex I, pages 94--96.
    - ISO/IEC 18004:2015(E)   Figure I.2, Annex I, pages 94--96.
    - ISO/IEC 18004:2024(en)  Figure I.2, Annex I, pages 89--91.
    """

    payload = "01234567"

    return [
        RenderHtmlExample(
            description=f"Annex G example\n{payload!r}\nISO/IEC 18004:2000",
            descriptor = write_optimal_qrcode(
                payload=payload,
                png_filename="qrcode_iso18004_2000_AnnexG_{VERSION}{LEVEL}p{PATTERN}.png",
                include_quiet_zone=include_quiet_zone,
                pattern=DataMaskPattern.PATTERN3,
                version_preference_list=[(1, ErrorCorrectionLevel.M)],
                colormap=colormap,
                optimize_png=optimize_png
            )
        ),
        RenderHtmlExample(
            description=f"Annex I example\n{payload!r}\nISO/IEC 18004:{{2006,2015,2024}}",
            descriptor=write_optimal_qrcode(
                payload=payload,
                png_filename="qrcode_iso18004_2006_2015_2024_AnnexI_{VERSION}{LEVEL}p{PATTERN}.png",
                include_quiet_zone=include_quiet_zone,
                pattern=DataMaskPattern.PATTERN2,
                version_preference_list=[(1, ErrorCorrectionLevel.M)],
                colormap=colormap,
                optimize_png=optimize_png
            )
        )
    ]


def render(include_quiet_zone: bool, colormap: str, optimize_png: bool) -> list[RenderHtmlExample]:
    """Render QR-codes from the standard."""
    return [
        # Reproduces the example QR code of Figure 1 of the 2015 version of the standard.
        *write_introduction_examples(
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        ),
        # This produces a QR code with the Greek characters "ΑΒΓΔΕ" encoded in ISO-8859-7,
        # using ECI designator 9, as discussed in the standard.
        *write_explicit_eci_designator_example(
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        ),
        # Reproduce the "structured append" examples.
        *write_structured_append_mode_examples(
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        ),
        # Reproduces the example QR code discussed in the annex of the standard.
        *write_annex_examples(
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        )
    ]


def main():

    # Remove stale QR code example files.

    include_quiet_zone=True
    colormap = 'default'
    optimize_png = True

    remove_stale_files()
    render(include_quiet_zone, colormap, optimize_png)


if __name__ == "__main__":
    main()
