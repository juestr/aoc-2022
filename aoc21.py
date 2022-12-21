#!/usr/bin/env python3

import operator as op
from functools import cache, partial

from funcy import fallback
from sympy import Eq, S, solve, symbols, sympify

from aoc_util import run_aoc


def parse(line):
    monkey, job = line.split(": ")
    return monkey, fallback(partial(int, job), job.split)


def aoc21(monkey_jobs):
    OPS = {"+": op.add, "-": op.sub, "*": op.mul, "/": op.floordiv}
    tasks = dict(monkey_jobs)

    @cache
    def calc(name):
        match tasks[name]:
            # fmt: off
            case int(i):       return i
            case (a, op, b):   return OPS[op](calc(a), calc(b))
            # fmt: on

    yield calc("root")

    @cache
    def expr(name):
        match name, tasks[name]:
            # fmt: off
            case "humn", _:        return humn
            case _, int(i):        return sympify(i)
            case _, (a, op, b):    return OPS2[op](expr(a), expr(b))
            # fmt: on

    OPS2 = OPS | ({"/": op.truediv})
    humn = symbols("humn", integers=True)
    root_left, _, root_right = tasks["root"]
    root = Eq(expr(root_left), expr(root_right))
    [result] = solve(root, humn, domain=S.Integers)

    yield result


if __name__ == "__main__":
    run_aoc(aoc21, split="lines", apply=parse, time=(1000, "ms"))
