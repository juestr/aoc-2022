#!/usr/bin/env python3

import operator as op
import re
from collections import deque
from dataclasses import dataclass
from math import lcm
from types import FunctionType

from aoc_util import d, run_aoc


@dataclass
class Monkey:
    id: int
    items: deque[int]
    op: FunctionType
    test: int
    next: (int, int)
    inspections: int = 0

    def toss(self, relief=1):
        item = self.items.popleft()
        worry = self.op(item) // relief
        target = self.next[worry % self.test == 0]
        self.inspections += 1
        return worry, target

    def receive(self, item):
        self.items.append(item)


class Monkeys(list):

    _re = re.compile(
        r"""Monkey (\d+):
\s*Starting items: ([\d, ]*)
\s*Operation: new = old (\+|\*) (\d+|old)
\s*Test: divisible by (\d+)
\s*If true: throw to monkey (\d+)
\s*If false: throw to monkey (\d+)""",
        flags=re.MULTILINE,
    )

    @staticmethod
    def from_str(text):
        def from_match(match):
            groups = match.groups()
            _op = op.add if groups[2] == "+" else op.mul
            if groups[3] == "old":
                _op2 = lambda x: _op(x, x)
            else:
                y = int(groups[3])
                _op2 = lambda x: _op(x, y)
            return Monkey(
                id=int(groups[0]),
                items=deque(map(int, groups[1].split(", "))),
                op=_op2,
                test=int(groups[4]),
                next=(int(groups[6]), int(groups[5])),
            )

        monkeys = Monkeys(map(from_match, Monkeys._re.finditer(text)))
        assert [m.id for m in monkeys] == list(range(len(monkeys)))
        return monkeys

    def keep_away(self, rounds, relief=1):
        if relief == 1:
            magic_factor = lcm(*(monkey.test for monkey in self))
            d("magic_factor", magic_factor)
        else:
            magic_factor = None
        for _ in range(rounds):
            for monkey in self:
                while monkey.items:
                    item, target = monkey.toss(relief)
                    if magic_factor:
                        item %= magic_factor
                    self[target].receive(item)
        self.sort(key=lambda m: m.inspections, reverse=True)
        d(self, p=True, t="end of game:")
        return self[0].inspections * self[1].inspections


def aoc11(input):
    yield Monkeys.from_str(input).keep_away(20, relief=3)
    yield Monkeys.from_str(input).keep_away(10000, relief=1)


if __name__ == "__main__":
    run_aoc(aoc11)
