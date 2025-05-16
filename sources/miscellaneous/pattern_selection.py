#! /usr/bin/env -S python3 -B

"""Make overview of the pattern selections done in the standard."""

import base64
import textwrap
from enum import Enum
from typing import NamedTuple

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskPattern
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render.utilities import save_qrcode_as_png_file
from qrcode_generator.render.xml_writer import XmlWriter


class StandardEdition(Enum):
    E2000 = 2000
    E2006 = 2006
    E2015 = 2015
    E2024 = 2024


class Example(Enum):
    Introduction = 1
    StructuredAppendModeCombined = 2
    StructuredAppendModePart1 = 3
    StructuredAppendModePart2 = 4
    StructuredAppendModePart3 = 5
    StructuredAppendModePart4 = 6
    Annex = 7


class ExampleCodeSpec(NamedTuple):
    edition: StandardEdition
    location: str
    pattern: DataMaskPattern


StructuredAppendExampleParity = 1

class EditionInfo(NamedTuple):
    pattern: DataMaskPattern
    location: str

class ExampleSpec(NamedTuple):
    shortname: str
    description: str
    editions: dict[StandardEdition, EditionInfo]
    version: int
    level: ErrorCorrectionLevel
    data_encoder: DataEncoder

example_specs = {
    Example.Introduction: ExampleSpec(
        shortname="introduction_example",
        description="String \"QR Code Symbol\" encoded using byte mode in a 1-M QR code symbol",
        editions={
            StandardEdition.E2000: EditionInfo(DataMaskPattern.PATTERN5, "Section 7.1, Figure 1, Page 5"),
            StandardEdition.E2006: EditionInfo(DataMaskPattern.PATTERN5, "Section 5.2, Figure 1(a), Page 7"),
            StandardEdition.E2015: EditionInfo(DataMaskPattern.PATTERN5, "Section 6.2, Figure 1(a), Page 7"),
            StandardEdition.E2024: EditionInfo(DataMaskPattern.PATTERN6, "Section 5.2, Figure 1(a), Page 6")
        },
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_byte_mode_block(b"QR Code Symbol")
    ),
    Example.StructuredAppendModeCombined: ExampleSpec(
        shortname="structured_append_mode_example_combined",
        description="Structured Append Mode example: 62 alphanumeric characters, combined in a 4-M QR code symbol",
        editions={
            StandardEdition.E2000: EditionInfo(DataMaskPattern.PATTERN4, "Section 9.1, Figure 22 (top), page 56"),
            StandardEdition.E2006: EditionInfo(DataMaskPattern.PATTERN4, "Section 7.1, Figure 29 (top), page 59"),
            StandardEdition.E2015: EditionInfo(DataMaskPattern.PATTERN4, "Section 8.1, Figure 29 (top), page 60"),
            StandardEdition.E2024: EditionInfo(DataMaskPattern.PATTERN4, "Section 8.1, Figure 29 (top), page 56")
        },
        version=4,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_alphanumeric_mode_block("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ),
    Example.StructuredAppendModePart1: ExampleSpec(
        shortname="structured_append_mode_example_1_of_4",
        description="Structured Append Mode example: 14 alphanumeric characters characters, first of four parts, in a 1-M QR code symbol",
        editions={
            StandardEdition.E2000: EditionInfo(DataMaskPattern.PATTERN0, "Section 9.1, Figure 22 (bottom row, first of four), page 56"),
            StandardEdition.E2006: EditionInfo(DataMaskPattern.PATTERN0, "Section 7.1, Figure 29 (bottom row, first of four), page 59"),
            StandardEdition.E2015: EditionInfo(DataMaskPattern.PATTERN0, "Section 8.1, Figure 29 (bottom row, first of four), page 60"),
            StandardEdition.E2024: EditionInfo(DataMaskPattern.PATTERN0, "Section 8.1, Figure 29 (bottom row, first of four), page 56")
        },
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(0, 4, StructuredAppendExampleParity).append_alphanumeric_mode_block("ABCDEFGHIJKLMN")
    ),
    Example.StructuredAppendModePart2: ExampleSpec(
        shortname="structured_append_mode_example_2_of_4",
        description="Structured Append Mode example, 16 alphanumeric characters characters, second of four parts, in a 1-M QR code symbol",
        editions={
            StandardEdition.E2000: EditionInfo(DataMaskPattern.PATTERN7, "Section 9.1, Figure 22 (bottom row, second of four), page 56"),
            StandardEdition.E2006: EditionInfo(DataMaskPattern.PATTERN7, "Section 7.1, Figure 29 (bottom row, second of four), page 59"),
            StandardEdition.E2015: EditionInfo(DataMaskPattern.PATTERN7, "Section 8.1, Figure 29 (bottom row, second of four), page 60"),
            StandardEdition.E2024: EditionInfo(DataMaskPattern.PATTERN7, "Section 8.1, Figure 29 (bottom row, second of four), page 56")
        },
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(1, 4, StructuredAppendExampleParity).append_alphanumeric_mode_block("OPQRSTUVWXYZ0123")
    ),
    Example.StructuredAppendModePart3: ExampleSpec(
        shortname="structured_append_mode_example_3_of_4",
        description="Structured Append Mode example, 16 alphanumeric characters characters, third of four parts, in a 1-M QR code symbol",
        editions={
            StandardEdition.E2000: EditionInfo(DataMaskPattern.PATTERN7, "Section 9.1, Figure 22 (bottom row, third of four), page 56"),
            StandardEdition.E2006: EditionInfo(DataMaskPattern.PATTERN7, "Section 7.1, Figure 29 (bottom row, third of four), page 59"),
            StandardEdition.E2015: EditionInfo(DataMaskPattern.PATTERN7, "Section 8.1, Figure 29 (bottom row, third of four), page 60"),
            StandardEdition.E2024: EditionInfo(DataMaskPattern.PATTERN7, "Section 8.1, Figure 29 (bottom row, third of four), page 56")
        },
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(2, 4, StructuredAppendExampleParity).append_alphanumeric_mode_block("456789ABCDEFGHIJ")
    ),
    Example.StructuredAppendModePart4: ExampleSpec(
        shortname="structured_append_mode_example_4_of_4",
        description="Structured Append Mode example, 16 alphanumeric characters characters, fourth of four parts, in a 1-M QR code symbol",
        editions={
            StandardEdition.E2000: EditionInfo(DataMaskPattern.PATTERN3, "Section 9.1, Figure 22 (bottom row, last of four), page 56"),
            StandardEdition.E2006: EditionInfo(DataMaskPattern.PATTERN3, "Section 7.1, Figure 29 (bottom row, last of four), page 59"),
            StandardEdition.E2015: EditionInfo(DataMaskPattern.PATTERN3, "Section 8.1, Figure 29 (bottom row, last of four), page 60"),
            StandardEdition.E2024: EditionInfo(DataMaskPattern.PATTERN3, "Section 8.1, Figure 29 (bottom row, last of four), page 56")
        },
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(3, 4, StructuredAppendExampleParity).append_alphanumeric_mode_block("KLMNOPQRSTUVWXYZ")
    ),
    Example.Annex: ExampleSpec(
        shortname="annex_example",
        description="Annex example, \"01234567\" encoded as numeric characters, 1-M symbol",
        editions={
            StandardEdition.E2000: EditionInfo(DataMaskPattern.PATTERN3, "Annex G, Figure G.2, page 85"),
            StandardEdition.E2006: EditionInfo(DataMaskPattern.PATTERN2, "Annex I, Figure I.2, page 96"),
            StandardEdition.E2015: EditionInfo(DataMaskPattern.PATTERN2, "Annex I, Figure I.2, page 96"),
            StandardEdition.E2024: EditionInfo(DataMaskPattern.PATTERN2, "Annex I, Figure I.2, page 91")
        },
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_numeric_mode_block("01234567")
    )
}


def main():

    css_style_definitions ="""    
        table,th,td { border: 1px solid black; }
        p.author { font-style: italic; font-size: 1.5em; }
        img.qr-code { width: 25mm; margin: 5mm; image-rendering: pixelated; }
        td { text-align: center; }
        .good { font-weight: bold; color: green; }
        .bad { font-weight: bold; color: red; }
    """

    with XmlWriter("pattern_selection.html") as html:

        with html.write_container_tag("html"):
            with html.write_container_tag("head"):
                html.write_leaf_tag("title", content="Data Mask Pattern Selection of example QR codes in the ISO/IEC 18004 standard")
                with html.write_container_tag("style"):
                    for line in textwrap.dedent(css_style_definitions).strip().splitlines():
                        html.write_indented_line(line)

            with html.write_container_tag("body"):
                html.write_leaf_tag("h1", content="Data Mask Pattern Selection of QR codes in the ISO/IEC 18004 standard")
                html.write_leaf_tag("p", { "class": "author" }, content="Sidney Cadot <tt>&lt;sidney.cadot@gmail.com&gt;</tt>")
                html.write_leaf_tag("hr")
                html.write_leaf_tag("h2", content="Introduction")
                html.write_leaf_tag(
                    "p",
                    content="All four editions of the ISO/IEC 18004 standard contain seven QR code symbols: one example early in the document; "
                            "five examples that demonstrate <emph>structured append mode</emph>, and one as an example in an Annex.")
                html.write_leaf_tag(
                    "p",
                    content="These seven examples should use the Data Mask Pattern selected in accordance with the scoring algorithm described in the standard "
                            "(specifically, the one having the lowest score), but unfortunately this isn't always the case.")
                html.write_leaf_tag(
                    "p",
                    content="Below, we show the score calculation for each of the seven QR code symbol "
                            "examples, and all of the eight possible Data Mask Pattern choices, as a table. For each example, the table is followed by "
                            "a statement of the optimal Data Mask Pattern choice, and a list of the four standard editions, that says which "
                            "Data Mask Pattern was actually used in that particular edition.")
                html.write_leaf_tag(
                    "p",
                    content="This is shown in <span class=\"good\">green</span> in case the choice complies with the optimal choice, "
                            "and <span class=\"bad\">red</span> if it doesn't. The latter indicates an inconsistency in the standard.")
                for (example, example_spec) in example_specs.items():
                    html.write_leaf_tag("hr")
                    html.write_leaf_tag("h2", content=f"{example_spec.description}.")
                    with html.write_container_tag("table"):
                        with html.write_container_tag("tr"):
                            html.write_leaf_tag("th", content="QR code symbol")
                            html.write_leaf_tag("th", content="Data Mask Pattern")
                            html.write_leaf_tag("th", content="Score term 1")
                            html.write_leaf_tag("th", content="Score term 2")
                            html.write_leaf_tag("th", content="Score term 3")
                            html.write_leaf_tag("th", content="Score term 4")
                            html.write_leaf_tag("th", content="Total score (lower is better)")

                        best_score = None
                        best_pattern = None

                        for pattern in DataMaskPattern:

                            with html.write_container_tag("tr"):

                                canvas = make_qr_code(
                                    de=example_spec.data_encoder,
                                    version=example_spec.version,
                                    level=example_spec.level,
                                    pattern=pattern,
                                    include_quiet_zone=False,
                                )

                                assert best_score != canvas.score
                                if best_score is None or canvas.score < best_score:
                                    best_score = canvas.score
                                    best_pattern = canvas.pattern

                                descriptor = save_qrcode_as_png_file(
                                    png_filename=f"{example_spec.shortname}_{{VERSION}}{{LEVEL}}p{{PATTERN}}.png",
                                    canvas=canvas,
                                    colormap='default',
                                    optimize_png=True
                                )

                                with open(descriptor.png_filename, "rb") as fi:
                                    imagedata = fi.read()

                                    with html.write_container_tag("td"):
                                        source = f"data:image/png;base64,{base64.b64encode(imagedata).decode('ascii')}"
                                        html.write_leaf_tag("img class=\"qr-code\"", {"src": source})
                                    html.write_leaf_tag("td", content=f"Pattern&nbsp;{canvas.pattern.name[-1]}")
                                    html.write_leaf_tag("td", content=f"{canvas.split_score[0]}")
                                    html.write_leaf_tag("td", content=f"{canvas.split_score[1]}")
                                    html.write_leaf_tag("td", content=f"{canvas.split_score[2]}")
                                    html.write_leaf_tag("td", content=f"{canvas.split_score[3]}")
                                    html.write_leaf_tag("td", content=f"{canvas.score}")

                    html.write_leaf_tag("p", content=f"The best score is <b>{best_score}</b>, for <b>Data Mask Pattern {best_pattern.name[-1]}</b>.")

                    with html.write_container_tag("ul"):
                        for edition, edition_info in example_spec.editions.items():
                            ok = (edition_info.pattern == best_pattern)
                            class_value = "good" if ok else "bad"
                            html.write_leaf_tag("li", {"class": class_value}, content=f"The {edition.value} edition of the ISO/IEC 18004 standard shows this QR code symbol using Data Mask Pattern {edition_info.pattern.name[-1]}: {edition_info.location}.")


if __name__ == "__main__":
    main()
