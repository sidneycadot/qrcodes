"""High-level utility functions to generate QR codes."""

import os
import subprocess
from typing import NamedTuple,Optional

from qrcode_generator.enum_types import ErrorCorrectionLevel, DataMaskingPattern
from qrcode_generator.optimal_encoding import make_optimal_qrcode
from qrcode_generator.qr_code import QRCodeCanvas
from qrcode_generator.render.render_pil import render_qrcode_as_pil_image


class QRCodePngFileDescriptor(NamedTuple):
    png_filename: str
    canvas: QRCodeCanvas


def write_optimal_qrcode(
        *,
        payload: str,
        png_filename: str,
        include_quiet_zone: Optional[bool] = None,
        pattern: Optional[DataMaskingPattern] = None,
        version_preference_list: Optional[list[tuple[int, ErrorCorrectionLevel]]] = None,
        byte_mode_encoding: Optional[str] = None,
        mode: Optional[str] = None,
        colormap: Optional[str|dict] = None,
        magnification: Optional[int] = None,
        optimize_png: Optional[bool] = None
    ) -> QRCodePngFileDescriptor:

    qr_canvas = make_optimal_qrcode(
        payload=payload,
        include_quiet_zone=include_quiet_zone,
        pattern=pattern,
        version_preference_list=version_preference_list,
        byte_mode_encoding=byte_mode_encoding
    )
    if qr_canvas is None:
        raise RuntimeError("Unable to store the string in a QR code.")

    return save_qrcode_as_png_file(
        png_filename=png_filename,
        canvas=qr_canvas,
        mode=mode,
        colormap=colormap,
        magnification=magnification,
        optimize_png=optimize_png
    )


def optimize_png_file_size(png_filename: str):
    if os.name == 'posix':
        # We only know how to optimize on posix systems.
        # On other systems, do nothing.
        subprocess.run(["optipng", png_filename], stderr=subprocess.DEVNULL, check=False)


def save_qrcode_as_png_file(
        *,
        png_filename: str,
        canvas: QRCodeCanvas,
        mode: Optional[str] = None,
        colormap: Optional[str | dict] = None,
        magnification: Optional[int] = None,
        optimize_png: Optional[bool] = None) -> QRCodePngFileDescriptor:

    if optimize_png is None:
        optimize_png = False

    # Apply filename substitutions.
    png_filename = png_filename.replace("{VERSION}" , f"{canvas.version}")
    png_filename = png_filename.replace("{LEVEL}"   , f"{canvas.level.name}")
    png_filename = png_filename.replace("{PATTERN}" , f"{canvas.pattern.name[-1]}")

    # Save the canvas as a PNG file.
    im = render_qrcode_as_pil_image(canvas, mode=mode, colormap=colormap, magnification=magnification)
    print(f"Saving {png_filename} ...")
    im.save(png_filename)

    # If requested, attempt PNG optimization.
    if optimize_png:
        optimize_png_file_size(png_filename)

    return QRCodePngFileDescriptor(png_filename=png_filename, canvas=canvas)
