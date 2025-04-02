#! /usr/bin/env -S python3 -B

"""Generate QR code examples."""

import subprocess

from enum_types import ErrorCorrectionLevel, EncodingVariant
from data_encoder import DataEncoder
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


def main():

    magnification = 4
    version = 40
    variant = EncodingVariant.LARGE
    level = ErrorCorrectionLevel.L
    include_quiet_zone = True
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

    de.append_terminator()
    de.append_padding_bits()

    qr_canvas = make_qr_code(de, version, level, include_quiet_zone, None)

    # Capture image.
    im = render_qrcode_as_pil_image(qr_canvas, 'RGB', colormap1, magnification)

    filename = f"v{version}{level.name}.png"
    print(f"Saving {filename} ...")
    im.save(filename)

    if post_optimize:
        subprocess.run(["optipng", filename])


if __name__ == "__main__":
    main()
