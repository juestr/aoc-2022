#!/usr/bin/env python3

import logging
import math
from itertools import takewhile

import numpy as np
from funcy import complement, count, curry, cycle, ilen, last, lcat, some, take

from aoc_util import d, prompt, run_aoc

ROCKS = 2022
ROCKS2 = 1_000_000_000_000
WIDTH = 7
# Shapes are mirrored row-wise since the cave is too for bottom == 0.
ROCK_SHAPES = [
    np.array([[1, 1, 1, 1]], dtype=np.int32),
    np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.int32),
    np.array([[1, 1, 1], [0, 0, 1], [0, 0, 1]], dtype=np.int32),
    np.array([[1], [1], [1], [1]], dtype=np.int32),
    np.array([[1, 1], [1, 1]], dtype=np.int32),
]
NEW_OFFS = np.array([4, 2], dtype=np.int32)


def setup(input):
    return (lcat((1,) if c == ">" else (-1,) if c == "<" else () for c in input),)


def aoc17(jet: list[int]):  # of -1, 1
    def rock_init(height, rock):
        position = np.array([[height, 0], [0, 0]], dtype=np.int32)
        position[1] = position[0] + rock.shape
        position += NEW_OFFS
        return position

    def project(cave, position):
        return cave[tuple(slice(*u) for u in position.T)]

    def try_move(cave, position, rock, delta, mark_fixed=False):
        dest = position + delta
        if dest[0, 1] < 0 or dest[1, 1] > WIDTH:
            return False, position
        elif np.tensordot(project(cave, dest), rock):
            if mark_fixed:
                view = project(cave, position)
                view |= rock * mark_fixed
            return False, position
        else:
            return True, dest

    def jet_move(cave, position, rock, delta):
        _, position = try_move(cave, position, rock, [0, delta])
        return position

    def move_down(cave, position, rock, mark=1):
        return try_move(cave, position, rock, [-1, 0], mark_fixed=mark)

    def grow_cave(cave, required_size):
        cursize = cave.shape[0]
        if cursize < required_size:
            new = np.zeros((cursize * 2, WIDTH), dtype=np.int32)
            new[:cursize] = cave
            return new
        else:
            return cave

    def cave_fingerprint(cave, height):
        # Not optimal but fast and safe, no jet can get a rock shape through the
        # possible gaps in 3 lines.
        for h in range(height, 3, -1):
            flag = np.logical_or.reduce(cave[h - 2 : h + 1, :], axis=0)
            if np.alltrue(flag):
                return cave[h - 2 : height + 1].copy().astype(bool)
        return cave

    def array_equal(a1, a2):
        return a1.shape == a2.shape and np.alltrue(np.equal(a1, a2))

    def show_cave(cave, add_rock=None, height=None, level=logging.DEBUG):
        if logging.getLogger().isEnabledFor(level):
            if add_rock:
                position, rock_shape = add_rock
                cave = cave.copy()
                view = project(cave, position)
                view |= rock_shape * -1
            with np.printoptions(
                linewidth=50,
                threshold=1000000,
                formatter={
                    "int": lambda x: "@" if x == -1 else str(x % 10) if x else "·",
                    "bool": "·#".__getitem__,
                },
            ):
                d(str(cave[height::-1]), l=level)

    def run():
        """Series of caves with rocks added, starting with zero and a floor

        Yields (view to a) cave, height tuples.
        Cave is a np.array of int32, row zero is the bottom of the cave.
        Each rock is marked by its sequence number starting from 1, this
        improves debugging with `show_cave`.
        """

        cave = np.zeros((1000, WIDTH), dtype=np.int32)
        cave[0, :] = -10
        height = 0
        yield cave, height

        jet_moves = cycle(jet)
        for rock, rock_shape in zip(count(1), cycle(ROCK_SHAPES)):
            position = rock_init(height, rock_shape)
            cave = grow_cave(cave, position[1, 0])
            # show_cave(cave, add_rock=(position, rock), height=height + 8)
            # prompt(prompt=2)
            not_stuck = True
            while not_stuck:
                position = jet_move(cave, position, rock_shape, j := next(jet_moves))
                # d(position.flatten(), j, m="       jet")
                not_stuck, position = move_down(cave, position, rock_shape, mark=rock)
                # d(position.flatten(), not_stuck, m="moved down")
                # show_cave(cave, add_rock=(position, rock), height=height + 8)
                # prompt(prompt=2)

            # show_cave(cave, height=height + 8)
            # prompt(prompt=1)
            height = max(height, position[1, 0] - 1)
            yield cave, height

    def tower_size1(rocks):
        _, tower1 = last(take(rocks + 1, run()))
        return tower1

    def pecalculate_tower_size():
        cycle_divisor = math.lcm(len(jet), len(ROCK_SHAPES))
        d(cycle_divisor, m="cycle_divisor")

        fprs = []
        table = []
        for rock, (cave, height) in enumerate(run()):
            table.append(height)
            if rock and rock % cycle_divisor == 0:
                fpr = cave_fingerprint(cave, height)
                is_fpr = curry(array_equal)(fpr)
                d(rock, rock // cycle_divisor, height, m="rock cycle height")
                show_cave(fpr)
                prompt()
                if some(is_fpr, fprs) is not None:
                    break
                else:
                    fprs.append(fpr)

        start = ilen(takewhile(complement(is_fpr), fprs)) + 1
        end = rock // cycle_divisor
        d("cycle: divisors first second length", start, end, end - start)
        start_rocks = start * cycle_divisor
        d("start_rocks", start_rocks)
        d("start height", table[start_rocks])
        cycle_length = (end - start) * cycle_divisor
        cycle_growth = height - table[start_rocks]
        d("cycle_length", cycle_length)
        d("cycle_growth", cycle_growth)
        d("2nd cycle height", table[start_rocks + cycle_length])

        params = np.array([start_rocks, cycle_length, cycle_growth])
        np.savez_compressed("precalc17", cave=cave, table=table, params=params)

        def tower_size(rocks):
            if rocks < len(table):
                return table[rocks]
            else:
                cycles, steps = divmod(rocks - start_rocks, cycle_length)
                return cycles * cycle_growth + table[start_rocks + steps]

        return tower_size

    tower1 = tower_size1(ROCKS)
    yield tower1

    tower_size2 = pecalculate_tower_size()  # slow
    assert tower_size2(ROCKS) == tower1  # but this is instant now
    tower2 = tower_size2(ROCKS2)
    yield tower2

    # cycle: divisors first second length 39 51 12
    # start_rocks 1967745
    # start size 3120176
    # cycle_length 605460
    # cycle_growth 960069
    # 2nd cycle size 4080245
    #
    # 1585685264045
    # is too high

    # rock cycle size: 5953690 118 9440586
    # cycle: divisors first second length 59 118 59
    # start_rocks 2976845
    # start size 4720297
    # cycle_length 2976845
    # cycle_growth 4720289
    # 2nd cycle size 9440586
    #
    # 1585668383818
    # too low


if __name__ == "__main__":
    run_aoc(
        aoc17,
        transform=setup,
        np_printoptions=dict(
            linewidth=50, threshold=100000, formatter={"bool": "·#".__getitem__}
        ),
    )
