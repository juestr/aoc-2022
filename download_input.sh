#!/usr/bin/env bash

if [ -z "$SESSION" ] ; then
  echo "export SESSION= missing"
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
from more-itertools import chunked
import numpy as np
import pandas as pd
from runner import run_aoc, error, info, debug, d, pd_table, np_ascii_table

def aoc%02d(input):


    yield 1

    yield 2


if __name__ == '__main__':
    run_aoc(aoc%02d)
#    run_aoc(aoc%02d, split='lines', apply=int)
#    run_aoc(aoc%02d, apply=(np_ascii_table, dict(dtype=np.int8)))
#    run_aoc(aoc%02d, read=(pd_table, dict(names=('elf', 'you'), dtype='category')))
" $1 $1 $1 $1 > $fn
chmod 755 $fn
fi

fn=`printf 'aoc%02d_example.txt' $1`
echo "Touching $fn"
touch $fn

fn=`printf 'aoc%02d_input.txt' $1`
echo "Downloading input for day <$1> to $fn"
curl --cookie session=${SESSION} "https://adventofcode.com/2022/day/$1/input" | tee $fn || ( echo "something failed" && exit 1 )
