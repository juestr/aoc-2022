#!/usr/bin/env python3

import re

import numpy as np
from funcy import *

from aoc_util import d, np_condense, run_aoc


class tiles:
    OPEN, WALL, WARP = (ord(c) for c in ".# ")


RIGHT = np.array([0, 1])
TURN_R = np.array([[0, -1], [1, 0]])
TURN_L = TURN_R @ TURN_R @ TURN_R


def setup(lines):
    *p1, _, p2 = lines
    width = max(map(len, p1))
    board = np.array([[ord(c) for c in l.ljust(width, " ")] for l in p1])
    moves = [m or int(d) for d, m in re_iter(r"(\d+)|(\D+)", p2, re.ASCII)]
    return board, moves


def aoc22(board, moves):
    def forward(dist):
        nonlocal pos
        for _ in range(dist):
            fwd = (pos + facing) % board.shape
            match board[*fwd]:
                case tiles.WALL:
                    return
                case tiles.WARP:
                    while board[*fwd] == tiles.WARP:
                        fwd = (fwd + facing) % board.shape
                    if board[*fwd] == tiles.WALL:
                        return
            pos = fwd

    def do(cmd):
        nonlocal facing
        match cmd:
            case "R":
                facing = facing @ TURN_R
            case "L":
                facing = facing @ TURN_L
            case int():
                forward(cmd)

    def facing_idx():
        return ilen(
            takewhile(
                lambda x: np.any(x != facing),
                iterate(lambda x: np.matmul(x, TURN_R), RIGHT),
            )
        )

    def result():
        d(facing_idx())
        return np.dot([*pos + 1, facing_idx()], [1000, 4, 1])

    def show_board():
        with np.printoptions(linewidth=500, threshold=100000, formatter={"int": chr}):
            d(np_condense(board))

    show_board()
    d(moves)
    facing = RIGHT
    ([col, *_],) = np.nonzero(board[0] == tiles.OPEN)
    pos = np.array([0, col])
    for move in moves:
        do(move)
        d(move, pos, facing)

    yield result()

    def forward(dist):
        nonlocal pos
        for _ in range(dist):
            fwd = (pos + facing) % board.shape
            match board[*fwd]:
                case tiles.WALL:
                    return
                case tiles.WARP:
                    if
            pos = fwd

    def do(cmd):
        nonlocal facing
        match cmd:
            case "R":
                facing = facing @ TURN_R
            case "L":
                facing = facing @ TURN_L
            case int():
                forward(cmd)

    BLOCKSIZE = 4 if board.shape[0] < 50 else 50
    facing = RIGHT
    ([col, *_],) = np.nonzero(board[0] == tiles.OPEN)
    pos = np.array([0, col])
    for move in moves:
        do(move)
        d(move, pos, facing)



    # yield 2


if __name__ == "__main__":
    run_aoc(aoc22, transform=setup, split="lines")
