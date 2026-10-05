# Run ATC Guardian on your computer

You do not need a server account, an AI subscription, an ADS-B receiver, or an API key. Everything you see is simulated.

## Windows: first installation

1. Install [Python 3.12](https://www.python.org/downloads/) and enable the installer's Python launcher/PATH option when available.
2. Install [Node.js](https://nodejs.org/en/download) version 22.12 or newer. The tested environment used Node 24.
3. Right-click the downloaded ZIP and choose **Extract All**. Open the extracted `atc-guardian` folder. Do not run it from inside the ZIP preview.
4. Double-click **setup.cmd**. It creates an isolated Python environment, installs pinned dependencies, builds the interface, and runs Python tests. Let the window finish; the first installation needs internet.
5. Double-click **start.cmd**. Leave that console open. Your browser should open at **http://127.0.0.1:8000**; you can enter that address manually if needed.
6. Click **+30 sec** to reproduce the missed-turn warning. Follow [DEMO.md](DEMO.md).

After installation, launch with `start.cmd`. To stop, focus its console and press **Ctrl+C**. Restarting opens a fresh paused demo. Prior session events stay in `data/guardian.sqlite3`; scenario motion is not restored from disk.

## macOS or Linux

Install Python 3.12 and Node 22.12+ first. In the extracted folder:

```bash
bash setup.sh
.venv/bin/python run.py
```

To avoid opening a browser automatically:

```bash
.venv/bin/python run.py --no-browser
```

## Where the pieces live

| Piece | What it does |
| --- | --- |
| Python | Moves the synthetic aircraft, owns clearances, checks risks, and writes events |
| FastAPI | Accepts interface commands and streams current state |
| React | Draws radar, shows findings, and sends your actions to Python |
| SQLite | Stores event history in `data/guardian.sqlite3` |
| Node.js | Installs/builds the interface; not needed to run an already built UI |

## Common setup problems

| Message or symptom | Next step |
| --- | --- |
| Python or Node not found | Install it, close the old console, and run setup again |
| Build requires newer Node | Check `node --version`; use Node 22.12+ or 24 |
| Missing interface | Run setup again, or `npm ci` and `npm run build` in `frontend` |
| Address already in use | Close your previous Guardian console, then restart; do not run multiple backend copies |
| Browser says connection unavailable | Confirm the launch console is running; inspect its latest error, then reload the page |
| Windows firewall prompt | The launcher only needs local loopback access; do not configure public/LAN hosting |
| Restore assistance rejected | Correct the readback and restore interrupted feeds first; then explicitly restore assistance |
| 30-minute scenario limit | Reset or load a preset to begin a new session |

## Development with immediate interface updates

In terminal one, at the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

In terminal two:

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173**. Frontend edits update there automatically. Backend reload resets the active scenario into a new session. Do not use multiple Uvicorn workers.

For macOS/Linux, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`.

## Tests

Run `python -m pytest` using the virtual environment's Python. Run `npm run build` from `frontend` to check TypeScript and rebuild.

To run browser tests, leave `start.cmd` running, then in `frontend` run `npx playwright install chromium` once and `npm run test:e2e`. Browser-test installation is optional for ordinary use. Tests reset the active simulation, so export any current experiment first.

The launcher scripts target Windows, but this handoff was executed and visually checked on Linux; the included Windows CI job remains to be run on GitHub.
