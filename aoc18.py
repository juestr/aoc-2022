#!/usr/bin/env python3

import numpy as np
import pandas as pd
from scipy.ndimage import binary_fill_holes

from aoc_util import run_aoc

VOXEL_SURFACE_OFFSETS = np.array(
    [  # columns are the 6 surfaces of a voxel at x y z
        [0, 1, 2, 0, 1, 2],  # orientation x=0, y=1, z=2
        [0, 0, 0, 1, 0, 0],  # x-offset
        [0, 0, 0, 0, 1, 0],  # y-offset
        [0, 0, 0, 0, 0, 1],  # z-offset
    ],
    dtype=np.int32,
)
ADD_ORIENTATION = np.identity(4, dtype=np.int32)[:, 1:]


def surface_area(voxel_idx, world_shape):
    # of shape+1 with orientation dimension (0-2) prefixed
    surface = np.zeros((3, *(world_shape + 1)), dtype=np.int32)
    # (orientation x y z) x 6n for voxel_idx of shape (x y z) x n
    surface_idx = np.add(
        (ADD_ORIENTATION @ voxel_idx)[:, np.newaxis, :],
        VOXEL_SURFACE_OFFSETS[:, :, np.newaxis],
    ).reshape(4, -1)
    np.add.at(surface, tuple(surface_idx), 1)
    return np.sum(surface == 1)


def aoc18(df):
    assert df.min().min() >= 0
    world_shape = df.max().to_numpy() + 1
    voxel_idx = df.to_numpy().T

    yield surface_area(voxel_idx, world_shape)

    voxels = np.zeros(world_shape, dtype=bool)
    voxels[tuple(voxel_idx)] = 1
    voxels_filled = binary_fill_holes(voxels)
    voxel_filled_idx = np.array(np.nonzero(voxels_filled))

    yield surface_area(voxel_filled_idx, world_shape)


if __name__ == "__main__":
    run_aoc(aoc18, read=(pd.read_csv, dict(header=None)), time=(1000, "ms"))
