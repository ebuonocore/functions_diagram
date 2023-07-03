import itertools
from typing import Iterable
import requests  # type: ignore
import json


def get_city_coord(city: str) -> tuple[float, float] | None:
    """Retrieves the GPS coordinates of a town using the Openstreetmap API."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        if "lat" in data[0] and "lon" in data[0]:
            return data[0]["lat"], data[0]["lon"]
        else:
            return None
    else:
        return None


def get_distance_between_cities(city1: str, city2: str) -> float | None:
    """Use the openstreetmap API to calculate the distance by car between two towns."""
    coord_city1 = get_city_coord(city1)
    coord_city2 = get_city_coord(city2)
    if coord_city1 is not None and coord_city2 is not None:
        url = "https://router.project-osrm.org/route/v1/driving/{},{};{},{}?overview=false".format(
            coord_city1[1], coord_city1[0], coord_city2[1], coord_city2[0]
        )
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            try:
                distance = data["routes"][0]["distance"]
                result: float = round(distance / 1000, 3)
                return result
            except:
                return None
    return None  # Request failed


def create_cost_table(cities: list[str]) -> dict[str, dict[str, float | None]]:
    """Create the cost table between the cities.
    The cost table is a dictionary of dictionaries.
    Simplifying assumption: The distance between A and B is the same as the distance between B and A.
    """
    cost: dict[str, dict[str, float]] = {}
    for city1 in cities:
        cost[city1] = {}
        for city2 in cities:
            cost[city1][city2] = {}
    for j in range(len(cities)):
        print(".", end="")
        city1 = cities[j]
        for i in range(j, len(cities)):
            city2 = cities[i]
            if city1 != city2:
                distance = get_distance_between_cities(city1, city2)
                cost[city1][city2] = distance
                cost[city2][city1] = distance
            else:
                cost[city1][city2] = 0
    print()
    return cost


def distance_route(cost: dict[str, dict[str, float]], route: list[str]) -> float:
    """Return the total distance of a route."""
    distance: int | float = 0
    for i in range(len(route) - 1):
        town1 = route[i]
        town2 = route[i + 1]
        distance += cost[town1][town2]
    return distance


def intermediate_towns(cities: list[str]) -> list[str]:
    """Return the list of the intermediate towns of the route."""
    return cities[1:-1]


def permutations(stages: list[str]) -> list[tuple[str, ...]]:
    """Return the list of the possible permutations between the different stage towns."""
    return list(itertools.permutations(stages, len(stages)))


def routes(
    cities: list[str], permutations_stages: list[tuple[str, ...]]
) -> list[list[str]]:
    """Return a list of possible routes (starting and ending in the city of origin)."""
    town_origine = cities[0]
    return [
        [town_origine] + list(stage) + [town_origine] for stage in permutations_stages
    ]


def search_minimum(
    cities: list[str], permutations_routes: list[list[str]]
) -> tuple[float | None, list[str]]:
    """Return the tuple consisting of the distance and the shortest path among all possible permutations."""
    distance_min = None
    route_min: list[str] = []
    town_origine = cities[0]
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
    """The naive TSP algorithm explores all possible combinations and finds the shortest possible
     route that visits each city exactly once and returns to the city of origin.
    A double entry table is used to query the distance between each city.
    It is implemented by a dictionary of dictionaries. This array is built from a list of cities:
    the first city in the list is the city of origin and the city of arrival to complete the route.
    The OpenStreetMap API is used to populate the table."""
    cities = [
        "Paris",
        "Lyon",
        "Marseille",
        "Bordeau",
        "Nice",
        "Nantes",
    ]
    cost = create_cost_table(cities)
    for k, v in cost.items():
        print(k, v)
    origin = cities[0]
    stages = intermediate_towns(cities)
    permutations_stages = permutations(stages)
    permutations_routes = routes(cities, permutations_stages)
    score, best_route = search_minimum(cities, permutations_routes)
    print_score(score, best_route)

cost = {
    Paris: {"Paris": 0, "Lyon": 462.941, "Marseille": 772.335, ...},
    Lyon: {"Paris": 462.941, "Lyon": 0, "Marseille": 312.659, ...},
    Marseille: {"Paris": 772.335, "Lyon": 312.659, "Marseille": 0, ...},
    ...
}
