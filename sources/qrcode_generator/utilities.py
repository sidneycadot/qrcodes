"""High-level utility functions to generate QR codes."""

import os
import subprocess
from typing import Optional

from .enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from .data_encoder import DataEncoder
from .lookup_tables import version_specification_table
from .optimal_encoding import find_optimal_string_encoding, EncodingSolution
from .qr_code import make_qr_code, QRCodeCanvas
from .render_pil import render_qrcode_as_pil_image


def make_default_version_preference_list() -> list[tuple[int, ErrorCorrectionLevel]]:
    return [
        (version, level)
        for version in range(1, 41)
        for level in (ErrorCorrectionLevel.H, ErrorCorrectionLevel.Q, ErrorCorrectionLevel.M, ErrorCorrectionLevel.L)
    ]


def make_optimal_qrcode(
            payload: str,
            *,
            include_quiet_zone: Optional[bool] = None,
            pattern: Optional[DataMaskingPattern] = None,
            version_preference_list: Optional[list[tuple[int, ErrorCorrectionLevel]]] = None,
            byte_mode_encoding: Optional[str] = None
        ) -> Optional[QRCodeCanvas]:

    if version_preference_list is None:
        version_preference_list = make_default_version_preference_list()

    variant_cache: dict[EncodingVariant, Optional[EncodingSolution]] = {}
    for (version, level) in version_preference_list:
        variant = EncodingVariant.from_version(version)
        if variant in variant_cache:
            solution = variant_cache[variant]
        else:
            solutions = find_optimal_string_encoding(payload, variant, byte_mode_encoding)
            # print(f"Number of optimal solutions: {len(solutions)}.")
            if len(solutions) == 0:
                solution = None
            else:
                # for solution in solutions:
                #    print("->", solution)
                solution = solutions[0]
                # print(f"Shortest solution: {solution.bitcount()} bits.")
            variant_cache[variant] = solution
        if solution is None:
            continue

        # See if this solution would fit in this (version, level) code.
        version_specification = version_specification_table[(version, level)]

        if version_specification.number_of_data_codewords() * 8 >= solution.bitcount():
            print(f"Selected code: {version}-{level.name}")
            # print(solution)
            break

    else:
        # No acceptable solution found.
        return None

    de = DataEncoder(variant)
    solution.render(de)

    return make_qr_code(de, version, level, include_quiet_zone=include_quiet_zone, pattern=pattern)


def optimize_png(filename: str) -> None:
    if os.name == 'posix':
        # We only know how to optimize on posix systems.
        # On other systems, do nothing.
        subprocess.run(["optipng", filename], stderr=subprocess.DEVNULL, check=False)


def write_optimal_qrcode(
        payload: str,
        filename: str,
        *,
        include_quiet_zone: Optional[bool] = None,
        pattern: Optional[DataMaskingPattern] = None,
        version_preference_list: Optional[list[tuple[int, ErrorCorrectionLevel]]] = None,
        byte_mode_encoding: Optional[str] = None,
        mode: Optional[str] = None,
        colormap: Optional[str|dict] = None,
        magnification: Optional[int] = None,
        post_optimize: Optional[bool] = None
    ) -> None:

    if post_optimize is None:
        post_optimize = False

    qr_canvas = make_optimal_qrcode(
        payload,
        include_quiet_zone=include_quiet_zone,
        pattern=pattern,
        version_preference_list=version_preference_list,
        byte_mode_encoding=byte_mode_encoding
    )
    if qr_canvas is None:
        raise RuntimeError("Unable to store the string in a QR code.")

    im = render_qrcode_as_pil_image(qr_canvas, mode=mode, colormap=colormap, magnification=magnification)
    print(f"Saving {filename} ...")
    im.save(filename)
    if post_optimize:
        optimize_png(filename)
