#!/usr/bin/env python3

import os
from functools import partial
from heapq import heapify, heappop, heappush
from itertools import pairwise

import numpy as np
import pandas as pd
from funcy import count, lmap, lmapcat, map, mapcat, zipdict

from aoc_util import d, run_aoc

np, pd, pairwise, d, map, lmap, mapcat, lmapcat, zipdict, heappush, heappop
heapify, count, partial

identity4 = np.identity(4, dtype=int)
_weights4 = np.array([1, 2, 3, 0])
weight4 = lambda x: np.dot(x, _weights4)

DBG_RATE = 1
DBG_RATE = int(os.environ.get("DBG_RATE") or 1)


def aoc19(df):
    blueprints = df.to_numpy()

    tie_breaker = partial(next, count())

    def can_build(costs, inventory, rtype):
        return np.alltrue(costs[rtype] <= inventory)

    def add_score(time, costs, inventory, robots):
        return (
            (
                -inventory[3] - (time + 1) * robots[3],
                -weight4(inventory) - time * (10 + weight4(robots)),
                tie_breaker(),
            ),
            (time, costs, inventory, robots),
        )

    def init_state(blueprint, duration=23):
        ore_ore, clay_ore, obs_ore, obs_clay, geode_ore, geode_obs = blueprint
        d(ore_ore, clay_ore, obs_ore, obs_clay, geode_ore, geode_obs, m="blueprint")

        inventory = np.array([0, 0, 0, 0])
        robots = np.array([1, 0, 0, 0])

        rtypes = dict(enumerate("geode obs clay ore".split()))
        costs = np.array(
            [
                [ore_ore, 0, 0, 0],
                [clay_ore, 0, 0, 0],
                [obs_ore, obs_clay, 0, 0],
                [geode_ore, 0, geode_obs, 0],
            ]
        )
        d(costs, t="costs")
        return add_score(duration, costs, inventory, robots)

    def expand(time, costs, inventory, robots):
        new_time = time - 1
        new_inventory = inventory + robots
        for rtype, rcost in reversed(list(enumerate(costs))):
            if np.alltrue(rcost <= inventory):
                yield (
                    new_time,
                    costs,
                    new_inventory - rcost,
                    robots + identity4[rtype],
                )
        yield (new_time, costs, new_inventory, robots)

    def search(blueprint, duration):
        def h(time, costs, inventory, robots):
            geodes = inventory[3]
            geode_robots = (time + 1) * robots[3]
            # if robots[3] == 0 and not can_build(costs, inventory, 3):
            #     time -= 1

            # if robots[2] == 0 and not can_build(costs, inventory, 2):
            #     time -= 1
            # if robots[1] == 0 and not can_build(costs, inventory, 1):
            #     time -= 1

            # elif not can_build(costs, inventory, 3):
            #     time -= 1  # can't create an geode robot this round

            time = max(0, time)
            new_geode_robots = (time * (time + 1)) // 2
            return geodes + geode_robots + new_geode_robots

        def check_visited(time, costs, inventory, robots):
            t = (time, *iter(inventory), *iter(robots))
            if t in visited:
                return False
            else:
                visited.add(t)
                return True

        def check_best(time, costs, inventory, robots):
            nonlocal max_geodes
            future_geodes = (
                inventory[3]
                + (time + 1) * robots[3]
                + time * can_build(costs, inventory, 3)
            )
            if future_geodes > max_geodes:
                max_geodes = future_geodes
                d(max_geodes, m="new max_geodes")
            if future_geodes + h2(time, costs, inventory, robots) <= max_geodes:
                # d("abort")
                return False
            return True

        def h2(time, costs, inventory, robots):
            # if robots[3] == 0 and not can_build(costs, inventory, 3):
            if not can_build(costs, inventory, 3):
                time -= 1

            time = max(-2, time)
            new_geode_robots = ((time + 1) * (time + 2)) // 2
            return max(0, new_geode_robots)

        def check_best2(time, costs, inventory, robots):
            nonlocal max_geodes
            future_geodes = inventory[3] + (time + 1) * robots[3]
            if future_geodes > max_geodes:
                max_geodes = future_geodes
                d(max_geodes, m="new max_geodes")
            if (
                max_geodes > 0
                and future_geodes + h2(time, costs, inventory, robots) <= max_geodes
            ):
                # d("abort")
                return False
            return True

        queue = [init_state(blueprint, duration)]
        visited = set()
        max_geodes = 0
        loop = 0
        while queue:
            loop += 1
            score, data = state = heappop(queue)
            time, costs, inventory, robots = data
            if loop % DBG_RATE == 0:
                # fmt: off
                d("loop", loop, len(queue), "|", inventory[3], max_geodes, "|", time, inventory, robots)
                # fmt: on

            if time == 0:
                inventory = inventory + robots
                # if inventory[3] == max_geodes:
                #     d(inventory, robots, max_geodes, "max leaf")
                max_geodes = max(max_geodes, inventory[3])
            elif check_visited(*data) and check_best(*data):
                for newdata in expand(*data):
                    heappush(queue, add_score(*newdata))

            # else:
            #     for newdata in expand(*data):
            #         if check_visited(*newdata) and check_best2(*newdata):
            #             heappush(queue, add_score(*newdata))

        d(max_geodes, "search return")
        return max_geodes

    quality_levels = [search(bp, 23) for bp in blueprints]
    yield np.dot(np.arange(len(quality_levels)) + 1, quality_levels)

    yield 1
    return

    factors = [search(bp, 32) for bp in blueprints[:3]]
    yield np.multiply.reduce(factors)

    # 9 0 1 9 0 2 8 1 0 0 6 2 2 0 2 0 0 13 0 7 6 0 15 1 3 4 13 6 => 2160


if __name__ == "__main__":
    run_aoc(
        aoc19,
        read=(
            pd.read_table,
            dict(header=None, sep=" ", usecols=[6, 12, 18, 21, 27, 30]),
        ),
    )
