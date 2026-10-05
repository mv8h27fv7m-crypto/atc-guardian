"""Pure monitoring: observe state and return explainable findings; never command."""
from itertools import combinations

from .geometry import angle_error, conflict, weather_intersection
from .models import Aircraft, Settings, WeatherZone

SEVERITY = {"CRITICAL": 0, "WARNING": 1, "CAUTION": 2, "ADVISORY": 3, "INFORMATION": 4}


def evaluate(aircraft: list[Aircraft], weather: list[WeatherZone], now: float,
             weather_age: float, settings: Settings) -> list[dict]:
    alerts = []

    def add(key, severity, kind, subjects, title, detail, evidence=None):
        alerts.append(dict(id=key, severity=severity, kind=kind, aircraft=subjects,
                           title=title, detail=detail, evidence=evidence or {}))

    wx_stale = weather_age >= settings.weather_stale_s
    if wx_stale:
        add("weather-feed", "WARNING", "DATA", [], "Weather assessment unavailable",
            f"Synthetic weather is {weather_age:.0f}s old. Human review required.")
    fresh = []
    for a in aircraft:
        age = now - a.last_seen_s
        if age >= settings.surveillance_stale_s:
            add(f"stale:{a.callsign}", "WARNING", "DATA", [a.callsign], "Surveillance unavailable",
                f"Last observation {age:.0f}s ago. Prediction and compliance assessment withheld.")
            continue
        fresh.append(a)
        c = a.clearance
        if c:
            elapsed = now - (c.acknowledged_at if c.acknowledged_at is not None else c.issued_at)
            if c.readback in ("MISMATCH", "UNVERIFIED"):
                add(f"readback:{a.callsign}", "WARNING", "READBACK", [a.callsign], "Readback requires correction",
                    "Mismatch or unsupported text. Clearance is not acknowledged; verify with the pilot.")
            elif c.acknowledged_at is None and elapsed >= 15:
                add(f"readback:{a.callsign}", "CAUTION", "READBACK", [a.callsign], "Awaiting pilot readback",
                    f"No verified readback after {elapsed:.0f}s.")
            if c.acknowledged_at is not None:
                error = abs(angle_error(c.heading_deg, a.heading_deg))
                progress = abs(angle_error(a.heading_deg, c.initial_heading_deg))
                if error > settings.heading_tolerance_deg and elapsed >= settings.turn_grace_s:
                    # A long but progressing turn is not a missed turn.
                    if progress < 3 or c.heading_reached or elapsed > 150:
                        add(f"heading:{a.callsign}", "CAUTION", "CLEARANCE", [a.callsign],
                            "Heading deviation" if c.heading_reached else "Turn not detected" if progress < 3 else "Turn completion overdue",
                            f"Assigned {c.heading_deg:03.0f}° · observed {a.heading_deg:03.0f}° · {elapsed:.0f}s since readback.",
                            {"assigned_heading_deg": c.heading_deg, "observed_heading_deg": a.heading_deg})
                altitude_error = c.altitude_ft - a.altitude_ft
                if abs(altitude_error) > settings.altitude_tolerance_ft:
                    moving_away = altitude_error * a.vertical_rate_fpm < 0
                    stalled = abs(a.vertical_rate_fpm) < 50 and elapsed >= 30
                    if c.altitude_reached or moving_away or stalled:
                        add(f"altitude:{a.callsign}", "WARNING", "CLEARANCE", [a.callsign], "Altitude deviation",
                            f"Assigned {c.altitude_ft:,.0f} ft · observed {a.altitude_ft:,.0f} ft. Human review required.")
        if not wx_stale:
            for zone in weather:
                eta = weather_intersection(a, zone, settings)
                if eta is not None:
                    add(f"weather:{a.callsign}:{zone.id}", zone.severity, "WEATHER", [a.callsign],
                        f"{zone.label} on projected path", f"Entry in {eta:.0f}s under constant current velocity. Synthetic hazard.",
                        {"entry_s": eta, "zone": zone.id})
    for a, b in combinations(fresh, 2):
        result = conflict(a, b, settings)
        if result:
            add(f"traffic:{':'.join(sorted([a.callsign, b.callsign]))}",
                "CRITICAL" if result["entry_s"] <= 60 else "WARNING", "TRAFFIC", [a.callsign, b.callsign],
                "Predicted traffic conflict", f"Research volume entry in {result['entry_s']:.0f}s · horizontal CPA {result['horizontal_nm']:.2f} NM.", result)
    return sorted(alerts, key=lambda a: (SEVERITY[a["severity"]], a["id"]))
