"""Planar research geometry. East/north in NM, true headings, seconds, feet.

These are synthetic protected volumes, NOT regulatory separation minima.
The interval method catches vertical/horizontal overlap away from horizontal CPA.
"""
from math import cos, hypot, radians, sin, sqrt

from .models import Aircraft, Settings, WeatherZone


def angle_error(target: float, current: float) -> float:
    return (target - current + 180) % 360 - 180


def velocity(aircraft: Aircraft) -> tuple[float, float]:
    angle = radians(aircraft.heading_deg)
    return sin(angle) * aircraft.speed_kt / 3600, cos(angle) * aircraft.speed_kt / 3600


def projected(aircraft: Aircraft, seconds: float) -> tuple[float, float, float]:
    vx, vy = velocity(aircraft)
    return (aircraft.x_nm + vx * seconds, aircraft.y_nm + vy * seconds,
            aircraft.altitude_ft + aircraft.vertical_rate_fpm * seconds / 60)


def horizontal_interval(x: float, y: float, vx: float, vy: float,
                        radius: float, horizon: float) -> tuple[float, float] | None:
    """Closed interval inside a disk, including tangency and zero speed."""
    a, b, c = vx * vx + vy * vy, 2 * (x * vx + y * vy), x * x + y * y - radius * radius
    if a < 1e-12:
        return (0, horizon) if c <= 0 else None
    discriminant = b * b - 4 * a * c
    if discriminant < -1e-12:
        return None
    root = sqrt(max(0, discriminant))
    start, end = max(0, (-b - root) / (2 * a)), min(horizon, (-b + root) / (2 * a))
    return (start, end) if start <= end else None


def vertical_interval(z: float, vz: float, low: float, high: float,
                      horizon: float) -> tuple[float, float] | None:
    if abs(vz) < 1e-12:
        return (0, horizon) if low <= z <= high else None
    a, b = sorted(((low - z) / vz, (high - z) / vz))
    start, end = max(0, a), min(horizon, b)
    return (start, end) if start <= end else None


def overlap(a: tuple | None, b: tuple | None) -> tuple[float, float] | None:
    if a is None or b is None:
        return None
    start, end = max(a[0], b[0]), min(a[1], b[1])
    return (start, end) if start <= end else None


def conflict(a: Aircraft, b: Aircraft, settings: Settings) -> dict | None:
    ax, ay = velocity(a)
    bx, by = velocity(b)
    x, y, vx, vy = b.x_nm - a.x_nm, b.y_nm - a.y_nm, bx - ax, by - ay
    z = b.altitude_ft - a.altitude_ft
    vz = (b.vertical_rate_fpm - a.vertical_rate_fpm) / 60
    interval = overlap(horizontal_interval(x, y, vx, vy, settings.horizontal_nm, settings.lookahead_s),
                       vertical_interval(z, vz, -settings.vertical_ft, settings.vertical_ft, settings.lookahead_s))
    if interval is None:
        return None
    speed2 = vx * vx + vy * vy
    cpa_s = max(0, min(settings.lookahead_s, -(x * vx + y * vy) / speed2)) if speed2 > 1e-12 else 0
    return {"entry_s": round(interval[0], 1), "exit_s": round(interval[1], 1),
            "cpa_s": round(cpa_s, 1), "horizontal_nm": round(hypot(x + vx * cpa_s, y + vy * cpa_s), 2),
            "vertical_ft_at_cpa": round(abs(z + vz * cpa_s))}


def weather_intersection(a: Aircraft, zone: WeatherZone, settings: Settings) -> float | None:
    vx, vy = velocity(a)
    interval = overlap(horizontal_interval(a.x_nm - zone.x_nm, a.y_nm - zone.y_nm, vx, vy,
                                           zone.radius_nm, settings.lookahead_s),
                       vertical_interval(a.altitude_ft, a.vertical_rate_fpm / 60,
                                         zone.floor_ft, zone.ceiling_ft, settings.lookahead_s))
    return round(interval[0], 1) if interval else None
