"""Loopback-only FastAPI service, one shared simulation, one process/worker."""
import asyncio
from contextlib import asynccontextmanager, suppress
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .engine import Engine, catalog
from .models import ClearanceInput, ControlInput, ReadbackInput, ScenarioInput, SimulationInput
from .recorder import Recorder

ROOT = Path(__file__).resolve().parents[1]
ORIGINS = {f"http://{host}:{port}" for host in ("localhost", "127.0.0.1") for port in (8000, 5173)}


def create_app(db_path: str | None = None, tick: bool = True):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        recorder = Recorder(db_path or os.environ.get("ATC_DB_PATH", str(ROOT / "data" / "guardian.sqlite3")))
        app.state.engine = Engine(recorder)
        app.state.fault = None

        async def clock():
            try:
                while True:
                    await asyncio.sleep(.25)
                    if app.state.engine.running:
                        app.state.engine.advance(.25 * app.state.engine.speed)
            except asyncio.CancelledError:
                raise
            except Exception:
                # Stop the clock and surface a fault; never silently restart authority.
                app.state.engine.running = False
                for a in app.state.engine.aircraft.values():
                    a.control, a.human_reason = "HUMAN", "Simulation engine fault"
                app.state.fault = "Simulation engine stopped. Restart after investigating server logs."
                import logging
                logging.exception("Simulation clock failed")

        task = asyncio.create_task(clock()) if tick else None
        yield
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        recorder.close()

    app = FastAPI(title="ATC Guardian — Simulation API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])

    @app.middleware("http")
    async def local_origin(request: Request, call_next):
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            origin = request.headers.get("origin")
            if origin and origin not in ORIGINS:
                return JSONResponse({"detail": "Untrusted origin"}, status_code=403)
            if request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse({"detail": "Cross-site commands rejected"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(ValueError)
    async def invalid_input(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=400)

    def engine():
        if app.state.fault:
            raise HTTPException(503, app.state.fault)
        return app.state.engine

    @app.get("/api/state")
    async def state():
        return engine().snapshot()

    @app.get("/api/scenarios")
    async def scenarios():
        return [{key: s[key] for key in ("id", "name", "description")} for s in catalog()]

    @app.post("/api/scenario")
    async def load(body: ScenarioInput):
        engine().load(body.scenario)
        return engine().snapshot()

    @app.post("/api/simulation")
    async def simulation(body: SimulationInput):
        engine().simulation(body.action, body.value)
        return engine().snapshot()

    @app.post("/api/aircraft/{callsign}/control")
    async def control(callsign: str, body: ControlInput):
        engine().control(callsign, body.action)
        return engine().snapshot()

    @app.post("/api/aircraft/{callsign}/preview")
    async def preview(callsign: str, body: ClearanceInput):
        return engine().preview(callsign, body)

    @app.post("/api/aircraft/{callsign}/clearance")
    async def clearance(callsign: str, body: ClearanceInput):
        engine().issue(callsign, body)
        return engine().snapshot()

    @app.post("/api/aircraft/{callsign}/readback")
    async def readback(callsign: str, body: ReadbackInput):
        engine().readback(callsign, body.text)
        return engine().snapshot()

    @app.post("/api/alerts/{alert_id}/acknowledge")
    async def acknowledge(alert_id: str):
        engine().acknowledge(alert_id)
        return engine().snapshot()

    @app.get("/api/export")
    async def export():
        return JSONResponse(engine().export(), headers={"Content-Disposition": 'attachment; filename="atc-guardian-events.json"'})

    @app.websocket("/ws")
    async def stream(ws: WebSocket):
        if ws.headers.get("origin") not in ORIGINS:
            await ws.close(code=1008)
            return
        await ws.accept()
        try:
            while True:
                await ws.send_json({**app.state.engine.snapshot(), "system_fault": app.state.fault})
                await asyncio.sleep(.25)
        except (WebSocketDisconnect, RuntimeError, OSError):
            pass

    dist = ROOT / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="interface")
    return app


app = create_app()
