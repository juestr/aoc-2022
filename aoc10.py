#!/usr/bin/env python3

import numpy as np
import pandas as pd

from aoc_util import run_aoc


def aoc10(df):
    def emit_signal():
        x = 1
        yield x
        for _, cmd, v in df.itertuples():
            if cmd == "addx":
                yield x
                x += v
            yield x

    signal = np.array(list(emit_signal()))[:240]
    signal_strength = np.dot(signal[19::40], np.ogrid[20:240:40])

    yield signal_strength

    idx = np.arange(240) % 40
    screen = np.logical_and(signal - 1 <= idx, idx <= signal + 1)

    with np.printoptions(linewidth=100, formatter={"bool": "·#".__getitem__}):
        yield str(screen.reshape(-1, 40))


if __name__ == "__main__":
    run_aoc(
        aoc10,
        read=(
            pd.read_table,
            dict(header=None, sep=" ", dtype={0: "category", 1: "Int8"}),
        ),
        time=(1000, "ms"),
    )
