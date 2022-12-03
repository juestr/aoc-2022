#!/usr/bin/env python3

import numpy as np
import pandas as pd
from runner import run_aoc, d, pd_table

def aoc02(strategy: pd.DataFrame):
    elf = strategy['elf'].cat.codes.to_numpy()
    you = strategy['you'].cat.codes.to_numpy()
    score = 1 + you + 3 * (you == elf) + 6 * (you == (elf + 1) % 3)
    d('elf  ', elf)
    d('you  ', you)
    d('score', score)

    yield np.sum(score)

    win2 = you
    you2 = (elf + win2 - 1) % 3
    score2 = 1 + you2 + 3 * win2
    d('elf   ', elf)
    d('win2  ', win2)
    d('you2  ', you2)
    d('score2', score2)

    yield np.sum(score2)


if __name__ == '__main__':
    run_aoc(aoc02, read=(pd_table, ('elf', 'you'), 'category'))
