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

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskPattern
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render.utilities import write_optimal_qrcode, save_qrcode_as_png_file

from examples.utilities.render_html_examples import RenderHtmlExample


def remove_stale_files() -> None:
    """Remove stale QR code files."""

    for filename in glob.glob("qrcode_mirror_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)


def render_mirroring_examples(
        *,
        include_quiet_zone: bool,
        colormap: Optional[str | dict],
        optimize_png: bool):
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

    write_optimal_qrcode(
        payload=payload,
        png_filename="qrcode_iso18004_2024_MirrorExample_Normal_{VERSION}{LEVEL}p{PATTERN}.png",
        include_quiet_zone=include_quiet_zone,
        pattern=DataMaskPattern.PATTERN6,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        optimize_png=optimize_png
    )

    write_optimal_qrcode(
        payload=payload,
        png_filename="qrcode_iso18004_2024_MirrorExample_HorizontallyMirror_{VERSION}{LEVEL}p{PATTERN}.png",
        include_quiet_zone=include_quiet_zone,
        pattern=DataMaskPattern.PATTERN6,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        transform="mirror-horizontal",
        optimize_png=optimize_png
    )

    write_optimal_qrcode(
        payload=payload,
        png_filename="qrcode_iso18004_2024_MirrorExample_Transposed_{VERSION}{LEVEL}p{PATTERN}.png",
        include_quiet_zone=include_quiet_zone,
        pattern=DataMaskPattern.PATTERN6,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        transform="transpose",
        optimize_png=optimize_png
    )


def main():

    # Remove stale QR code example files.

    include_quiet_zone=True
    colormap = 'default'
    optimize_png = True

    remove_stale_files()

    render_mirroring_examples(
        include_quiet_zone = include_quiet_zone,
        colormap = colormap,
        optimize_png = optimize_png
    )


if __name__ == "__main__":
    main()
