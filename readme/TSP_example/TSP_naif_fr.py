import itertools
from typing import Iterable


def distance_trajet(
    tableau: dict[str, dict[str, float]], trajet: list[str]
) -> float:
    distance: int | float = 0
    for i in range(len(trajet) - 1):
        ville1 = trajet[i]
        ville2 = trajet[i + 1]
        distance += tableau[ville1][ville2]
    return distance


def villes_intermédiaires(
    tableau: dict[str, dict[str, float]], ville_origine: str
) -> list[str]:
    villes = tableau.keys()
    return [v for v in villes if v != ville_origine]


def permutations(étapes: list[str]) -> list[tuple[str, ...]]:
    return list(itertools.permutations(étapes, len(étapes)))


def trajets(
    ville_origine: str, permutations_étapes: list[tuple[str, ...]]
) -> list[list[str]]:
    return [
        [ville_origine] + list(étape) + [ville_origine] for étape in permutations_étapes
    ]


def recherche_minimum(
    tableau: dict[str, dict[str, float]], permutations_trajets: list[list[str]]
) -> tuple[float | None, list[str]]:
    distance_min = None
    trajet_min: list[str] = []
    ville_origine = permutations_trajets[0][0]
    for trajet in permutations_trajets:
        distance = distance_trajet(tableau, trajet)
        if distance_min is None:
            distance_min = distance
        else:
            if distance_min > distance:
                distance_min = distance
                trajet_min = trajet
    return (distance_min, trajet_min)


def affiche_score(score: float| None, meilleur_trajet: list[str]) -> None:
    print(">>> ", meilleur_trajet, ":", score)


tableau: dict[str, dict[str, float]] = {
    "P": {"P": 0, "L": 466.1, "M": 775, "B": 584, "N": 932},
    "L": {"P": 466.1, "L": 0, "M": 314, "B": 557, "N": 471},
    "M": {"P": 775, "L": 314, "M": 0, "B": 645, "N": 199},
    "B": {"P": 584, "L": 557, "M": 645, "B": 0, "N": 803},
    "N": {"P": 932, "L": 471, "M": 199, "B": 803, "N": 0},
}

étapes = villes_intermédiaires(tableau, "P")
permutations_étapes = permutations(étapes)
permutations_trajets = trajets("P", permutations_étapes)
score, meilleur_trajet = recherche_minimum(tableau, permutations_trajets)
affiche_score(score, meilleur_trajet)
