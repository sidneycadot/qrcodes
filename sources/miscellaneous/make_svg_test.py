#! /usr/bin/env -S python3 -B

"""Write PNG, SVG, PDF that shows a 2x2 pixel image.

As it turns out, the PDF generated from the SVG file (using rsvg-convert) uses pixel interpolation,
where we'd like to see a perfectly pixelated image.
"""

import base64

from PIL import Image
import subprocess

from qrcode.render.xml_writer import XmlWriter
from qrcode.render.utilities import optimize_png_file_size


def main():

    filename_png = "svg_test.png"
    filename_svg ="svg_test.svg"
    filename_pdf = "svg_test.pdf"

    im = Image.new('RGB', (2, 2))
    im.putpixel((0, 0), (255, 0, 0))
    im.putpixel((0, 1), (0, 255, 0))
    im.putpixel((1, 0), (0, 0, 255))
    im.putpixel((1, 1), (255, 255, 0))
    im.save(filename_png)
    optimize_png_file_size(filename_png)

    with open(filename_png, "rb") as fi:
        png_data = fi.read()

    png_data_encoded = base64.b64encode(png_data).decode('ascii')
    print(png_data_encoded)

    with XmlWriter(filename_svg) as svg:
        with svg.write_container_tag(
            "svg", {
                    "viewBox": "0 0 2 2",
                    "xmlns": "http://www.w3.org/2000/svg"
                }
            ):
            svg.write_leaf_tag(
                "image",
                {
                    "style" : "image-rendering: pixelated;",
                    "href"  : f"data:image/png;base64,{png_data_encoded}"
                }
            )

    # Try to write a PDF file. If rsvg-convert is not available, this is a no-op.
    try:
        subprocess.run(["rsvg-convert", "--format", "pdf", "--output", filename_pdf, filename_svg], check=False)
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
