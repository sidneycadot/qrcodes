#! /usr/bin/env -S python3 -B

"""Write QR code that contains an image.

Note: this requires cooperation from an externally configured HTTP server.
"""

import os
import base64

from PIL import Image, ImageDraw, ImageFont

from qrcode_generator.utilities import write_optimal_qrcode, optimize_png_file_size


def write_image_via_reflector(png_filename: str) -> None:

    # Make image.

    im = Image.new('RGB', (160, 160), color='blue')
    draw = ImageDraw.Draw(im)
    draw.circle((79.5, 79.5), 65, fill='yellow', outline=None)
    font = ImageFont.load_default(20)
    draw.text((79.5, 79.5), "Hello, World!", fill='red', anchor='mm', font=font)

    # Save image to temporary file.

    temp_filename = "temp_" + png_filename
    im.save(temp_filename)
    optimize_png_file_size(temp_filename)

    # Read image file data.

    with open(temp_filename, "rb") as fi:
        imagedata = fi.read()

    # Remove temporary image file.

    os.remove(temp_filename)

    # Represent image data as URL-safe base64 ASCII text.

    base64_imagedata = base64.urlsafe_b64encode(imagedata).decode('ascii')

    # Create the reflector URL.

    url = f"http://r.jigsaw.nl?c=image/png&p={base64_imagedata}"
    print("URL:", url)

    # Write the example.

    write_optimal_qrcode(payload=url, png_filename=png_filename, optimize_png=True)


def main():

    # This produces a QR code with an image, using a reflector site.
    write_image_via_reflector("example_image_via_reflector_{VERSION}{LEVEL}p{PATTERN}.png")


if __name__ == "__main__":
    main()
