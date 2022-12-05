#!/usr/bin/env python3

import numpy as np
import pandas as pd

from aoc_util import d, run_aoc


def aoc04(df):
    d(df)
    a1, b1, a2, b2 = (df[col].to_numpy() for col in df.columns)

    includes = lambda a1, b1, a2, b2: (a1 <= a2) & (a2 <= b1) & (b2 <= b1)

    yield np.sum(includes(a1, b1, a2, b2) | includes(a2, b2, a1, b1))

    yield np.sum((a1 <= b2) & (a2 <= b1))


if __name__ == "__main__":
    run_aoc(aoc04, read=(pd.read_table, dict(header=None, sep="[,-]", engine="python")))
