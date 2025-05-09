"""Render a QRCodeCanvas as SVG graphics."""

from typing import Optional

from qrcode_generator.qr_code import QRCodeCanvas
from qrcode_generator.render.xml_writer import XmlWriter


def render_qr_canvas_as_svg_path(svg: XmlWriter, qr_canvas: QRCodeCanvas, extra_path_attributes: Optional[dict]):
    if extra_path_attributes is None:
        extra_path_attributes = {}
    squares = []
    for i in range(qr_canvas.height):
        for j in range(qr_canvas.width):
            value = qr_canvas.get_module_value(i, j)
            if value % 2 != 0:
                square = f"M {j} {i} h 1 v 1 h -1 Z"
                squares.append(square)
    path = " ".join(squares)
    svg.write_leaf_tag("path", {"d": path} | extra_path_attributes)
