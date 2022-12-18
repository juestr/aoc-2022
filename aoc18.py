#!/usr/bin/env python3

import numpy as np
import pandas as pd
from scipy.ndimage import binary_fill_holes

from aoc_util import run_aoc


def surface_area(voxel_idx, shape):
    # surface shape: orientation x y z
    surface = np.zeros((3, *(shape + 1)), dtype=np.int32)
    identity3 = np.identity(3, dtype=np.int32)
    for orientation in range(3):
        opposing_side_offset = identity3[:, orientation : orientation + 1]
        np.add.at(surface[orientation], tuple(voxel_idx), 1)
        np.add.at(
            surface[orientation],
            tuple(voxel_idx + opposing_side_offset[orientation]),
            1,
        )
    return np.sum(surface == 1)


def aoc18(df):
    assert df.min().min() >= 0
    shape = df.max().to_numpy() + 1
    voxel_idx = df.to_numpy().T

    yield surface_area(voxel_idx, shape)

    voxels = np.zeros(shape, dtype=bool)
    voxels[tuple(voxel_idx)] = 1
    voxels_filled = binary_fill_holes(voxels)
    voxel_filled_idx = np.array(np.nonzero(voxels_filled))

    yield surface_area(voxel_filled_idx, shape)


if __name__ == "__main__":
    run_aoc(aoc18, read=(pd.read_csv, dict(header=None)))
