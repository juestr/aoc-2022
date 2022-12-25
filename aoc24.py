#!/usr/bin/env python3

import numpy as np
import scipy.sparse as sp
from funcy import lmap, map, partial

from aoc_util import np_raw_table, run_aoc


def aoc24(grid0):
    """Transform this to a static directed graph, incorporating time.

    Blizzards repeat in a predictable cycle, we'll have vertices for every
    grid cell in every point of time in this cycle, wrapping around to the
    start. We'll do most of the calculations with vertex indices this
    time.
    """

    def add_wrapping(x, y, mod):
        return (x // mod) * mod + (x + y) % mod

    def get_good_places():
        def run_blizzards(blizzards, offs, mod):
            return np.add(
                add_wrapping(blizzards[:, np.newaxis], offs * cycle_ar, mod),
                cycle_ar * size,
            ).reshape(-1)

        cycle_ar = np.arange(cycle)
        blizzards_nesw = [np.nonzero(grid.flat == kind)[0] for kind in map(ord, "^>v<")]
        all_blizzards = np.unique(
            np.hstack(lmap(run_blizzards, blizzards_nesw, offs_nesw, mod_nesw))
        )
        lmap
        all_grid_vertices = np.arange(size * cycle)
        return np.setdiff1d(all_grid_vertices, all_blizzards, assume_unique=True)

    def connect_grid(dest, offs, mod=1):
        src = dest - offs
        is_valid = src // mod == dest // mod
        return [add_wrapping(src[is_valid], -size, cycle * size), dest[is_valid]]

    def connect_special(base, grid_connect):
        connect_timeshifted = lambda a, b: [a, np.roll(b, -1)]
        base_idx = np.mgrid[base : base + cycle]
        grid_connect_idx = np.mgrid[grid_connect : grid_connect + size * cycle : size]
        base_waits = connect_timeshifted(base_idx, base_idx)
        base_to_grid = connect_timeshifted(base_idx, grid_connect_idx)
        grid_to_base = connect_timeshifted(grid_connect_idx, base_idx)
        return base_waits, base_to_grid, grid_to_base

    def shortest_path(graph, start, destination_zone):
        distances = sp.csgraph.dijkstra(graph, indices=start, min_only=True)
        idx = np.argmin(distances[destination_zone])
        length = int(distances[destination_zone][idx])
        return length, idx

    grid = grid0[1:-1, 1:-1]
    height, width = grid.shape
    size = grid.size
    cycle = np.lcm(height, width)
    graph_size = size * cycle + 2 * cycle  # (grid, start, end) x cycle
    start = graph_size - cycle * 2  # start of cycle-long slice
    end = graph_size - cycle  # start of cycle-long slice
    offs_nesw = np.array([-width, 1, width, -1])
    mod_nesw = np.array([size, width, size, width])

    start_col, end_col = (
        np.nonzero(g == ord("."))[0][0] - 1 for g in (grid0[0], grid0[-1])
    )
    good_places = get_good_places()
    grid_waits = connect_grid(good_places, 0)
    grid_moves = lmap(partial(connect_grid, good_places), offs_nesw, mod_nesw)
    connections = np.hstack(
        [
            grid_waits,
            *grid_moves,
            *connect_special(start, start_col),
            *connect_special(end, size - width + end_col),
        ]
    )
    graph = sp.csr_array(
        (np.ones(connections.shape[1]), connections),
        shape=(graph_size, graph_size),
    )
    length, idx = shortest_path(graph, start, np.s_[end : end + cycle])

    yield length

    length2, idx2 = shortest_path(graph, end + idx, np.s_[start : start + cycle])
    length3, idx3 = shortest_path(graph, start + idx2, np.s_[end : end + cycle])

    yield length + length2 + length3


if __name__ == "__main__":
    run_aoc(aoc24, transform=np_raw_table)
