"""Render QR Canvas as PIL image."""

from PIL import Image, ImageDraw

from qr_code import QRCodeCanvas


def render_qrcode_as_pil_image(qr_canvas: QRCodeCanvas, mode, colormap, magnification: int = 1) -> Image.Image:
    im = Image.new(mode, (qr_canvas.width * magnification, qr_canvas.height * magnification))
    draw = ImageDraw.Draw(im)

    for i in range(qr_canvas.height):
        for j in range(qr_canvas.width):
            value = qr_canvas.get_module_value(i, j)
            color = colormap[value]
            draw.rectangle((j * magnification, i * magnification, (j + 1) * magnification - 1, (i + 1) * magnification - 1), color)

    return im
