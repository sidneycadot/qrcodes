#! /usr/bin/env -S python3 -B

"""Write QR code poster with encodings of pi as an SVG image."""

from qrcode_generator.render_svg import render_qr_canvas_as_svg_path
from qrcode_generator.xml_writer import XmlWriter
from qrcode_generator.enum_types import DataMaskingPattern, ErrorCorrectionLevel
from qrcode_generator.lookup_tables import version_specification_table
from qrcode_generator.utilities import make_optimal_qrcode

from examples.make_qrcode_pi_as_svg import number_of_pi_characters_that_can_be_represented, pi_10k


def write_svg_qrcode_poster(filename: str) -> None:

    with XmlWriter(filename) as svg:

        with svg.write_container_tag("svg", {"viewBox": "0 0 5400 5400", "xmlns": "http://www.w3.org/2000/svg"}):

            svg.write_leaf_tag("rect", {"width": "100%", "height": "100%", "fill": "white"})

            svg.write_leaf_tag("text", {"x": 2700.0, "y": 350.0, "fill": "red", "font-size": "300px", "dominant-baseline": "middle", "text-anchor": "middle"}, content="Decimals of π encoded in QR codes")

            with svg.write_container_tag("g", {"transform": "translate(400 500) scale(100)"}):

                for version in range(1, 41):

                    # if version not in (1, 40): continue

                    with svg.write_container_tag("g", {"transform": f"translate(0 {(version - 1) * 1.2:.9f})"}):

                        for level in reversed(ErrorCorrectionLevel):

                            number_of_pi_characters = number_of_pi_characters_that_can_be_represented(version, level)

                            with svg.write_container_tag("g", {"transform": f"translate({(ErrorCorrectionLevel.H.value - level.value) * 13.0:.9f} 0 )"}):

                                version_specification = version_specification_table[(version, level)]

                                label = f"{version}-{level.name}, " \
                                        f"{version_specification.number_of_data_codewords() * 8} databits, " \
                                        f"π to {number_of_pi_characters - 2} digits:"

                                svg.write_leaf_tag("text", {
                                    "x": "-0.3", "y": "0.55",
                                    "fill": "blue",
                                    "font-size": "0.18px",
                                    "dominant-baseline": "middle",
                                    "text-anchor": "end"
                                }, content=label)

                                with svg.write_container_tag("g"):

                                    for pattern in DataMaskingPattern:

                                        pi_characters = pi_10k[:number_of_pi_characters]

                                        qr_canvas = make_optimal_qrcode(pi_characters, pattern=pattern, version_preference_list=[(version, level)], include_quiet_zone=False)

                                        render_qr_canvas_as_svg_path(svg, qr_canvas, {
                                            "fill": "black",
                                            "transform": f"translate({(pattern.value - DataMaskingPattern.PATTERN0.value) * 1.2:.9f} 0) scale({1.0 / qr_canvas.width:.9f})"
                                        })


def main():
    write_svg_qrcode_poster("qrcode_pi_poster.svg")


if __name__ == "__main__":
    main()
