#!/usr/bin/env python3

import numpy as np
import scipy.ndimage as ndi
from funcy import count, cycle, take

from aoc_util import d, np_condense, run_aoc

# convolvement kernels to filter proposing elfs
k_north = np.array([-9, -9, -9, 1, 30, 1, 1, 1, 1][::-1], dtype=np.int8).reshape(3, 3)
k_west = np.rot90(k_north)
k_south = np.rot90(k_west)
k_east = np.rot90(k_south)

DIRECTIONS = [k_north, k_south, k_west, k_east]
SHIFTS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def setup(lines):
    return (np.array([[c == "#" for c in line] for line in lines]),)


def show(grid, t=None):
    with np.printoptions(
        linewidth=500,
        threshold=50000,
        formatter={"bool": "·#".__getitem__, "int": lambda i: str(i) if i else "·"},
    ):
        d(np_condense(grid), t=t)


def do_round(grid, director):
    def pad(grid):
        return np.pad(
            grid,
            [[np.any(x) * 10 for x in (g[0], g[-1])] for g in (grid, grid.T)],
        )

    def get_proposals():
        active = grid.copy()
        for kernel, _ in take(4, director):
            proposal = ndi.convolve(grid.astype(np.int8), kernel) >= 31
            proposal &= active
            active &= np.logical_not(proposal)
            yield proposal

    def get_valid(proposals):
        merge = np.zeros_like(grid, dtype=np.int8)
        for proposal, (_, shift) in zip(proposals, director):
            merge += np.roll(proposal, shift=shift, axis=(0, 1))
        return merge == 1

    def update(grid, proposals, valid_mask):
        for proposal, (_, shift) in zip(proposals, director):
            proposal &= np.roll(valid_mask, shift=-shift, axis=(0, 1))
            grid ^= proposal
        grid |= valid_mask
        return grid

    grid = pad(grid)
    proposals = list(get_proposals())
    valid_mask = get_valid(proposals)
    if not np.any(valid_mask):
        return grid, False
    else:
        return update(grid, proposals, valid_mask), True


def result1(grid):
    nz = np.array(np.nonzero(grid))
    shape = np.max(nz, axis=1) - np.min(nz, axis=1) + 1
    return np.product(shape) - np.sum(grid)


def aoc23(grid0):
    grid = grid0.copy()
    show(grid)
    director = cycle(zip(DIRECTIONS, map(np.array, SHIFTS)))
    for i in range(10):
        grid, _ = do_round(grid, director)
        next(director)
        show(grid, t=i)
    yield result1(grid)

    grid = grid0.copy()
    director = cycle(zip(DIRECTIONS, map(np.array, SHIFTS)))
    for n in count(1):
        grid, changed = do_round(grid, director)
        if not changed:
            show(grid, t="final")
            break
        next(director)
    yield n


if __name__ == "__main__":
    run_aoc(aoc23, split="lines", transform=setup)
