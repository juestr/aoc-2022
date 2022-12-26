#!/usr/bin/env python3

import re

import numpy as np
from funcy import *

from aoc_util import d, np_condense, run_aoc


def setup(lines):
    *p1, _, p2 = lines
    width = max(map(len, p1))
    board = np.array([[ord(c) for c in l.ljust(width, " ")] for l in p1])
    moves = [m or int(d) for d, m in re_iter(r"(\d+)|(\D+)", p2, re.ASCII)]
    return board, moves


def aoc22(board, moves):
    def skip_empty(fwd):
        while board[*fwd] == EMPTY:
            fwd = (fwd + facing * BLOCKSIZE) % board.shape
        return fwd, facing

    def warp_3d(fwd):
        block, delta = divmod(fwd, BLOCKSIZE)
        dest, turns_r = block_trans.get((*block, facing_idx()), (block, 0))
        dest_facing = facing @ np.linalg.matrix_power(TURN_R, turns_r)
        dest_delta = delta
        for _ in range(turns_r):
            dest_delta = dest_delta @ TURN_R + [0, BLOCKSIZE - 1]
        return np.array(dest) * BLOCKSIZE + dest_delta, dest_facing

    def do(cmd, cross_block):
        nonlocal pos, facing
        match cmd:
            case "R":
                facing = facing @ TURN_R
            case "L":
                facing = facing @ TURN_L
            case int(dist):
                for _ in range(dist):
                    fwd_dir = facing
                    fwd = (pos + fwd_dir) % board.shape
                    if np.any(pos // BLOCKSIZE != fwd // BLOCKSIZE):
                        fwd, fwd_dir = cross_block(fwd)
                    if board[*fwd] == WALL:
                        return
                    pos, facing = fwd, fwd_dir

    def facing_idx():
        return ilen(
            takewhile(
                lambda x: np.any(x != facing),
                iterate(lambda x: np.matmul(x, TURN_R), EAST),
            )
        )

    def get_trans_tbl():
        # yeah it's hardcoded
        if BLOCKSIZE == 4:
            return {
                (0, 0, 3): ((0, 2), 2),
                (0, 1, 2): ((1, 1), 3),
                (0, 1, 3): ((0, 2), 1),
                (0, 3, 0): ((2, 3), 2),
                (0, 3, 2): ((1, 0), 3),
                #
                (1, 3, 0): ((2, 3), 1),
                (1, 3, 3): ((1, 2), 3),
                #
                (2, 0, 1): ((2, 2), 2),
                (2, 0, 0): ((0, 2), 2),
                (1, 1, 1): ((2, 2), 3),
                (1, 1, 2): ((1, 1), 1),
                #
                (0, 2, 1): ((1, 0), 2),
                (2, 2, 3): ((1, 0), 2),
            }
        elif BLOCKSIZE == 50:
            return {
                (0, 0, 0): ((2, 1), 2),  # conn 0
                (0, 0, 1): ((0, 2), 0),  # conn 1
                (0, 0, 2): ((2, 0), 2),  # conn 2
                #
                (1, 0, 2): ((2, 0), 3),  # conn 3
                (1, 0, 3): ((1, 1), 1),  # conn 3
                (1, 2, 0): ((0, 2), 3),  # conn 4
                (1, 2, 1): ((1, 1), 1),  # conn 4
                #
                (2, 2, 0): ((0, 2), 2),  # conn 0
                (2, 2, 2): ((0, 1), 2),  # conn 2
                #
                (3, 1, 0): ((2, 1), 3),  # conn 5
                (3, 1, 1): ((3, 0), 1),  # conn 5
                (3, 1, 3): ((3, 0), 1),  # conn 6  1
                (3, 2, 2): ((0, 1), 3),  # conn 6
                (3, 2, 3): ((3, 0), 0),  # conn 1
            }
        else:
            assert False, "unexpected input"

    def result():
        return np.dot([*pos + 1, facing_idx()], [1000, 4, 1])

    def show_board():
        with np.printoptions(linewidth=500, threshold=100000, formatter={"int": chr}):
            d(np_condense(board))

    show_board()
    d(moves, "\n")
    OPEN, WALL, EMPTY = (ord(c) for c in ".# ")
    TURN_R = np.array([[0, -1], [1, 0]])
    TURN_L = TURN_R @ TURN_R @ TURN_R
    EAST = np.array([0, 1])
    BLOCKSIZE = 4 if board.shape[0] < 50 else 50

    # "global" position and facing direction for turtle-like procedures
    facing = EAST
    pos = pos0 = np.array([0, np.nonzero(board[0] == OPEN)[0][0]])

    for move in moves:
        do(move, cross_block=skip_empty)
        d(str(move).rjust(3), "->", pos, facing)

    yield result()

    facing = EAST
    pos = pos0
    block_trans = get_trans_tbl()
    for move in moves:
        do(move, cross_block=warp_3d)
        d(str(move).rjust(3), "->", pos, facing)

    yield result()


if __name__ == "__main__":
    run_aoc(aoc22, transform=setup, split="lines")
