#!/usr/bin/env python3

from more_itertools import chunked, divide, one

from aoc_util import run_aoc


def priority(x):
    i = ord(x)
    return i - 96 if i > 96 else i - 38


def aoc03(rucksacks):
    compartments = (divide(2, r) for r in rucksacks)
    in_both = (one(set(a) & set(b)) for a, b in compartments)
    sum_priorities = sum(map(priority, in_both))

    yield sum_priorities

    groups = chunked(rucksacks, 3)
    shared_items = (one(set(a) & set(b) & set(c)) for a, b, c in groups)
    sum_priorities2 = sum(map(priority, shared_items))

    yield sum_priorities2


if __name__ == "__main__":
    run_aoc(aoc03, split="lines")
