#!/usr/bin/env python3

from functools import partial

import numpy as np
import pandas as pd

from aoc_util import run_aoc


def aoc09(df):
    MOVES = dict(R=1, L=-1, U=1j, D=-1j)
    moves = np.concatenate(
        ([0j], np.repeat(df[0].map(MOVES).to_numpy(), df[1].to_numpy()))
    )

    @partial(np.frompyfunc, nin=2, nout=1)
    def knot_move(tail: complex, head: complex) -> complex:
        diff = head - tail
        if abs(diff) >= 2:
            tail = tail + np.sign(diff.real) + np.sign(diff.imag) * 1j
        return tail

    head_path = np.add.accumulate(moves)
    tail_path = knot_move.accumulate(head_path)

    yield len(set(tail_path))

    path = tail_path
    for _ in range(8):
        path = knot_move.accumulate(path)

    yield len(set(path))


if __name__ == "__main__":
    run_aoc(
        aoc09,
        read=(pd.read_table, dict(header=None, sep=" ", dtype={0: "category", 1: int})),
    )
