#!/usr/bin/env python3

from aoc_util import run_aoc


def aoc07(lines):
    def create_fs():
        stack = [{}]
        assert lines[0] == ("$", "cd", "/")
        for line in lines[1:]:
            match line:
                case "$", "cd", "/":
                    del stack[1:]
                case "$", "cd", "..":
                    assert len(stack) > 1
                    del stack[-1]
                case "$", "cd", x:
                    assert isinstance(stack[-1][x], dict)
                    stack.append(stack[-1][x])
                case "$", "ls":
                    pass
                case "dir", name:
                    assert name not in stack[-1], "duplicate"
                    stack[-1][name] = {}
                case size, name:
                    assert name not in stack[-1], "duplicate"
                    stack[-1][name] = int(size)
                case _:
                    assert False, "known line format"
        return stack[0]

    def get_dir_sizes(fs):
        size = 0
        for name, data in fs.items():
            match data:
                case int():
                    size += data
                case dict():
                    size += yield from get_dir_sizes(data)
        yield size
        return size  # provide sum to recursive "yield from"

    fs = create_fs()
    dir_sizes = list(get_dir_sizes(fs))
    sum_small_dirs = sum(size for size in dir_sizes if size <= 100_000)

    yield sum_small_dirs

    taken_space = dir_sizes[-1]
    must_delete = taken_space - (70_000_000 - 30_000_000)
    best_to_delete = min(size for size in dir_sizes if size >= must_delete)

    yield best_to_delete


if __name__ == "__main__":
    run_aoc(aoc07, split="lines_fields", time=(1000, "ms"))
