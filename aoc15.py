#!/usr/bin/env python3

import re
from typing import Generator

import numpy as np
from funcy import lmap

from aoc_util import d, run_aoc


def setup(lines: list[str]):
    # Note: the official inputs were extended by a 3 line header
    # giving the extra numbers specified in the text and varying
    # between the official mission and the smaller example.
    convert = lambda line: lmap(int, re.findall("=(\-?\d+)", line))
    ([target_row], [xy_limit], _, *data) = lmap(convert, lines)
    return (*np.array(data, dtype=np.int32).T, target_row, xy_limit)


def aoc15(
    sensor_x: np.ndarray,
    sensor_y: np.ndarray,
    beacon_x: np.ndarray,
    beacon_y: np.ndarray,
    target_row: int,
    xy_limit: int,
) -> Generator[int, None, None]:
    def x_ranges_by_sensor(rows):
        xlength = sensor_beacon_dist - np.abs(np.subtract.outer(rows, sensor_y))
        is_in_range = xlength >= 0
        left = sensor_x - xlength
        right = sensor_x_p1 + xlength
        for y, l, r, select in zip(rows, left, right, is_in_range):
            yield y, sorted(zip(l[select], r[select]))

    def len_covered(ranges):
        if not ranges:
            return 0
        else:
            head = ranges[0][0]
            covered = 0
            for x0, x1 in ranges:
                covered += max(head, x1) - max(head, x0)
                head = max(head, x1)
            return covered

    sensor_x_p1 = sensor_x + 1
    sensor_beacon_dist = np.abs(beacon_x - sensor_x) + np.abs(beacon_y - sensor_y)
    [(_, x_ranges)] = x_ranges_by_sensor([target_row])
    beacons = len(set(beacon_x[beacon_y == target_row]))
    not_beacons = len_covered(x_ranges) - beacons

    yield not_beacons

    def first_uncovered(ranges, head=0):
        for x0, x1 in ranges:
            if x0 > head:
                return head
            else:
                head = max(head, x1)
        return head

    def tuning_freq(blocksize=10_000):
        for block in range(0, xy_limit + 1, blocksize):
            if block % 100_000 == 0:
                d(block, m="progress y")
            rows = np.arange(blocksize, dtype=np.int32) + block
            for y, x_ranges in x_ranges_by_sensor(rows):
                distress_x = first_uncovered(x_ranges)
                if distress_x <= xy_limit:
                    return distress_x * 4000000 + y

    yield tuning_freq()


if __name__ == "__main__":
    run_aoc(aoc15, split="lines", transform=setup)
