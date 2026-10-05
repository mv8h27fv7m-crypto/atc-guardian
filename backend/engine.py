"""Single authoritative simulation state. All commands enter here, not the UI."""
from copy import deepcopy
from dataclasses import asdict
import json
from math import copysign
from pathlib import Path
import re
from uuid import uuid4

from .geometry import angle_error, projected
from .models import Aircraft, Clearance, ClearanceInput, Settings, WeatherZone
from .monitor import evaluate
from .recorder import Recorder

SCENARIOS = Path(__file__).resolve().parents[1] / "scenarios"


def catalog() -> list[dict]:
    return [json.loads(path.read_text()) for path in sorted(SCENARIOS.glob("*.json"))]


class Engine:
    def __init__(self, recorder: Recorder, settings: Settings | None = None):
        self.recorder, self.settings = recorder, settings or Settings()
        self.load("missed_turn")

    def event(self, kind: str, message: str, callsign=None, data=None):
        self.recorder.record(self.session, self.now, kind, message, callsign, data)

    def load(self, scenario_id: str):
        scenario = next((s for s in catalog() if s["id"] == scenario_id), None)
        if scenario is None:
            raise ValueError("Unknown scenario")
        self.session, self.scenario = str(uuid4()), scenario
        self.now, self.running, self.speed = 0.0, False, 1
        self.weather_available, self.weather_updated = True, 0.0
        self.aircraft = {item["callsign"]: Aircraft(**item) for item in scenario["aircraft"]}
        self.weather = [WeatherZone(**item) for item in scenario.get("weather", [])]
        self.alerts, self.acknowledged = [], set()
        self.recorder.begin(self.session, scenario_id, asdict(self.settings))
        self.event("SESSION", f"Loaded {scenario['name']}. Simulation paused.", data={"scenario": scenario})
        for item in scenario.get("clearances", []):
            self.issue(item["callsign"], ClearanceInput(**item["clearance"], reviewed=True))
            self.readback(item["callsign"], item["readback"])
        self.refresh()

    def aircraft_by_id(self, callsign: str) -> Aircraft:
        if callsign not in self.aircraft:
            raise ValueError("Unknown aircraft")
        return self.aircraft[callsign]

    def preview(self, callsign: str, command: ClearanceInput) -> dict:
        """Screen a proposal through the same turn/climb model as the simulator.

        Other aircraft follow current velocity. This is a conditional experiment,
        not a clearance safety guarantee; uncertainty envelopes are future work.
        """
        source = self.aircraft_by_id(callsign)
        unknown = []
        if self.now - self.weather_updated >= self.settings.weather_stale_s:
            unknown.append("Weather data is stale")
        if not self.weather_available:
            unknown.append("Weather feed is interrupted")
        if any(not a.feed_available or self.now - a.last_seen_s >= self.settings.surveillance_stale_s for a in self.aircraft.values()):
            unknown.append("One or more aircraft observations are unavailable")
        candidate = deepcopy(source)
        candidate.pilot_follows_turn = True
        candidate.clearance = Clearance("preview", command.heading_deg, command.altitude_ft,
                                        command.turn, self.now, candidate.heading_deg, candidate.altitude_ft,
                                        acknowledged_at=self.now, readback="MATCH")
        others = [deepcopy(a) for a in self.aircraft.values() if a.callsign != callsign]
        found = {}
        # Per-second swept intervals avoid skipping collisions between samples.
        segment_settings = Settings(**{**asdict(self.settings), "lookahead_s": 1})
        for second in range(int(self.settings.lookahead_s)):
            findings = evaluate([candidate, *others], self.weather, self.now + second,
                                0, segment_settings)
            for finding in findings:
                if finding["kind"] in ("TRAFFIC", "WEATHER") and callsign in finding["aircraft"]:
                    found.setdefault(finding["id"], {**finding, "first_detected_s": second})
            self.move(candidate, 1)
            for other in others:
                other.x_nm, other.y_nm, other.altitude_ft = projected(other, 1)
            for a in [candidate, *others]:
                a.last_seen_s = self.now + second + 1
        return {"status": "UNAVAILABLE" if unknown else "REVIEW REQUIRED" if found else "NO MODELED CONFLICT",
                "unknown": unknown, "findings": list(found.values()),
                "assumptions": "Immediate correct readback; 3°/s turn; 600 ft/min climb/descent; other traffic maintains current velocity; static weather. No terrain/runway/wake checks."}

    def issue(self, callsign: str, command: ClearanceInput) -> dict:
        a = self.aircraft_by_id(callsign)
        result = self.preview(callsign, command)
        if not command.reviewed:
            raise ValueError("Controller review is required for every simulated clearance")
        if result["status"] == "UNAVAILABLE":
            raise ValueError("Clearance experiment blocked: data unavailable. Restore feeds first.")
        if a.clearance:
            previous = asdict(a.clearance)
            previous["status"] = "SUPERSEDED"
            a.history.append(previous)
        a.clearance = Clearance(str(uuid4()), command.heading_deg, command.altitude_ft, command.turn,
                                self.now, a.heading_deg, a.altitude_ft)
        self.event("CLEARANCE", "Human-approved simulated clearance; awaiting readback.", callsign,
                   {"clearance": asdict(a.clearance), "screening": result})
        self.refresh()
        return result

    def readback(self, callsign: str, text: str):
        a = self.aircraft_by_id(callsign)
        c = a.clearance
        if c is None:
            raise ValueError("No clearance to read back")
        match = re.fullmatch(r"([A-Z0-9]+)\s+heading\s+(\d{1,3})\s+altitude\s+(\d{1,5})\s*\.?", text.strip(), re.I)
        correct = bool(match and match[1].upper() == callsign and
                       int(match[2]) == c.heading_deg and int(match[3]) == c.altitude_ft)
        # Never let a second identical readback reset compliance timers.
        if correct:
            if c.acknowledged_at is None:
                c.acknowledged_at = self.now
            c.readback = "MATCH"
            c.status = "ACKNOWLEDGED"
        else:
            c.readback = "MISMATCH" if match else "UNVERIFIED"
            c.status = "AWAITING CORRECTION"
            c.acknowledged_at = None
            self.human(a, "Readback requires human verification")
        self.event("READBACK", c.readback, callsign, {"text": text, "clearance_id": c.id})
        self.refresh()

    def human(self, a: Aircraft, reason: str):
        if a.control != "HUMAN":
            a.control, a.human_reason = "HUMAN", reason
            self.event("HUMAN", reason, a.callsign)

    def control(self, callsign: str, action: str):
        a = self.aircraft_by_id(callsign)
        if action in ("takeover", "request_human"):
            self.human(a, "Pilot requested human" if action == "request_human" else "Controller took ownership")
        elif action == "resume":
            blockers = [x for x in self.alerts if x["kind"] in ("DATA", "READBACK") and (not x["aircraft"] or callsign in x["aircraft"])]
            if blockers or not a.feed_available or not self.weather_available:
                raise ValueError("Resolve data/readback faults before explicitly restoring assistance")
            a.control, a.human_reason = "ASSISTED", None
        elif action in ("follow_turn", "miss_turn"):
            a.pilot_follows_turn = action == "follow_turn"
        elif action in ("lose_track", "restore_track"):
            a.feed_available = action == "restore_track"
            if a.feed_available:
                a.last_seen_s = self.now
            else:
                self.human(a, "Synthetic surveillance interrupted")
        else:
            raise ValueError("Unknown control action")
        self.event("CONTROL", action, callsign)
        self.refresh()

    def move(self, a: Aircraft, dt: float):
        c = a.clearance
        if c and c.acknowledged_at is not None:
            if a.pilot_follows_turn:
                distance = ((c.heading_deg - a.heading_deg) % 360) if c.turn == "right" else ((a.heading_deg - c.heading_deg) % 360)
                step = min(distance, self.settings.turn_rate_deg_s * dt)
                a.heading_deg = (a.heading_deg + step * (1 if c.turn == "right" else -1)) % 360
            change = c.altitude_ft - a.altitude_ft
            delta = copysign(min(abs(change), self.settings.climb_rate_fpm * dt / 60), change)
            a.vertical_rate_fpm = delta * 60 / dt if dt else 0
            a.altitude_ft += delta
            if a.altitude_ft == c.altitude_ft:
                a.vertical_rate_fpm = 0
            if abs(angle_error(c.heading_deg, a.heading_deg)) <= self.settings.heading_tolerance_deg:
                c.heading_reached = True
            if abs(change) <= self.settings.altitude_tolerance_ft:
                c.altitude_reached = True
            within = abs(angle_error(c.heading_deg, a.heading_deg)) <= self.settings.heading_tolerance_deg and abs(c.altitude_ft-a.altitude_ft) <= self.settings.altitude_tolerance_ft
            c.status = "COMPLETED · MONITORING" if within else "COMPLYING" if a.pilot_follows_turn else "TURN PENDING"
        else:
            a.altitude_ft += a.vertical_rate_fpm * dt / 60
        a.x_nm, a.y_nm, _ = projected(a, dt)

    def advance(self, seconds: float):
        # Bound step size; fast playback still evaluates every simulated second.
        remaining = min(seconds, max(0, self.settings.session_limit_s - self.now))
        while remaining > 1e-9:
            dt = min(1.0, remaining)
            self.now += dt
            for a in self.aircraft.values():
                if a.feed_available:
                    old_status = a.clearance.status if a.clearance else None
                    self.move(a, dt)
                    a.last_seen_s = self.now
                    a.trail.append([round(a.x_nm, 4), round(a.y_nm, 4)])
                    a.trail = a.trail[-45:]
                    if a.clearance and a.clearance.status != old_status:
                        self.event("COMPLIANCE", a.clearance.status, a.callsign)
            if self.weather_available:
                self.weather_updated = self.now
            self.refresh()
            remaining -= dt
        if self.now >= self.settings.session_limit_s and self.running:
            self.running = False
            self.event("SYSTEM", "30-minute scenario limit reached; load a scenario to restart.")

    def refresh(self):
        current = evaluate(list(self.aircraft.values()), self.weather, self.now,
                           self.now - self.weather_updated, self.settings)
        previous = {a["id"]: a for a in self.alerts}
        active = {a["id"]: a for a in current}
        for key, item in active.items():
            if key not in previous:
                self.event("ALERT", item["title"], ", ".join(item["aircraft"]) or None, item)
            elif item["severity"] != previous[key]["severity"]:
                self.acknowledged.discard(key)
                self.event("SEVERITY", f"{previous[key]['severity']} to {item['severity']}",
                           ", ".join(item["aircraft"]) or None, item)
            if item["kind"] == "DATA":
                targets = item["aircraft"] or list(self.aircraft)
                for callsign in targets:
                    self.human(self.aircraft[callsign], "Data integrity requires human review")
        for key, item in previous.items():
            if key not in active:
                unavailable = any(self.now-self.aircraft[c].last_seen_s >= self.settings.surveillance_stale_s for c in item["aircraft"])
                unavailable |= item["kind"] == "WEATHER" and self.now-self.weather_updated >= self.settings.weather_stale_s
                self.event("WITHHELD" if unavailable else "RESOLVED", item["title"],
                           ", ".join(item["aircraft"]) or None, {"alert_id": key,
                           "reason": "Assessment unavailable; not evidence of safety" if unavailable else "Condition no longer detected"})
                self.acknowledged.discard(key)
        self.alerts = current

    def acknowledge(self, alert_id: str):
        if alert_id not in {a["id"] for a in self.alerts}:
            raise ValueError("Alert is no longer active")
        if alert_id not in self.acknowledged:
            self.acknowledged.add(alert_id)
            self.event("ACKNOWLEDGED", "Alert acknowledged; monitoring remains active.", data={"alert_id": alert_id})

    def simulation(self, action: str, value: int):
        if action == "play":
            if self.now >= self.settings.session_limit_s:
                raise ValueError("Scenario complete; reload to restart")
            self.running = True
        elif action == "pause":
            self.running = False
        elif action == "step":
            self.running = False
            self.advance(value)
        elif action == "speed":
            if value not in (1, 2, 4):
                raise ValueError("Speed must be 1, 2, or 4")
            self.speed = value
        elif action in ("weather_fail", "weather_restore"):
            self.weather_available = action == "weather_restore"
            if self.weather_available:
                self.weather_updated = self.now
            else:
                for a in self.aircraft.values():
                    self.human(a, "Synthetic weather feed interrupted")
        elif action == "takeover_all":
            for a in self.aircraft.values():
                self.human(a, "Sector-wide human takeover")
        else:
            raise ValueError("Unknown simulation action")
        self.event("SIMULATION", action, data={"value": value})
        self.refresh()

    def snapshot(self):
        aircraft = []
        for a in self.aircraft.values():
            stale = self.now - a.last_seen_s >= self.settings.surveillance_stale_s
            aircraft.append({**asdict(a), "track_deg": a.heading_deg, "stale": stale,
                             "age_s": round(self.now-a.last_seen_s, 1),
                             "trajectory": [] if stale else [list(projected(a, t)) for t in (0, 30, 60, 120, 300)]})
        return {"version": "0.1.0", "session": self.session, "time_s": round(self.now, 2),
                "running": self.running, "speed": self.speed, "scenario": self.scenario["id"],
                "scenario_name": self.scenario["name"], "description": self.scenario["description"],
                "aircraft": aircraft, "weather": [asdict(w) for w in self.weather],
                "weather_age_s": round(self.now-self.weather_updated, 1), "weather_available": self.weather_available,
                "weather_stale": self.now-self.weather_updated >= self.settings.weather_stale_s,
                "alerts": [{**a, "acknowledged": a["id"] in self.acknowledged} for a in self.alerts],
                "events": self.recorder.events(self.session, 45), "settings": asdict(self.settings)}

    def export(self):
        return {"format": "atc-guardian-event-export-v1", "simulation_only": True,
                "note": "Event record plus final state, not a complete trajectory recording or incident replay.",
                "scenario": self.scenario, "final_state": self.snapshot(),
                "events": list(reversed(self.recorder.events(self.session)))}
