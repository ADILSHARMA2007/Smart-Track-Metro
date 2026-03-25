/**
 * Delhi Metro Route Planner — Frontend Logic
 * Handles API calls, DOM updates, comparison, and visualization.
 */

const API_BASE = "";

// --- DOM Elements ---
const $startStation = document.getElementById("start-station");
const $endStation = document.getElementById("end-station");
const $algorithmSelect = document.getElementById("algorithm-select");
const $findRouteBtn = document.getElementById("find-route-btn");
const $blockStationSelect = document.getElementById("block-station-select");
const $blockBtn = document.getElementById("block-btn");
const $unblockBtn = document.getElementById("unblock-btn");
const $blockedList = document.getElementById("blocked-list");
const $delayFrom = document.getElementById("delay-from-select");
const $delayTo = document.getElementById("delay-to-select");
const $delayValue = document.getElementById("delay-value");
const $delayBtn = document.getElementById("delay-btn");
const $delayList = document.getElementById("delay-list");
const $resetBtn = document.getElementById("reset-btn");
const $resultsSection = document.getElementById("results-section");
const $routePath = document.getElementById("route-path");
const $routeMetrics = document.getElementById("route-metrics");
const $comparisonCard = document.getElementById("comparison-card");
const $comparisonBody = document.getElementById("comparison-body");
const $heuristicCard = document.getElementById("heuristic-card");
const $heuristicBody = document.getElementById("heuristic-body");
const $visCard = document.getElementById("visualization-card");
const $visNodes = document.getElementById("vis-nodes");
const $visPlayBtn = document.getElementById("vis-play-btn");
const $visPauseBtn = document.getElementById("vis-pause-btn");
const $visResetBtn = document.getElementById("vis-reset-btn");
const $visSpeed = document.getElementById("vis-speed");
const $visCounter = document.getElementById("vis-counter");
const $loading = document.getElementById("loading-overlay");
const $toast = document.getElementById("toast");
const $statStations = document.getElementById("stat-stations");
const $statBlocked = document.getElementById("stat-blocked");
const $statDelays = document.getElementById("stat-delays");

// --- State ---
let allStations = [];
let currentResults = null;
let visTimer = null;
let visIndex = 0;
let visExplored = [];
let visPath = [];

// --- Utility ---
function showLoading() { $loading.classList.remove("hidden"); }
function hideLoading() { $loading.classList.add("hidden"); }

function showToast(msg, type = "error") {
    $toast.textContent = msg;
    $toast.className = `toast ${type} show`;
    setTimeout(() => { $toast.classList.remove("show"); }, 3000);
}

async function apiCall(endpoint, method = "GET", body = null) {
    const opts = { method, headers: { "Content-Type": "application/json" } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${endpoint}`, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

// --- Load Stations ---
async function loadStations() {
    try {
        const data = await apiCall("/stations");
        allStations = data.stations;
        $statStations.textContent = data.total;
        populateDropdowns();
        updateBlockedList(data.blocked);
        updateDelayList(data.delays);
        updateStats(data.blocked.length, data.delays.length);
    } catch (e) {
        showToast("Cannot connect to backend. Start the server first.", "error");
    }
}

function populateDropdowns() {
    const dropdowns = [$startStation, $endStation, $blockStationSelect, $delayFrom, $delayTo];
    dropdowns.forEach((sel) => {
        const placeholder = sel.options[0]?.text || "Select...";
        sel.innerHTML = `<option value="">${placeholder}</option>`;
        allStations.forEach((s) => {
            const opt = document.createElement("option");
            opt.value = s;
            opt.textContent = s;
            sel.appendChild(opt);
        });
    });
}

function updateStats(blocked, delays) {
    $statBlocked.textContent = blocked;
    $statDelays.textContent = delays;
}

// --- Block/Unblock ---
$blockBtn.addEventListener("click", async () => {
    const station = $blockStationSelect.value;
    if (!station) return showToast("Select a station to block");
    try {
        const data = await apiCall("/block", "POST", { station, action: "block" });
        showToast(data.message, "success");
        updateBlockedList(data.blocked);
        updateStats(data.blocked.length, null);
    } catch (e) { showToast(e.message); }
});

$unblockBtn.addEventListener("click", async () => {
    const station = $blockStationSelect.value;
    if (!station) return showToast("Select a station to unblock");
    try {
        const data = await apiCall("/block", "POST", { station, action: "unblock" });
        showToast(data.message, "success");
        updateBlockedList(data.blocked);
        updateStats(data.blocked.length, null);
    } catch (e) { showToast(e.message); }
});

function updateBlockedList(blocked) {
    $blockedList.innerHTML = blocked.map(
        (s) => `<span class="tag tag-blocked">🚫 ${s}</span>`
    ).join("");
    if (blocked.length === 0) {
        $blockedList.innerHTML = '<span style="font-size:0.78rem;color:var(--text-muted);">No stations blocked</span>';
    }
}

// --- Delay ---
$delayBtn.addEventListener("click", async () => {
    const from = $delayFrom.value;
    const to = $delayTo.value;
    const delay = parseFloat($delayValue.value);
    if (!from || !to) return showToast("Select both stations");
    if (from === to) return showToast("Stations must be different");
    if (!delay || delay <= 0) return showToast("Enter a positive delay value");
    try {
        const data = await apiCall("/delay", "POST", { station_a: from, station_b: to, delay, action: "add" });
        showToast(data.message, "success");
        updateDelayList(data.delays);
        updateStats(null, data.delays.length);
    } catch (e) { showToast(e.message); }
});

function updateDelayList(delays) {
    if (!delays) return;
    $delayList.innerHTML = delays.map(
        (d) => `<span class="tag tag-delay">⏱ ${d.from} ↔ ${d.to} (+${d.delay} min)</span>`
    ).join("");
    if (delays.length === 0) {
        $delayList.innerHTML = '<span style="font-size:0.78rem;color:var(--text-muted);">No delays active</span>';
    }
}

// --- Reset ---
$resetBtn.addEventListener("click", async () => {
    try {
        await apiCall("/reset", "POST", {});
        showToast("Simulation reset", "success");
        updateBlockedList([]);
        updateDelayList([]);
        updateStats(0, 0);
    } catch (e) { showToast(e.message); }
});

// --- Find Route ---
$findRouteBtn.addEventListener("click", findRoute);

async function findRoute() {
    const start = $startStation.value;
    const end = $endStation.value;
    const algo = $algorithmSelect.value;

    if (!start || !end) return showToast("Select both start and destination stations");
    if (start === end) return showToast("Start and destination must be different");

    showLoading();
    try {
        const data = await apiCall("/route", "POST", { start, end, algorithm: algo });
        currentResults = data;
        displayResults(data);
        $resultsSection.classList.remove("hidden");
        $resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (e) {
        showToast(e.message);
    } finally {
        hideLoading();
    }
}

// --- Display Results ---
function displayResults(data) {
    const results = data.results;
    const isCompare = data.mode === "compare";

    // Pick best result (for route display): prefer A*, then BFS, then DFS
    const primary = isCompare
        ? results.find((r) => r.algorithm === "A*" && !r.error) || results.find((r) => !r.error) || results[0]
        : results[0];

    // Route path
    displayRoutePath(primary);

    // Metrics
    displayMetrics(primary);

    // Comparison table
    if (isCompare) {
        displayComparison(results);
        $comparisonCard.classList.remove("hidden");
    } else {
        $comparisonCard.classList.add("hidden");
    }

    // Heuristic data (A*)
    const astarResult = results.find((r) => r.algorithm === "A*");
    if (astarResult && astarResult.heuristic_data && astarResult.heuristic_data.length > 0) {
        displayHeuristic(astarResult.heuristic_data);
        $heuristicCard.classList.remove("hidden");
    } else {
        $heuristicCard.classList.add("hidden");
    }

    // Visualization
    setupVisualization(primary);
}

function displayRoutePath(result) {
    if (result.error || !result.path || result.path.length === 0) {
        $routePath.innerHTML = `<div style="color:var(--danger);font-weight:600;">❌ No route found: ${result.error || "Unknown error"}</div>`;
        return;
    }

    $routePath.innerHTML = result.path.map((station, i) => {
        let cls = "mid";
        if (i === 0) cls = "start";
        else if (i === result.path.length - 1) cls = "end";

        const arrow = i < result.path.length - 1
            ? '<span class="route-arrow">→</span>'
            : '';

        return `<span class="route-station ${cls}">${station}</span>${arrow}`;
    }).join("");
}

function displayMetrics(result) {
    if (result.error) {
        $routeMetrics.innerHTML = "";
        return;
    }
    $routeMetrics.innerHTML = `
        <div class="metric-card blue">
            <div class="metric-value">${result.algorithm || "—"}</div>
            <div class="metric-label">Algorithm</div>
        </div>
        <div class="metric-card green">
            <div class="metric-value">${result.total_stops}</div>
            <div class="metric-label">Total Stops</div>
        </div>
        <div class="metric-card purple">
            <div class="metric-value">${result.total_cost}</div>
            <div class="metric-label">Cost (min)</div>
        </div>
        <div class="metric-card blue">
            <div class="metric-value">${result.nodes_explored}</div>
            <div class="metric-label">Nodes Explored</div>
        </div>
    `;
}

function displayComparison(results) {
    // Find best (lowest cost) for highlighting
    const validResults = results.filter((r) => !r.error);
    const bestCost = validResults.length > 0
        ? Math.min(...validResults.map((r) => r.total_cost))
        : -1;

    $comparisonBody.innerHTML = results.map((r) => {
        const isWinner = !r.error && r.total_cost === bestCost;
        const statusClass = r.error ? "status-error" : "status-found";
        const statusText = r.error ? "No Path" : "Found ✓";

        return `
            <tr class="${isWinner ? "winner" : ""}">
                <td><strong>${r.algorithm}</strong></td>
                <td>${r.error ? "—" : r.total_stops}</td>
                <td>${r.error ? "—" : r.total_cost}</td>
                <td>${r.nodes_explored}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            </tr>
        `;
    }).join("");
}

function displayHeuristic(data) {
    $heuristicBody.innerHTML = data.map((d, i) => `
        <tr>
            <td>${i + 1}</td>
            <td><strong>${d.station}</strong></td>
            <td>${d.g}</td>
            <td>${d.h}</td>
            <td><strong>${d.f}</strong></td>
        </tr>
    `).join("");
}

// --- Step-by-Step Visualization ---
function setupVisualization(result) {
    stopVisualization();
    visIndex = 0;
    visExplored = result.explored_order || [];
    visPath = result.path || [];

    // Render all nodes as unexplored
    const allNodes = [...new Set([...visExplored])];
    $visNodes.innerHTML = allNodes.map(
        (s) => `<span class="vis-node" data-station="${s}">${s}</span>`
    ).join("");

    $visCounter.textContent = `0 / ${visExplored.length}`;
    $visPlayBtn.classList.remove("hidden");
    $visPauseBtn.classList.add("hidden");
}

$visPlayBtn.addEventListener("click", () => {
    $visPlayBtn.classList.add("hidden");
    $visPauseBtn.classList.remove("hidden");
    runVisualization();
});

$visPauseBtn.addEventListener("click", () => {
    stopVisualization();
    $visPlayBtn.classList.remove("hidden");
    $visPauseBtn.classList.add("hidden");
});

$visResetBtn.addEventListener("click", () => {
    if (currentResults) {
        const primary = currentResults.mode === "compare"
            ? currentResults.results.find((r) => r.algorithm === "A*" && !r.error) || currentResults.results.find((r) => !r.error) || currentResults.results[0]
            : currentResults.results[0];
        setupVisualization(primary);
    }
});

function runVisualization() {
    const speed = 550 - parseInt($visSpeed.value); // invert: higher slider = faster
    visTimer = setInterval(() => {
        if (visIndex >= visExplored.length) {
            // Highlight final path
            highlightPath();
            stopVisualization();
            $visPlayBtn.classList.remove("hidden");
            $visPauseBtn.classList.add("hidden");
            return;
        }

        const station = visExplored[visIndex];
        const node = $visNodes.querySelector(`[data-station="${CSS.escape(station)}"]`);
        if (node) {
            node.classList.add("explored");
        }
        visIndex++;
        $visCounter.textContent = `${visIndex} / ${visExplored.length}`;
    }, speed);
}

function highlightPath() {
    visPath.forEach((station) => {
        const node = $visNodes.querySelector(`[data-station="${CSS.escape(station)}"]`);
        if (node) {
            node.classList.remove("explored");
            node.classList.add("on-path");
        }
    });
}

function stopVisualization() {
    if (visTimer) {
        clearInterval(visTimer);
        visTimer = null;
    }
}

// --- Init ---
document.addEventListener("DOMContentLoaded", loadStations);
