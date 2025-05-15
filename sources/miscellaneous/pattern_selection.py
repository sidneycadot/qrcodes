#! /usr/bin/env -S python3 -B

"""Make overview of the pattern selections done in the standard."""

from enum import Enum
from typing import NamedTuple

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from qrcode_generator.qr_code import make_qr_code
from qrcode_generator.render.utilities import save_qrcode_as_png_file


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
    pattern: DataMaskingPattern


StructuredAppendExampleParity = 1

class ExampleSpec(NamedTuple):
    shortname: str
    description: str
    version: int
    level: ErrorCorrectionLevel
    data_encoder: DataEncoder

example_specs = {
    Example.Introduction: ExampleSpec(
        shortname="introduction_example",
        description="Introduction example",
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_byte_mode_block(b"QR Code Symbol")
    ),
    Example.StructuredAppendModeCombined: ExampleSpec(
        shortname="structured_append_mode_example_combined",
        description="Structured Append Mode example, combined",
        version=4,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_alphanumeric_mode_block("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ),
    Example.StructuredAppendModePart1: ExampleSpec(
        shortname="structured_append_mode_example_1_of_4",
        description="Structured Append Mode example, 1 of 4",
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(0, 4, StructuredAppendExampleParity).append_alphanumeric_mode_block("ABCDEFGHIJKLMN")
    ),
    Example.StructuredAppendModePart2: ExampleSpec(
        shortname="structured_append_mode_example_2_of_4",
        description="Structured Append Mode example, 2 of 4",
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(1, 4, StructuredAppendExampleParity).append_alphanumeric_mode_block("OPQRSTUVWXYZ0123")
    ),
    Example.StructuredAppendModePart3: ExampleSpec(
        shortname="structured_append_mode_example_3_of_4",
        description="Structured Append Mode example, 3 of 4",
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(2, 4, StructuredAppendExampleParity).append_alphanumeric_mode_block("456789ABCDEFGHIJ")
    ),
    Example.StructuredAppendModePart4: ExampleSpec(
        shortname="structured_append_mode_example_4_of_4",
        description="Structured Append Mode example, 4 of 4",
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_structured_append_marker(3, 4, StructuredAppendExampleParity).append_alphanumeric_mode_block("KLMNOPQRSTUVWXYZ")
    ),
    Example.Annex: ExampleSpec(
        shortname="annex_example",
        description="Annex example",
        version=1,
        level=ErrorCorrectionLevel.M,
        data_encoder=DataEncoder(EncodingVariant.SMALL).append_numeric_mode_block("01234567")
    )
}




def main():

    with open("latex_tables.tex", "w") as fo:

        # |  Data Mask Pattern  |  Score term 1  |  Score term 2  |  Score term 3  |  Score term 4  |  Total score  |
        # |---------------------+----------------+----------------+----------------+---------------+----------------|
        # | Pattern 0           |                |        a                b              c              d          |
        #
        # Data Masking Scores for the 'xxxx example', lower is better. Pattern YYY has the lowest score, so should be selected.

        for (example, example_spec) in example_specs.items():

            print("\\begin{table}", file=fo)
            print("\\begin{tabular}[|c|c|c|c|c|c|c|]", file=fo)
            print("\\hline", file=fo)
            print("Symbol & Data Mask Pattern & Score term 1 & Score term 2 & Score term 3 & Score term 4 & Total score \\\\", file=fo)
            print("\\hline", file=fo)
            canvas = make_qr_code(
                de=example_spec.data_encoder,
                version=example_spec.version,
                level=example_spec.level,
                include_quiet_zone=False,
                pattern=None
            )

            best_score = min(sum(value) for value in canvas.split_score_dict.values())
            best_patterns = [p for p in DataMaskingPattern if sum(canvas.split_score_dict[p]) == best_score]
            assert len(best_patterns) == 1
            best_pattern = best_patterns[0]

            for pattern in DataMaskingPattern:

                descriptor = save_qrcode_as_png_file(
                    png_filename=f"{example_spec.shortname}_{{VERSION}}{{LEVEL}}p{{PATTERN}}.png",
                    canvas=canvas,
                    colormap='default',
                    optimize_png=True
                )

                print(f"\\includegraphics{descriptor.png_filename} & Pattern~{pattern.name[-1]} & {canvas.split_score_dict[pattern][0]:6d} & {canvas.split_score_dict[pattern][1]:6d} & {canvas.split_score_dict[pattern][2]:6d} & {canvas.split_score_dict[pattern][3]:6d} & {sum(canvas.split_score_dict[pattern]):6d} \\\\", file=fo)

            print("\\hline", file=fo)
            print("\\end{tabular}", file=fo)
            print(f"\\caption{{Score of {example_spec.description}. The best pattern is Pattern~{best_pattern.name[-1]} with a score of {best_score}.", file=fo)
            print(f"\\label{{tab:score-{example_spec.shortname}}}", file=fo)
            print("\\end{table}", file=fo)
            print(file=fo)


if __name__ == "__main__":
    main()
