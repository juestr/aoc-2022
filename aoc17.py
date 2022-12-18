#!/usr/bin/env python3

import logging
import math
import os
from itertools import pairwise

import numpy as np
import pandas as pd
from funcy import cat, count, cycle, drop, last, lcat, lmap, lmapcat, map, mapcat, take

from aoc_util import d, run_aoc

np, pd, pairwise, d, map, lmap, mapcat, lmapcat, cat, lcat, cycle, last, take, count, drop

ROCKS = 2022
ROCKS2 = 1_000_000_000_000
WIDTH = 7
# shapes are mirrored row-wise since we want to have the cave bottom at 0
ROCK_SHAPES = [
    np.array([[1, 1, 1, 1]], dtype=np.int8),
    np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.int8),
    np.array([[1, 1, 1], [0, 0, 1], [0, 0, 1]], dtype=np.int8),
    np.array([[1], [1], [1], [1]], dtype=np.int8),
    np.array([[1, 1], [1, 1]], dtype=np.int8),
]
NEW_OFFS = np.array([4, 2], dtype=np.int32)
INTERACTIVE = int(os.environ.get("AOC_INTERACTIVE") or 0)


def setup(input):
    return (lcat((1,) if c == ">" else (-1,) if c == "<" else () for c in input),)


def aoc17(jet: list[int]):  # of -1, 1
    def rock_init(floor, rock):
        pos = np.array([[floor, 0], [0, 0]], dtype=np.int32)
        pos[1] = pos[0] + rock.shape
        pos += NEW_OFFS
        return pos

    def project(cave, pos):
        return cave[tuple(slice(*u) for u in pos.T)]

    def try_move(cave, pos, rock, delta, fix_stuck=False):
        dest = pos + delta
        if dest[0, 1] < 0 or dest[1, 1] > WIDTH:
            return False, pos
        elif np.tensordot(project(cave, dest), rock):
            if fix_stuck:
                view = project(cave, pos)
                view |= rock * fix_stuck
            return False, pos
        else:
            return True, dest

    def jet_move(cave, pos, rock, delta):
        _, pos = try_move(cave, pos, rock, [0, delta])
        return pos

    def move_down(cave, pos, rock, mark=1):
        return try_move(cave, pos, rock, [-1, 0], fix_stuck=mark)

    def grow_cave(cave, size):
        if (h := cave.shape[0]) < size:
            new = np.zeros((h * 2, WIDTH), dtype=np.int32)
            new[:h] = cave
            del cave
            return new
        else:
            return cave

    def cave_fingerprint(cave, floor):
        flag = np.zeros(WIDTH, bool)
        for n, line in enumerate(cave[floor:0:-1]):
            flag |= line.astype(bool)
            if np.alltrue(flag):
                return cave[floor : floor - n - 1 : -1].copy().astype(bool)
        else:
            assert False, "invalid cave"

    def array_equal(a1, a2):
        return a1.shape == a2.shape and np.alltrue(np.equal(a1, a2))

    def prompt_interactive(msg="continue?", prompt=None, level=logging.DEBUG):
        if logging.getLogger().isEnabledFor(level):
            if INTERACTIVE >= prompt:
                return __builtins__.input(msg)

    def show_cave(cave, add_rock=None, height=None, level=logging.DEBUG):
        if logging.getLogger().isEnabledFor(level):
            if add_rock:
                pos, rock = add_rock
                cave = cave.copy()
                view = project(cave, pos)
                view |= rock * -1
            with np.printoptions(
                linewidth=50,
                threshold=1000000,
                formatter={
                    "int": lambda x: "@" if x == -1 else str(x % 10) if x else "·"
                },
            ):
                d(str(cave[height::-1]), l=level)

    def run(start=1, cave=None, floor=None, jet_moves=None):
        cave = np.zeros((1000, WIDTH), dtype=np.int32) if cave is None else cave
        if floor is None:
            floor = 0
            cave[floor, :] = -10
        jet_moves = jet_moves or cycle(jet)

        for i, rock in zip(count(start), cycle(ROCK_SHAPES)):
            pos = rock_init(floor, rock)
            cave = grow_cave(cave, pos[1, 0])

            # d(i, floor, m="=== i floor")
            # d(rock, t="rock")
            # d(pos.flatten(), m="initial pos")
            # show_cave(cave, add_rock=(pos, rock), height=floor + 8)
            # prompt_interactive(prompt=2)
            # d("---")

            not_stuck = True
            while not_stuck:
                pos = jet_move(cave, pos, rock, j := next(jet_moves))
                not_stuck, pos = move_down(cave, pos, rock, mark=i)

                # d(pos.flatten(), j, m="       jet")
                # d(pos.flatten(), not_stuck, m="moved down")
                # show_cave(cave, add_rock=(pos, rock), height=floor + 8)
                # prompt_interactive(prompt=2)
            # show_cave(cave, height=floor + 8)
            # prompt_interactive(prompt=1)

            floor = max(floor, pos[1, 0] - 1)
            yield i, cave, floor

    # _, _, floor = last(take(ROCKS, run()))
    # yield floor

    def optimized_tower_size():
        cycle_divisor = math.lcm(len(jet), len(ROCK_SHAPES))
        d(cycle_divisor, m="cycle_divisor")

        process = run()
        _, cave0, size0 = last(take(cycle_divisor, process))
        cave0 = cave0.copy()
        fpr0 = cave_fingerprint(cave0, size0)
        show_cave(cave0[size0 - 20 : size0 + 3])
        for j in count(1):
            i, cave, floor = last(take(cycle_divisor, process))
            d(j, i, floor, m="j i floor")
            show_cave(cave[floor - 20 : floor + 3])
            prompt_interactive(prompt=1)
            fpr = cave_fingerprint(cave, floor)
            if array_equal(fpr, fpr0):
                d("found a cycle", j)
                process.close()
                break

        cycle_size = j * cycle_divisor
        cycle_growth = floor - size0
        d("cycle_size", cycle_size)
        d("cycle_growth", cycle_growth)

        def tower_size(rocks):
            if rocks < cycle_divisor:
                _, _, floor = last(take(n, run()))
                return floor
            elif rocks == cycle_divisor:
                return size0
            else:
                n = cycle_divisor + (rocks - cycle_divisor) % cycle_size
                _, _, floor = last(take(n, run()))

                # _, _, floor = last(take(cycle_divisor, (p := run())))
                # logging.getLogger().setLevel(logging.DEBUG)
                # n = (rocks - cycle_divisor) % cycle_size
                # _, _, floor = last(take(n, p))

                # logging.getLogger().setLevel(logging.DEBUG)
                # n = (rocks - cycle_divisor) % cycle_size
                # _, _, floor = last(
                #     take(
                #         n,
                #         run(
                #             start=cycle_divisor + 1,
                #             cave=cave0,
                #             floor=size0,
                #             jet_moves=drop(cycle_divisor - 1, cycle(jet)),
                #         ),
                #     )
                # )
                d("floor", floor)
                return (
                    size0
                    + ((rocks - cycle_divisor) // cycle_size) * cycle_growth
                    + (floor - size0) % cycle_growth
                )

        return tower_size

    tower_size = optimized_tower_size()

    yield tower_size(ROCKS)
    yield tower_size(ROCKS2)


if __name__ == "__main__":
    run_aoc(
        aoc17,
        transform=setup,
        np_printoptions=dict(
            linewidth=50, threshold=100000, formatter={"bool": "·#".__getitem__}
        ),
    )
