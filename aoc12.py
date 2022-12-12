#!/usr/bin/env python3

from functools import partial

import numpy as np
from scipy.sparse import dok_array
from scipy.sparse.csgraph import dijkstra

from aoc_util import d, np_raw_table, run_aoc


def aoc12(grid):
    flatten_index = partial(np.ravel_multi_index, dims=grid.shape)

    start, goal = (np.nonzero(grid == ord(loc)) for loc in "SE")
    grid[start] = ord("a")
    grid[goal] = ord("z")
    d(start, goal, grid, s="\n", t="start goal grid")

    graph = dok_array((grid.size, grid.size), dtype=np.uint8)
    vertices = np.arange(grid.size).reshape(grid.shape)
    # fmt: off
    left  = vertices[ :  ,  :-1].flatten()
    right = vertices[ :  , 1:  ].flatten()
    upper = vertices[ :-1,  :  ].flatten()
    lower = vertices[1:  ,  :  ].flatten()
    # fmt: on
    for side1, side2 in [(left, right), (right, left), (upper, lower), (lower, upper)]:
        connected = grid.flat[side1] + 1 >= grid.flat[side2]
        graph[(side1[connected], side2[connected])] = 1
    d(graph, m="graph", p=1)

    distances = dijkstra(graph, indices=flatten_index(start), min_only=True)
    d(distances.reshape(grid.shape).astype(np.uint16), t="distances")
    distance_to_goal = int(distances[flatten_index(goal)])

    yield distance_to_goal

    start2 = np.nonzero(grid == ord("a"))
    distances2 = dijkstra(graph, indices=flatten_index(start2), min_only=True)
    d(distances2.reshape(grid.shape).astype(np.uint16), t="distances2")
    distance_to_goal2 = int(distances2[flatten_index(goal)])

    yield distance_to_goal2


if __name__ == "__main__":
    run_aoc(
        aoc12,
        transform=np_raw_table,
        np_printoptions=dict(linewidth=120, threshold=5000, edgeitems=10),
    )
