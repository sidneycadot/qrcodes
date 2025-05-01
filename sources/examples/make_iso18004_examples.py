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


def remove_stale_files() -> None:
    """Remove stale QR code files."""

    for filename in glob.glob("qrcode_iso18004_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)


def write_introduction_example(
        *,
        include_quiet_zone: bool,
        colormap: Optional[str | dict],
        post_optimize: bool) -> list[str]:
    """Write the first example of a QR code found in the standard, from the 2006 edition onwards.

    Note that the data masking pattern selected differs between the standard versions:
    - 2000       ...... : example is not present.
    - 2006, 2015 ...... : pattern 5
    - 2024       ...... : pattern 6

    References:
    - ISO/IEC 18004:2000(E)   Not included in this version of the standard.
    - ISO/IEC 18004:2006(E)   Figure 1, Section 5.2, page 7.
    - ISO/IEC 18004:2015(E)   Figure 1, Section 6.2, page 7.
    - ISO/IEC 18004:2024(en)  Figure 1, Section 5.2, page 6.
    """

    payload = "QR Code Symbol"

    filenames = []

    filename = "qrcode_iso18004_2006_2015_QRCodeSymbol_1Mp5.png"
    write_optimal_qrcode(
        payload=payload,
        filename=filename,
        include_quiet_zone=include_quiet_zone,
        pattern=DataMaskingPattern.PATTERN5,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )
    filenames.append(filename)

    filename = "qrcode_iso18004_2024_QRCodeSymbol_1Mp6.png"
    write_optimal_qrcode(
        payload=payload,
        filename=filename,
        include_quiet_zone=include_quiet_zone,
        pattern=DataMaskingPattern.PATTERN6,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )
    filenames.append(filename)

    return filenames

def write_explicit_eci_designator_example(
        *,
        colormap: Optional[str | dict],
        post_optimize: bool,
        include_quiet_zone: bool) -> list[str]:
    """Represent Greek characters in ISO-8859-7, which corresponds to ECI designator 9.

    This is an example from the standard. The standard just discusses the encoding using
    an ECI designator; it does not show a corresponding QR code symbol.

    Note that the encoding given in the standard is wrong; the string "ΑΒΓΔΕ" encoded
    using iso-8859-7 is 0xc1..0xc5, not 0xa1..0xa5.

    References:
    - ISO/IEC 18004:2000(E)   Section 8.4.1.1, page 19.
    - ISO/IEC 18004:2006(E)   Section 6.4.2.1, page 24.
    - ISO/IEC 18004:2015(E)   Section 7.4.2.2, page 24.
    - ISO/IEC 18004:2024(en)  <not yet available>
    """

    filenames = []

    payload = "ΑΒΓΔΕ"
    filename = "qrcode_iso18004_2000_2006_2015_ExplicitEciDesignator_1H.png"

    octets = payload.encode("iso-8859-7")
    de = DataEncoder(EncodingVariant.SMALL)
    de.append_eci_designator(9)
    de.append_byte_mode_block(octets)
    qr_canvas = make_qr_code(de, 1, ErrorCorrectionLevel.H, include_quiet_zone=include_quiet_zone)
    im = render_qrcode_as_pil_image(qr_canvas, colormap=colormap)
    print(f"Saving {filename} ...")
    im.save(filename)
    if post_optimize:
        optimize_png(filename)

    filenames.append(filename)

    return filenames


def write_structured_append_mode_examples(
        *,
        colormap: Optional[str | dict],
        post_optimize: bool,
        include_quiet_zone: bool) -> list[str]:
    """This reproduces the structured append mode example as given in the standard.

    References:
    - ISO/IEC 18004:2000(E)   Section 9.1, Figure 22, page 56.
    - ISO/IEC 18004:2006(E)   Section 7.1, Figure 29, page 59.
    - ISO/IEC 18004:2015(E)   Section 8.1, Figure 28, page 60.
    - ISO/IEC 18004:2024(en)  <not yet available>
    """

    payload = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    filenames = []

    # Reproduces the example where the payload is encoded in a single QR code.
    # The 62 characters are encoded in a single alphanumeric block.
    filename = "qrcode_iso18004_2000_2006_2015_StructuredAppendMode_combined_4Mp4.png"
    write_optimal_qrcode(
        payload=payload,
        filename=filename,
        include_quiet_zone=include_quiet_zone,
        pattern=DataMaskingPattern.PATTERN4,
        version_preference_list=[(4, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )

    checksum = 0
    for c in payload:
        checksum ^= ord(c)

    structured_append_qrcode_specs = [
        (0, DataMaskingPattern.PATTERN0, payload[0:14]),
        (1, DataMaskingPattern.PATTERN7, payload[14:30]),
        (2, DataMaskingPattern.PATTERN7, payload[30:46]),
        (3, DataMaskingPattern.PATTERN3, payload[46:62])
    ]

    for (index, pattern, substring) in structured_append_qrcode_specs:
        de = DataEncoder(EncodingVariant.SMALL)
        de.append_structured_append_marker(index, 4, checksum)
        de.append_alphanumeric_mode_block(substring)
        qr_canvas = make_qr_code(de, 1, ErrorCorrectionLevel.M, pattern=pattern, include_quiet_zone=include_quiet_zone)
        im = render_qrcode_as_pil_image(qr_canvas, colormap=colormap)
        filename = f"qrcode_iso18004_2000_2006_2015_StructuredAppendMode_split{index}_1Mp{pattern.name[-1]}.png"
        print(f"Saving {filename} ...")
        im.save(filename)
        if post_optimize:
            optimize_png(filename)
        filenames.append(filename)

    return filenames

def write_annex_examples(
        *,
        colormap: Optional[str | dict] = None,
        post_optimize: bool = None,
        include_quiet_zone: bool) -> list[str]:
    """Write the appendix example of a QR code found in the standard.

    Note that the data masking pattern selected differs between the standard versions:
    - 2000       ...... : pattern 3
    - 2006, 2015 ...... : pattern 2
    - 2024       ...... : (unknown)

    References:
    - ISO/IEC 18004:2000(E)   Figure G.2, Annex G, pages 84--85.
    - ISO/IEC 18004:2006(E)   Figure I.2, Annex I, pages 94--96.
    - ISO/IEC 18004:2015(E)   Figure I.2, Annex I, pages 94--96.
    - ISO/IEC 18004:2024(en)  <not yet available>
    """

    filenames = []

    filename = "qrcode_iso18004_2000_AnnexG_1Mp3.png"
    write_optimal_qrcode(
        payload="01234567",
        filename=filename,
        include_quiet_zone=include_quiet_zone,
        pattern=DataMaskingPattern.PATTERN3,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )
    filenames.append(filename)

    filename = "qrcode_iso18004_2006_2015_AnnexI_1Mp2.png"
    write_optimal_qrcode(
        payload="01234567",
        filename=filename,
        include_quiet_zone=include_quiet_zone,
        pattern=DataMaskingPattern.PATTERN2,
        version_preference_list=[(1, ErrorCorrectionLevel.M)],
        colormap=colormap,
        post_optimize=post_optimize
    )
    filenames.append(filename)

    return filenames


def render(include_quiet_zone: bool, colormap: str, post_optimize: bool) -> list[str]:

    filenames = []

    # This example reproduces the example QR code of Figure 1 of the 2015 version of the standard.
    filenames.extend(write_introduction_example(
        include_quiet_zone=include_quiet_zone,
        colormap=colormap,
        post_optimize=post_optimize
    ))

    # This produces a QR code with the Greek characters "ΑΒΓΔΕ" encoded in ISO-8859-7,
    # using ECI designator 9, as discussed in the standard.
    filenames.extend(write_explicit_eci_designator_example(
        include_quiet_zone=include_quiet_zone,
        colormap=colormap,
        post_optimize=post_optimize
    ))

    # Reproduce the "structured append" examples.
    filenames.extend(write_structured_append_mode_examples(
        include_quiet_zone=include_quiet_zone,
        colormap=colormap,
        post_optimize=True
    ))

    # Reproduces the example QR code discussed in the appendix of the standard.
    filenames.extend(write_annex_examples(
        include_quiet_zone=include_quiet_zone,
        colormap=colormap,
        post_optimize=post_optimize
    ))

    return filenames


def main():

    # Remove stale QR code example files.

    include_quiet_zone=True
    colormap = 'default'
    post_optimize = True

    remove_stale_files()
    render(include_quiet_zone, colormap, post_optimize)


if __name__ == "__main__":
    main()
