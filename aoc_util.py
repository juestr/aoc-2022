"""AOC puzzle solving support"""

import logging
import os
import sys
import timeit
from argparse import ArgumentParser
from logging import debug, error, info, warn

_keep_imports = error, warn, info, debug  # re-export
_root_logger = logging.getLogger()


def _fix_lambda(f):
    match f:
        case None:
            return lambda x: x
        case (f, *args, kw) if isinstance(kw, dict):
            return lambda input: f(input, *args, **kw)
        case (f, *args):
            return lambda input: f(input, *args)
        case _:
            return f


def d(*args, s=" ", r=False, p=False, m="", t="", l=logging.DEBUG):
    """Simple logging.debug helper"""
    if p:
        from pprint import pformat  # noqa: autoimport

        if s == " ":
            s = "\n"
    if _root_logger.isEnabledFor(l):
        logging.log(
            l,
            (t + ":\n" if t else "")
            + (m + ":" + s if m else "")
            + s.join(("%" + "sr"[r],) * len(args)),
            *(map(pformat, args) if p else args),
        )


def readfile(fn):
    """Default input reader"""
    with open(fn) as fd:
        return fd.read()


def np_raw_table(input, dtype="uint8", offs=0):
    """Transform raw tabular data to a 2d np.array"""
    import numpy as np  # noqa: autoimport

    l = input.index("\n")
    flat = np.fromstring(input, dtype=dtype)
    return (flat.reshape((-1, l + 1))[:, :-1] - offs,)


def mk_input_reader(read=readfile, split=None, apply=None, transform=None):
    """Returns a function reading and transforming an input file"""

    def get_input(filename):
        input = read(filename)
        match split:
            case None:
                pass
            case "fields":
                input = [apply(x) for x in input.split()]
            case "lines":
                input = [apply(x) for x in input.splitlines()]
            case "lines_fields":
                input = [
                    tuple(apply(x) for x in line.split()) for line in input.splitlines()
                ]
            case c:
                input = [apply(x) for x in input.split(c)]
        if transform:
            return transform(input)
        else:
            return (input,)

    read = _fix_lambda(read)
    apply = _fix_lambda(apply)
    transform = _fix_lambda(transform)
    return get_input


def mk_parser(day: int, loglevel):
    parser = ArgumentParser(description=f"Run AOC example {day}")
    parser.add_argument(
        "--input",
        default=f"data/aoc{day:02}_input.txt",
        help=f"input file to read (data/aoc{day:02}_input.txt)",
    )
    parser.add_argument(
        "--example",
        action="store_const",
        dest="input",
        const=f"data/aoc{day:02}_example.txt",
        help=f"read input from data/aoc{day:02}_example.txt",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        default=False,
        help="test against <input>.results",
    )
    parser.add_argument(
        "--expect", action="append", default=[], help="check expected result (multiple)"
    )
    parser.add_argument(
        "--write-results",
        action="store_true",
        default=False,
        help="create <input>.results",
    )
    parser.add_argument(
        "--timeit", action="store_true", default=False, help="show timing information"
    )
    parser.add_argument(
        "--loglevel",
        default=loglevel,
        choices=["OFF", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="log level, overrides $LOGLEVEL",
    )
    return parser


def run_aoc(
    aocf,
    *,
    read=readfile,
    split=None,
    apply=None,
    transform=None,
    time=(1, "s"),
    np_printoptions=None,
):
    """Runs puzzle solving generator function aocf

    The name of aocf needs to end in 2 digits giving the AOC day.

    An input file is read, optionally split into lines and/or fields which
    are mapped by appy, then finally passed through transform and provided
    as multiple arguments to aocf.

    The aocf function should yield its results.

    See --help for options taken from command line.
    """

    def lap_time(label="Time: "):
        nonlocal t1, t2
        if cmdargs.timeit:
            t1, t2 = t2, timeit.default_timer()
            info(f"{label}{(t2-t1)*time[0]:_.3f}{time[1]}")

    def total_time(label="Total time: "):
        if cmdargs.timeit:
            t = timeit.default_timer()
            info(f"{label}{(t-t0)*time[0]:_.3f}{time[1]}")

    t0 = t1 = t2 = timeit.default_timer()
    day = int(aocf.__name__[-2:])
    session = os.environ.get("SESSION")
    loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
    cmdargs = mk_parser(day, loglevel).parse_args()
    assert (
        not cmdargs.expect or not cmdargs.test
    ), "--expect and --test are incompatible"
    cmdargs.results = cmdargs.input + ".results"

    logging.basicConfig(
        stream=sys.stdout,
        encoding="utf-8",
        format="%(message)s",
        level=100 if cmdargs.loglevel == "OFF" else getattr(logging, cmdargs.loglevel),
    )

    aocf_args = mk_input_reader(read, split, apply, transform)(cmdargs.input)

    if cmdargs.test:
        with open(cmdargs.results) as fd:
            cmdargs.expect = fd.read().splitlines()
    cmdargs.expect.reverse()

    if np_printoptions:
        import numpy as np  # noqa: autoimport

        np.set_printoptions(**np_printoptions)

    info("")
    lap_time("Setup time: ")
    info("")

    results = []
    for i, r in enumerate(aocf(*aocf_args), start=1):
        info(f"\n### Result {i} of {aocf.__name__}():\n")
        print(r)
        info("")
        results.append(r)
        if cmdargs.expect:
            expected = cmdargs.expect.pop()
            if str(r) == expected:
                info("✅ matches the expected value\n")
            else:
                warn(f"❌ does not match {expected}\n")
        lap_time("Result time: ")
        info("")
    total_time()

    if cmdargs.write_results:
        info("Writing results to %s", cmdargs.results)
        with open(cmdargs.results, "w") as fd:
            fd.write("\n".join(map(str, results)))

    logging.shutdown()
