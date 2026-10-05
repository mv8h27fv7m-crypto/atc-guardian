import pytest
from fastapi.testclient import TestClient
from backend.app import create_app


@pytest.fixture
def client():
    with TestClient(create_app(":memory:",tick=False)) as c:
        yield c


def test_state_scenario_and_event_export(client):
    assert client.get("/api/state").json()["version"]=="0.1.0"
    assert len(client.get("/api/scenarios").json())==5
    assert client.post("/api/simulation",json={"action":"step","value":30}).json()["time_s"]==30
    assert client.get("/api/export").json()["events"]


@pytest.mark.parametrize("body",[{"heading_deg":360,"altitude_ft":5000},
 {"heading_deg":20.5,"altitude_ft":5000},
 {"heading_deg":20,"altitude_ft":-10},{"heading_deg":20,"altitude_ft":5000,"arbitrary":"value"}])
def test_invalid_clearances_are_rejected(client,body):
    assert client.post("/api/aircraft/N123AB/clearance",json=body).status_code==422


def test_cross_origin_commands_rejected(client):
    assert client.post("/api/simulation",json={"action":"play"},headers={"origin":"https://example.com"}).status_code==403


def test_unknown_targets_and_unreviewed_clearances_rejected(client):
    assert client.post("/api/aircraft/UNKNOWN/control",json={"action":"takeover"}).status_code==400
    assert client.post("/api/scenario",json={"scenario":"unknown"}).status_code==400
    assert client.post("/api/aircraft/N123AB/clearance",json={"heading_deg":20,"altitude_ft":5000}).status_code==400


def test_websocket_stream_is_actual_shared_state(client):
    with client.websocket_connect("/ws",headers={"origin":"http://127.0.0.1:8000"}) as ws:
        state=ws.receive_json()
        assert state["scenario"]=="missed_turn"
        assert len(state["aircraft"])==4


def test_invalid_websocket_origin_rejected(client):
    from starlette.websockets import WebSocketDisconnect
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws",headers={"origin":"https://example.com"}):
            pass


def test_takeover_all_preserves_tracks(client):
    state=client.post("/api/simulation",json={"action":"takeover_all"}).json()
    assert all(a["control"]=="HUMAN" for a in state["aircraft"])
    assert len(state["aircraft"])==4
