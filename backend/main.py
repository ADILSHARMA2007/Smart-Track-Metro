"""
Delhi Metro Route Planner - FastAPI Backend
REST API for route finding with BFS, DFS, and A* algorithms.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from graph import get_all_stations, STATION_COORDINATES
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.astar import astar
from simulation import (
    get_effective_graph,
    block_station,
    unblock_station,
    add_delay,
    remove_delay,
    get_blocked_stations,
    get_delays,
    reset_simulation,
)

app = FastAPI(title="Delhi Metro Route Planner", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def dashboard():
    """Serve the frontend dashboard from the backend server."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_path)


# --- Request Models ---

class RouteRequest(BaseModel):
    start: str
    end: str
    algorithm: str  # "bfs", "dfs", "astar", or "compare"


class BlockRequest(BaseModel):
    station: str
    action: str = "block"  # "block" or "unblock"


class DelayRequest(BaseModel):
    station_a: str
    station_b: str
    delay: float
    action: str = "add"  # "add" or "remove"


# --- Endpoints ---

@app.get("/stations")
def list_stations():
    """Return all stations for dropdown menus."""
    stations = get_all_stations()
    blocked = get_blocked_stations()
    return {
        "stations": stations,
        "blocked": blocked,
        "delays": get_delays(),
        "total": len(stations),
    }


@app.post("/route")
def find_route(req: RouteRequest):
    """Find route between two stations using specified algorithm."""
    graph = get_effective_graph()

    if req.start not in graph and req.start not in get_blocked_stations():
        raise HTTPException(status_code=404, detail=f"Station '{req.start}' not found")
    if req.end not in graph and req.end not in get_blocked_stations():
        raise HTTPException(status_code=404, detail=f"Station '{req.end}' not found")

    if req.start in get_blocked_stations():
        raise HTTPException(status_code=400, detail=f"Station '{req.start}' is blocked")
    if req.end in get_blocked_stations():
        raise HTTPException(status_code=400, detail=f"Station '{req.end}' is blocked")

    if req.algorithm == "compare":
        bfs_result = bfs(graph, req.start, req.end)
        bfs_result["algorithm"] = "BFS"

        dfs_result = dfs(graph, req.start, req.end)
        dfs_result["algorithm"] = "DFS"

        astar_result = astar(graph, req.start, req.end)
        astar_result["algorithm"] = "A*"

        return {
            "mode": "compare",
            "results": [bfs_result, dfs_result, astar_result],
        }

    algorithm_map = {
        "bfs": ("BFS", bfs),
        "dfs": ("DFS", dfs),
        "astar": ("A*", astar),
    }

    if req.algorithm not in algorithm_map:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {req.algorithm}")

    algo_name, algo_func = algorithm_map[req.algorithm]
    result = algo_func(graph, req.start, req.end)
    result["algorithm"] = algo_name

    return {
        "mode": "single",
        "results": [result],
    }


@app.post("/block")
def manage_block(req: BlockRequest):
    """Block or unblock a station."""
    all_stations = get_all_stations()
    if req.station not in all_stations:
        raise HTTPException(status_code=404, detail=f"Station '{req.station}' not found")

    if req.action == "block":
        block_station(req.station)
        return {"message": f"Station '{req.station}' has been blocked", "blocked": get_blocked_stations()}
    elif req.action == "unblock":
        unblock_station(req.station)
        return {"message": f"Station '{req.station}' has been unblocked", "blocked": get_blocked_stations()}
    else:
        raise HTTPException(status_code=400, detail="Action must be 'block' or 'unblock'")


@app.post("/delay")
def manage_delay(req: DelayRequest):
    """Add or remove delay between stations."""
    all_stations = get_all_stations()
    if req.station_a not in all_stations:
        raise HTTPException(status_code=404, detail=f"Station '{req.station_a}' not found")
    if req.station_b not in all_stations:
        raise HTTPException(status_code=404, detail=f"Station '{req.station_b}' not found")

    if req.action == "add":
        add_delay(req.station_a, req.station_b, req.delay)
        return {"message": f"Delay of {req.delay} min added between '{req.station_a}' and '{req.station_b}'", "delays": get_delays()}
    elif req.action == "remove":
        remove_delay(req.station_a, req.station_b)
        return {"message": f"Delay removed between '{req.station_a}' and '{req.station_b}'", "delays": get_delays()}
    else:
        raise HTTPException(status_code=400, detail="Action must be 'add' or 'remove'")


@app.post("/reset")
def reset():
    """Reset all simulation state."""
    reset_simulation()
    return {"message": "Simulation reset successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
