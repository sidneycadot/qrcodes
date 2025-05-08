"""Render a QRCodeCanvas as a PIL image."""

from __future__ import annotations

from typing import Optional

from .qr_code import QRCodeCanvas, ModuleValue

pil_imported_successfully = False
try:
    from PIL import Image, ImageDraw
except ModuleNotFoundError:
    pass
else:
    pil_imported_successfully = True


colormap_default = {
    ModuleValue.QUIET_ZONE_0: '#ffffff',
    ModuleValue.FINDER_PATTERN_0: '#ffffff',
    ModuleValue.FINDER_PATTERN_1: '#000000',
    ModuleValue.SEPARATOR_0: '#ffffff',
    ModuleValue.TIMING_PATTERN_0: '#ffffff',
    ModuleValue.TIMING_PATTERN_1: '#000000',
    ModuleValue.ALIGNMENT_PATTERN_0: '#ffffff',
    ModuleValue.ALIGNMENT_PATTERN_1: '#000000',
    ModuleValue.FORMAT_INFORMATION_0: '#ffffff',
    ModuleValue.FORMAT_INFORMATION_1: '#000000',
    ModuleValue.FORMAT_INFORMATION_FIXED_1: '#000000',
    ModuleValue.FORMAT_INFORMATION_INDETERMINATE: '#ffffff',
    ModuleValue.VERSION_INFORMATION_0: '#ffffff',
    ModuleValue.VERSION_INFORMATION_1: '#000000',
    ModuleValue.VERSION_INFORMATION_INDETERMINATE: '#ffffff',
    ModuleValue.DATA_0: '#ffffff',
    ModuleValue.DATA_1: '#000000',
    ModuleValue.ERRC_0: '#ffffff',
    ModuleValue.ERRC_1: '#000000',
    ModuleValue.PAD_0: '#ffffff',
    ModuleValue.PAD_1: '#000000',
    ModuleValue.DATA_ERRC_INDETERMINATE: '#ffffff',
    ModuleValue.INDETERMINATE: '#ffffff'
}

colormap_color = {
    ModuleValue.QUIET_ZONE_0: '#fff0f0',
    ModuleValue.FINDER_PATTERN_0: '#ffcccc',
    ModuleValue.FINDER_PATTERN_1: '#ff0000',
    ModuleValue.SEPARATOR_0: '#ffcccc',
    ModuleValue.TIMING_PATTERN_0: '#ffcccc',
    ModuleValue.TIMING_PATTERN_1: '#ff0000',
    ModuleValue.ALIGNMENT_PATTERN_0: '#ffcccc',
    ModuleValue.ALIGNMENT_PATTERN_1: '#ff0000',
    ModuleValue.FORMAT_INFORMATION_0: '#ccffcc',
    ModuleValue.FORMAT_INFORMATION_1: '#00bb00',
    ModuleValue.FORMAT_INFORMATION_FIXED_1: '#00bb00',
    ModuleValue.FORMAT_INFORMATION_INDETERMINATE: '#ccffcc',
    ModuleValue.VERSION_INFORMATION_0: '#ddddff',
    ModuleValue.VERSION_INFORMATION_1: '#0000ff',
    ModuleValue.VERSION_INFORMATION_INDETERMINATE: '#ddddff',
    ModuleValue.DATA_0: '#eeffee',
    ModuleValue.DATA_1: '#001100',
    ModuleValue.ERRC_0: '#ffeeff',
    ModuleValue.ERRC_1: '#110033',
    ModuleValue.PAD_0: '#ffffdd',
    ModuleValue.PAD_1: '#000022',
    ModuleValue.DATA_ERRC_INDETERMINATE: '#777777',
    ModuleValue.INDETERMINATE: '#ff0000'
}


def render_qrcode_as_pil_image(
        qr_canvas: QRCodeCanvas, *,
        mode: Optional[str] = None,
        colormap: Optional[str|dict] = None,
        magnification: Optional[int] = None
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

    return im
