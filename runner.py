
from argparse import ArgumentParser
import logging
import timeit
import os
from logging import error, warning, info, debug

def run_aoc(f, /, time=(1, 's'), split=None, conv=None):
    t0 = t1 = timeit.default_timer()
    def print_lap_time(label='Time: '):
        nonlocal t0, t1
        if args.timeit:
            t0, t1 = t1, timeit.default_timer()
            print(f'{label}{(t1-t0)*time[0]:_.3f}{time[1]}')

    n = int(f.__name__[-2:])
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
    # parser.add_argument('--submit', type=int, default=0,
    #     help='submit result 1|2 using $SESSION' + ('' if session else ' (not set)'))
    args = parser.parse_args()
    args.expect.reverse()

    logging.basicConfig(encoding='utf-8',
        format='%(message)s', level=getattr(logging, args.loglevel))

    with open(args.input) as fd:
        input = fd.read()
    match split:
        case None:      pass
        case ():        input = input.split()
        case 'lines':   input = input.splitlines()
        case c:         input = input.split(c)
    if conv:
        input = [conv(x) for x in input] if split is not None else conv(input)

    print_lap_time('Setup time: ')

    for i, r in enumerate(f(input), start=1):
        print(f'\n### Result {i} of {f.__name__}():\n\n{r}\n')
        if args.expect:
            expected = args.expect.pop()
            if str(r) == expected:
                print('✅ matches the expected value\n')
            else:
                print(f'❌ does not match {expected}\n')
        print_lap_time()
        print()

    logging.shutdown()
