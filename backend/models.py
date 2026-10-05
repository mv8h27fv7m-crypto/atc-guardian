"""Explicit units keep geometry, simulation, and presentation easy to inspect."""
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True)
class Settings:
    lookahead_s: float = 300
    horizontal_nm: float = 3
    vertical_ft: float = 1000
    turn_grace_s: float = 30
    heading_tolerance_deg: float = 5
    altitude_tolerance_ft: float = 150
    surveillance_stale_s: float = 10
    weather_stale_s: float = 120
    turn_rate_deg_s: float = 3
    climb_rate_fpm: float = 600
    session_limit_s: float = 1800


@dataclass
class Clearance:
    id: str
    heading_deg: float
    altitude_ft: float
    turn: str
    issued_at: float
    initial_heading_deg: float
    initial_altitude_ft: float
    status: str = "AWAITING READBACK"
    acknowledged_at: float | None = None
    heading_reached: bool = False
    altitude_reached: bool = False
    readback: str = "AWAITING"


@dataclass
class Aircraft:
    callsign: str
    aircraft_type: str
    x_nm: float
    y_nm: float
    altitude_ft: float
    heading_deg: float
    speed_kt: float
    squawk: str = "1200"
    vertical_rate_fpm: float = 0
    last_seen_s: float = 0
    feed_available: bool = True
    pilot_follows_turn: bool = True
    control: str = "ASSISTED"
    human_reason: str | None = None
    clearance: Clearance | None = None
    history: list[dict] = field(default_factory=list)
    trail: list[list[float]] = field(default_factory=list)


@dataclass
class WeatherZone:
    id: str
    label: str
    kind: str
    x_nm: float
    y_nm: float
    radius_nm: float
    floor_ft: float
    ceiling_ft: float
    severity: str = "WARNING"


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ClearanceInput(Input):
    heading_deg: int = Field(ge=0, lt=360)
    altitude_ft: int = Field(ge=0, le=20000)
    turn: Literal["left", "right"] = "right"
    reviewed: bool = False


class ReadbackInput(Input):
    text: str = Field(min_length=1, max_length=200)


class ControlInput(Input):
    action: Literal["takeover", "request_human", "resume", "follow_turn", "miss_turn", "lose_track", "restore_track"]


class SimulationInput(Input):
    action: Literal["play", "pause", "step", "speed", "weather_fail", "weather_restore", "takeover_all"]
    value: int = Field(default=1, ge=1, le=30)


class ScenarioInput(Input):
    scenario: str = Field(pattern=r"^[a-z_]{1,40}$")
