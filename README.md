# Smart Track Metro

An interactive metro route planner and algorithm visualizer built with FastAPI and vanilla JavaScript.

Plan routes across the metro network using BFS, DFS, and A*, compare results instantly, and simulate real-world disruptions like blocked stations and delays.

## Live Demo

🚀 **Try it now:** https://smarttrackmetro.vercel.app

## Highlights

- 🚇 Route planning with `BFS`, `DFS`, and `A*`
- ⚖️ Compare-all mode to evaluate all algorithms side by side
- 🧠 A* heuristic table with `g(n)`, `h(n)`, and `f(n)`
- 🛑 Station blocking simulation
- ⏱️ Delay simulation between connected stations
- ▶️ Step-by-step exploration playback

## Tech Stack

- 🐍 Backend: Python, FastAPI, Uvicorn
- 🌐 Frontend: HTML, CSS, JavaScript
- 🗺️ Data Model: In-memory weighted graph

## Project Structure

```text
Smart Track Metro/
├── run.py
├── requirements.txt
├── vercel.json
├── api/
│   └── index.py
├── backend/
│   ├── main.py
│   ├── graph.py
│   ├── heuristic.py
│   ├── simulation.py
│   └── algorithms/
│       ├── bfs.py
│       ├── dfs.py
│       └── astar.py
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

## Run Locally

### Prerequisites

- Python 3.10+

### Quick Start

```bash
python run.py
```

What this launcher does:

1. Verifies and installs required packages from `requirements.txt` if needed
2. Starts the FastAPI server
3. Opens your browser automatically
4. Picks the next available port if `8000` is busy

Stop the server anytime with `Ctrl+C`.

### Manual Start (Optional)

```bash
python -m pip install -r requirements.txt
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open in browser:

```text
http://127.0.0.1:8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /stations | List stations, blocked stations, and delays |
| POST | /route | Find route with `bfs`, `dfs`, `astar`, or `compare` |
| POST | /block | Block or unblock a station |
| POST | /delay | Add or remove delay between stations |
| POST | /reset | Reset all simulation state |

### Sample Requests

```bash
curl -X POST http://127.0.0.1:8000/route \
  -H "Content-Type: application/json" \
  -d '{"start":"Rajiv Chowk","end":"Huda City Centre","algorithm":"astar"}'
```

```bash
curl -X POST http://127.0.0.1:8000/route \
  -H "Content-Type: application/json" \
  -d '{"start":"Rajiv Chowk","end":"Huda City Centre","algorithm":"compare"}'
```

## Deployment

This project is configured for Vercel deployment with:

- `api/index.py` as Python serverless entrypoint
- `vercel.json` for frontend and API routing

### Vercel Link

✅ https://smarttrackmetro.vercel.app

## Notes

- Browser favicon 404 (if shown) does not affect functionality.
- For local development, run only one backend instance at a time.

## License

Educational and demonstration use.
