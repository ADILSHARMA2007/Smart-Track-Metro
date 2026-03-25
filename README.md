# Delhi Metro Route Planner

Algorithm Visualization and Analysis System built with FastAPI and vanilla JavaScript.

This project models the Delhi Metro network as a graph and finds routes using BFS, DFS, and A*.

## Features

- Route search with BFS, DFS, and A*
- Compare-all mode to run all algorithms side by side
- A* heuristic table with g(n), h(n), and f(n)
- Simulation controls to block stations and add delays
- Step-by-step exploration playback

## Tech Stack

- Backend: Python, FastAPI, Uvicorn
- Frontend: HTML, CSS, JavaScript
- Data: In-memory weighted graph

## Project Structure

```text
delhi-metro-planner/
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

What the launcher does:

1. Verifies and repairs required Python packages from requirements.txt if needed
2. Starts FastAPI server
3. Opens your browser automatically
4. If port 8000 is busy, selects the next free port

To stop the server, press Ctrl+C in the terminal where it is running.

### Manual Start (Optional)

```bash
python -m pip install -r requirements.txt
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## API Endpoints

| Method | Endpoint   | Description |
|--------|------------|-------------|
| GET    | /stations  | List stations, blocked stations, delays |
| POST   | /route     | Find route with bfs, dfs, astar, or compare |
| POST   | /block     | Block or unblock a station |
| POST   | /delay     | Add or remove delay between stations |
| POST   | /reset     | Reset all simulation state |

### Example Requests

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

## Deploy on Vercel

This repository is already prepared for Vercel deployment using:

- api/index.py as Python serverless entrypoint
- vercel.json for routing static frontend and backend API

### Deploy via Dashboard

1. Push this repo to GitHub
2. Import the repo in Vercel
3. Keep root directory as project root
4. Deploy

### Deploy via CLI

```bash
npm i -g vercel
vercel login
vercel
vercel --prod
```

After deployment, verify:

- / loads the frontend
- /docs opens FastAPI docs
- /stations returns JSON

## Notes

- Browser favicon request may show a 404 if no favicon file is provided. This does not affect app functionality.
- For best results, run only one backend instance locally at a time.

## License

Educational and demonstration use.
