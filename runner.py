
'''AOC puzzle solving tools'''

from argparse import ArgumentParser
import logging
import timeit
import os
from logging import error, warning, info, debug

def _fix_lambda(f):
    match f:
        case (f, *args, kw) if isinstance(kw, dict):
            return lambda input: f(input, *args, **kw)
        case (f, *args):
            return lambda input: f(input, *args)
        case _:
            return f

def d(*args, s=' ', r=False):
    '''Simple logging.debug helper'''

    debug(s.join(('%'+'sr'[r],) * len(args)), *args)

def readfile(fn):
    '''Default input reader'''

    with open(fn) as fd:
        return fd.read()

def pd_table(fn, names=None, dtype=None, header=None, delim_whitespace=True, **kw):
    import pandas as pd
    return pd.read_table(fn, names=names, dtype=dtype,
        header=header, delim_whitespace=delim_whitespace, **kw)

def np_ascii_table(input, dtype='uint8'):
    '''Transform str table to a 2d np.array of ASCII values'''

    import numpy as np
    l = input.index('\n')
    flat = np.fromstring(input, dtype=dtype)
    return flat.reshape((-1, l+1))[:, :-1]

def run_aoc(aocf, /, time=(1, 's'), read=readfile, split=None, apply=None):
    '''Runs puzzle solving generator function aocf

    Name of aocf needs to end in 2 digits giving the AOC day.
    Will provide possibly transformed input as argument (read, split, apply)
    Should yield its results.
    See --help for options taken from command line.
    '''

    t0 = t1 = timeit.default_timer()
    def print_lap_time(label='Time: '):
        nonlocal t0, t1
        if cmdargs.timeit:
            t0, t1 = t1, timeit.default_timer()
            print(f'{label}{(t1-t0)*time[0]:_.3f}{time[1]}')

    n = int(aocf.__name__[-2:])
    session = os.environ.get('SESSION')
    loglevel = os.environ.get('LOGLEVEL', 'INFO').upper()

    parser = ArgumentParser(description = f'Run AOC example {n}')
    parser.add_argument('--input', default=f'aoc{n:02}_input.txt',
        help=f'input file to read (aoc{n:02}_input.txt)')
    parser.add_argument('--example', action='store_const',
        dest='input', const=f'aoc{n:02}_example.txt',
        help=f'read input from aoc{n:02}_example.txt')
    parser.add_argument('--expect', action='append', default=[],
        help='check expected result (multiple)')
    parser.add_argument('--timeit', action='store_true', default=False,
        help='show timing information')
    parser.add_argument('--loglevel', default=loglevel,
        choices=['CRITICAL, ERROR', 'WARNING', 'INFO', 'DEBUG'],
        help='log level, overrides $LOGLEVEL')
    cmdargs = parser.parse_args()
    cmdargs.expect.reverse()

    logging.basicConfig(encoding='utf-8',
        format='%(message)s', level=getattr(logging, cmdargs.loglevel))

    input = _fix_lambda(read)(cmdargs.input)
    match split:
        case None:      pass
        case True:      input = input.split()
        case 'lines':   input = input.splitlines()
        case 'matrix':  input = [line.split() for line in input.splitlines()]
        case c:         input = input.split(c)
    if apply:
        apply = _fix_lambda(apply)
        match split:
            case None:      input = apply(input)
            case 'matrix':  input = [[apply(x) for x in row] for row in input]
            case _:         input = [apply(x) for x in input]

    print()
    print_lap_time('### Setup time: ')
    print()

    for i, r in enumerate(aocf(input), start=1):
        print(f'\n### Result {i} of {aocf.__name__}():\n\n{r}\n')
        if cmdargs.expect:
            expected = cmdargs.expect.pop()
            if str(r) == expected:
                print('✅ matches the expected value\n')
            else:
                print(f'❌ does not match {expected}\n')
        print_lap_time('### Result time: ')
        print()

    logging.shutdown()
