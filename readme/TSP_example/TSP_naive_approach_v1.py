import itertools
from typing import Iterable


def distance_route(cost: dict[str, dict[str, float]], route: list[str]) -> float:
    """returns the total distance of a route."""
    distance: int | float = 0
    for i in range(len(route) - 1):
        town1 = route[i]
        town2 = route[i + 1]
        distance += cost[town1][town2]
    return distance


def intermediate_towns(
    cost: dict[str, dict[str, float]], town_origine: str
) -> list[str]:
    """Return the list of the intermediate towns of the route."""
    towns = cost.keys()
    return [v for v in towns if v != town_origine]


def permutations(stages: list[str]) -> list[tuple[str, ...]]:
    """Return the list of the possible permutations between the different stage towns."""
    return list(itertools.permutations(stages, len(stages)))


def routes(
    town_origine: str, permutations_stages: list[tuple[str, ...]]
) -> list[list[str]]:
    """Return a list of possible routes (starting and ending in the city of origin)."""
    return [
        [town_origine] + list(stage) + [town_origine] for stage in permutations_stages
    ]


def search_minimum(
    cost: dict[str, dict[str, float]], permutations_routes: list[list[str]]
) -> tuple[float | None, list[str]]:
    """Returns the tuple consisting of the distance and the shortest path among all possible permutations."""
    distance_min = None
    route_min: list[str] = []
    town_origine = permutations_routes[0][0]
    for route in permutations_routes:
        distance = distance_route(cost, route)
        if distance_min is None:
            distance_min = distance
        else:
            if distance_min > distance:
                distance_min = distance
                route_min = route
    return (distance_min, route_min)


def print_score(score: float | None, best_route: list[str]) -> None:
    """Just print the result : shortest path and the associated distance."""
    print(">>> ", best_route, ":", score)


if __name__ == "__main__":
    """The naive TSP algorithm explores all possible combinations and finds the shortest possible route that visits each city exactly once and returns to the city of origin.
    A double entry table is used to query the distance between two cities. It is implemented by a dictionary of dictionaries.
    The algorithm is based on the itertools library which allows you to generate all the possible permutations of a list.
    """
    cost: dict[str, dict[str, float]] = {
        "P": {"P": 0, "L": 466.1, "M": 775, "B": 584, "N": 932},
        "L": {"P": 466.1, "L": 0, "M": 314, "B": 557, "N": 471},
        "M": {"P": 775, "L": 314, "M": 0, "B": 645, "N": 199},
        "B": {"P": 584, "L": 557, "M": 645, "B": 0, "N": 803},
        "N": {"P": 932, "L": 471, "M": 199, "B": 803, "N": 0},
    }
    stages = intermediate_towns(cost, "P")
    permutations_stages = permutations(stages)
    permutations_routes = routes("P", permutations_stages)
    score, best_route = search_minimum(cost, permutations_routes)
    print_score(score, best_route)
