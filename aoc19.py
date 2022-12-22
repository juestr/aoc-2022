#!/usr/bin/env python3

import numpy as np
import pandas as pd

from aoc_util import d, run_aoc


def max_geodes(blueprint, total_time):
    """Find max geodes using a DP bottom up strategy with bells and whistles"""

    def init_costs():
        ore_ore, clay_ore, obs_ore, obs_clay, geode_ore, geode_obs = blueprint
        return np.array(
            [
                [ore_ore, 0, 0],  # cost to build an ore robot
                [clay_ore, 0, 0],  # + clay robot etc
                [obs_ore, obs_clay, 0],
                [geode_ore, 0, geode_obs],
            ]
        )

    def init_state():
        # (ore clay obs geode  ore-r clay-r obs-r  skip-ore-r skip-cla-ry skip-obs-r)
        #                 0  1  2  3  4  5  6  7  8  9
        return np.array([[0, 0, 0, 0, 1, 0, 0, 0, 0, 0]])

    def sample_most_promising(state):
        n = 0
        samples = []
        for col in [3, 6, 5, 4, 2, 1, 0]:
            hi = np.argpartition(state[:, col], -200)[-200:]
            state_hi = state[hi]
            samples.append(state_hi[state_hi[:, col] > 0])
            n += samples[-1].shape[0]
            if n > 500:
                break
        return np.vstack(samples)

    def estimate(state, time):
        """Produce a reasonable result fast without branching and in place"""
        if time <= 2:
            return np.max(state[:, 3])

        has_materials = state[:, 0:3, np.newaxis] >= costs.T[np.newaxis, :, :]
        can_build = np.bitwise_and.reduce(has_materials, axis=1)
        can_build[:, 0:3] &= np.random.randint(0, 6, state[:, 0:3].shape) > 0

        state[:, 0:3] += state[:, 4:7]
        state[:, 7:10] = 0

        state[:, 0:3][can_build[:, 3]] -= costs[3]
        state[:, 3][can_build[:, 3]] += time - 1
        whitelist = np.logical_not(can_build[:, 3])
        for rtype in (2, 1, 0):
            state[:, 0:3][can_build[:, rtype] & whitelist] -= costs[rtype]
            state[:, 4][can_build[:, rtype] & whitelist] += 1
            if rtype != 0:
                whitelist &= np.logical_not(can_build[:, rtype])
        return estimate(state, time - 1)

    def work_and_build_robots(state, time):
        """A full single round, returns new state with ores mined and robots created"""

        if state.shape[0] > 2000 and time > 2:
            best = estimate(sample_most_promising(state), time)
            best_present = np.max(state[:, 3])
            d("# estimated geodes: ", best, " | best present: ", best_present)
        else:
            best = 0

        # bool: n x material x rtypes  [material = 0,1,2! since geodes aren't used]
        has_materials = state[:, 0:3, np.newaxis] >= costs.T[np.newaxis, :, :]
        # bool: n x robot_types
        can_build = np.bitwise_and.reduce(has_materials, axis=1)
        can_build[:, 0:3] &= np.logical_not(state[:, 7:10])
        can_skip = np.logical_not(can_build[:, 3])

        # eliminate hopeless cases
        if best > 0:
            time_left = (time - 1) + can_build[:, 3]
            max_remaining = time_left * (time_left - 1) // 2
            whitelist = np.logical_or(
                state[:, 3] + max_remaining > best, state[:, 3] == best_present
            )
            can_build &= whitelist[:, np.newaxis]
            can_skip &= whitelist
            t, w = state.shape[0], np.sum(whitelist)
            d(f"# infeasable states eliminated: {t-w} {(t-w)/t*100:2.0f}%")

        d("# robots and factory working")
        # after deciding can_* let existing robots work
        state[:, 0:3] += state[:, 4:7]

        # create states with new robots
        builds = []
        for rtype in range(4):
            tmp = state[can_build[:, rtype]]
            tmp[:, 0:3] -= costs[rtype]
            if rtype == 3:
                # geodes are never used, so we can book lifetime production
                # immediately instead of messing with robots
                tmp[:, 3] += time - 1
            else:
                tmp[:, 4 + rtype] += 1
            tmp[:, 7:10] = 0
            builds.append(tmp)

        # Create states where we skip building anything.
        # We never do so if we could build a geode robot.
        # If we don't build another type we remember it, so we don't build
        # the same type in the following round; this would be suboptimal.
        tmp = state[can_skip]
        tmp[:, 7:10] = can_build[:, 0:3][can_skip]
        builds.append(tmp)

        state = np.vstack(builds)
        if time > 2:
            s1 = state.shape[0]
            state = np.unique(state, axis=0)
            s2 = state.shape[0]
            d(f"# duplicates eliminated: {s1-s2} {(s1-s2)/s1*100:2.0f}%")
        return state

    d("##### starting work on blueprint", blueprint)
    costs = init_costs()
    state = init_state()
    d(costs, t="costs")
    d(state, t="state")
    # skip the last round, since geode robots built in it won't produce anything
    for time in range(total_time, 1, -1):
        d("### time left", time)
        state = work_and_build_robots(state, time)
        d(state.shape, m="state")
        d(state)
    return np.max(state[:, 3])


def aoc19(df):
    # Was meant to use DP, but the large state space makes it akin to brute force.
    # In the middle of each blueprint run eliminating duplicate states proved effective.
    # A way to also eliminate dominated states for reasonable effort would be awesome.
    # Beam search for estimation & pruning is very effective towards the end.

    def result1(geodes):
        return np.dot(np.arange(len(geodes)) + 1, geodes)

    def result2(geodes):
        return np.product(geodes)

    blueprints = df.to_numpy()
    geodes = [max_geodes(blueprint, 24) for blueprint in blueprints]
    d(geodes, m="geodes")
    yield result1(geodes)

    geodes = [max_geodes(blueprint, 32) for blueprint in blueprints[:3]]
    d(geodes, m="geodes")
    yield result2(geodes)


if __name__ == "__main__":
    run_aoc(
        aoc19,
        read=(
            pd.read_table,
            dict(header=None, sep=" ", usecols=[6, 12, 18, 21, 27, 30]),
        ),
        np_printoptions=dict(linewidth=120, threshold=500, edgeitems=5),
    )
