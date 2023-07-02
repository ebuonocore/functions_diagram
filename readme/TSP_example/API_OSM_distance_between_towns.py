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


if __name__ == "__main__":
    city1 = input("Ville 1 :")
    city2 = input("Ville 2 :")
    distance = get_distance_between_cities(city1, city2)
    if distance is not None:
        print("Distance entre {} et {} : {} km".format(city1, city2, distance))
    else:
        print("Impossible de calculer la distance entre {} et {}".format(city1, city2))
