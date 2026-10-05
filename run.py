"""Start the built interface and API together. No cloud or aviation connections."""
import argparse
from pathlib import Path
import sys
from threading import Timer
import webbrowser

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATC Guardian research simulator")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not (Path(__file__).parent / "frontend" / "dist" / "index.html").exists():
        sys.exit("Build the interface first: run setup.cmd, or cd frontend then npm ci and npm run build.")
    try:
        import uvicorn
    except ImportError:
        sys.exit("Dependencies are missing. Run setup.cmd first, then start.cmd.")
    print("ATC GUARDIAN — SIMULATION ONLY\nOpen http://127.0.0.1:8000\nPress Ctrl+C to stop.")
    if not args.no_browser:
        timer = Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:8000"))
        timer.daemon = True
        timer.start()
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, workers=1)
