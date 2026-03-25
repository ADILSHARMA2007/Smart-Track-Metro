"""
Depth-First Search Algorithm
Explores deeply - not guaranteed to find optimal path.
"""


def dfs(graph: dict, start: str, end: str) -> dict:
    """
    DFS pathfinding - explores depth-first.

    Returns:
        dict with keys: path, total_stops, total_cost, nodes_explored, explored_order
    """
    if start not in graph or end not in graph:
        return {
            "path": [],
            "total_stops": 0,
            "total_cost": 0,
            "nodes_explored": 0,
            "explored_order": [],
            "error": "Station not found in graph"
        }

    if start == end:
        return {
            "path": [start],
            "total_stops": 0,
            "total_cost": 0,
            "nodes_explored": 1,
            "explored_order": [start],
        }

    visited = set()
    explored_order = []
    result = {"found": False, "path": [], "cost": 0}

    def _dfs_recursive(current, path, cost):
        if result["found"]:
            return
        visited.add(current)
        explored_order.append(current)

        if current == end:
            result["found"] = True
            result["path"] = path[:]
            result["cost"] = cost
            return

        for neighbor, weight in graph.get(current, {}).items():
            if neighbor not in visited and not result["found"]:
                _dfs_recursive(neighbor, path + [neighbor], cost + weight)

    _dfs_recursive(start, [start], 0)

    if result["found"]:
        return {
            "path": result["path"],
            "total_stops": len(result["path"]) - 1,
            "total_cost": round(result["cost"], 2),
            "nodes_explored": len(explored_order),
            "explored_order": explored_order,
        }

    return {
        "path": [],
        "total_stops": 0,
        "total_cost": 0,
        "nodes_explored": len(explored_order),
        "explored_order": explored_order,
        "error": "No path found"
    }
