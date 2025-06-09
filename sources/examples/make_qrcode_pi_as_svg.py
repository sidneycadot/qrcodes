#! /usr/bin/env -S python3 -B

"""Write QR code poster with encodings of pi as an SVG image."""

import subprocess

from qrcode.render.render_svg import render_qr_canvas_as_svg_path
from qrcode.render.xml_writer import XmlWriter
from qrcode.enum_types import DataMaskPattern, ErrorCorrectionLevel
from qrcode.render.utilities import make_optimal_qrcode

from utilities.render_pi import number_of_pi_characters_that_can_be_represented, first_n_characters_of_pi


def write_qrcode_pi_as_svg(version: int, level: ErrorCorrectionLevel, pattern: DataMaskPattern, include_quiet_zone: bool) -> None:

    number_of_pi_characters = number_of_pi_characters_that_can_be_represented(version, level)

    pi_characters = first_n_characters_of_pi(number_of_pi_characters)

    canvas = make_optimal_qrcode(
        payload=pi_characters,
        pattern=pattern,
        version_preference_list=[(version, level)],
        include_quiet_zone=include_quiet_zone
    )

    print(f"Writing code {version}-{level.name} with {number_of_pi_characters} characters of pi ...")

    filename_prefix = f"qrcode_pi_{version}{level.name}p{pattern.name[-1]}_{number_of_pi_characters}_digits"
    filename_svg = filename_prefix + ".svg"
    filename_pdf = filename_prefix + ".pdf"

    with XmlWriter(filename_svg) as svg:

        with svg.write_container_tag("svg", {"viewBox": f"0 0 {canvas.width} {canvas.height}", "xmlns": "http://www.w3.org/2000/svg"}):
            render_qr_canvas_as_svg_path(svg, canvas=canvas, light_color="yellow", dark_color="blue")
            #render_qr_canvas_as_svg_group(svg, canvas=canvas, colormap='color')

    # Try to write a PDF file. If rsvg-convert is not available, this is a no-op.
    try:
        subprocess.run(["rsvg-convert", "--format", "pdf", "--output", filename_pdf, filename_svg], check=False)
    except FileNotFoundError:
        pass


def main():

    include_quiet_zone = False

    write_qrcode_pi_as_svg(1, ErrorCorrectionLevel.H, DataMaskPattern.PATTERN0, include_quiet_zone)
    write_qrcode_pi_as_svg(1, ErrorCorrectionLevel.L, DataMaskPattern.PATTERN0, include_quiet_zone)
    #write_qrcode_pi_as_svg(40, ErrorCorrectionLevel.H, DataMaskingPattern.PATTERN0, include_quiet_zone)
    #write_qrcode_pi_as_svg(40, ErrorCorrectionLevel.L, DataMaskingPattern.PATTERN0, include_quiet_zone)


if __name__ == "__main__":
    main()
