#!/usr/bin/env python3

from funcy import collecting, flip, joining, post_processing

from aoc_util import run_aoc

SNAFU = {"2": 2, "1": 1, "0": 0, "-": -1, "=": -2}
SNAFU_R = flip(SNAFU)


def aoc25(lines):
    def from_SNAFU(s):
        return sum(SNAFU[c] * 5**i for i, c in enumerate(reversed(s)))

    @joining("")
    @post_processing(reversed)
    @collecting
    def to_SNAFU(x):
        while x:
            r = x % 5
            corr = (r > 2) * 5
            yield SNAFU_R[r - corr]
            x += corr
            x //= 5

    yield to_SNAFU(sum(map(from_SNAFU, lines)))


if __name__ == "__main__":
    run_aoc(aoc25, split="lines")
