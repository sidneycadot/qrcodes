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
from qrcode_generator.render_pil import render_qrcode_as_pil_image
from qrcode_generator.utilities import optimize_png


def write_eci_test(
        filename: str,
        payload: str,
        encoding: str,
        eci_designator_value: int,
        colormap: Optional[str | dict] = None,
        post_optimize: bool = False) -> None:
    """Write QR code using an ECI designator combined with a specific encoding."""

    payload_octets = payload.encode(encoding)

    for version, level in itertools.product(range(1, 41), reversed(ErrorCorrectionLevel)):
        version_specification = version_specification_table[(version, level)]
        # 12 bits for the ECI designator.
        # 4 bits for the bytes block intro.
        # k bits for the bytes block count bits.
        bits_available = 8 * version_specification.number_of_data_codewords() - 16 - count_bits_table[EncodingVariant.from_version(version)][CharacterEncodingType.BYTES]
        if 8 * len(payload_octets) <= bits_available:
            break
    else:
        raise RuntimeError("Cannot encode the string with an ECI prefix (too big).")

    de = DataEncoder(EncodingVariant.from_version(version))
    de.append_eci_designator(eci_designator_value),
    de.append_byte_mode_block(payload_octets)

    qr_canvas = make_qr_code(de, version, level)
    im = render_qrcode_as_pil_image(qr_canvas, colormap=colormap)
    print(f"Saving {filename} ...")
    im.save(filename)
    if post_optimize:
        optimize_png(filename)


def write_extended_ascii_test(
        encoding: str,
        encoding_description: str,
        eci_designator_value: int,
        colormap: Optional[str | dict] = None,
        post_optimize: bool = False) -> None:

    slist = []

    for octet_value in range(128, 256):
        octet = bytes([octet_value])
        try:
            c = octet.decode(encoding)
        except UnicodeDecodeError:
            pass
        else:
            s = f"'{c}'"
            slist.append(s)

    payload = f"{encoding_description} is encoded using ECI designator value {eci_designator_value}, and can represent the following {len(slist)} non-ascii characters: " + ", ".join(slist) + "."
    payload_octets = payload.encode(encoding)

    # Find the smallest QR code that can encode the octets.
    for version, level in itertools.product(range(1, 41), reversed(ErrorCorrectionLevel)):
        version_specification = version_specification_table[(version, level)]
        # 12 bits for the ECI designator.
        # 4 bits for the bytes block intro.
        # k bits for the bytes block count bits.
        bits_available = 8 * version_specification.number_of_data_codewords() - 16 - count_bits_table[EncodingVariant.from_version(version)][CharacterEncodingType.BYTES]
        if 8 * len(payload_octets) <= bits_available:
            break
    else:
        raise RuntimeError()

    filename = f"qrcode_eci_{eci_designator_value}_{encoding}.png"

    write_eci_test(
        filename = filename,
        payload = payload,
        encoding = encoding,
        eci_designator_value = eci_designator_value,
        colormap = colormap,
        post_optimize = post_optimize
    )


def main():

    # Remove stale QR code example files.

    for filename in glob.glob("qrcode_eci_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)

    colormap = 'color'
    post_optimize = True

    extended_ascii_table = [
        ("cp437"       , "Codepage-437", 0),
        ("cp437"       , "Codepage-437", 2),
        ("iso_8859_1"  , "ISO-8859-1"  , 1),
        ("iso_8859_1"  , "ISO-8859-1"  , 3),
        ("iso_8859_2"  , "ISO-8859-2"  , 4),
        ("iso_8859_3"  , "ISO-8859-3"  , 5),
        ("iso_8859_4"  , "ISO-8859-4"  , 6),
        ("iso_8859_5"  , "ISO-8859-5"  , 7),
        ("iso_8859_6"  , "ISO-8859-6"  , 8),
        ("iso_8859_7"  , "ISO-8859-7"  , 9),
        ("iso_8859_8"  , "ISO-8859-8"  , 10),
        ("iso_8859_9"  , "ISO-8859-9"  , 11),
        ("iso_8859_10" , "ISO-8859-10" , 12),
        ("iso_8859_11" , "ISO-8859-11" , 13),
        ("iso_8859_13" , "ISO-8859-13" , 15),
        ("iso_8859_14" , "ISO-8859-14" , 16),
        ("iso_8859_15" , "ISO-8859-15" , 17),
        ("iso_8859_16" , "ISO-8859-16" , 18)
    ]

    for (encoding, encoding_description, eci_designator_value) in extended_ascii_table:
        write_extended_ascii_test(
            encoding,
            encoding_description,
            eci_designator_value,
            colormap,
            post_optimize
        )

    level = ErrorCorrectionLevel.H

    write_eci_test(
        filename="qrcode_eci_25_utf16be.png",
        payload="This is a UTF-16 (big endian) encoded text, using ECI designator value 25.",
        encoding="utf_16_be",
        eci_designator_value = 25,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_26_utf8.png",
        payload="This is a UTF-8 encoded text, using ECI designator value 26.",
        encoding="utf_8",
        eci_designator_value = 26,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_27_ascii.png",
        payload="This is an ASCII encoded text, using ECI designator value 27.",
        encoding="ascii",
        eci_designator_value = 27,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_33_utf16le.png",
        payload="This is a UTF-16 (little endian) encoded text, using ECI designator value 33.",
        encoding="utf_16_le",
        eci_designator_value = 33,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_34_utf32be.png",
        payload="This is a UTF-32 (big endian) encoded text, using ECI designator value 34.",
        encoding="utf_32_be",
        eci_designator_value=34,
        colormap=colormap,
        post_optimize=post_optimize
    )

    write_eci_test(
        filename="qrcode_eci_35_utf32le.png",
        payload="This is a UTF-32 (little endian) encoded text, using ECI designator value 35.",
        encoding="utf_32_le",
        eci_designator_value=35,
        colormap=colormap,
        post_optimize=post_optimize
    )


if __name__ == "__main__":
    main()
