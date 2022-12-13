#!/usr/bin/env python3

from dataclasses import dataclass
from functools import total_ordering

from more_itertools import chunked

from aoc_util import run_aoc


@total_ordering
@dataclass(order=False, frozen=True)
class CmpInt:
    """Am int wrapper able to compare to lists"""

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


def setup(lines):
    def wrap(x: int | list[int | list]) -> "CmpInt | list[CmpInt | list]":
        # fmt: off
        match x:
            case int():     return CmpInt(x)
            case list():    return [wrap(i) for i in x]
            case _:         assert False, 'int-lists only'
        # fmt: on

    return ([wrap(eval(line)) for line in lines if line],)


def aoc13(packets):
    indexed_pairs = enumerate(chunked(packets, 2), start=1)
    correct = (idx for idx, (a, b) in indexed_pairs if a < b)

    yield sum(correct)

    divider1 = [[CmpInt(2)]]
    divider2 = [[CmpInt(6)]]
    packets.extend([divider1, divider2])
    packets.sort()
    idx1 = packets.index(divider1) + 1
    idx2 = packets.index(divider2) + 1

    yield idx1 * idx2


if __name__ == "__main__":
    run_aoc(aoc13, split="lines", transform=setup, time=(1000, "ms"))
