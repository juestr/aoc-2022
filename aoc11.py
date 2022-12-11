#!/usr/bin/env python3

import operator as op
import re
from collections import deque
from dataclasses import dataclass
from math import lcm
from types import FunctionType

from aoc_util import d, run_aoc

monkey_re = re.compile(
    r"""Monkey (\d+):
\s*Starting items: ([\d, ]*)
\s*Operation: new = old (\+|\*) (\d+|old)
\s*Test: divisible by (\d+)
\s*If true: throw to monkey (\d+)
\s*If false: throw to monkey (\d+)""",
    flags=re.MULTILINE,
)


@dataclass
class Monkey:
    id: int
    items: deque[int]
    op: FunctionType
    test: int
    next: (int, int)
    inspections: int = 0

    @staticmethod
    def from_match(match, relief=1):
        groups = match.groups()
        _op = op.add if groups[2] == "+" else op.mul
        if groups[3] == "old":
            _op2 = lambda x: _op(x, x) // relief
        else:
            y = int(groups[3])
            _op2 = lambda x: _op(x, y) // relief
        return Monkey(
            id=int(groups[0]),
            items=deque(map(int, groups[1].split(", "))),
            op=_op2,
            test=int(groups[4]),
            next=(int(groups[6]), int(groups[5])),
        )

    def toss(self):
        item = self.items.popleft()
        worry = self.op(item)
        target = self.next[worry % self.test == 0]
        self.inspections += 1
        return worry, target

    def receive(self, item):
        self.items.append(item)


def aoc11(input):
    def create_monkeys(input, relief=1):
        return [Monkey.from_match(m, relief) for m in monkey_re.finditer(input)]

    def keep_away(monkeys, rounds, magic_factor=None):
        for _ in range(rounds):
            for monkey in monkeys:
                while monkey.items:
                    item, target = monkey.toss()
                    if magic_factor:
                        item %= magic_factor
                    monkeys[target].receive(item)
        d(monkeys, p=True)
        monkeys.sort(key=lambda m: m.inspections, reverse=True)
        return monkeys[0].inspections * monkeys[1].inspections

    monkeys = create_monkeys(input, relief=3)
    assert [m.id for m in monkeys] == list(range(len(monkeys)))

    yield keep_away(monkeys, 20)

    monkeys = create_monkeys(input, relief=1)
    magic_factor = lcm(*(monkey.test for monkey in monkeys))
    d("magic_factor", magic_factor)

    yield keep_away(monkeys, 10000, magic_factor)


if __name__ == "__main__":
    run_aoc(aoc11)
