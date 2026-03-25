"""
Simulation module for dynamic graph modifications.
Handles station blocking and delay injection.
"""

from graph import get_graph

# Global state for simulation
blocked_stations = set()
delays = {}  # key: (station_a, station_b), value: extra delay


def reset_simulation():
    """Reset all simulation state."""
    global blocked_stations, delays
    blocked_stations = set()
    delays = {}


def block_station(station_name: str):
    """Block a station so it cannot be traversed."""
    blocked_stations.add(station_name)


def unblock_station(station_name: str):
    """Unblock a previously blocked station."""
    blocked_stations.discard(station_name)


def add_delay(station_a: str, station_b: str, extra_time: float):
    """Add extra delay between two adjacent stations."""
    delays[(station_a, station_b)] = extra_time
    delays[(station_b, station_a)] = extra_time


def remove_delay(station_a: str, station_b: str):
    """Remove delay between two stations."""
    delays.pop((station_a, station_b), None)
    delays.pop((station_b, station_a), None)


def get_effective_graph():
    """
    Return the metro graph with simulation effects applied:
    - Remove blocked stations
    - Add delays to edge weights
    """
    graph = get_graph()

    # Remove blocked stations
    for station in blocked_stations:
        if station in graph:
            del graph[station]
        # Remove edges pointing to blocked stations
        for s in graph:
            if station in graph[s]:
                del graph[s][station]

    # Apply delays
    for (sa, sb), extra in delays.items():
        if sa in graph and sb in graph[sa]:
            graph[sa][sb] += extra

    return graph


def get_blocked_stations():
    """Return list of currently blocked stations."""
    return list(blocked_stations)


def get_delays():
    """Return list of currently active delays."""
    result = []
    seen = set()
    for (sa, sb), extra in delays.items():
        key = tuple(sorted([sa, sb]))
        if key not in seen:
            seen.add(key)
            result.append({"from": sa, "to": sb, "delay": extra})
    return result
