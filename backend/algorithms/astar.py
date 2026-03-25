"""
A* Search Algorithm
Uses heuristic function for optimal pathfinding.
h(n) = Euclidean straight-line distance to goal.
"""

import heapq
from heuristic import euclidean_distance


def astar(graph: dict, start: str, end: str) -> dict:
    """
    A* pathfinding with Euclidean distance heuristic.

    Returns:
        dict with keys: path, total_stops, total_cost, nodes_explored,
                        explored_order, heuristic_data
    """
    if start not in graph or end not in graph:
        return {
            "path": [],
            "total_stops": 0,
            "total_cost": 0,
            "nodes_explored": 0,
            "explored_order": [],
            "heuristic_data": [],
            "error": "Station not found in graph"
        }

    if start == end:
        return {
            "path": [start],
            "total_stops": 0,
            "total_cost": 0,
            "nodes_explored": 1,
            "explored_order": [start],
            "heuristic_data": [{
                "station": start,
                "g": 0, "h": 0, "f": 0
            }],
        }

    # Priority queue: (f_score, counter, station, path, g_score)
    counter = 0
    open_set = []
    h_start = euclidean_distance(start, end)
    heapq.heappush(open_set, (h_start, counter, start, [start], 0))

    g_scores = {start: 0}
    visited = set()
    explored_order = []
    heuristic_data = []

    while open_set:
        f_score, _, current, path, g_score = heapq.heappop(open_set)

        if current in visited:
            continue

        visited.add(current)
        explored_order.append(current)

        h_val = euclidean_distance(current, end)
        heuristic_data.append({
            "station": current,
            "g": round(g_score, 2),
            "h": round(h_val, 2),
            "f": round(f_score, 2),
        })

        if current == end:
            return {
                "path": path,
                "total_stops": len(path) - 1,
                "total_cost": round(g_score, 2),
                "nodes_explored": len(explored_order),
                "explored_order": explored_order,
                "heuristic_data": heuristic_data,
            }

        for neighbor, weight in graph.get(current, {}).items():
            if neighbor not in visited:
                new_g = g_score + weight
                if neighbor not in g_scores or new_g < g_scores[neighbor]:
                    g_scores[neighbor] = new_g
                    h_val_n = euclidean_distance(neighbor, end)
                    f_val = new_g + h_val_n
                    counter += 1
                    heapq.heappush(open_set, (f_val, counter, neighbor, path + [neighbor], new_g))

    return {
        "path": [],
        "total_stops": 0,
        "total_cost": 0,
        "nodes_explored": len(explored_order),
        "explored_order": explored_order,
        "heuristic_data": heuristic_data,
        "error": "No path found"
    }
