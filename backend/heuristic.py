import math
from graph import STATION_COORDINATES


def euclidean_distance(station_a: str, station_b: str) -> float:
    """
    Calculate approximate Euclidean distance between two stations
    using their geographic coordinates.
    Returns distance in approximate km (scaled from lat/lon degrees).
    """
    if station_a not in STATION_COORDINATES or station_b not in STATION_COORDINATES:
        return 0.0

    lat1, lon1 = STATION_COORDINATES[station_a]
    lat2, lon2 = STATION_COORDINATES[station_b]

    # Convert to approximate km (1 degree ≈ 111 km at this latitude)
    dlat = (lat2 - lat1) * 111.0
    dlon = (lon2 - lon1) * 111.0 * math.cos(math.radians((lat1 + lat2) / 2))

    return math.sqrt(dlat ** 2 + dlon ** 2)
