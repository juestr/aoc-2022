#!/usr/bin/env python3

""" A simple adaption of aoc20.py to Numpy

The code is very similar, yet elimination of the 2 loops adjusting
permutation values in mix yields a 13x speedup.
"""

import numpy as np

from aoc_util import run_aoc


def aoc20(numbers):
    def mix(xs, permutation=None):
        n = len(xs)
        if permutation is None:
            permutation = np.arange(n, dtype=int)
        for i, x in enumerate(xs):
            pos = permutation[i]
            newpos = (pos + x) % (n - 1)
            if newpos > pos:
                permutation[(pos < permutation) & (permutation <= newpos)] -= 1
            elif newpos < pos:
                permutation[(newpos <= permutation) & (permutation < pos)] += 1
            permutation[i] = newpos
        return permutation

    def permute(xs, permutation):
        mixed = np.empty_like(xs)
        mixed[permutation] = xs
        return mixed

    def sum_coord(xs):
        ([zero],) = np.nonzero(xs == 0)
        return np.sum(xs[(SOLUTION_OFFS + zero) % len(xs)])

    SOLUTION_OFFS = np.array([1000, 2000, 3000])
    permutation = mix(numbers)
    mixed = permute(numbers, permutation)
    yield sum_coord(mixed)

    DECRYPTION_KEY = 811589153
    encrypted = numbers * DECRYPTION_KEY
    permutation = None
    for _ in range(10):
        permutation = mix(encrypted, permutation)
    mixed = permute(encrypted, permutation)
    yield sum_coord(mixed)


if __name__ == "__main__":
    run_aoc(aoc20, read=(np.loadtxt, dict(dtype=int)))
