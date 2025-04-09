"""Find the optimal data encoding(s) of a given string.

An encoding solution is optimal if:

  (1) its bit-count is minimal;
  (2) among the encoding solutions with minimal bit-count, the number of blocks is minimal.

Note: pathological input strings exist that lead to many different optimal encoding solutions that are all
      optimal in the sense as defined above.

Solutions are represented by instances of the EncodingSolution class. They can be rendered into a DataEncoder.
"""

from __future__ import annotations

from typing import Optional

from .data_encoder import numeric_character_map, alphanumeric_character_map, DataEncoder
from .enum_types import CharacterEncodingType, EncodingVariant
from .kanji_encode import kanji_character_value
from .lookup_tables import count_bits_table


class EncodingBlock:
    """Abstract base class for data encoding blocks in QR codes."""
    pass


class EncodingBlockNumeric(EncodingBlock):

    encoding = CharacterEncodingType.NUMERIC

    def __init__(self, variant: EncodingVariant, initial_payload: Optional[str] = None):
        self.variant = variant
        self.payload = "" if initial_payload is None else initial_payload

    def __repr__(self):
        return f"EncodingBlockNumeric({self.payload!r})"

    def copy(self) -> EncodingBlockNumeric:
        return EncodingBlockNumeric(self.variant, self.payload)

    def render(self, data_encoder: DataEncoder) -> None:
        data_encoder.append_numeric_mode_block(self.payload)

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


class EncodingBlockAlphanumeric(EncodingBlock):

    encoding = CharacterEncodingType.ALPHANUMERIC

    def __init__(self, variant: EncodingVariant, initial_payload: Optional[str] = None):
        if not isinstance(variant, EncodingVariant):
            raise RuntimeError()
        self.variant = variant
        self.payload = "" if initial_payload is None else initial_payload

    def __repr__(self):
        return f"EncodingBlockAlphanumeric({self.payload!r})"

    def copy(self) -> EncodingBlockAlphanumeric:
        return EncodingBlockAlphanumeric(self.variant, self.payload)

    def render(self, data_encoder: DataEncoder) -> None:
        data_encoder.append_alphanumeric_mode_block(self.payload)

    def append_character(self, c: str) -> None:
        self.payload = self.payload + c

    def bitcount(self) -> int:
        n = len(self.payload)
        count_bits = count_bits_table[self.variant][self.encoding]
        if n % 2 == 0:
            return 4 + count_bits + (n // 2) * 11
        if n % 2 == 1:
            return 4 + count_bits + (n // 2) * 11 + 6


class EncodingBlockBytes(EncodingBlock):

    encoding = CharacterEncodingType.BYTES

    def __init__(self, variant: EncodingVariant, initial_payload: Optional[bytes] = None):
        self.variant = variant
        self.payload = b"" if initial_payload is None else initial_payload

    def __repr__(self):
        return f"EncodingBlockBytes({self.payload!r})"

    def copy(self) -> EncodingBlockBytes:
        return EncodingBlockBytes(self.variant, self.payload)

    def render(self, data_encoder: DataEncoder) -> None:
        data_encoder.append_byte_mode_block(self.payload)

    def append_bytes(self, b: bytes):
        self.payload = self.payload + b

    def bitcount(self) -> int:
        n = len(self.payload)
        count_bits = count_bits_table[self.variant][self.encoding]
        return 4 + count_bits + n * 8


class EncodingBlockKanji(EncodingBlock):

    encoding = CharacterEncodingType.KANJI

    def __init__(self, variant: EncodingVariant, initial_payload: Optional[str] = None):
        self.variant = variant
        self.payload = "" if initial_payload is None else initial_payload

    def __repr__(self):
        return f"EncodingBlockKanji({self.payload!r})"

    def copy(self) -> EncodingBlockKanji:
        return EncodingBlockKanji(self.variant, self.payload)

    def render(self, data_encoder: DataEncoder) -> None:
        data_encoder.append_kanji_mode_block(self.payload)

    def append_character(self, c: str) -> None:
        self.payload = self.payload + c

    def bitcount(self) -> int:
        n = len(self.payload)
        count_bits = count_bits_table[self.variant][self.encoding]
        return 4 + count_bits + n * 13


class EncodingSolution:

    def __init__(self, variant: EncodingVariant, blocks=None):
        if blocks is None:
            blocks = []
        self.variant = variant
        self.blocks = blocks

    def __repr__(self):
        return f"EncodingSolution({self.variant}, {self.blocks})"

    def copy(self) -> EncodingSolution:
        return EncodingSolution(self.variant, [block.copy() for block in self.blocks])

    def render(self, data_encoder: DataEncoder) -> None:
        for block in self.blocks:
            block.render(data_encoder)

    def append_block(self, block: EncodingBlock) -> None:
        self.blocks.append(block)

    def pop_block(self) -> EncodingBlock:
        return self.blocks.pop()

    def active_encoding(self) -> Optional[CharacterEncodingType]:
        if len(self.blocks) == 0:
            return None
        return self.blocks[-1].encoding

    def bitcount(self) -> int:
        # Note that we DO NOT add 4 bits for the terminator.
        return sum(block.bitcount() for block in self.blocks)

    def strictly_better(self, other: EncodingSolution) -> bool:
        return (self.active_encoding() == other.active_encoding()) and self.better(other)

    def better(self, other: EncodingSolution) -> bool:

        self_bitcount = self.bitcount()
        other_bitcount = other.bitcount()
        if self_bitcount < other_bitcount:
            return True

        return (self_bitcount == other_bitcount) and (len(self.blocks) < len(other.blocks))


def find_optimal_string_encoding(s: str, variant: EncodingVariant, byte_mode_encoding: Optional[str] = None) -> list[EncodingSolution]:
    """Find the optimal (shortest) encoding of a given string.

    There are three variants of the encoding, that differ only in the number of bits used to represent
    character counts in each of the four data block types (numeric, alphanumeric, bytes, and Kanji).
    Larger versions of the QR code symbols allow more bits for those counts.

    The byte mode encoding specifies which encoding should be assumed for 'byte' mode blocks. For most modern
    applications, UTF-8 is a good default.
    """

    if byte_mode_encoding is None:
        byte_mode_encoding = 'utf-8'

    partial_solutions = [
        EncodingSolution(variant)  # An empty encoding solution.
    ]

    # Walk all characters in the string.
    for c in s:

        partial_solution_candidates = []

        for partial_solution in partial_solutions:

            active_encoding = partial_solution.active_encoding()

            # Consider NUMERIC encoding for this character.

            if c in numeric_character_map:
                partial_solution_candidate = partial_solution.copy()
                if active_encoding == CharacterEncodingType.NUMERIC:
                    # Append the character to the last block.
                    block = partial_solution_candidate.pop_block()
                    block.append_character(c)
                else:
                    # Add a new numeric encoding block.
                    block = EncodingBlockNumeric(variant, c)

                partial_solution_candidate.append_block(block)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider ALPHANUMERIC encoding for this character.

            if c in alphanumeric_character_map:
                partial_solution_candidate = partial_solution.copy()
                if active_encoding == CharacterEncodingType.ALPHANUMERIC:
                    # Append the character to the last encoding block.
                    block = partial_solution_candidate.pop_block()
                    block.append_character(c)
                else:
                    # Add a new alphanumeric encoding block.
                    block = EncodingBlockAlphanumeric(variant, c)

                partial_solution_candidate.append_block(block)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider BYTE encoding for this character.

            try:
                encoded_character_bytes = c.encode(encoding=byte_mode_encoding, errors='strict')
            except UnicodeEncodeError:
                pass
            else:
                partial_solution_candidate = partial_solution.copy()
                if active_encoding == CharacterEncodingType.BYTES:
                    # Append the character to the last encoding block.
                    block = partial_solution_candidate.pop_block()
                    block.append_bytes(encoded_character_bytes)
                else:
                    # Add a new bytes block.
                    block = EncodingBlockBytes(variant, encoded_character_bytes)

                partial_solution_candidate.append_block(block)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider KANJI encoding for this character.

            if kanji_character_value(c) is not None:
                partial_solution_candidate = partial_solution.copy()
                if active_encoding == CharacterEncodingType.KANJI:
                    # Append the character to the last encoding block.
                    block = partial_solution_candidate.pop_block()
                    block.append_character(c)
                else:
                    # Add a new kanji encoding block.
                    block = EncodingBlockKanji(variant, c)

                partial_solution_candidate.append_block(block)
                partial_solution_candidates.append(partial_solution_candidate)

        partial_solutions.clear()

        # Make a new list of partial solutions before processing the next character,
        # by pruning the solutions that can never become optimal.
        for p1 in partial_solution_candidates:
            if not any(p2.strictly_better(p1) for p2 in partial_solution_candidates):
                partial_solutions.append(p1)

    # All characters have now been processed. Prune all non-optimal solutions.
    solution_candidates = partial_solutions

    solutions = []
    for s1 in solution_candidates:
        if not any(s2.better(s1) for s2 in solution_candidates):
            solutions.append(s1)

    # Sort solutions by bitcount.
    solutions_list = [(solution.bitcount(), solution) for solution in solutions]
    solutions_list.sort(key=lambda x: x[0], reverse=True)
    solutions = [solution for (bitcount, solution) in solutions_list]

    return solutions
