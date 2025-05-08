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
from qrcode_generator.utilities import save_qrcode_as_png_file

from render_html_examples import RenderableExample


def remove_stale_files() -> None:
    """Remove stale QR code files."""
    for filename in glob.glob("qrcode_eci_*.png"):
        print("Removing", filename, "...")
        os.remove(filename)


def write_eci_test(
        *,
        payload: str,
        encoding: str,
        encoding_description: str,
        eci_designator_value: int,
        include_quiet_zone: bool,
        colormap: Optional[str | dict],
        optimize_png: bool) -> RenderableExample:
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
        raise RuntimeError("Cannot encode the string with an ECI designator prefix (too big).")

    de = DataEncoder(EncodingVariant.from_version(version)).append_eci_designator(eci_designator_value).append_byte_mode_block(payload_octets)

    canvas = make_qr_code(de, version=version, level=level, include_quiet_zone=include_quiet_zone)

    png_filename = f"qrcode_eci_{eci_designator_value}_{encoding}_{{VERSION}}{{LEVEL}}p{{PATTERN}}.png"

    return RenderableExample(
        description=f"ECI {eci_designator_value}\n{encoding_description}",
        descriptor=save_qrcode_as_png_file(
            png_filename=png_filename,
            canvas=canvas,
            colormap=colormap,
            optimize_png=optimize_png
        )
    )


def write_extended_ascii_test(
        *,
        encoding: str,
        encoding_description: str,
        eci_designator_value: int,
        include_quiet_zone: bool,
        colormap: Optional[str | dict],
        optimize_png: bool) -> RenderableExample:
    """Write QR code using an ECI code for an extended ASCII encoding."""

    slist = []

    for octet_value in range(128, 256):
        octet = bytes([octet_value])
        try:
            c = octet.decode(encoding)
        except UnicodeDecodeError:
            pass
        else:
            assert len(c) == 1
            s = f"{octet_value}: '{c}'\n"
            slist.append(s)

    payload = f"{encoding_description} is encoded using ECI designator value {eci_designator_value}, and can represent the following {len(slist)} non-ascii characters:\n\n{''.join(slist)}."
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

    return write_eci_test(
        payload=payload,
        encoding=encoding,
        encoding_description=encoding_description,
        eci_designator_value=eci_designator_value,
        include_quiet_zone=include_quiet_zone,
        colormap=colormap,
        optimize_png=optimize_png
    )


def render(include_quiet_zone: bool, colormap: str, optimize_png: bool) -> list[RenderableExample]:
    """Render ECI examples."""

    return [

        # Explicit ASCII encoding.
        write_eci_test(
            payload="This is an ASCII encoded text, using ECI designator value 27.",
            encoding="ascii",
            encoding_description="ASCII",
            eci_designator_value = 27,
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        ),

        # Extended ASCII encodings (ASCII with interpretations given to characters 128 .. 255).
        *(
            write_extended_ascii_test(
                encoding=encoding,
                encoding_description=encoding_description,
                eci_designator_value=eci_designator_value,
                include_quiet_zone=include_quiet_zone,
                colormap=colormap,
                optimize_png=optimize_png
            )
            for (encoding, encoding_description, eci_designator_value) in [
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
        ),

        # Unicode encodings.
        write_eci_test(
            payload="This is a UTF-8 encoded text, using ECI designator value 26.",
            encoding="utf_8",
            encoding_description="UTF-8",
            eci_designator_value = 26,
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        ),

        write_eci_test(
            payload="This is a UTF-16 (big endian) encoded text, using ECI designator value 25.",
            encoding="utf_16_be",
            encoding_description="UTF-16 (Big Endian)",
            eci_designator_value = 25,
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        ),

        write_eci_test(
            payload="This is a UTF-16 (little endian) encoded text, using ECI designator value 33.",
            encoding="utf_16_le",
            encoding_description="UTF-16 (Little Endian)",
            eci_designator_value = 33,
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        ),

        write_eci_test(
            payload="This is a UTF-32 (big endian) encoded text, using ECI designator value 34.",
            encoding="utf_32_be",
            encoding_description="UTF-32 (Big Endian)",
            eci_designator_value=34,
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        ),

        write_eci_test(
            payload="This is a UTF-32 (little endian) encoded text, using ECI designator value 35.",
            encoding="utf_32_le",
            encoding_description="UTF-32 (Little Endian)",
            eci_designator_value=35,
            include_quiet_zone=include_quiet_zone,
            colormap=colormap,
            optimize_png=optimize_png
        )
    ]


def main():

    include_quiet_zone=True
    colormap = 'color'
    optimize_png = True

    remove_stale_files()
    render(include_quiet_zone, colormap, optimize_png)


if __name__ == "__main__":
    main()
