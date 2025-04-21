#! /usr/bin/env -S python3 -B

"""Write QR code that contains an image."""
import os
import subprocess
import base64

from PIL import Image, ImageDraw, ImageFont


from qrcode_generator.utilities import write_optimal_qrcode


def write_image_via_reflector(filename: str) -> None:

    im = Image.new('RGB', (160, 160), color='blue')
    draw = ImageDraw.Draw(im)
    draw.circle((79.5, 79.5), 65, fill='yellow', outline=None)
    font = ImageFont.load_default(20)
    draw.text((79.5, 79.5), "Hello, World!", fill='red', anchor='mm', font=font)

    temp_filename = "temp.png"
    im.save(temp_filename)
    subprocess.run(["optipng", temp_filename], stderr=subprocess.DEVNULL, check=True)
    with open(temp_filename, "rb") as fi:
        imagedata = fi.read()
    os.remove(temp_filename)

    base64_imagedata = base64.urlsafe_b64encode(imagedata).decode('ascii')

    # Create the reflector URL.
    url = "http://r.jigsaw.nl?c=image/png&p=" + base64_imagedata

    print("URL:", url)

    write_optimal_qrcode(url, filename, post_optimize=True)


def main():

    # This produces a QR code with an image, using a reflector site.
    write_image_via_reflector("example_image_via_reflector.png")


if __name__ == "__main__":
    main()
