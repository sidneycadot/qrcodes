#! /usr/bin/env -S python3 -B

"""Write QR code as SVG image."""

import os
import subprocess
import base64
import textwrap
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from examples.xml_writer import XmlWriter
from qrcode_generator.enum_types import DataMaskingPattern, ErrorCorrectionLevel
from qrcode_generator.lookup_tables import version_specification_table
from qrcode_generator.render_pil import colormap_color
from sources.qrcode_generator.utilities import write_optimal_qrcode, make_optimal_qrcode


def write_image(filename: str) -> None:

    im = Image.new('RGB', (160, 160), color='blue')
    draw = ImageDraw.Draw(im)
    draw.circle((79.5, 79.5), 65, fill='yellow', outline=None)
    font = ImageFont.load_default(40)
    draw.text((79.5, 79.5), "Hello!", fill='red', anchor='mm', font=font)
    im.save(filename)
    subprocess.run(["optipng", filename], stderr=subprocess.DEVNULL, check=True)
    with open(filename, "rb") as fi:
        imagedata = fi.read()

    base64_imagedata = base64.b64encode(imagedata).decode('ascii')

    s = "data:image/png;base64," + base64_imagedata

    write_optimal_qrcode(s, filename, post_optimize=True)


def write_vcard(filename: str) -> None:

    im = Image.new('RGB', (160, 160), color='blue')
    draw = ImageDraw.Draw(im)
    draw.circle((79.5, 79.5), 65, fill='yellow', outline=None)
    font = ImageFont.load_default(40)
    draw.text((79.5, 79.5), "Hello!", fill='red', anchor='mm', font=font)
    im.save("temp.png")
    #subprocess.run(["optipng", filename], stderr=subprocess.DEVNULL, check=True)
    with open("temp.png", "rb") as fi:
        imagedata = fi.read()
    os.remove("temp.png")

    base64_imagedata = base64.b64encode(imagedata).decode('ascii')

    vcard = textwrap.dedent("""
    BEGIN:VCARD
    VERSION:4.0
    FN:Sidney Cadot
    N:Cadot;Sidney;;;
    BDAY:19721020
    PHOTO;ENCODING=BASE64;TYPE=PNG:{}
    GENDER:M
    END:VCARD
    """.format(base64_imagedata)).strip()

    write_optimal_qrcode(vcard, filename, post_optimize=True)


def write_svg_qrcode(
            s: str, filename: str, *,
            include_quiet_zone: Optional[bool] = None,
            pattern: Optional[DataMaskingPattern] = None,
            version_preference_list: Optional[list[tuple[int, ErrorCorrectionLevel]]] = None,
            byte_mode_encoding: Optional[str] = None,
            # mode: Optional[str] = None,
            colormap: Optional[str|dict] = None
            # magnification: Optional[int] = None
        ) -> None:

    with XmlWriter() as svg:
        with svg.write_container_tag("svg", {"width": 640, "height": 640, "viewBox": "0 0 640 640", "fill": "none", "xmlns": "http://www.w3.org/2000/svg"}):
            with svg.write_container_tag("g", {"transform": "scale(10)"}):
                for version in range(1, 5):
                    with svg.write_container_tag("g", {"transform": f"translate({0} {version * 1})"}):
                        for level in (ErrorCorrectionLevel.L, ErrorCorrectionLevel.M, ErrorCorrectionLevel.Q, ErrorCorrectionLevel.H):
                            with svg.write_container_tag("g", {"transform": f"translate({0} {(level.value - ErrorCorrectionLevel.L.value) * 1})"}):
                                for pattern in DataMaskingPattern:
                                    with svg.write_container_tag("g", {"transform": f"translate({(pattern.value - DataMaskingPattern.PATTERN0.value) * 1} {0})"}):

                                        qr_canvas = make_optimal_qrcode(
                                            s,
                                            include_quiet_zone=include_quiet_zone,
                                            pattern=pattern,
                                            version_preference_list=[(version, level)],
                                            byte_mode_encoding=byte_mode_encoding
                                        )

                                        if qr_canvas is None:
                                            raise RuntimeError("Unable to store the string in a QR code.")

                                        with svg.write_container_tag("g", {"transform" : f"scale({1/qr_canvas.width})" }):
                                            for i in range(qr_canvas.height):
                                                for j in range(qr_canvas.width):
                                                    value = qr_canvas.get_module_value(i, j)
                                                    color = colormap[value]
                                                    svg.write_leaf_tag("rect", {"x": j, "y": i, "width": 1, "height": 1, "fill": color})

    content = svg.get_content()
    with open(filename, "w") as fo:
        fo.write(content)

def main():

    # This produces a QR code with the snowman character (\u2603) from UTF-8, written in a "bytes" block.
    write_svg_qrcode("☃", "example_utf8_snowman.svg", colormap = colormap_color)



if __name__ == "__main__":
    main()
