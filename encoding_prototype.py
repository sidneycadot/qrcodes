#! /usr/bin/env -S python3 -B

"""Generate QR code examples."""

import subprocess
import base64

from typing import Optional

from enum_types import ErrorCorrectionLevel, EncodingVariant
from data_encoder import DataEncoder
from lookup_tables import version_specifications
from optimal_encoding import find_optimal_string_encoding
from qr_code import ModuleValue, make_qr_code
from render_pil import render_qrcode_as_pil_image


def append_pi(de):
    with open("tests/pi_10k.txt", "r") as fi:
        pi_chars = fi.read()
    de.append_alphanumeric_mode_block(pi_chars[:2])
    de.append_numeric_mode_block(pi_chars[2:7081])

def append_html(de):
    with open("examples/sidney.html", "r") as fi:
        html = fi.read()
    html = "data:text/html," + html
    de.append_byte_mode_block(html.encode())

def append_url(de):
    de.append_byte_mode_block(b"http://data.jigsaw.nl/tegeltjes.gif")

def append_vcard(de):
    with open("examples/sidney.vcard", "r") as fi:
        vcard = fi.read()
    de.append_byte_mode_block(vcard.encode())

def append_geo_position(de):
    # Supported by iOS
    #de.append_byte_mode_block(b"geo:37.91334,15.33897")
    #de.append_byte_mode_block(b"geo:37.364722,14.334722")
    de.append_byte_mode_block(b"geo:37.917419,15.330548")

def append_mailto(de):
    # Supported by iOS
    de.append_byte_mode_block(b"mailto:sidney@jigsaw.nl")

def append_kanji(de):
    de.append_kanji_mode_block('点茗')

def append_kanji_test(de):
    de.append_byte_mode_block(b'Japanese characters in Kanji block: ')
    de.append_kanji_mode_block('点茗')
    de.append_byte_mode_block(b'\nJapanese characters in byte block (UTF-8 bytes): ' + '点茗'.encode('utf-8') + b'\n')


colormap1 = {
    ModuleValue.QUIET_ZONE_0: '#ffffff',
    ModuleValue.FINDER_PATTERN_0: '#ffcccc',
    ModuleValue.FINDER_PATTERN_1: '#ff0000',
    ModuleValue.SEPARATOR_0: '#ffffff',
    ModuleValue.TIMING_PATTERN_0: '#ffcccc',
    ModuleValue.TIMING_PATTERN_1: '#ff0000',
    ModuleValue.ALIGNMENT_PATTERN_0: '#ffcccc',
    ModuleValue.ALIGNMENT_PATTERN_1: '#ff0000',
    ModuleValue.FORMAT_INFORMATION_0: '#ccffcc',
    ModuleValue.FORMAT_INFORMATION_1: '#00bb00',
    ModuleValue.FORMAT_INFORMATION_INDETERMINATE: '#ccffcc',
    ModuleValue.VERSION_INFORMATION_0: '#ddddff',
    ModuleValue.VERSION_INFORMATION_1: '#0000ff',
    ModuleValue.VERSION_INFORMATION_INDETERMINATE: '#ddddff',
    ModuleValue.DATA_ERC_0: '#ffffff',
    ModuleValue.DATA_ERC_1: '#000000',
    ModuleValue.INDETERMINATE: '#ff0000'
}

colormap2 = {
    ModuleValue.QUIET_ZONE_0: '#ffffff',
    ModuleValue.FINDER_PATTERN_0: '#ffffff',
    ModuleValue.FINDER_PATTERN_1: '#000000',
    ModuleValue.SEPARATOR_0: '#ffffff',
    ModuleValue.TIMING_PATTERN_0: '#ffffff',
    ModuleValue.TIMING_PATTERN_1: '#000000',
    ModuleValue.ALIGNMENT_PATTERN_0: '#ffffff',
    ModuleValue.ALIGNMENT_PATTERN_1: '#000000',
    ModuleValue.FORMAT_INFORMATION_0: '#ffffff',
    ModuleValue.FORMAT_INFORMATION_1: '#000000',
    ModuleValue.FORMAT_INFORMATION_INDETERMINATE: '#ffffff',
    ModuleValue.VERSION_INFORMATION_0: '#ffffff',
    ModuleValue.VERSION_INFORMATION_1: '#000000',
    ModuleValue.VERSION_INFORMATION_INDETERMINATE: '#ffffff',
    ModuleValue.DATA_ERC_0: '#ffffff',
    ModuleValue.DATA_ERC_1: '#000000',
    ModuleValue.INDETERMINATE: '#ffffff'
}


def make_natural_preference_order() -> list[tuple[int, ErrorCorrectionLevel]]:
    return [
        (version, level)
        for version in range(1, 41)
        for level in (ErrorCorrectionLevel.H, ErrorCorrectionLevel.Q, ErrorCorrectionLevel.M, ErrorCorrectionLevel.L)
    ]


def version_to_variant(version: int) -> EncodingVariant:
    if not (1 <= version <= 40):
        raise ValueError()

    if version <= 9:
        return EncodingVariant.SMALL
    elif version <= 26:
        return EncodingVariant.MEDIUM
    else:
        return EncodingVariant.LARGE


def make_optimal_qrcode(s: str, include_quiet_zone: bool, preflist = None, byte_mode_encoding: Optional[str] = None):

    if preflist is None:
        preflist = make_natural_preference_order()

    variant_cache = {}
    for (version, level) in preflist:
        variant = version_to_variant(version)
        if variant in variant_cache:
            solution = variant_cache[variant]
        else:
            solutions = find_optimal_string_encoding(s, variant, byte_mode_encoding)
            if len(solutions) == 0:
                solution = None
            else:
                solution = solutions[0]
            variant_cache[variant] = solution
        if solution is None:
            continue

        # See if this solution would fit in this (version, level) code.
        version_specification = version_specifications[(version, level)]

        if version_specification.number_of_data_codewords() * 8 >= solution.bitcount():
            print(f"Selected code: {version}-{level.name}")
            break

    else:
        # No acceptable solution found.
        return None

    de = DataEncoder(variant)
    solution.render(de)

    return make_qr_code(de, version, level, include_quiet_zone, None)


def write_optimal_qrcode(s: str, filename: str, colormap, magnification: int, post_optimize: bool) -> None:
    qr_canvas = make_optimal_qrcode(s, True)
    if qr_canvas is None:
        raise RuntimeError("Unable to store the string in a QR code.")
    im = render_qrcode_as_pil_image(qr_canvas, 'RGB', colormap, magnification)
    print(f"Saving {filename} ...")
    im.save(filename)
    if post_optimize:
        subprocess.run(["optipng", filename], stderr=subprocess.DEVNULL)

def main2():

    version = 40
    variant = EncodingVariant.LARGE
    level = ErrorCorrectionLevel.L
    include_quiet_zone = True
    magnification = 4
    post_optimize = True

    de = DataEncoder(variant)

    #append_geo_position(de)
    append_pi(de)
    #append_url(de)
    #append_mailto(de)
    #append_kanji_test(de)

    #de.append_eci_designator(899)
    #de.append_byte_mode_block('Hallo Petra!\n'.encode())
    #append_kanji(de)
    #de.append_byte_mode_block('Hallo Sidney!\n'.encode())
    #de.append_byte_mode_block('Hello ⛄ Snowman!\n'.encode())
    #de.append_numeric_mode_block("01234567")
    #de.append_byte_mode_block(b"http://www.jigsaw.nl?data=sidney")
    #de.append_byte_mode_block(b"https://www.jigsaw.nl/")

    qr_canvas = make_qr_code(de, version, level, include_quiet_zone, None)

    # Capture image.
    im = render_qrcode_as_pil_image(qr_canvas, 'RGB', colormap1, magnification)

    filename = f"v{version}{level.name}.png"
    print(f"Saving {filename} ...")
    im.save(filename)

def main():
    #write_optimal_qrcode("Hello World!", "hello.png", colormap1, 20, True)
    #write_optimal_qrcode("Hello Mr. Snowman! ⛄⛄⛄", "snowman.png", colormap2, 1, True)

    with open("tests/pi_10k.txt", "r") as fi:
        pi_characters = fi.read()
    #write_optimal_qrcode(pi_characters[:7082], "pi.png", colormap1, 1, True)
    write_optimal_qrcode(pi_characters[:4680], "pi.png", colormap1, 1, True)

    #write_optimal_qrcode("http://data.jigsaw.nl/tegeltjes.gif", "rick.png", colormap2, 1, True)

    #with open("examples/sidney.vcard", "r") as fi:
    #    vcard = fi.read()
    #write_optimal_qrcode(vcard, "vcard.png", colormap2, 1, True)

    #with open("examples/sidney.html", "r") as fi:
    #    html = fi.read()
    #write_optimal_qrcode("data:text/html;base64," + base64.b64encode(html.encode()).decode(), "html.png", colormap2, 1, True)

    #write_optimal_qrcode("geo:37.917419,15.330548", "geo.png", colormap2, 1, True)


if __name__ == "__main__":
    main()
