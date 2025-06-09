"""Test the QR code decoder."""

import textwrap
from typing import NamedTuple

from qrcode.decoder import decode_pixels


class DecoderTestCase(NamedTuple):
    name: str
    contents: str
    pixels: list[list[bool]]


def make_testcase_oralb() -> DecoderTestCase:
    pixel_string = """
    #######.#.#.##.##.#.#.#######
    #.....#.#...#.####..#.#.....#
    #.###.#.##..##.##..##.#.###.#
    #.###.#...##.##..##.#.#.###.#
    #.###.#...#.#.....#...#.###.#
    #.....#.##..#.##..#.#.#.....#
    #######.#.#eeeeeee#.#.#######
    ........#.#eeeeeee###........
    ..###.#.#.#eeeeeee#.####..###
    #...#..##.#eeeeeee#..##.#..##
    .##.####...eeeeeee.##.....#..
    ...###.####eeeeeee##..#####..
    ##...##....eeeeeee#.##..#.##.
    #......####eeeeeee.##.#.##..#
    .#.#..###..eeeeeee.#...#..#.#
    #.#.#..#.##eeeeeee##.####.###
    ##.##.##.#.eeeeeee#..#.#.....
    ####.....#.eeeeeee##.###.#.#.
    #.#.#.#..##eeeeeee...#....#..
    #.#..#.##..eeeeeee.##.#.##.##
    #.##..#....eeeeeee#.#####..##
    ........#..eeeeeee###...##..#
    #######...#eeeeeee.##.#.####.
    #.....#.......#...###...##.##
    #.###.#.#..#######.######....
    #.###.#.########.##.###.##...
    #.###.#.##.####.###..####.##.
    #.....#..#..#.#..##..#.#.#..#
    #######...##..#..##.#.####...
    """

    lines = [line.strip() for line in textwrap.dedent(pixel_string.strip()).splitlines()]
    pixels = [ [(c == '#') for c in line] for line in lines]

    return DecoderTestCase(
        name = "oralb",
        contents = "https://qrco.de/bb8b9t",
        pixels = pixels
    )


def make_testcase_lego():
    pixel_string = """
    #######.#.#.#.#.#.#######
    #.....#..#####..#.#.....#
    #.###.#.###..##...#.###.#
    #.###.#.###.#####.#.###.#
    #.###.#.#..##..##.#.###.#
    #.....#.#.##.#....#.....#
    #######.#.#.#.#.#########
    ........#.#.#.###........
    ####..#.#.##..####..###.#
    #.#.#.....#.##..#..#...#.
    ###...#..###.....#.##....
    ###....####.##.##.#..##..
    .##...##.#######.##.#.###
    .#.###...#....#######...#
    .###..###.#..#...###..###
    #.##...#.#.#..####...#..#
    .....##...#..#..#########
    ........######..#...#...#
    #######..#..#...#.#.#####
    #.....#..##.#..##...#...#
    #.###.#....#..#.#####...#
    #.###.#.##.##.##.##.#.###
    #.###.#.#####..#.#######.
    #.....#.####.#.#.##.#.#..
    #######.##...##....######
    """

    lines = [line.strip() for line in textwrap.dedent(pixel_string.strip()).splitlines()]
    pixels = [ [(c == '#') for c in line] for line in lines]

    return DecoderTestCase(
        name = "lego",
        contents = "http://debontebouwplaats.nl",
        pixels = pixels
    )


def make_testcase_hello_bye(transpose_flag: bool):
    pixel_string = """
    #######.##..###.#.#######
    #.....#....###.#..#.....#
    #.###.#....###.##.#.###.#
    #.###.#..##.##.##.#.###.#
    #.###.#.#.##...##.#.###.#
    #.....#.##..#..##.#.....#
    #######.#.#.#.#.#.#######
    ........#...##.#.........
    #...######.#.#...####...#
    #..#...#..##..#.###.###..
    ##....#...#.#..#.#...##..
    ....##.##..##....#.#..#..
    #.##..#.#.....#..#.#..###
    ....##.##..####.##...##..
    ....#.#.###.#.##..#.###..
    ...#...####.....#.###.##.
    ..#..###.###.#.######.#..
    ........####....#...###.#
    #######.#.##..#.#.#.#....
    #.....#.#...#..##...###..
    #.###.#.###.#########..##
    #.###.#..#.#.###..##.#..#
    #.###.#..#.####.#.##.#.#.
    #.....#....#..######..##.
    #######.##..#######.##.##
    """

    lines = [line.strip() for line in textwrap.dedent(pixel_string.strip()).splitlines()]
    pixels = [ [(c == '#') for c in line] for line in lines]

    if transpose_flag:
        pixels = [ list(line) for line in zip(*pixels)]

    return DecoderTestCase(
        name = "hello_bye_transposed" if transpose_flag else "hello_bye",
        contents = "Bye" if transpose_flag else "Hello",
        pixels = pixels
    )


def main():

    testcases = [
        make_testcase_oralb(),
        make_testcase_lego(),
        make_testcase_hello_bye(False),
        make_testcase_hello_bye(True)
    ]

    decoded_strings = []
    for testcase in testcases:
        print(f"Processing testcase: {testcase.name!r}")
        print()
        decoded_string = decode_pixels(testcase.pixels)
        decoded_strings.append(decoded_string)
        assert decoded_string == testcase.contents
        print()

    print("Summary of testcases:")
    print()
    for (testcase, decoded_string) in zip(testcases, decoded_strings):
        print(f"  testcase {testcase.name!r} {'.' * (26 - len(testcase.name))} : {decoded_string!r}")


if __name__ == "__main__":
    main()
