# 📖 Delhi Metro Route Planner — Project Documentation

> A detailed guide on how every part of this project works and how they connect.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [System Flow](#2-system-flow)
3. [Backend — How It Works](#3-backend--how-it-works)
4. [Frontend — How It Works](#4-frontend--how-it-works)
5. [Algorithm Deep Dive](#5-algorithm-deep-dive)
6. [File-by-File Breakdown](#6-file-by-file-breakdown)
7. [How Components Connect](#7-how-components-connect)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    USER (Browser)                    │
│   index.html  +  style.css  +  script.js            │
└──────────────────────┬──────────────────────────────┘
                       │  HTTP Requests (fetch API)
                       │  JSON ↑↓
                       ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)             │
│                     main.py                          │
│         ┌───────────┼───────────┐                    │
│         ▼           ▼           ▼                    │
│    /stations     /route     /block  /delay  /reset   │
└─────┬───────────────┬───────────────┬───────────────┘
      │               │               │
      ▼               ▼               ▼
┌──────────┐  ┌──────────────┐  ┌─────────────┐
│ graph.py │  │ algorithms/  │  │simulation.py│
│ (data)   │  │ bfs/dfs/a*   │  │(block/delay)│
└──────────┘  └──────┬───────┘  └─────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ heuristic.py │
              │ (A* only)    │
              └──────────────┘
```

**The project has two layers:**

| Layer | What | Files |
|-------|------|-------|
| **Frontend** | User interface in the browser | `index.html`, `style.css`, `script.js` |
| **Backend** | Python REST API server | `main.py`, `graph.py`, `heuristic.py`, `simulation.py`, `algorithms/*.py` |

They communicate over **HTTP** using JSON. The frontend sends requests, the backend computes results, and sends them back.

---

## 2. System Flow

Here's what happens step-by-step when a user finds a route:

```
1. User selects "Rajiv Chowk" → "Huda City Centre" → "Compare All"
                    │
2. script.js sends POST /route with JSON body:
   { start: "Rajiv Chowk", end: "Huda City Centre", algorithm: "compare" }
                    │
3. main.py receives the request
                    │
4. main.py calls simulation.py → get_effective_graph()
   This returns the metro graph with any blocked stations removed
   and any delays added to edge weights.
                    │
5. main.py runs all 3 algorithms on the effective graph:
   ├── bfs.py  → finds path with fewest hops
   ├── dfs.py  → finds path via deep exploration
   └── astar.py → finds optimal path using heuristic
                    │
6. main.py returns JSON response with all 3 results
                    │
7. script.js receives the response and updates the DOM:
   ├── Renders the route path (station → station → ...)
   ├── Shows metrics (stops, cost, nodes explored)
   ├── Fills the comparison table
   ├── Shows A* heuristic data (g, h, f values)
   └── Sets up step-by-step visualization
```

---

## 3. Backend — How It Works

### 3.1 Graph Data (`graph.py`)

This is the **foundation** of the entire project.

- **`METRO_GRAPH`** — A Python dictionary representing the metro network as an **adjacency list**:
  ```python
  {
      "Rajiv Chowk": {
          "New Delhi": 1.1,      # connected, 1.1 min travel time
          "Patel Chowk": 1.0,
          "Barakhamba": 1.0
      },
      ...
  }
  ```
  - **Keys** = Station names (graph nodes)
  - **Values** = Dictionary of {neighbor: weight} (graph edges)
  - **Weight** = Travel time in minutes between adjacent stations

- **`STATION_COORDINATES`** — Approximate latitude/longitude for each station, used by A*'s heuristic function.

- **`get_graph()`** — Returns a deep copy of `METRO_GRAPH` so the original is never mutated.
- **`get_all_stations()`** — Returns a sorted list of all 62 station names.

### 3.2 Heuristic Function (`heuristic.py`)

Used **only by A***. Provides the `h(n)` estimate.

- **`euclidean_distance(station_a, station_b)`** — Calculates the straight-line distance between two stations using their geographic coordinates.
- Converts lat/lon to approximate kilometers using: `1° ≈ 111 km`.
- This is the **admissible heuristic** that makes A* optimal — it never overestimates the actual travel cost.

**Relationship:** `astar.py` imports `euclidean_distance` from `heuristic.py`, which reads coordinates from `graph.py`.

### 3.3 Simulation Module (`simulation.py`)

Manages **dynamic changes** to the graph at runtime.

**State (global variables):**
- `blocked_stations` — A `set` of station names that are currently blocked
- `delays` — A `dict` mapping `(station_a, station_b)` → extra delay time

**Key function — `get_effective_graph()`:**
1. Gets a fresh copy of the original graph via `graph.get_graph()`
2. Removes all blocked stations (deletes them as nodes AND removes edges pointing to them)
3. Adds delay values to edge weights
4. Returns the modified graph

**Relationship:** `main.py` calls `get_effective_graph()` before every route calculation, so algorithms always work on the current simulation state.

### 3.4 Algorithms (`algorithms/`)

All three algorithms take the same inputs and return the same output format:

**Input:** `graph` (dict), `start` (str), `end` (str)

**Output:**
```python
{
    "path": ["Rajiv Chowk", "Patel Chowk", ...],  # ordered list of stations
    "total_stops": 21,                              # len(path) - 1
    "total_cost": 24.1,                             # sum of edge weights
    "nodes_explored": 25,                           # how many nodes were visited
    "explored_order": ["Rajiv Chowk", ...],         # order of exploration
    # A* only:
    "heuristic_data": [{"station": "...", "g": 0, "h": 24.01, "f": 24.01}, ...]
}
```

#### BFS (`bfs.py`) — Breadth-First Search
- **Strategy:** Explore level by level (all neighbors first, then their neighbors)
- **Data structure:** Queue (`collections.deque`)
- **Guarantees:** Finds the path with the **fewest stations** (hops)
- **Does NOT consider edge weights** for pathfinding — it counts hops
- **Weakness:** Explores broadly, often visits many nodes

#### DFS (`dfs.py`) — Depth-First Search
- **Strategy:** Go as deep as possible before backtracking
- **Data structure:** Recursion (call stack)
- **Guarantees:** Finds **a** path, but NOT necessarily the shortest/optimal one
- **Weakness:** Can find very long, winding paths
- **Strength:** Can find paths quickly in some graph structures

#### A* (`astar.py`) — A-Star Search
- **Strategy:** Always expand the most promising node (lowest `f(n)`)
- **Data structure:** Priority queue (min-heap via `heapq`)
- **Formula:** `f(n) = g(n) + h(n)`
  - `g(n)` = actual cost from start to current node
  - `h(n)` = estimated cost from current node to goal (Euclidean distance)
  - `f(n)` = total estimated cost
- **Guarantees:** Finds the **optimal path** (lowest total cost)
- **Strength:** Explores far fewer nodes than BFS by using the heuristic to "aim" toward the goal

### 3.5 FastAPI App (`main.py`)

The **central coordinator** — connects everything together.

**Endpoints:**

| Endpoint | What it does | Calls |
|----------|-------------|-------|
| `GET /stations` | Returns station list + current simulation state | `graph.get_all_stations()`, `simulation.get_blocked_stations()`, `simulation.get_delays()` |
| `POST /route` | Finds route using selected algorithm(s) | `simulation.get_effective_graph()` → `bfs()` / `dfs()` / `astar()` |
| `POST /block` | Blocks or unblocks a station | `simulation.block_station()` / `simulation.unblock_station()` |
| `POST /delay` | Adds or removes delay | `simulation.add_delay()` / `simulation.remove_delay()` |
| `POST /reset` | Clears all simulation state | `simulation.reset_simulation()` |

**CORS middleware** is enabled so the frontend (served from a file:// URL) can make requests to localhost:8000.

---

## 4. Frontend — How It Works

### 4.1 Structure (`index.html`)

The page is divided into sections:

```
┌──────────────────────────────────┐
│          Header                   │  Title + stats (62 Stations, 0 Blocked, ...)
├──────────────────────────────────┤
│      Find Route Card             │  Start/End dropdowns + Algorithm + Button
├──────────────────────────────────┤
│   Simulation Controls Card       │  Block station, Add delay, Reset
├──────────────────────────────────┤
│   (Hidden until route is found)  │
│   ┌──────────────────────────┐   │
│   │ Route Result             │   │  Path display + metrics
│   ├──────────────────────────┤   │
│   │ Algorithm Comparison     │   │  BFS vs DFS vs A* table
│   ├──────────────────────────┤   │
│   │ A* Heuristic Data        │   │  g(n), h(n), f(n) table
│   ├──────────────────────────┤   │
│   │ Step-by-Step Viz         │   │  Animated node exploration
│   └──────────────────────────┘   │
└──────────────────────────────────┘
```

### 4.2 Styling (`style.css`)

- **Design system** with CSS custom properties (variables) for colors, spacing, shadows
- **Card-based layout** — each section is a `.card` with subtle shadow and rounded corners
- **Animations:** `card-in` (fade up on load), `tag-pop` (tags appear), `node-explore` / `node-path` (visualization)
- **Responsive:** Grid layouts collapse on smaller screens

### 4.3 Logic (`script.js`)

The JavaScript handles **all interaction**:

1. **On page load** → Calls `GET /stations` → Populates all dropdown menus
2. **Find Route click** → Calls `POST /route` → Renders results:
   - `displayRoutePath()` — station → station → station badges
   - `displayMetrics()` — stops, cost, nodes explored cards
   - `displayComparison()` — BFS vs DFS vs A* table (winner highlighted green)
   - `displayHeuristic()` — A* g/h/f values table
   - `setupVisualization()` — prepares nodes for step-by-step animation
3. **Block/Unblock** → Calls `POST /block` → Updates blocked tag list
4. **Add Delay** → Calls `POST /delay` → Updates delay tag list
5. **Reset** → Calls `POST /reset` → Clears all tags

**Visualization engine:**
- On "Play" → A `setInterval` timer reveals explored nodes one by one
- Each node gets the `.explored` class (blue highlight) with animation
- After all nodes are revealed, final path nodes get `.on-path` class (green)
- Speed slider adjusts the interval timing

---

## 5. Algorithm Deep Dive

### Why do the three algorithms give different results?

Using the example **Rajiv Chowk → Huda City Centre**:

| | BFS | DFS | A* |
|---|---|---|---|
| **Strategy** | Level-by-level | Go deep first | Best-first (by f=g+h) |
| **Stops** | 21 | 34 | 21 |
| **Cost** | 21.0 | 35.5 | 24.1 |
| **Explored** | 62 | 38 | 25 |

- **BFS** finds the path with fewest stops (21), but since it doesn't consider weights, the cost it reports is just the sum of weights along the shortest-hop path.
- **DFS** wanders around deeply — it finds A path but not the best one. It took 34 stops because it likely went down a wrong branch before finding the destination.
- **A*** uses the Euclidean distance heuristic to "aim" toward Huda City Centre. It explored only 25 nodes (fewer than both BFS and DFS) because the heuristic effectively guided the search toward the goal.

### How A*'s Heuristic Works

```
At each step, A* asks: "Which unexplored node has the lowest f(n)?"

f(n) = g(n) + h(n)

g(n) = actual cost from start to this node (sum of edge weights traveled)
h(n) = straight-line distance from this node to the destination
f(n) = estimated total cost of the full path through this node
```

The `h(n)` value is calculated using geographic coordinates:
- Each station has approximate (latitude, longitude)
- Euclidean distance formula converts this to approximate km
- Since this is a straight line, it's always ≤ actual travel distance → **admissible heuristic** → guarantees optimality

---

## 6. File-by-File Breakdown

| File | Purpose | Depends On | Used By |
|------|---------|-----------|---------|
| `graph.py` | Station data + coordinates | — | `heuristic.py`, `simulation.py`, `main.py` |
| `heuristic.py` | Euclidean distance function | `graph.py` (coordinates) | `astar.py` |
| `algorithms/bfs.py` | BFS algorithm | — | `main.py` |
| `algorithms/dfs.py` | DFS algorithm | — | `main.py` |
| `algorithms/astar.py` | A* algorithm | `heuristic.py` | `main.py` |
| `simulation.py` | Block/delay management | `graph.py` (get_graph) | `main.py` |
| `main.py` | FastAPI server + endpoints | ALL backend files | `script.js` (via HTTP) |
| `index.html` | Page structure | — | Browser |
| `style.css` | Visual design | — | `index.html` |
| `script.js` | UI logic + API calls | `main.py` (via HTTP) | `index.html` |
| `run.py` | One-click launcher | `main.py` (via uvicorn) | User |

---

## 7. How Components Connect

```
                    ┌──────────┐
                    │  run.py  │──── Installs deps, starts uvicorn, opens browser
                    └────┬─────┘
                         │ starts
                         ▼
  ┌─────────────────────────────────────────┐
  │              main.py (FastAPI)           │
  │                                         │
  │  GET /stations ──→ graph.get_all_stations()
  │                    simulation.get_blocked_stations()
  │                    simulation.get_delays()
  │                                         │
  │  POST /route ──→ simulation.get_effective_graph()
  │                  ├── bfs(graph, start, end)
  │                  ├── dfs(graph, start, end)
  │                  └── astar(graph, start, end)
  │                       └── heuristic.euclidean_distance()
  │                            └── graph.STATION_COORDINATES
  │                                         │
  │  POST /block ──→ simulation.block_station()
  │  POST /delay ──→ simulation.add_delay()
  │  POST /reset ──→ simulation.reset_simulation()
  └────────────────────┬────────────────────┘
                       │ JSON responses
                       ▼
  ┌─────────────────────────────────────────┐
  │          script.js (Frontend)           │
  │                                         │
  │  loadStations() ──→ populateDropdowns() │
  │  findRoute()    ──→ displayResults()    │
  │                    ├── displayRoutePath()│
  │                    ├── displayMetrics()  │
  │                    ├── displayComparison()│
  │                    ├── displayHeuristic()│
  │                    └── setupVisualization()
  │  Block/Delay/Reset ──→ update tag lists │
  └─────────────────────────────────────────┘
```

**In short:**
- `graph.py` is the **data layer** — everyone reads from it
- `simulation.py` is the **state layer** — modifies the graph dynamically
- `algorithms/*.py` are the **compute layer** — pure functions that find paths
- `main.py` is the **API layer** — orchestrates everything and exposes HTTP endpoints
- `script.js` is the **presentation layer** — calls APIs and renders results
- `run.py` is the **entry point** — wires it all together with one click
