from dataclasses import replace
import pytest
from backend.engine import Engine, catalog
from backend.models import ClearanceInput, Settings
from backend.recorder import Recorder


@pytest.fixture
def engine():
    recorder=Recorder(":memory:")
    yield Engine(recorder)
    recorder.close()


def kinds(engine, kind):
    return [a for a in engine.alerts if a["kind"] == kind]


def test_missed_turn_persists_after_acknowledgement_and_resolves(engine):
    engine.advance(29)
    assert not kinds(engine,"CLEARANCE")
    engine.advance(1)
    alert=next(a for a in engine.alerts if a["title"]=="Turn not detected")
    engine.acknowledge(alert["id"])
    engine.advance(5)
    assert any(a["id"]==alert["id"] for a in engine.alerts)
    engine.control("N123AB","takeover")
    engine.control("N123AB","follow_turn")
    engine.advance(20)
    assert not any(a["id"]==alert["id"] for a in engine.alerts)
    assert engine.aircraft["N123AB"].control=="HUMAN"


def test_climb_towards_clearance_is_not_an_altitude_deviation(engine):
    engine.advance(60)
    assert not any(a["title"]=="Altitude deviation" for a in engine.alerts)
    assert engine.aircraft["N123AB"].altitude_ft==4100


def test_altitude_hold_deviation_is_detected(engine):
    a=engine.aircraft["N123AB"]
    a.clearance.altitude_reached=True
    a.altitude_ft=5600
    a.vertical_rate_fpm=0
    engine.refresh()
    assert any(a["title"]=="Altitude deviation" for a in engine.alerts)


@pytest.mark.parametrize("text,status",[("N123AB heading 310 altitude 4000","MISMATCH"),
 ("OTHER heading 310 altitude 5000","MISMATCH"),("climb five thousand, maybe","UNVERIFIED")])
def test_bad_readbacks_do_not_acknowledge_clearance(engine,text,status):
    engine.readback("N123AB",text)
    a=engine.aircraft["N123AB"]
    assert a.clearance.acknowledged_at is None
    assert a.clearance.readback==status
    assert a.control=="HUMAN"


def test_repeated_correct_readback_does_not_reset_timer(engine):
    engine.advance(20)
    engine.readback("N123AB","N123AB heading 310 altitude 5000")
    assert engine.aircraft["N123AB"].clearance.acknowledged_at==0


def test_stale_track_stops_predictions_and_does_not_revert_to_assistance(engine):
    engine.load("surveillance_loss")
    engine.advance(10)
    a=next(a for a in engine.snapshot()["aircraft"] if a["callsign"]=="N123AB")
    assert a["trajectory"]==[] and a["stale"]
    assert a["control"]=="HUMAN"
    with pytest.raises(ValueError): engine.control("N123AB","resume")
    engine.control("N123AB","restore_track")
    assert engine.aircraft["N123AB"].control=="HUMAN"
    engine.control("N123AB","resume")
    assert engine.aircraft["N123AB"].control=="ASSISTED"


def test_lost_weather_withholds_assessment_instead_of_resolving_hazard(engine):
    engine.simulation("weather_fail",1)
    engine.advance(120)
    assert not kinds(engine,"WEATHER")
    assert kinds(engine,"DATA")
    events=engine.recorder.events(engine.session)
    assert any(e["kind"]=="WITHHELD" and "Convective" in e["message"] for e in events)
    assert all(a.control=="HUMAN" for a in engine.aircraft.values())
    with pytest.raises(ValueError): engine.control("N123AB","resume")


def test_pilot_request_does_not_stop_physical_simulated_flight(engine):
    engine.control("N123AB","request_human")
    x=engine.aircraft["N123AB"].x_nm
    engine.advance(1)
    assert engine.aircraft["N123AB"].control=="HUMAN"
    assert engine.aircraft["N123AB"].x_nm < x


def test_clearance_requires_review_and_retains_superseded_history(engine):
    command=ClearanceInput(heading_deg=20,altitude_ft=5000)
    with pytest.raises(ValueError): engine.issue("N123AB",command)
    engine.issue("N123AB",command.model_copy(update={"reviewed":True}))
    a=engine.aircraft["N123AB"]
    assert a.history[-1]["heading_deg"]==310
    assert a.history[-1]["status"]=="SUPERSEDED"
    assert a.clearance.acknowledged_at is None


def test_screening_is_read_only_and_checks_turn_path(engine):
    before=engine.snapshot()
    result=engine.preview("N123AB",ClearanceInput(heading_deg=270,altitude_ft=5000))
    assert result["status"]=="REVIEW REQUIRED"
    assert any(f["kind"]=="WEATHER" for f in result["findings"])
    assert engine.snapshot()==before


def test_clearance_blocked_on_missing_data(engine):
    engine.control("N123AB","lose_track")
    assert engine.preview("N123AB",ClearanceInput(heading_deg=0,altitude_ft=5000))["status"]=="UNAVAILABLE"
    with pytest.raises(ValueError): engine.issue("N123AB",ClearanceInput(heading_deg=0,altitude_ft=5000,reviewed=True))


def test_turn_direction_and_360_wrap(engine):
    a=engine.aircraft["N123AB"]
    a.heading_deg=359
    a.pilot_follows_turn=True
    a.clearance.heading_deg=1
    a.clearance.turn="right"
    engine.move(a,1)
    assert a.heading_deg==1
    a.heading_deg=1
    a.clearance.heading_deg=359
    a.clearance.turn="left"
    engine.move(a,1)
    assert a.heading_deg==359


def test_alert_deduplication_and_new_session_does_not_erase_history(engine):
    engine.advance(40)
    session=engine.session
    before=engine.recorder.events(session)
    engine.refresh()
    assert engine.recorder.events(session)==before
    engine.load("crossing_traffic")
    assert engine.recorder.events(session)==before
    assert engine.session!=session


@pytest.mark.parametrize("scenario",[s["id"] for s in catalog()])
def test_every_preset_runs_and_exports(engine,scenario):
    engine.load(scenario)
    engine.advance(300)
    export=engine.export()
    assert export["simulation_only"] is True
    assert export["events"] and engine.now==300
    assert all(a.altitude_ft>=0 for a in engine.aircraft.values())


def test_duration_limit_stops_without_clearing_monitoring(engine):
    engine.settings=replace(Settings(),session_limit_s=35)
    engine.running=True
    engine.advance(50)
    assert engine.now==35 and not engine.running
    assert kinds(engine,"CLEARANCE")
    with pytest.raises(ValueError): engine.simulation("play",1)


def test_escalated_severity_requires_new_acknowledgement(engine):
    engine.load("crossing_traffic")
    alert=kinds(engine,"TRAFFIC")[0]
    assert alert["severity"]=="WARNING"
    engine.acknowledge(alert["id"])
    engine.advance(30)
    assert kinds(engine,"TRAFFIC")[0]["severity"]=="CRITICAL"
    assert alert["id"] not in engine.acknowledged
    assert any(e["kind"]=="SEVERITY" for e in engine.recorder.events(engine.session))
