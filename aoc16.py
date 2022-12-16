#!/usr/bin/env python3

import re
from heapq import heappop, heappush
from itertools import zip_longest

from funcy import mapcat, second, set_in

from aoc_util import d, run_aoc


def setup(input):
    record_re = re.compile(
        "^Valve (\w\w) has flow rate=(\d+); tunnels? leads? to valves? ([\w, ]*)$",
        re.MULTILINE,
    )
    valves, rates, connections = zip(
        *((m[1], int(m[2]), m[3].split(", ")) for m in record_re.finditer(input))
    )
    return dict(zip(valves, rates)), dict(zip(valves, connections))


def aoc16(
    rates: dict[str, int],
    connections: dict[str:[str]],
    LOOKBACK=3,
    DBG_RATE=100_000,
):
    def distance_closest(valve, destinations):
        assert destinations
        n = 0
        visited = set(destinations)
        while valve not in destinations:
            n += 1
            destinations = set(mapcat(connections.__getitem__, destinations)) - visited
            visited |= destinations
        return n

    def normalize(state):
        # It doesn't matter who is the prime actor or the elephant,
        # this cuts down search space by 50%.
        flow, time, score, *valves, todo = state
        return (flow, time, score, *sorted(valves), todo)

    def h(state):
        # Admissable heuristic for A*.
        # this is one of the most performance critical parts:
        # - extra effort to make this as tight as possible pays off A LOT
        # - todo being a presorted tuple instead of a set gave another 3x
        flow, time, score, *valves, todo = state
        tight_times = mapcat(
            sorted,
            zip_longest(
                *(range(time + 1 + distance_closest(v, todo), 0, 2) for v in valves),
                fillvalue=0,
            ),
        )
        todo_rates_sorted = (rates[v] for v in todo)
        return sum(r * t for r, t in zip(todo_rates_sorted, tight_times))

    def search_Astar(time, actors=1):
        def improves(state):
            # mutates best
            flow, time, _, *valves, todo = state
            # This is not a complete check, which would harm performance.
            # Could use a segment tree, but it's fast enough now.
            for time_plus in range(max(start_time, time - LOOKBACK), time + 1):
                idx = (time_plus, *valves, todo)
                if idx in best and flow >= best[idx]:
                    return False
            best[time, *valves, todo] = flow
            return True

        def can_beat_best_flow(state):
            nonlocal best_flow
            flow, time, score, *valves, todo = state
            if flow < best_flow:
                # found a new champion
                best_flow = flow
                d("new best_flow", best_flow)
            if time == -1 or not todo:
                # out of time or open valves
                return False
            if best_flow < 0 and flow + h(state) >= best_flow:
                # h() says this is futile
                return False
            return True

        def expand(state, idx=0):
            flow, time, score, *valves, todo = state
            if valves[idx] in todo:
                yield (
                    flow + rates[valves[idx]] * time,
                    time,
                    score if idx else 0,
                    *valves,
                    tuple(v for v in todo if v != valves[idx]),
                )
            if todo:
                for nextvalve in sorted(
                    connections[valves[idx]], key=todo.__contains__
                ):
                    newvalves = set_in(valves, [idx], nextvalve)
                    yield (
                        flow,
                        time,
                        (score - (nextvalve != valves[0] and nextvalve in todo))
                        if idx
                        else -(nextvalve in todo),
                        *newvalves,
                        todo,
                    )

        assert actors in (1, 2)
        start_time = -time
        todo0 = tuple(
            v for v, r in sorted(rates.items(), key=second, reverse=True) if r
        )
        # State tuple fields (queue is a min-heap):
        # a. flow negated
        # b. time negated
        # c. score negated (only used for tie order tie breaking)
        # d. actor(s) location(s) at valves
        # e. todo, open valves
        queue = [(0, start_time, 0, *(["AA"] * actors), todo0)]
        best = {}
        best_flow = 0
        loop = 0

        while queue:
            loop += 1
            flow, time, *rest = state = heappop(queue)
            if loop % DBG_RATE == 0:
                d("loop", loop, "|", len(queue), len(best), best_flow, "|", state)

            if improves(state) and can_beat_best_flow(state):
                newstate0 = (flow, time + 1, *rest)
                for newstate1 in expand(newstate0, idx=0):
                    if actors == 1:
                        heappush(queue, newstate1)
                    else:
                        for newstate2 in expand(newstate1, idx=1):
                            heappush(queue, normalize(newstate2))

        d(loop, m="loops")
        return -min(best.values())

    yield search_Astar(time=30)

    yield search_Astar(time=26, actors=2)


if __name__ == "__main__":
    run_aoc(aoc16, transform=setup)
