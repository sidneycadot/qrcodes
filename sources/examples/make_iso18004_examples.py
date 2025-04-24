#! /usr/bin/env -S python3 -B

"""Write QR codes discussed in the standard as PNG image files.

There are currently four editions of the standard:

ISO/IEC 18004:2000(E)
ISO/IEC 18004:2006(E)
ISO/IEC 18004:2015(E)
ISO/IEC 18004:2024(en)
"""

import glob
import os
from typing import Optional

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render_pil import render_qrcode_as_pil_image
from qrcode_generator.utilities import write_optimal_qrcode, optimize_png


def write_introduction_example(
        colormap: Optional[str | dict] = None,
        post_optimize: bool = False) -> None:
    """Write the first example of a QR code found in the standard, from the 2006 edition onwards.

    References:
    - ISO/IEC 18004:2000(E)   Not included in this version of the standard.
    - ISO/IEC 18004:2006(E)   Figure 1, Section 5.2, page 7.
    - ISO/IEC 18004:2015(E)   Figure 1, Section 6.2, page 7.
    - ISO/IEC 18004:2024(en)  <not yet available>
    """
    write_optimal_qrcode(
        "QR Code Symbol",
        "qrcode_iso18004_2006_2015_QRCodeSymbol_1Mp5.png",
        pattern=DataMaskingPattern.PATTERN5,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )


def write_explicit_eci_designator_example(
            colormap: Optional[str | dict] = None,
            post_optimize: bool = False) -> None:
    """Represent Greek characters in ISO-8859-7, which corresponds to ECI designator 9.

    This is an example from the standard. The standard just discusses the encoding using
    an ECI designator; it does not show a corresponding QR code symbol.

    Note that the encoding given in the standard is wrong; the string "ΑΒΓΔΕ" encoded
    using iso-8859-7 is 0xc1..0xc5, not 0xa1..0xa5.

    References:
    - ISO/IEC 18004:2000(E)   Section 8.4.1.1, page 19.
    - ISO/IEC 18004:2015(E)   Section 7.4.2.2, page 24.
    - ISO/IEC 18004:2024(en)  <not yet available>
    """

    payload = "ΑΒΓΔΕ"
    filename = "qrcode_iso18004_2000_2015_ExplicitEciDesignator_1H.png"

    octets = payload.encode("iso-8859-7")
    de = DataEncoder(EncodingVariant.SMALL)
    de.append_eci_designator(9)
    de.append_byte_mode_block(octets)
    qr_canvas = make_qr_code(de, 1, ErrorCorrectionLevel.H)
    im = render_qrcode_as_pil_image(qr_canvas, colormap=colormap)
    print(f"Saving {filename} ...")
    im.save(filename)
    if post_optimize:
        optimize_png(filename)


def write_structured_append_mode_examples(
        colormap: Optional[str | dict] = None,
        post_optimize: bool = False):
    """This reproduces the structured append mode example as given in the standard.

    References:
    - ISO/IEC 18004:2000(E)   Section 9.1, Figure 22, page 56.
    - ISO/IEC 18004:2015(E)   Section 8.1, Figure 28, page 60.
    - ISO/IEC 18004:2024(en)  <not yet available>
    """

    combined_payload = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Reproduces the example where the payload is encoded in a single QR code.
    write_optimal_qrcode(
        combined_payload,
        "qrcode_iso18004_2000_2015_StructuredAppendMode_combined_4Mp4.png",
        pattern=DataMaskingPattern.PATTERN4,
        version_preference_list=[(4, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )

    checksum = 0
    for c in combined_payload:
        checksum ^= ord(c)

    structured_append_qrcode_specs = [
        (0, DataMaskingPattern.PATTERN0, "ABCDEFGHIJKLMN"),
        (1, DataMaskingPattern.PATTERN7, "OPQRSTUVWXYZ0123"),
        (2, DataMaskingPattern.PATTERN7, "456789ABCDEFGHIJ"),
        (3, DataMaskingPattern.PATTERN3, "KLMNOPQRSTUVWXYZ")
    ]

    for (index, pattern, substring) in structured_append_qrcode_specs:
        de = DataEncoder(EncodingVariant.SMALL)
        de.append_structured_append_marker(index, 4, checksum)
        de.append_alphanumeric_mode_block(substring)
        qr_canvas = make_qr_code(de, 1, ErrorCorrectionLevel.M, pattern=pattern)
        im = render_qrcode_as_pil_image(qr_canvas, colormap=colormap)
        filename = f"qrcode_iso18004_2000_2015_StructuredAppendMode_split{index}_1Mp{pattern.name[-1]}.png"
        print(f"Saving {filename} ...")
        im.save(filename)
        if post_optimize:
            optimize_png(filename)


def write_annex_examples(
        colormap: Optional[str | dict] = None,
        post_optimize: bool = False) -> None:
    """Write the appendix example of a QR code found in the standard.

    Note that the data masking pattern selected differs between the standard versions.

    References:
    - ISO/IEC 18004:2000(E)   Figure G.2, Annex G, pages 84--85.
    - ISO/IEC 18004:2015(E)   Figure I.2, Annex I, pages 94--96.
    - ISO/IEC 18004:2024(en)  <not yet available>
    """

    write_optimal_qrcode(
        "01234567",
        "qrcode_iso18004_2000_AnnexG_1Mp3.png",
        pattern=DataMaskingPattern.PATTERN3,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_optimal_qrcode(
        "01234567",
        "qrcode_iso18004_2015_AnnexI_1Mp2.png",
        pattern=DataMaskingPattern.PATTERN2,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )


def main():

    # Remove stale QR code example files.

    for filename in glob.glob("qrcode_iso18004_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)

    colormap = 'default'
    post_optimize = True

    # This example reproduces the example QR code of Figure 1 of the 2015 version of the standard.
    write_introduction_example(
        colormap=colormap,
        post_optimize=post_optimize
    )

    # This produces a QR code with the Greek characters "ΑΒΓΔΕ" encoded in ISO-8859-7, using ECI designator 9.
    write_explicit_eci_designator_example(
        colormap=colormap,
        post_optimize=post_optimize
    )

    # Reproduce the "structured append" examples, where the information in the previous
    # example is split over four QR codes.
    write_structured_append_mode_examples(
        colormap=colormap,
        post_optimize=True
    )

    # This example reproduces the example QR code as discussed in the appendix of the standard.
    write_annex_examples(
        colormap=colormap,
        post_optimize=post_optimize
    )


if __name__ == "__main__":
    main()
