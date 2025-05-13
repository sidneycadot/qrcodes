#! /usr/bin/env -S python3 -B

"""Write QR code poster with encodings of pi as an SVG image."""
import base64
import os
import subprocess

from qrcode_generator.render.render_svg import render_qr_canvas_as_svg_path
from qrcode_generator.render.xml_writer import XmlWriter
from qrcode_generator.enum_types import DataMaskingPattern, ErrorCorrectionLevel
from qrcode_generator.lookup_tables import version_specification_table
from qrcode_generator.render.utilities import make_optimal_qrcode, save_qrcode_as_png_file

from examples.utilities.render_pi import number_of_pi_characters_that_can_be_represented, first_n_characters_of_pi


def write_svg_qrcode_poster(filename_svg: str) -> None:

    with XmlWriter(filename_svg) as svg:

        with svg.write_container_tag(
            "svg", {
                "viewBox": "0 0 5400 5400",
                "xmlns": "http://www.w3.org/2000/svg",
                "xmlns:xlink": "http://www.w3.org/1999/xlink"
            }):

            svg.write_leaf_tag("rect", {"width": "100%", "height": "100%", "fill": "white"})

            svg.write_leaf_tag("text", {"x": 2700.0, "y": 350.0, "fill": "red", "font-size": "300px", "dominant-baseline": "middle", "text-anchor": "middle"}, content="Decimals of π encoded in QR codes")

            with svg.write_container_tag("g", {"transform": "translate(600 700) scale(800)"}):

                for version in range(1, 41):

                    if version not in (1, 3): continue

                    with svg.write_container_tag("g", {"transform": f"translate(0 {(version - 1) * 1.2:.9f})"}):

                        for level in reversed(ErrorCorrectionLevel):

                            number_of_pi_characters = number_of_pi_characters_that_can_be_represented(version, level)
                            pi_characters = first_n_characters_of_pi(number_of_pi_characters)

                            with svg.write_container_tag("g", {"transform": f"translate({(ErrorCorrectionLevel.H.value - level.value) * 1.2:.9f} 0 )"}):

                                version_specification = version_specification_table[(version, level)]

                                canvas = make_optimal_qrcode(
                                    payload=pi_characters,
                                    pattern=None,
                                    version_preference_list=[(version, level)],
                                    include_quiet_zone=False
                                )

                                label = f'<tspan x="0" y="0.8">{version}-{level.name}, pattern {canvas.pattern.name[-1]}</tspan>' \
                                        f'<tspan x="0" y="1.2">{version_specification.number_of_data_codewords() * 8} databits</tspan>' \
                                        f'<tspan x="0" y="1.6">π to {number_of_pi_characters - 2} digits</tspan>'

                                svg.write_leaf_tag("text", {
                                    "x": 0, "y": "1.2",
                                    "fill": "blue",
                                    "font-size": "0.06px",
                                    "font-weight": "bold",
                                    "dominant-baseline": "middle",
                                    "text-anchor": "middle"
                                }, content=label)

                                colormap = "color"

                                descriptor = save_qrcode_as_png_file(
                                    png_filename="temp.png",
                                    canvas=canvas,
                                    colormap=colormap,
                                    optimize_png=True
                                )

                                with open(descriptor.png_filename, "rb") as fi:
                                    imagedata = fi.read()
                                    source = f"data:image/png;base64,{base64.b64encode(imagedata).decode('ascii')}"
                                    #description = f"{canvas.version}-{canvas.level.name}, pattern {canvas.pattern.name[-1]}\n{number_of_pi_characters} characters of π"
                                    svg.write_leaf_tag("image", arguments={
                                        "x": "-0.5",
                                        "width": 1,
                                        "height": 1,
                                        "href": source
                                    })

    os.unlink("temp.png")

    filename_pdf = os.path.splitext(filename_svg)[0] + ".pdf"

    # Try to write a PDF file. If rsvg-convert is not available, this is a no-op.
    try:
        subprocess.run(["rsvg-convert", "--format", "pdf", "--output", filename_pdf, filename_svg], check=False)
    except FileNotFoundError:
        pass


def main():
    write_svg_qrcode_poster("qrcode_pi_poster.svg")


if __name__ == "__main__":
    main()
