#!/usr/bin/env python3

import re
from copy import deepcopy
from itertools import zip_longest

from more_itertools import always_reversible, lstrip, split_at

from aoc_util import run_aoc


def parse(lines):
    def equals(const):
        return lambda x: x == const

    def to_move(line):
        n, src, dst = re.match(r"move (\d+) from (\d+) to (\d+)", line).groups()
        return int(n), int(src) - 1, int(dst) - 1

    def to_stacks(lines):
        crates_h = [list(line[1::4]) for line in lines]
        return tuple(
            list(always_reversible(lstrip(crates, equals(" "))))
            for crates in zip_longest(*crates_h, fillvalue=" ")
        )

    (*crates_txt, _), moves_txt = split_at(lines, equals(""))
    stacks = to_stacks(crates_txt)
    moves = [to_move(line) for line in moves_txt]
    return stacks, moves


def aoc05(stacks, moves):
    stacks2 = deepcopy(stacks)

    for n, src, dst in moves:
        stacks[dst].extend(stacks[src][-1 : -n - 1 : -1])
        del stacks[src][-n:]
    top = "".join(crates[-1] for crates in stacks)
    yield top

    stacks = stacks2
    for n, src, dst in moves:
        stacks[dst].extend(stacks[src][-n:])
        del stacks[src][-n:]
    top = "".join(crates[-1] for crates in stacks)
    yield top


if __name__ == "__main__":
    run_aoc(aoc05, split="lines", transform=parse)
