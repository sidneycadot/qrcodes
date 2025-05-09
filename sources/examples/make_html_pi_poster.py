#! /usr/bin/env python3

"""Write poster with pi QR codes as HTML file."""

import base64
import textwrap

from examples.make_qrcode_pi_as_svg import number_of_pi_characters_that_can_be_represented, pi_10k
from qrcode_generator.enum_types import ErrorCorrectionLevel
from qrcode_generator.utilities import make_optimal_qrcode, save_qrcode_as_png_file
from qrcode_generator.xml_writer import XmlWriter


def render_html_pi_poster(filename_html: str) -> None:

    # Generate HTML file.

    colormap='color'

    css_style_definitions ="""
    
        table,th,td { border: 1px solid black; }
        td { padding-left: 10mm; padding-right: 10mm; }
        .qr-code img { display: block; width: 80mm; margin-left: auto; margin-right: auto; margin-top: 8mm; margin-bottom: 8mm; image-rendering: pixelated; }
        .qr-code p { text-align: center; font-weight: bold; color: blue; }
    """

    with XmlWriter(filename_html) as html:
        with html.write_container_tag("html"):
            with html.write_container_tag("head"):
                html.write_leaf_tag("title", content="Example QR codes")
                html.write_leaf_tag("meta", arguments = {"charset": "UTF-8"})
                with html.write_container_tag("style"):
                    for line in textwrap.dedent(css_style_definitions).strip().splitlines():
                        html.write_indented_line(line)
            with html.write_container_tag("body"):
                html.write_leaf_tag("h1", content="Pi encoded in all QR-code versions")
                with html.write_container_tag("table"):
                    for version in range(1, 41):
                        with html.write_container_tag("tr"):
                            for level in reversed(ErrorCorrectionLevel):
                                with html.write_container_tag("td",  arguments={"class": "qr-code"}):
                                    # Generate the QR code.
                                    number_of_pi_characters = number_of_pi_characters_that_can_be_represented(version, level)
                                    pi_characters = pi_10k[:number_of_pi_characters]
                                    canvas = make_optimal_qrcode(payload=pi_characters, version_preference_list=[(version, level)], include_quiet_zone=False)
                                    png_filename = "temp.png"
                                    descriptor = save_qrcode_as_png_file(
                                        png_filename=png_filename,
                                        canvas=canvas,
                                        colormap=colormap,
                                        optimize_png=True
                                    )
                                    with open(descriptor.png_filename, "rb") as fi:
                                        imagedata = fi.read()
                                        source = f"data:image/png;base64,{base64.b64encode(imagedata).decode('ascii')}"
                                        html.write_leaf_tag("img", arguments={"src": source})
                                        html.write_leaf_tag("p", content=f"{canvas.version}-{canvas.level.name}, pattern {canvas.pattern.name[-1]}\n{number_of_pi_characters} characters of π".replace("\n", "<br/>"))

def main():
    render_html_pi_poster("pi_poster.html")

if __name__ == "__main__":
    main()
