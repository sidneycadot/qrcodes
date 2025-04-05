#! /usr/bin/env -S python3 -B

"""Write QR code that contains an image."""
import os
import subprocess
import base64
import textwrap

from PIL import Image, ImageDraw, ImageFont


from sources.qrcode_generator.utilities import write_optimal_qrcode


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


def main():

    # This produces a QR code with an empty string.
    #write_image("example_image.png")
    write_vcard("example_vcard.png")


if __name__ == "__main__":
    main()
