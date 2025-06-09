"""Render a QRCodeCanvas as SVG graphics."""

from typing import Optional

from qrcode.qr_code import QRCodeCanvas
from qrcode.render.colormaps import colormap_default, colormap_color
from qrcode.render.xml_writer import XmlWriter


def render_qr_canvas_as_svg_path(
        svg: XmlWriter,
        *,
        canvas: QRCodeCanvas,
        light_color: Optional[str] = None,
        dark_color: Optional[str] = None,
        extra_path_attributes: Optional[dict] = None
    ):

    if light_color is None:
        light_color = "white"

    if dark_color is None:
        dark_color = "black"

    if extra_path_attributes is None:
        extra_path_attributes = {}

    with svg.write_container_tag("g"):
        # Render the light background.
        svg.write_leaf_tag("rect", {"width": canvas.width, "height": canvas.height, "fill": light_color})

        squares = []
        for i in range(canvas.height):
            for j in range(canvas.width):
                value = canvas.get_module_value(i, j)
                if value % 2 != 0:
                    square = f"M {j} {i} h 1 v 1 h -1 Z"
                    squares.append(square)
        path = " ".join(squares)
        svg.write_leaf_tag("path", {"fill": dark_color, "d": path} | extra_path_attributes)


def render_qr_canvas_as_svg_group(
        svg: XmlWriter,
        *,
        canvas: QRCodeCanvas,
        extra_group_attributes: Optional[dict] = None,
        colormap : Optional[str | dict] = None
    ):

    if colormap is None:
        colormap = 'default'

    if colormap == 'default':
        colormap = colormap_default
    elif colormap == 'color':
        colormap = colormap_color

    if extra_group_attributes is None:
        extra_group_attributes = {}

    with svg.write_container_tag("g", arguments=extra_group_attributes):
        for i in range(canvas.height):
            for j in range(canvas.width):
                value = canvas.get_module_value(i, j)
                color = colormap[value]
                svg.write_leaf_tag("rect", {"x": j, "y": i, "width": 1, "height": 1, "fill": color})
