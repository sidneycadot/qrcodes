"""Find optimal encoding of a string."""

from __future__ import annotations

from typing import Optional

from data_encoder import Encoding, numeric_character_map, alphanumeric_character_map


class EncodingBlock:
    pass


class EncodingBlockNumeric(EncodingBlock):

    encoding = Encoding.NUMERIC

    def __init__(self, c: str):
        self.payload = c

    def __repr__(self):
        return f"EncodingBlockNumeric({self.payload!r})"

    def copy(self) -> EncodingBlockNumeric:
        return EncodingBlockNumeric(self.payload)

    def append_character(self, c: str) -> None:
        self.payload = self.payload + c

    def bitcount(self, version: int) -> int:
        if (1 <= version <= 9):
            countbits = 10
        elif (10 <= version <= 26):
            countbits = 12
        elif (27 <= version <= 40):
            countbits = 14
        else:
            raise ValueError()
        n = len(self.payload)
        if n % 3 == 0:
            return 4 + countbits + (n // 3) * 10
        if n % 3 == 1:
            return 4 + countbits + (n // 3) * 10 + 4
        if n % 3 == 2:
            return 4 + countbits + (n // 3) * 10 + 7


class EncodingBlockAlphanumeric(EncodingBlock):

    encoding = Encoding.ALPHANUMERIC

    def __init__(self, c: str):
        self.payload = c

    def __repr__(self):
        return f"EncodingBlockAlphanumeric({self.payload!r})"

    def copy(self) -> EncodingBlockAlphanumeric:
        return EncodingBlockAlphanumeric(self.payload)

    def append_character(self, c: str) -> None:
        self.payload = self.payload + c

    def bitcount(self, version: int) -> int:
        if (1 <= version <= 9):
            countbits = 9
        elif (10 <= version <= 26):
            countbits = 11
        elif (27 <= version <= 40):
            countbits = 13
        else:
            raise ValueError()
        n = len(self.payload)
        if n % 2 == 0:
            return 4 + countbits + (n // 2) * 11
        if n % 2 == 1:
            return 4 + countbits + (n // 2) * 11 + 6


class EncodingBlockBytes(EncodingBlock):

    encoding = Encoding.BYTES

    def __init__(self, b: bytes):
        self.payload = b

    def __repr__(self):
        return f"EncodingBlockBytes({self.payload!r})"

    def copy(self) -> EncodingBlockBytes:
        return EncodingBlockBytes(self.payload)

    def append_bytes(self, b: bytes):
        self.payload = self.payload + b

    def bitcount(self, version: int) -> int:
        if (1 <= version <= 9):
            countbits = 8
        elif (10 <= version <= 26):
            countbits = 16
        elif (27 <= version <= 40):
            countbits = 16
        else:
            raise ValueError()
        n = len(self.payload)
        return 4 + countbits + n * 8


class EncodingBlockKanji(EncodingBlock):

    encoding = Encoding.KANJI

    def __init__(self, c: str):
        self.payload = c

    def __repr__(self):
        return f"EncodingBlockKanji({self.payload!r})"

    def copy(self) -> EncodingBlockKanji:
        return EncodingBlockKanji(self.payload)

    def append_character(self, c: str) -> None:
        self.payload = self.payload + c

    def bitcount(self, version: int) -> int:
        if (1 <= version <= 9):
            countbits = 8
        elif (10 <= version <= 26):
            countbits = 10
        elif (27 <= version <= 40):
            countbits = 12
        else:
            raise ValueError()
        n = len(self.payload)
        return 4 + countbits + n * 13


class EncodingSolution:

    def __init__(self, blocks=None):
        if blocks is None:
            blocks = []
        self.blocks = blocks

    def __repr__(self):
        return f"EncodingSolution({self.blocks})"

    def copy(self):
        return EncodingSolution([block.copy() for block in self.blocks])

    def append_block(self, block: EncodingBlock):
        self.blocks.append(block)

    def pop_block(self):
        return self.blocks.pop()

    def active_encoding(self) -> Optional[Encoding]:
        if len(self.blocks) == 0:
            return None
        return self.blocks[-1].encoding

    def bitcount(self, version: int) -> int:
        # Add 4 bits for the terminator.
        return sum(block.bitcount(version) for block in self.blocks) + 4

    def strictly_better(self, other: EncodingSolution, version: int) -> bool:
        if self.active_encoding() != other.active_encoding():
            return False

        self_bitcount = self.bitcount(version)
        other_bitcount = other.bitcount(version)
        if self_bitcount < other_bitcount:
            return True

        return (self.bitcount == other_bitcount) and (len(self.blocks) < len(other.blocks))

    def better(self, other: EncodingSolution, version: int) -> bool:

        self_bitcount = self.bitcount(version)
        other_bitcount = other.bitcount(version)
        if self_bitcount < other_bitcount:
            return True

        return (self_bitcount == other_bitcount) and (len(self.blocks) < len(other.blocks))


def find_optimal_string_encoding(s: str, version: int, byte_mode_encoding: Optional[str] = None) -> list[EncodingSolution]:

    if byte_mode_encoding is None:
        byte_mode_encoding = 'utf-8'

    partial_solutions = [
        EncodingSolution()
    ]

    # Walk all characters in the string.
    for c in s:

        partial_solution_candidates = []

        for partial_solution in partial_solutions:

            active_encoding = partial_solution.active_encoding()

            # Consider NUMERIC encoding for this character.

            if c in numeric_character_map:
                partial_solution_candidate = partial_solution.copy()
                if active_encoding == Encoding.NUMERIC:
                    # Append the character to the last block.
                    block = partial_solution_candidate.pop_block()
                    block.append_character(c)
                else:
                    # Add a new numeric encoding block.
                    block = EncodingBlockNumeric(c)

                partial_solution_candidate.append_block(block)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider ALPHANUMERIC encoding for this character.

            if c in alphanumeric_character_map:
                partial_solution_candidate = partial_solution.copy()
                if active_encoding == Encoding.ALPHANUMERIC:
                    # Append the character to the last encoding block.
                    block = partial_solution_candidate.pop_block()
                    block.append_character(c)
                else:
                    # Add a new alphanumeric encoding block.
                    block = EncodingBlockAlphanumeric(c)

                partial_solution_candidate.append_block(block)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider BYTE encoding for this character.

            try:
                encoded_character_bytes = c.encode(encoding=byte_mode_encoding, errors='strict')
            except UnicodeEncodeError:
                pass
            else:
                partial_solution_candidate = partial_solution.copy()
                if active_encoding == Encoding.BYTES:
                    # Append the character to the last encoding block.
                    block = partial_solution_candidate.pop_block()
                    block.append_bytes(encoded_character_bytes)
                else:
                    # Add a new bytes block.
                    block = EncodingBlockBytes(encoded_character_bytes)

                partial_solution_candidate.append_block(block)
                partial_solution_candidates.append(partial_solution_candidate)

            # Consider KANJI encoding for this character.

            try:
                encoded_character_bytes = c.encode(encoding='shift-jis', errors='strict')
            except UnicodeEncodeError:
                pass
            else:
                value = int.from_bytes(encoded_character_bytes, byteorder='big')
                if (0x8140 <= value <= 0x9ffc) or (0xe040 <= value <= 0xebbf):
                    partial_solution_candidate = partial_solution.copy()
                    if active_encoding == Encoding.KANJI:
                        # Append the character to the last encoding block.
                        block = partial_solution_candidate.pop_block()
                        block.append_character(c)
                    else:
                        # Add a new kanji encoding block.
                        block = EncodingBlockKanji(c)

                    partial_solution_candidate.append_block(block)
                    partial_solution_candidates.append(partial_solution_candidate)

        partial_solutions.clear()

        for p1 in partial_solution_candidates:
            if not any(p2.strictly_better(p1, version) for p2 in partial_solution_candidates):
                partial_solutions.append(p1)

    solution_candidates = partial_solutions

    solutions = []
    for s1 in solution_candidates:
        if not any(s2.better(s1, version) for s2 in solution_candidates):
            solutions.append(s1)

    solutions = [(solution.bitcount(version), solution) for solution in solutions]

    solutions.sort(key=lambda x: x[0], reverse=True)

    solutions = [solution for (bitcount, solution) in solutions]

    return solutions
