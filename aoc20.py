#!/usr/bin/env python3

from aoc_util import run_aoc


def setup(lines):
    return ([int(l) for l in lines],)


def aoc20(numbers):
    def mix(xs, permutation=None):
        n = len(xs)
        permutation = permutation or list(range(n))
        for i, x in enumerate(xs):
            pos = permutation[i]
            newpos = (pos + x) % (n - 1)
            if newpos > pos:
                for j in range(len(permutation)):
                    permutation[j] -= pos < permutation[j] <= newpos
            elif newpos < pos:
                for j in range(len(permutation)):
                    permutation[j] += newpos <= permutation[j] < pos
            permutation[i] = newpos
        return permutation

    def permute(xs, permutation):
        mixed = [0] * len(xs)
        for i, p in enumerate(permutation):
            mixed[p] = xs[i]
        return mixed

    def sum_coord(xs):
        n = len(xs)
        zero = xs.index(0)
        return sum(xs[(zero + i) % n] for i in (1000, 2000, 3000))

    permutation = mix(numbers)
    mixed = permute(numbers, permutation)
    yield sum_coord(mixed)

    DECRYPTION_KEY = 811589153
    encrypted = [x * DECRYPTION_KEY for x in numbers]
    permutation = None
    for _ in range(10):
        permutation = mix(encrypted, permutation)
    mixed = permute(encrypted, permutation)
    yield sum_coord(mixed)


if __name__ == "__main__":
    run_aoc(aoc20, split="lines", transform=setup)
