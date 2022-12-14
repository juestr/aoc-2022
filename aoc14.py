#!/usr/bin/env python3

import re

import numpy as np
from funcy import lcat, lmapcat, map, partition

from aoc_util import d, np_condense, run_aoc

RockFormation = tuple[int, int, int, int]


def setup(lines: list[str]) -> tuple[list[RockFormation]]:
    convert = lambda line: map(
        tuple, partition(4, 2, map(int, re.split(",| -> ", line)))
    )
    return (lmapcat(convert, lines),)


def pour(cave, x, stop_at_y=None):
    y = 0
    if stop_at_y is None:
        stop_at_y = cave.shape[0]
    while y < stop_at_y:
        if not cave[y + 1, x]:
            y += 1
        elif not cave[y + 1, x - 1]:
            y += 1
            x -= 1
        elif not cave[y + 1, x + 1]:
            y += 1
            x += 1
        else:
            break
    cave[y, x] = 2
    return x, y


def aoc14(rocks: list[RockFormation]):
    d(rocks, p=1, t="rocks")
    all_numbers = lcat(rocks)
    min_x = min(all_numbers[0::2])
    max_x = max(all_numbers[0::2])
    max_y = max(all_numbers[1::2])
    offs_x = max_y - min_x
    pour_point = 500 + offs_x
    cave = np.zeros((max_y + 3, (max_x - min_x + 1) + 2 * max_y), dtype=np.uint8)
    to_slice = lambda v0, v1, s=0: slice(min(v0, v1) + s, max(v0, v1) + s + 1)
    for (x0, y0, x1, y1) in rocks:
        cave[to_slice(y0, y1), to_slice(x0, x1, offs_x)] = 1

    count = 0
    while pour(cave, pour_point, stop_at_y=max_y)[1] < max_y:
        count += 1
    d(cave[:-2, min_x + offs_x : max_x + offs_x], t="cave", apply=np_condense)

    yield count

    cave[cave == 2] = 0
    cave[max_y + 2, :] = 1

    count = 1
    while pour(cave, pour_point)[1] != 0:
        count += 1
    d(
        cave[:, max_y // 6 * 5 - 5 : -max_y // 6 * 5 + 5],
        t="cave (truncated x)",
        apply=np_condense,
    )

    yield count


if __name__ == "__main__":
    run_aoc(
        aoc14,
        split="lines",
        transform=setup,
        np_printoptions=dict(
            linewidth=300, threshold=50000, formatter={"int": "·#○".__getitem__}
        ),
    )
