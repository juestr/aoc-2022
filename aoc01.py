#!/usr/bin/env python3

from itertools import pairwise

from runner import run_aoc

def aoc01(input):

    groups = input.split('\n\n')
    calories = [sum(map(int, group.split())) for group in groups]

    yield max(calories)

    yield sum(sorted(calories)[-3:])


if __name__ == '__main__':
    run_aoc(aoc01)
