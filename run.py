"""
Delhi Metro Route Planner — One-Click Launcher
Starts the FastAPI backend and opens the frontend in your browser.
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading
import socket
import urllib.request
import urllib.error


HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def is_port_available(host, port):
    """Return True if the TCP port is free on host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((host, port)) != 0


def choose_port(host, preferred_port):
    """Pick preferred port if free, otherwise the next available port."""
    if is_port_available(host, preferred_port):
        return preferred_port

    for port in range(preferred_port + 1, preferred_port + 51):
        if is_port_available(host, port):
            return port

    raise RuntimeError("No free local port found in range 8000-8050")


def is_backend_running(host, port):
    """Return True if a Delhi Metro backend responds on host:port."""
    url = f"http://{host}:{port}/stations"
    try:
        with urllib.request.urlopen(url, timeout=1.5) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def install_dependencies():
    """Ensure required packages are importable; repair from requirements if needed."""
    project_root = os.path.dirname(__file__)
    requirements_file = os.path.join(project_root, "requirements.txt")

    check_cmd = [
        sys.executable,
        "-c",
        "import fastapi, uvicorn, pydantic; print('deps-ok')",
    ]

    try:
        # Import in a subprocess to avoid hanging the launcher process.
        subprocess.run(check_cmd, check=True, capture_output=True, text=True, timeout=20)
        return
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("📦 Fixing Python dependencies (this may take a minute)...")

    install_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall"]
    if os.path.exists(requirements_file):
        install_cmd.extend(["-r", requirements_file])
    else:
        install_cmd.extend(["fastapi", "uvicorn", "pydantic"])

    subprocess.check_call(install_cmd)

    # One final verification so startup fails fast with a clear message if env is still broken.
    subprocess.run(check_cmd, check=True, capture_output=True, text=True, timeout=20)
    print("✅ Dependencies are ready.")


def open_browser(url):
    """Open the dashboard after a short delay to let the server start."""
    time.sleep(2)
    print(f"\n🌐 Opening dashboard: {url}")
    webbrowser.open(url)


def main():
    print("=" * 55)
    print("  🚇  Delhi Metro Route Planner")
    print("  Algorithm Visualization & Analysis System")
    print("=" * 55)

    # Install deps if needed
    install_dependencies()

    default_url = f"http://{HOST}:{DEFAULT_PORT}"

    # If default port is occupied by this same app, reuse it.
    if (not is_port_available(HOST, DEFAULT_PORT)) and is_backend_running(HOST, DEFAULT_PORT):
        print(f"\nℹ️ Backend already running on {default_url}. Reusing it.")
        open_browser(default_url)
        return

    port = choose_port(HOST, DEFAULT_PORT)
    if port != DEFAULT_PORT:
        print(f"\n⚠️ Port {DEFAULT_PORT} is busy. Using port {port} instead.")

    base_url = f"http://{HOST}:{port}"

    # Open browser in a background thread
    threading.Thread(target=open_browser, args=(base_url,), daemon=True).start()

    # Start the server
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)

    print(f"\n🚀 Starting backend server on {base_url}")
    print("   Press Ctrl+C to stop.\n")

    import uvicorn
    uvicorn.run("main:app", host=HOST, port=port, log_level="info")


if __name__ == "__main__":
    main()
