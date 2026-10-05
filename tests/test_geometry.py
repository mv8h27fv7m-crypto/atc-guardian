"""Behavioral tests for time, unit, and geometry errors that matter to alerts."""
from dataclasses import replace
import pytest
from backend.geometry import angle_error, conflict, horizontal_interval, projected, weather_intersection
from backend.models import Aircraft, Settings, WeatherZone


def aircraft(**kwargs):
    return Aircraft(**{**dict(callsign="A", aircraft_type="synthetic", x_nm=0, y_nm=0,
                             altitude_ft=5000, heading_deg=90, speed_kt=120), **kwargs})


@pytest.mark.parametrize("target,current,expected", [(1,359,2),(359,1,-2),(0,180,-180),(90,90,0)])
def test_heading_wrap(target,current,expected):
    assert angle_error(target,current) == expected


def test_knots_and_minutes_are_converted_to_nm_and_feet():
    a = aircraft(vertical_rate_fpm=600)
    assert projected(a,60) == pytest.approx((2,0,5600))


def test_crossing_at_same_altitude():
    a = aircraft(x_nm=-5,speed_kt=180)
    b = aircraft(callsign="B",y_nm=-5,heading_deg=0,speed_kt=180)
    result = conflict(a,b,Settings())
    assert result["cpa_s"] == pytest.approx(100)
    assert result["horizontal_nm"] == pytest.approx(0)
    assert result["entry_s"] == pytest.approx(57.6)


def test_horizontal_nearness_alone_is_not_a_3d_conflict():
    assert conflict(aircraft(),aircraft(altitude_ft=8000),Settings()) is None


def test_vertical_conflict_away_from_horizontal_cpa_is_detected():
    # Horizontal CPA at t=0, but vertical overlap first happens at t=60.
    # A CPA-only altitude check would miss this conflict.
    a = aircraft(speed_kt=0)
    b = aircraft(callsign="B",x_nm=1,speed_kt=6,altitude_ft=7000,vertical_rate_fpm=-1000)
    result = conflict(a,b,Settings())
    assert result["cpa_s"] == 0
    assert result["entry_s"] == pytest.approx(60)
    assert result["vertical_ft_at_cpa"] == 2000


def test_parallel_velocity_and_already_inside_volume():
    assert conflict(aircraft(),aircraft(callsign="B",x_nm=1),Settings())["entry_s"] == 0
    assert conflict(aircraft(),aircraft(callsign="B",x_nm=5),Settings()) is None


def test_diverging_and_beyond_horizon_are_not_future_conflicts():
    assert conflict(aircraft(x_nm=10),aircraft(callsign="B",heading_deg=270),Settings()) is None
    assert conflict(aircraft(x_nm=-20),aircraft(callsign="B",x_nm=20,heading_deg=270),Settings()) is None


def test_tangent_and_stationary_weather_edges():
    assert horizontal_interval(-1,1,1,0,1,10) == pytest.approx((1,1))
    assert horizontal_interval(1,0,0,0,1,10) == (0,10)


def test_weather_uses_altitude_band_and_future_entry():
    zone = WeatherZone("Z","Icing","ICING",4,0,1,4000,7000)
    assert weather_intersection(aircraft(),zone,Settings()) == pytest.approx(90)
    assert weather_intersection(aircraft(altitude_ft=8000),zone,Settings()) is None
    assert weather_intersection(aircraft(),zone,replace(Settings(),lookahead_s=30)) is None
