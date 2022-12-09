#!/usr/bin/env python3

import numpy as np

from aoc_util import np_raw_table, run_aoc


def aoc08(field):
    h, w = field.shape

    _fwd_ = slice(1, ~0)
    _rev_ = slice(~1, 0, -1)
    fwd__ = slice(0, ~1)
    __rev = slice(~0, 1, -1)
    max_acc = np.maximum.accumulate
    visible = np.zeros(shape=(h - 2, w - 2), dtype=bool)
    # check visibility from up down right left
    visible |= field[_fwd_, _fwd_] > max_acc(field[fwd__, _fwd_], axis=0)
    visible |= (field[_rev_, _fwd_] > max_acc(field[__rev, _fwd_], axis=0))[::-1]
    visible |= field[_fwd_, _fwd_] > max_acc(field[_fwd_, fwd__], axis=1)
    visible |= (field[_fwd_, _rev_] > max_acc(field[_fwd_, __rev], axis=1))[:, ::-1]

    yield np.sum(visible) + h * 2 + w * 2 - 4

    def look(tree_height, along_row, along_col):
        line_of_sight = obstacles[tree_height, along_row, along_col]
        (obs_indices,) = np.nonzero(line_of_sight)
        return obs_indices[0] + 1 if obs_indices.size else line_of_sight.size

    def calc_score(row, col):
        tree_height = field[row, col]
        return (
            1  # at [row, col] outwards check tree_height up down right left
            * look(tree_height, slice(row + 1, None), col)
            * look(tree_height, slice(row - 1, None, -1), col)
            * look(tree_height, row, slice(col + 1, None))
            * look(tree_height, row, slice(col - 1, None, -1))
        )

    # lookup table: joined "tree of 0..9" <= "all field positions"
    obstacles = np.arange(10)[:, np.newaxis, np.newaxis] <= field
    calc_score_v = np.frompyfunc(calc_score, nin=2, nout=1)
    score = calc_score_v.outer(*np.ogrid[1 : h - 1, 1 : w - 1])

    yield max(score.flat)


if __name__ == "__main__":
    run_aoc(
        aoc08,
        transform=(np_raw_table, dict(offs=ord("0"))),
        time=(1000, "ms"),
    )
