#! /usr/bin/env -S python3 -B

"""Write application example QR codes as PNG image files.

Application examples contain strings that have are recognized by programs
that decode QR codes and can trigger specific actions.

Which types of strings are recognized and handled by different programs
is not really standardized.
"""

from qrcode_generator.render.utilities import write_optimal_qrcode


def main():

    include_quiet_zone=False
    colormap = 'color'
    optimize_png = True

    payload = "aAAAAAA0000000" * 3

    write_optimal_qrcode(
        payload=payload,
        png_filename=f"qrcode_ambiguous_{{VERSION}}{{LEVEL}}p{{PATTERN}}.png",
        include_quiet_zone=include_quiet_zone,
        colormap=colormap,
        optimize_png=optimize_png
    )


if __name__ == "__main__":
    main()
