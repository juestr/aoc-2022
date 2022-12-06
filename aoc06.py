#!/usr/bin/env python3

from aoc_util import run_aoc


def aoc06(input):
    def marker(length):
        for i in range(length, len(input)):
            if len(set(input[i - length : i])) == length:
                return i

    yield marker(4)
    yield marker(14)


if __name__ == "__main__":
    run_aoc(aoc06, time=(1000, "ms"))
