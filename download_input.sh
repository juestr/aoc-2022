#!/usr/bin/env bash

if [ -z "$SESSION" ] ; then
  echo "export SESSION= missing (cookie from browser)"
  exit 1
fi
if [ -z "$1" ] ; then
  echo "Provide a number"
  exit 1
fi

fn=`printf 'aoc%02d.py' $1`
if [ -e "$fn" ] ; then
  echo "$fn already exists"
else
  echo "Creating skeleton $fn"
  printf "#!/usr/bin/env python3

from itertools import pairwise
from more_itertools import chunked
import numpy as np
import pandas as pd
from aoc_util import run_aoc, error, info, debug, d, np_raw_table

def aoc%02d(input):


    yield 1

    yield 2


if __name__ == '__main__':
    run_aoc(aoc%02d)
#    run_aoc(aoc%02d, split='lines', apply=int)
#    run_aoc(aoc%02d, apply=(np_ascii_table, dict(dtype=np.int8)))
# run_aoc(
#     aoc%02d,
#     read=(pd.read_table, dict(header=None, header=(), sep="[,-]", delim_whitespace=True)),
# )
" $1 $1 $1 $1 > $fn
chmod 755 $fn
fi

fn=`printf 'data/aoc%02d_example.txt' $1`
echo "Touching $fn"
touch $fn
fn=`printf 'data/aoc%02d_example.txt.results' $1`
echo "Touching $fn"
touch $fn
fn=`printf 'data/aoc%02d_input.txt.results' $1`
echo "Touching $fn"
touch $fn

fn=`printf 'data/aoc%02d_input.txt' $1`
echo "Downloading input for day <$1> to $fn"
curl --cookie session=${SESSION} "https://adventofcode.com/2022/day/$1/input" > $fn || ( echo "download failed" && exit 1 )
