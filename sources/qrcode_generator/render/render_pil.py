"""Render a QRCodeCanvas as a PIL image."""

from __future__ import annotations

from typing import Optional

from qrcode_generator.render.colormaps import colormap_default, colormap_color
from qrcode_generator.qr_code import QRCodeCanvas

pil_imported_successfully = False
try:
    from PIL import Image, ImageDraw
except ModuleNotFoundError:
    pass
else:
    pil_imported_successfully = True


def render_qrcode_as_pil_image(
        qr_canvas: QRCodeCanvas, *,
        mode: Optional[str] = None,
        colormap: Optional[str|dict] = None,
        magnification: Optional[int] = None,
        transform: Optional[str] = None
    ) -> Image.Image:

    """Render QRCodeCanvas as a PIL image."""

    if not pil_imported_successfully:
        raise RuntimeError("The PIL package not available.")

    if mode is None:
        mode = "RGB"

    if colormap is None:
        colormap = 'default'

    if colormap == 'default':
        colormap = colormap_default
    elif colormap == 'color':
        colormap = colormap_color

    if magnification is None:
        magnification = 1

    im = Image.new(mode, (qr_canvas.width * magnification, qr_canvas.height * magnification))
    draw = ImageDraw.Draw(im)

    for i in range(qr_canvas.height):
        for j in range(qr_canvas.width):
            value = qr_canvas.get_module_value(i, j)
            color = colormap[value]
            rect = (j * magnification, i * magnification, (j + 1) * magnification - 1, (i + 1) * magnification - 1)
            draw.rectangle(rect, color)

    if transform is not None:
        for tr in transform.split(","):
            # Transpose.FLIP_LEFT_RIGHT
            # Transpose.FLIP_TOP_BOTTOM
            # Transpose.ROTATE_90
            # Transpose.ROTATE_180
            # Transpose.ROTATE_270
            # Transpose.TRANSPOSE
            # Transpose.TRANSVERSE
            if tr in ("cw", "clockwise", "rotate-clockwise"):
                im = im.transpose(Image.Transpose.ROTATE_270)
            elif tr in ("ccw", "counterclockwise", "rotate-counterclockwise"):
                im = im.transpose(Image.Transpose.ROTATE_90)
            elif tr == "rotate-180":
                im = im.transpose(Image.Transpose.ROTATE_180)
            elif tr in ("mirror-horizontal", "mirror"):
                im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif tr == "mirror-vertical":
                im = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            elif tr == "transpose":
                im = im.transpose(Image.Transpose.TRANSPOSE)
            else:
                raise ValueError(f"Bad transform: {tr!r}")
    return im
