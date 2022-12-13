#!/usr/bin/env python3

from dataclasses import dataclass
from functools import total_ordering
from typing import Iterator, TypeAlias, overload

from funcy import chunks, lmap

from aoc_util import run_aoc

IntTree: TypeAlias = list["int | IntTree"]
CmpIntTree: TypeAlias = list["CmpInt | CmpIntTree"]


@total_ordering
@dataclass(order=False, frozen=True)
class CmpInt:
    """An int wrapper able to compare to lists"""

    v: int

    def __eq__(self, other):
        # fmt: off
        match other:
            case CmpInt(o): return self.v == o
            case list():    return [self] == other
            case _:         return NotImplemented
        # fmt: on

    def __lt__(self, other):
        # fmt: off
        match other:
            case CmpInt(o): return self.v < o
            case list():    return [self] < other
            case _:         return NotImplemented
        # fmt: on


def setup(lines: list[str]) -> tuple[list[CmpIntTree]]:
    # fmt: off
    @overload
    def wrap(x: int) -> CmpInt: pass
    @overload
    def wrap(x: IntTree) -> CmpIntTree: pass
    # fmt: on

    def wrap(x):
        # fmt: off
        match x:
            case int():     return CmpInt(x)
            case list():    return lmap(wrap, x)
            case _:         assert False, 'wrong argument type'
        # fmt: on

    return ([wrap(eval(line)) for line in lines if line],)  # mypy: ignore


def aoc13(packets: list[CmpIntTree]) -> Iterator[int]:
    indexed_pairs = enumerate(chunks(2, packets), start=1)
    correct = (idx for idx, (a, b) in indexed_pairs if a < b)

    yield sum(correct)

    divider1: CmpIntTree = [[CmpInt(2)]]
    divider2: CmpIntTree = [[CmpInt(6)]]
    packets.extend([divider1, divider2])
    packets.sort()
    idx1 = packets.index(divider1) + 1
    idx2 = packets.index(divider2) + 1

    yield idx1 * idx2


if __name__ == "__main__":
    run_aoc(aoc13, split="lines", transform=setup, time=(1000, "ms"))
