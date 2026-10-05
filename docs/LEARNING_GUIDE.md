# Understand the project one piece at a time

Start with one aircraft and one warning. You do not need to understand React, Python, databases, and aviation assurance all at once.

## 1. Read a scenario

Open `scenarios/missed_turn.json`. It is data, not code. `x_nm` is east/west position, `y_nm` is north/south position, `speed_kt` is knots. `pilot_follows_turn: false` is the deliberately injected fault. These values are synthetic; the C172 label does not certify the movement model as C172 performance.

Exercise: duplicate the JSON file, change its `id` and `name`, and give the aircraft a different starting position. Restart the backend. The scenario catalog reads those files. Keep callsigns unique and use finite numeric values; scenario files are trusted developer fixtures, not validated external feeds.

## 2. Read the aircraft data model

Open `backend/models.py`. `Aircraft` is the computer's current observation of one airplane. `Clearance` stores the instruction and its lifecycle. `Settings` names the experimental thresholds and their units.

The altitude of an aircraft and its assigned altitude are deliberately different fields. Without that distinction, software could accidentally confuse what should happen with what actually happened.

## 3. Follow one second of motion

In `backend/engine.py`, read `advance()` and then `move()`. Time advances in steps of at most one simulated second. The aircraft turns and climbs only when the scripted pilot has acknowledged its clearance. A missing-turn fault prevents the turn but permits the climb.

Exercise: in a separate branch, change `turn_grace_s` in `Settings` from 30 to 45. Update the specific missed-turn timing test to match your new requirement. Explain why the warning now appears later.

## 4. Inspect the safety checks

Read `backend/geometry.py`, then `backend/monitor.py`. Geometry answers “when are these paths inside the same research volume?” The monitor turns that result into an alert with aircraft identities, evidence, and urgency. It does not issue a new clearance.

At 120 knots, an aircraft travels 2 NM in a minute: `120 / 3600 * 60`. North/east velocity comes from heading and trigonometry. The traffic check finds an interval of horizontal proximity and a second interval of vertical proximity, then checks their overlap.

Exercise: read `test_vertical_conflict_away_from_horizontal_cpa_is_detected`. Draw the two altitude profiles and explain why measuring vertical distance only at horizontal CPA could miss a conflict.

## 5. Trace a button

The **Pilot requests human** button in `frontend/src/main.tsx` sends an HTTP command. `backend/app.py` validates it. `Engine.control()` changes ownership and writes an event. The next WebSocket snapshot redraws the interface.

The browser does not directly edit authoritative aircraft state. A changed label in the browser would not change the Python engine.

## 6. Inspect an event record

`backend/recorder.py` writes SQLite rows. A row includes the session, simulated timestamp, actual UTC recording timestamp, event type, callsign, message, and structured details. Reset creates a new session, preserving earlier rows. JSON export makes the current session inspectable without a database viewer.

## 7. Make your first small commit

Choose one meaningful change: an additional synthetic scenario, a clearer alert explanation, or a test for a geometry boundary. Run the affected checks, describe the behavior you changed in CHANGELOG.md, and commit it. Those incremental changes build your understanding and an honest development history.

## What comes later

An AI model could propose structured interpretations of radio text. It must not replace these state and geometry checks, and its confidence would need calibration against representative data. That integration does not exist in v0.1; your first goal is understanding the baseline well enough to test any future model against it.
