"""A QR code decoder prototype."""

import textwrap

from miscellaneous.decoder_prototype import decode_pixels


def make_testcase_oralb():
    oralb = """
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

    lines = [line.strip() for line in textwrap.dedent(oralb.strip()).splitlines()]
    pixels = [ [(c == '#') for c in line] for line in lines]

    return pixels


def make_testcase_lego():
    lego = """
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

    lines = [line.strip() for line in textwrap.dedent(lego.strip()).splitlines()]
    pixels = [ [(c == '#') for c in line] for line in lines]

    return pixels


def make_testcase_hello_bye(transpose_flag: bool):
    hello_bye = """
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

    lines = [line.strip() for line in textwrap.dedent(hello_bye.strip()).splitlines()]
    pixels = [ [(c == '#') for c in line] for line in lines]

    if transpose_flag:
        pixels = [ list(line) for line in zip(*pixels)]

    return pixels


def main():
    testcases = {
        "oralb": make_testcase_oralb(),
        "lego": make_testcase_lego(),
        "hello_bye": make_testcase_hello_bye(False),
        "hello_bye_transposed": make_testcase_hello_bye(True)
    }

    results = []
    for (name, pixels) in testcases.items():
        print(f"Processing testcase: {name!r}")
        print()
        decoded_string = decode_pixels(pixels)
        results.append((name, decoded_string))
        print()

    print("Summary of testcases:")
    print()
    for (name, decoded_string) in results:
        print(f"  testcase {name!r} {'.' * (26 - len(name))} : {decoded_string!r}")


if __name__ == "__main__":
    main()
