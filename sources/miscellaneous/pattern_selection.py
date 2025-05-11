#! /usr/bin/env -S python3 -B

"""Write example QR codes."""

from colorama import Fore, Style

from qrcode_generator.data_encoder import DataEncoder
from qrcode_generator.enum_types import ErrorCorrectionLevel, EncodingVariant, DataMaskingPattern
from qrcode_generator.qr_code import QRCodeDrawer


def run_testcase(testcase_name: str, de: DataEncoder, version: int, level: ErrorCorrectionLevel, reference_pattern: DataMaskingPattern):
    filename = f"{testcase_name}.png"
    qr = QRCodeDrawer(version, include_quiet_zone = False)
    score1_map = {}
    score2_map = {}
    for pattern in DataMaskingPattern:
        qr.place_data_and_error_correction_bits(de, level)
        qr.apply_data_masking_pattern(pattern)
        qr.place_version_information_placeholders()
        qr.place_format_information_placeholders()
        score1 = qr.score()
        qr.place_version_information_patterns()
        qr.place_format_information_patterns(level, pattern)
        score2 = qr.score()
        score1_map[pattern] = score1
        score2_map[pattern] = score2
        #if pattern == reference_pattern:
        #    save_qrcode_as_png_file(filename, qr.canvas)

    score1_best = min(score1_map.values())
    score2_best = min(score2_map.values())

    scores = []
    for pattern in DataMaskingPattern:
        pattern_str = f"P{pattern.name[-1]}"
        score1 = score1_map[pattern]
        score2 = score2_map[pattern]
        score1_str = f"{score1}"
        score2_str = f"{score2}"
        spaces = 10 - len(score1_str) - len(score2_str)
        if pattern == reference_pattern:
            pattern_str = Fore.BLUE + pattern_str + Style.RESET_ALL
        else:
            pattern_str = Fore.YELLOW + pattern_str + Style.RESET_ALL
        if score1 == score1_best:
            score1_str = Fore.GREEN + score1_str + Style.RESET_ALL
        else:
            score1_str = Fore.RED + score1_str + Style.RESET_ALL
        if score2 == score2_best:
            score2_str = Fore.GREEN + score2_str + Style.RESET_ALL
        else:
            score2_str = Fore.RED + score2_str + Style.RESET_ALL
        score_str = f"{score1_str},{score2_str}" + " " * spaces
        scores.append(f"{pattern_str} {score_str}")
    scores_str = "".join(scores).strip()
    print(f"{testcase_name:20s}    {scores_str}")


def main():

    # Note: the 2006 and 2015 editions of the standard uses PATTERN5 here, while the 2024 version
    # of the standard uses PATTERN6.
    de = DataEncoder(EncodingVariant.SMALL)
    de.append_byte_mode_block(b"QR Code Symbol")
    run_testcase("fig_1_page_7", de, 1, ErrorCorrectionLevel.M, DataMaskingPattern.PATTERN6)

    de = DataEncoder(EncodingVariant.SMALL)
    de.append_alphanumeric_mode_block("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    run_testcase("fig_29-1_page_60", de, 4, ErrorCorrectionLevel.M, DataMaskingPattern.PATTERN4)

    de = DataEncoder(EncodingVariant.SMALL)
    de.append_structured_append_marker(0, 4, 1)
    de.append_alphanumeric_mode_block("ABCDEFGHIJKLMN")
    run_testcase("fig_29-2_page_60", de, 1, ErrorCorrectionLevel.M, DataMaskingPattern.PATTERN0)

    de = DataEncoder(EncodingVariant.SMALL)
    de.append_structured_append_marker(1, 4, 1)
    de.append_alphanumeric_mode_block("OPQRSTUVWXYZ0123")
    run_testcase("fig_29-3_page_60", de, 1, ErrorCorrectionLevel.M, DataMaskingPattern.PATTERN7)

    de = DataEncoder(EncodingVariant.SMALL)
    de.append_structured_append_marker(2, 4, 1)
    de.append_alphanumeric_mode_block("456789ABCDEFGHIJ")
    run_testcase("fig_29-4_page_60", de, 1, ErrorCorrectionLevel.M, DataMaskingPattern.PATTERN7)

    de = DataEncoder(EncodingVariant.SMALL)
    de.append_structured_append_marker(3, 4, 1)
    de.append_alphanumeric_mode_block("KLMNOPQRSTUVWXYZ")
    run_testcase("fig_29-5_page_60", de, 1, ErrorCorrectionLevel.M, DataMaskingPattern.PATTERN3)

    # Note: the 2000 version of the standard uses PATTERN3 here, while the 2015 version
    # of the standard uses PATTERN2.
    de = DataEncoder(EncodingVariant.SMALL)
    de.append_numeric_mode_block("01234567")
    run_testcase("fig_i2_page_96", de, 1, ErrorCorrectionLevel.M, DataMaskingPattern.PATTERN2)


if __name__ == "__main__":
    main()
