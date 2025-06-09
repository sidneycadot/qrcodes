#! /usr/bin/env -S python3 -B

"""Write QR code poster with encodings of pi as an SVG image."""

import base64
import os
import subprocess

from qrcode.optimal_encoding import make_optimal_qrcode
from qrcode.render.render_svg import render_qr_canvas_as_svg_group
from qrcode.render.xml_writer import XmlWriter
from qrcode.enum_types import ErrorCorrectionLevel
from qrcode.lookup_tables import version_specification_table
from qrcode.render.utilities import save_qrcode_as_png_file

from examples.utilities.render_pi import number_of_pi_characters_that_can_be_represented, first_n_characters_of_pi


def write_svg_qrcode_poster(filename_svg: str) -> None:

    with XmlWriter(filename_svg) as svg:

        with svg.write_container_tag(
            "svg", {
                "viewBox": "0 0 5000 52000",
                "xmlns": "http://www.w3.org/2000/svg",
                "xmlns:xlink": "http://www.w3.org/1999/xlink"
            }):

            svg.write_leaf_tag("rect", {"width": "100%", "height": "100%", "fill": "white"})

            with svg.write_container_tag("g", {"transform": "translate(2500 700) scale(800)"}):

                svg.write_leaf_tag(
                    "text",
                    {
                        "x": 0.0, "y": -0.42, "fill": "blue", "font-size": "0.36",
                        "dominant-baseline": "middle", "text-anchor": "middle"
                    },
                    content="Decimals of π encoded in QR codes"
                )

                for version in range(1, 41):

                    # if version not in (1, 2, 3): continue

                    with svg.write_container_tag("g", {"transform": f"translate(0 {(version - 1) * 1.6:.9f})"}):

                        for level in reversed(ErrorCorrectionLevel):

                            number_of_pi_characters = number_of_pi_characters_that_can_be_represented(version, level)
                            pi_characters = first_n_characters_of_pi(number_of_pi_characters)

                            with svg.write_container_tag("g", {"transform": f"translate({(ErrorCorrectionLevel.H.value - level.value - 1.5) * 1.4:.9f} 0)"}):

                                version_specification = version_specification_table[(version, level)]

                                canvas = make_optimal_qrcode(
                                    payload=pi_characters,
                                    pattern=None,
                                    version_preference_list=[(version, level)],
                                    include_quiet_zone=False
                                )

                                colormap = "color"

                                use_embedded_png = True

                                if use_embedded_png:

                                    descriptor = save_qrcode_as_png_file(
                                        png_filename="temp.png",
                                        canvas=canvas,
                                        colormap=colormap,
                                        optimize_png=True
                                    )

                                    with open(descriptor.png_filename, "rb") as fi:
                                        imagedata = fi.read()

                                    os.unlink(descriptor.png_filename)

                                    source = f"data:image/png;base64,{base64.b64encode(imagedata).decode('ascii')}"
                                    svg.write_leaf_tag("image", arguments={
                                        "x": "-0.5",
                                        "style" : "image-rendering: pixelated;",
                                        "width": 1,
                                        "height": 1,
                                        "href": source
                                    })

                                else:

                                    render_qr_canvas_as_svg_group(
                                        svg,
                                        canvas=canvas,
                                        extra_group_attributes={"transform": f"translate(-0.5 0) scale({1/canvas.width})"},
                                        colormap=colormap
                                    )

                                label = f'<tspan x="0" y="1.10">{version}-{level.name}, pattern {canvas.pattern.name[-1]}</tspan>' \
                                        f'<tspan x="0" y="1.24">{version_specification.number_of_data_codewords() * 8} databits</tspan>' \
                                        f'<tspan x="0" y="1.36">{version_specification.number_of_error_correcting_codewords * 8} error correction bits</tspan>' \
                                        f'<tspan x="0" y="1.48">π to {number_of_pi_characters - 2} digits</tspan>'

                                svg.write_leaf_tag("text", {
                                    "fill": "blue",
                                    "font-size": "0.10px",
                                    "font-weight": "bold",
                                    "dominant-baseline": "middle",
                                    "text-anchor": "middle"
                                }, content=label)

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
