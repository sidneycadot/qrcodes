"""Find the optimal data encoding(s) of a given string.

String data can be expressed in any of four modes inside a QR code. Each mode can express
a different subset of characters, and uses a different number of bits per character. For example,
numeric mode can only express the characters 0..9, but very efficiently (at 3.33 bits per character),
whereas byte mode can express the entire set of Unicode characters, but less efficiently (using the
variable-length UTF-8 encoding, with at least 8 bits per character).

Inside the QR code data encoding, it is possible to switch modes, at the cost of some bits to describe
the new mode and the number of characters to be encoded in that mode. This can be advantageous, for
example, if a string consists of mostly generic ASCII characters (that can be encoded in byte mode,
at 8 bits per character) but also contains a long stretch of decimal digits. In that case, switching
to numeric mode just prior to the decimal digits may be worthwhile.

The code presented here aims to find the optimal encoding for a given string, if we allow arbitrary
mode switches.

An encoding solution is optimal if:

  (1) its bit-count is minimal;
  (2) among the encoding solutions with minimal bit-count, the number of mode segments is minimal.

Note: pathological input strings exist that lead to many different optimal encoding solutions that are all
      optimal in the sense as defined above.

Solutions are represented by instances of the EncodingSolution class. They can be rendered into a DataEncoder.
"""

from __future__ import annotations

from typing import Optional

from .data_encoder import numeric_character_map, alphanumeric_character_map, DataEncoder
from .enum_types import CharacterEncodingType, EncodingVariant, ErrorCorrectionLevel, DataMaskPattern
from .kanji_encode import kanji_character_value
from .lookup_tables import count_bits_table, version_specification_table
from .qr_code import QRCodeCanvas, make_qr_code


class EncodingSegment:
    """Abstract base class for data encoding segments in QR codes."""

    def append_character(self, c: str) -> None:
        raise NotImplementedError()

    def append_bytes(self, b: bytes):
        raise NotImplementedError()


class EncodingSegmentNumeric(EncodingSegment):

    encoding = CharacterEncodingType.NUMERIC

    def __init__(self, variant: EncodingVariant, initial_payload: Optional[str] = None):
        self.variant = variant
        self.payload = "" if initial_payload is None else initial_payload

    def __repr__(self):
        return f"EncodingSegmentNumeric({self.payload!r})"

    def copy(self) -> EncodingSegmentNumeric:
        return EncodingSegmentNumeric(self.variant, self.payload)

    def render(self, data_encoder: DataEncoder) -> None:
        data_encoder.append_numeric_mode_segment(self.payload)

    def append_character(self, c: str) -> None:
        self.payload = self.payload + c

    def bitcount(self) -> int:
        n = len(self.payload)
        count_bits = count_bits_table[self.variant][self.encoding]
        if n % 3 == 0:
            return 4 + count_bits + (n // 3) * 10
        if n % 3 == 1:
            return 4 + count_bits + (n // 3) * 10 + 4
        if n % 3 == 2:
            return 4 + count_bits + (n // 3) * 10 + 7


class EncodingSegmentAlphanumeric(EncodingSegment):

    encoding = CharacterEncodingType.ALPHANUMERIC

    def __init__(self, variant: EncodingVariant, initial_payload: Optional[str] = None):
        if not isinstance(variant, EncodingVariant):
            raise RuntimeError()
        self.variant = variant
        self.payload = "" if initial_payload is None else initial_payload

    def __repr__(self):
        return f"EncodingSegmentAlphanumeric({self.payload!r})"

    def copy(self) -> EncodingSegmentAlphanumeric:
        return EncodingSegmentAlphanumeric(self.variant, self.payload)

    def render(self, data_encoder: DataEncoder) -> None:
        data_encoder.append_alphanumeric_mode_segment(self.payload)

    def append_character(self, c: str) -> None:
        self.payload = self.payload + c

    def bitcount(self) -> int:
        n = len(self.payload)
        count_bits = count_bits_table[self.variant][self.encoding]
        if n % 2 == 0:
            return 4 + count_bits + (n // 2) * 11
        if n % 2 == 1:
            return 4 + count_bits + (n // 2) * 11 + 6


class EncodingSegmentBytes(EncodingSegment):

    encoding = CharacterEncodingType.BYTES

    def __init__(self, variant: EncodingVariant, initial_payload: Optional[bytes] = None):
        self.variant = variant
        self.payload = b"" if initial_payload is None else initial_payload

    def __repr__(self):
        return f"EncodingSegmentBytes({self.payload!r})"

    def copy(self) -> EncodingSegmentBytes:
        return EncodingSegmentBytes(self.variant, self.payload)

    def render(self, data_encoder: DataEncoder) -> None:
        data_encoder.append_byte_mode_segment(self.payload)

    def append_bytes(self, b: bytes):
        self.payload = self.payload + b

    def bitcount(self) -> int:
        n = len(self.payload)
        count_bits = count_bits_table[self.variant][self.encoding]
        return 4 + count_bits + n * 8


class EncodingSegmentKanji(EncodingSegment):

    encoding = CharacterEncodingType.KANJI

    def __init__(self, variant: EncodingVariant, initial_payload: Optional[str] = None):
        self.variant = variant
        self.payload = "" if initial_payload is None else initial_payload

    def __repr__(self):
        return f"EncodingSegmentKanji({self.payload!r})"

    def copy(self) -> EncodingSegmentKanji:
        return EncodingSegmentKanji(self.variant, self.payload)

    def render(self, data_encoder: DataEncoder) -> None:
        data_encoder.append_kanji_mode_segment(self.payload)

    def append_character(self, c: str) -> None:
        self.payload = self.payload + c

    def bitcount(self) -> int:
        n = len(self.payload)
        count_bits = count_bits_table[self.variant][self.encoding]
        return 4 + count_bits + n * 13


class EncodingSolution:

    def __init__(self, variant: EncodingVariant, segments=None):
        if segments is None:
            segments = []
        self.variant = variant
        self.segments = segments

    def __repr__(self):
        return f"EncodingSolution({self.variant}, {self.segments})"

    def copy(self) -> EncodingSolution:
        return EncodingSolution(self.variant, [segment.copy() for segment in self.segments])

    def render(self, data_encoder: DataEncoder) -> None:
        for segment in self.segments:
            segment.render(data_encoder)

    def append_numeric_character(self, c: str) -> None:
        """Append a numeric character to the solution, in the last segment or as a new segment if needed."""
        if self.active_encoding() == CharacterEncodingType.NUMERIC:
            self.segments[-1].append_character(c)
        else:
            self.segments.append(EncodingSegmentNumeric(self.variant, c))

    def append_alphanumeric_character(self, c: str) -> None:
        """Append an alphanumeric character to the solution, in the last segment or as a new segment if needed."""
        if self.active_encoding() == CharacterEncodingType.ALPHANUMERIC:
            self.segments[-1].append_character(c)
        else:
            self.segments.append(EncodingSegmentAlphanumeric(self.variant, c))

    def append_bytes(self, encoded_character_bytes: bytes) -> None:
        """Append bytes to the solution, in the last segment or as a new segment if needed."""
        if self.active_encoding() == CharacterEncodingType.BYTES:
            self.segments[-1].append_bytes(encoded_character_bytes)
        else:
            self.segments.append(EncodingSegmentBytes(self.variant, encoded_character_bytes))

    def append_kanji_character(self, c: str) -> None:
        """Append a kanji character to the solution, in the last segment or as a new segment if needed."""
        if self.active_encoding() == CharacterEncodingType.KANJI:
            self.segments[-1].append_character(c)
        else:
            self.segments.append(EncodingSegmentKanji(self.variant, c))

    def active_encoding(self) -> Optional[EncodingSegment]:
        return self.segments[-1].encoding if self.segments else None

    def bitcount(self) -> int:
        # Note that we DO NOT add 4 bits for the terminator.
        return sum(segment.bitcount() for segment in self.segments)

    def strictly_better(self, other: EncodingSolution) -> bool:
        return (self.active_encoding() == other.active_encoding()) and self.better(other)

    def better(self, other: EncodingSolution) -> bool:

        self_bitcount = self.bitcount()
        other_bitcount = other.bitcount()
        if self_bitcount < other_bitcount:
            return True

        return (self_bitcount == other_bitcount) and (len(self.segments) < len(other.segments))


def find_optimal_string_encoding(
            payload: str,
            variant: EncodingVariant,
            byte_mode_encoding: Optional[str] = None
        ) -> list[EncodingSolution]:
    """Find the optimal (shortest) encoding of a given string.

    There are three variants of the encoding, that differ only in the number of bits used to represent
    character counts in each of the four data segment types (numeric, alphanumeric, bytes, and Kanji).
    Larger versions of the QR code symbols allow more bits for those counts.

    The byte mode encoding specifies which encoding should be assumed for 'byte' mode segments.

    The 2000 edition of the standard prescribes JIS8 as a default encoding for byte-mode segments.
    The 2006, 2015, and 2024 editions of the standard prescribes ISO-8859-1 as a default encoding for byte-mode
    segments.

    For most modern applications, UTF-8 is a good default; byte mode blocks are interpreted as UTF-8 on
    all modern widely available QR-code readers that were tried.

    How it works
    ------------

    This algorithm works by starting with a single empty solution that encodes a zero-character string;
    and then iterating over each character to be encoded.
      For each character, the set of partial solutions that were found without this new character are considered.
    Each of them is extended with an encoding of the currently visited character. The four data segment modes
    (numeric, alphanumeric, byte, and kanji) are all considered. If the character can be represented in the mode,
    we will generate a new (sub)solution that extends the current solution either by extending the last encoding
    segment of the currently considered partial solution, if no mode switch is required; or by introducing a new
    data segment that encodes the single character currently under consideration.
      After a new set of partial solutions is produced that generate all characters up to and including the
    currently visited character, a pruning step is performed: partial solutions that are "strictly worse" than
    another partial solution also generated are discarded. Strictly worse here means that the partial solution
    can never lead to an optimal solution for the entire string.

    Once all characters are visited, the set of partial solutions is pruned a last time with a stronger criterion;
    all solutions that are suboptimal are now discarded.

    The end result is a set (represented as a list) of EncodingSolution instances that are optimal. Each of these
    solutions will have (1) minimal bitcount; and (2) a minimal number of mode segments.

    Note that pathological inputs exist that lead to many 'equally optimal' solutions. In fact, inputs can be
    constructed that give rise to an exponential number of solutions as the input length grows linearly.

    This is, however, rare enough that (for now) we have decided to ignore it. A future version of this code will
    probably prune more aggressively on partial solutions, making this impossible.
    """

    if byte_mode_encoding is None:
        byte_mode_encoding = 'utf-8'

    # Start with an empty encoding solution.
    partial_solutions = [
        EncodingSolution(variant)
    ]

    # Loop over all characters in the payload string.
    for c in payload:

        partial_solution_candidates = []

        for partial_solution in partial_solutions:

            # Consider NUMERIC encoding for this character.

            if c in numeric_character_map:
                partial_solution_candidate = partial_solution.copy()
                partial_solution_candidate.append_numeric_character(c)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider ALPHANUMERIC encoding for this character.

            if c in alphanumeric_character_map:
                partial_solution_candidate = partial_solution.copy()
                partial_solution_candidate.append_alphanumeric_character(c)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider BYTE encoding for this character.

            try:
                # Try to encode the characters using the byte_mode_encoding.
                encoded_character_bytes = c.encode(encoding=byte_mode_encoding, errors='strict')
            except UnicodeEncodeError:
                pass
            else:
                partial_solution_candidate = partial_solution.copy()
                partial_solution_candidate.append_bytes(encoded_character_bytes)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider KANJI encoding for this character.

            if kanji_character_value(c) is not None:
                partial_solution_candidate = partial_solution.copy()
                partial_solution_candidate.append_kanji_character(c)
                partial_solution_candidates.append(partial_solution_candidate)

        partial_solutions.clear()

        # Make a new list of partial solutions before processing the next character,
        # by pruning the solutions that can never become optimal.
        for p1 in partial_solution_candidates:
            if not any(p2.strictly_better(p1) for p2 in partial_solution_candidates):
                partial_solutions.append(p1)

    # All characters have now been processed. Prune all non-optimal solutions.
    solutions = []
    for s1 in partial_solutions:
        if not any(s2.better(s1) for s2 in partial_solutions):
            solutions.append(s1)

    # Sort solutions by bitcount and number of segments. Best solutions will come first.
    solutions_list = [(solution.bitcount(), len(solution.segments), solution) for solution in solutions]
    solutions_list.sort(key=lambda x: (x[0], x[1]), reverse=True)
    solutions = [solution for (bitcount, segment_count, solution) in solutions_list]

    return solutions


def make_default_version_preference_list() -> list[tuple[int, ErrorCorrectionLevel]]:
    return [
        (version, level)
        for version in range(1, 41)
        for level in (ErrorCorrectionLevel.H, ErrorCorrectionLevel.Q, ErrorCorrectionLevel.M, ErrorCorrectionLevel.L)
    ]


def make_optimal_qrcode(
            *,
            payload: str,
            include_quiet_zone: Optional[bool] = None,
            pattern: Optional[DataMaskPattern] = None,
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
            print(f"Number of optimal solutions: {len(solutions)}.")
            if len(solutions) == 0:
                solution = None
            else:
                #for solution in solutions:
                #    print("->", solution)
                solution = solutions[0]
                # print(f"Shortest solution: {solution.bitcount()} bits.")
            variant_cache[variant] = solution
        if solution is None:
            continue

        # See if this solution would fit in this (version, level) code.
        version_specification = version_specification_table[(version, level)]

        if version_specification.number_of_data_codewords() * 8 >= solution.bitcount():
            break

    else:
        # No acceptable solution found.
        return None

    de = DataEncoder(variant)
    solution.render(de)

    return make_qr_code(de, version=version, level=level, include_quiet_zone=include_quiet_zone, pattern=pattern)
