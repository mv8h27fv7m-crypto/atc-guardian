# ATC Guardian v0.1 — start here, Manny

Your first working GitHub project is in **ATC_Guardian_v0.1.0.zip**. It includes the source code, a professional README, screenshots, five scenarios, 51 automated checks, setup scripts, and a roadmap that preserves your larger idea.

## Run it on Windows

1. Install **Python 3.12** and **Node.js 22.12 or newer** if you do not already have them.
2. Right-click the ZIP → **Extract All**.
3. Open the extracted **atc-guardian** folder.
4. Double-click **setup.cmd** once. It installs dependencies, builds the app, and checks the Python code. Internet is needed for installation.
5. Double-click **start.cmd**. The app opens at **http://127.0.0.1:8000**. Keep the launch window open while using it.
6. Click **+30 sec**. You will see your C172 missed-turn example become an active warning.

Tested here on Linux with desktop and mobile browser checks. The Windows launchers are provided, but were not executed on Windows in this environment.

## Put it on GitHub

Use **atc-guardian** as the repository name. Upload the extracted source, with **README.md** at the repository's top level. Do not upload only the ZIP.

Follow **docs/GITHUB.md** inside the project for the exact steps. The project has not been published to your GitHub account yet.

## What to open first

| File | Purpose |
| --- | --- |
| README.md | The page people will see on GitHub |
| docs/DEMO.md | Walk through your aviation idea in the running app |
| docs/LEARNING_GUIDE.md | Understand the code one subsystem at a time |
| docs/GETTING_STARTED.md | Detailed setup and troubleshooting |
| docs/GITHUB.md | Upload and maintain the repository |
| ROADMAP.md | Build toward your larger research vision |

This version uses deterministic simulation and safety checks. AI models, automated voice, and real aircraft/weather feeds are future work. It is research software and must not be used to direct real aircraft.
