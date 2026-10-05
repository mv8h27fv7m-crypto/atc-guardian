import { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import type { Aircraft, Preview, Scenario, State } from "./types";
import "./style.css";

const time = (s: number) =>
  `${Math.floor(s / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(s % 60)
    .toString()
    .padStart(2, "0")}`;
const hdg = (n: number) => `${Math.round(n).toString().padStart(3, "0")}°`;
const fmt = (n: number) => Math.round(n).toLocaleString("en-US");
const point = (x: number, y: number) => [400 + x * 20, 320 - y * 20];
function Mark({ small = false }: { small?: boolean }) {
  return (
    <svg
      width={small ? 22 : 36}
      height={small ? 25 : 42}
      viewBox="0 0 36 42"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M18 2 33 8v14c0 9-15 17-15 17S3 31 3 22V8Z"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path d="m18 10 8 17-8-4-8 4Z" fill="currentColor" />
      <path d="M18 24v8" stroke="currentColor" />
    </svg>
  );
}

function Radar({
  state,
  selected,
  select,
  weather,
  vectors,
}: {
  state: State;
  selected: string;
  select: (s: string) => void;
  weather: boolean;
  vectors: boolean;
}) {
  return (
    <svg
      className="scope"
      viewBox="0 0 800 640"
      role="img"
      aria-label="Synthetic radar sector showing simulated aircraft and weather"
    >
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path
            d="M 40 0 L 0 0 0 40"
            fill="none"
            stroke="#25382d"
            strokeWidth=".6"
          />
        </pattern>
        <pattern
          id="wx"
          width="8"
          height="8"
          patternUnits="userSpaceOnUse"
          patternTransform="rotate(45)"
        >
          <line y2="8" stroke="#c09a44" strokeWidth="1" opacity=".25" />
        </pattern>
        <clipPath id="scope-clip">
          <rect width="800" height="640" />
        </clipPath>
      </defs>
      <rect width="800" height="640" fill="#101c17" />
      <rect width="800" height="640" fill="url(#grid)" />
      <g clipPath="url(#scope-clip)">
        {[100, 200, 300].map((r) => (
          <g key={r}>
            <circle
              cx="400"
              cy="320"
              r={r}
              fill="none"
              stroke="#3d5143"
              strokeDasharray="3 7"
              opacity=".65"
            />
            <text x="409" y={320 - r + 17} className="scope-dim">
              {r / 20} NM
            </text>
          </g>
        ))}
        <path d="M400 0V640M0 320H800" stroke="#4c6352" opacity=".4" />
        <path
          d="M130 0 193 140 152 292 235 490 160 640 M635 0 600 115 657 302 570 430 640 640"
          fill="none"
          stroke="#53604b"
          strokeDasharray="10 9"
          opacity=".42"
        />
        <g transform="translate(405 330) rotate(-40)">
          <rect x="-3" y="-25" width="6" height="50" fill="#9db59d" />
          <line y1="-22" y2="22" stroke="#101c17" strokeDasharray="4 3" />
        </g>
        <text x="422" y="350" className="scope-dim">
          GDN / RWY 22 · FICTIONAL
        </text>
        {weather &&
          state.weather.map((w) => {
            const [x, y] = point(w.x_nm, w.y_nm);
            return (
              <g key={w.id} opacity={state.weather_stale ? 0.35 : 1}>
                <circle
                  cx={x}
                  cy={y}
                  r={w.radius_nm * 20}
                  fill="#9e7a2020"
                  stroke="#b3934a"
                  strokeWidth="1.4"
                  strokeDasharray="5 4"
                />
                <circle cx={x} cy={y} r={w.radius_nm * 20} fill="url(#wx)" />
                <circle cx={x} cy={y} r={w.radius_nm * 13} fill="#bd8e1820" />
                <text
                  x={x}
                  y={y - 8}
                  textAnchor="middle"
                  fill="#d9bd75"
                  fontSize="10"
                >
                  {w.kind}
                </text>
                <text
                  x={x}
                  y={y + 8}
                  textAnchor="middle"
                  fill="#b4a376"
                  fontSize="9"
                >
                  SYNTHETIC ZONE
                </text>
              </g>
            );
          })}
        {state.aircraft.map((a) => {
          const [x, y] = point(a.x_nm, a.y_nm),
            active = a.callsign === selected;
          const serious = state.alerts.some(
            (al) =>
              al.aircraft.includes(a.callsign) && al.severity === "CRITICAL",
          );
          const color = a.stale
            ? "#83928a"
            : serious
              ? "#ef8d83"
              : active
                ? "#efb871"
                : "#a0ceb1";
          return (
            <g key={a.callsign}>
              {a.trail.length > 1 && (
                <polyline
                  points={a.trail
                    .map((p) => point(p[0], p[1]).join(","))
                    .join(" ")}
                  fill="none"
                  stroke={color}
                  opacity=".25"
                  strokeWidth="2"
                />
              )}
              {vectors && !a.stale && (
                <polyline
                  points={a.trajectory
                    .map((p) => point(p[0], p[1]).join(","))
                    .join(" ")}
                  fill="none"
                  stroke={color}
                  strokeDasharray="5 6"
                  opacity={active ? 0.7 : 0.27}
                />
              )}
              <g
                onClick={() => select(a.callsign)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    select(a.callsign);
                  }
                }}
                tabIndex={0}
                role="button"
                aria-label={`Select ${a.callsign}`}
                className="track"
                style={{ color }}
              >
                <circle cx={x} cy={y} r="24" fill="transparent" />
                {active && (
                  <circle
                    cx={x}
                    cy={y}
                    r="15"
                    fill="none"
                    stroke={color}
                    opacity=".6"
                  />
                )}
                <path
                  d="M0 -9 5 6 0 3 -5 6Z"
                  transform={`translate(${x} ${y}) rotate(${a.heading_deg})`}
                  fill={a.stale ? "none" : color}
                  stroke={color}
                />
                <path
                  d={`M${x + 10} ${y - 8}l13 -12h12`}
                  fill="none"
                  stroke={color}
                  opacity=".7"
                />
                <g
                  transform={`translate(${Math.max(5, Math.min(673, x + 25))} ${Math.max(24, Math.min(602, y - 27))})`}
                >
                  <rect
                    x="-3"
                    y="-13"
                    width="112"
                    height="46"
                    rx="2"
                    fill="#101c17"
                    opacity=".88"
                  />
                  <text fill={color} fontSize="13" fontWeight="600">
                    {a.callsign}
                    {a.control === "HUMAN" ? " · H" : ""}
                  </text>
                  <text y="17" fill={color} fontSize="11">
                    {a.stale
                      ? `STALE ${Math.round(a.age_s)}s`
                      : `${Math.round(a.altitude_ft / 100)
                          .toString()
                          .padStart(
                            3,
                            "0",
                          )} ${a.vertical_rate_fpm > 0 ? "↑" : a.vertical_rate_fpm < 0 ? "↓" : "→"}  ${Math.round(a.speed_kt)} KT`}
                  </text>
                  {active && a.clearance && (
                    <text y="31" fill="#aa9b7f" fontSize="9">
                      ASSIGNED {hdg(a.clearance.heading_deg)} /{" "}
                      {fmt(a.clearance.altitude_ft)}
                    </text>
                  )}
                </g>
              </g>
            </g>
          );
        })}
      </g>
      <text x="400" y="22" textAnchor="middle" className="scope-dim">
        N · TRUE
      </text>
      <text x="18" y="622" className="scope-dim">
        LOCAL PLANE · NO WIND · 40 NM WIDE
      </text>
      <text x="782" y="622" textAnchor="end" className="scope-dim">
        SYNTHETIC DATA
      </text>
    </svg>
  );
}

function App() {
  const [state, setState] = useState<State | null>(null),
    [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selected, setSelected] = useState("N123AB"),
    [connected, setConnected] = useState(false),
    [error, setError] = useState("");
  const [wx, setWx] = useState(true),
    [vectors, setVectors] = useState(true),
    [tab, setTab] = useState("scope");
  const [busy, setBusy] = useState(false),
    [heading, setHeading] = useState("310"),
    [altitude, setAltitude] = useState("5000"),
    [turn, setTurn] = useState("right");
  const [readback, setReadback] = useState(""),
    [preview, setPreview] = useState<Preview | null>(null),
    [reviewed, setReviewed] = useState(false);
  const lastMessage = useRef(0),
    session = useRef("");
  const disabled = !connected || busy || !!state?.system_fault;
  const selectedAircraft =
    state?.aircraft.find((a) => a.callsign === selected) ?? state?.aircraft[0];

  useEffect(() => {
    let stopped = false,
      socket: WebSocket,
      timer: ReturnType<typeof setTimeout>;
    const connect = () => {
      socket = new WebSocket(
        `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`,
      );
      socket.onmessage = (event) => {
        const data: State = JSON.parse(event.data);
        lastMessage.current = Date.now();
        setConnected(true);
        setState(data);
      };
      socket.onclose = () => {
        setConnected(false);
        if (!stopped) timer = setTimeout(connect, 1500);
      };
      socket.onerror = () => socket.close();
    };
    connect();
    const watchdog = setInterval(() => {
      if (Date.now() - lastMessage.current > 2500) setConnected(false);
    }, 500);
    fetch("/api/scenarios")
      .then((r) => r.json())
      .then(setScenarios)
      .catch(() =>
        setError("Cannot load scenarios. Start the backend and reload."),
      );
    return () => {
      stopped = true;
      clearTimeout(timer);
      clearInterval(watchdog);
      socket.close();
    };
  }, []);
  useEffect(() => {
    if (state && session.current !== state.session) {
      session.current = state.session;
      setSelected(state.aircraft[0].callsign);
      setPreview(null);
      setReviewed(false);
      setReadback("");
    }
  }, [state?.session]);
  useEffect(() => {
    if (selectedAircraft) {
      setHeading(
        String(
          selectedAircraft.clearance?.heading_deg ??
            Math.round(selectedAircraft.heading_deg),
        ),
      );
      setAltitude(
        String(
          selectedAircraft.clearance?.altitude_ft ??
            Math.round(selectedAircraft.altitude_ft),
        ),
      );
      setTurn(selectedAircraft.clearance?.turn ?? "right");
      setPreview(null);
      setReviewed(false);
      setReadback("");
    }
  }, [selectedAircraft?.callsign, state?.session]);

  async function post(path: string, data: unknown) {
    setBusy(true);
    setError("");
    try {
      const r = await fetch(`/api/${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const body = await r.json();
      if (!r.ok)
        throw new Error(
          typeof body.detail === "string"
            ? body.detail
            : "Check input: heading 0–359, altitude 0–20,000 ft.",
        );
      if (body.aircraft && body.session) setState(body);
      return body;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Command failed");
      return null;
    } finally {
      setBusy(false);
    }
  }
  const sim = (action: string, value = 1) =>
    post("simulation", { action, value });
  const control = (action: string) =>
    post(`aircraft/${selectedAircraft?.callsign}/control`, { action });
  const command = {
    heading_deg: Number(heading),
    altitude_ft: Number(altitude),
    turn,
    reviewed,
  };
  const change = (fn: () => void) => {
    fn();
    setPreview(null);
    setReviewed(false);
  };
  const trafficUnknown = state?.aircraft.some((a) => a.stale);

  return (
    <>
      <header>
        <div className="brand">
          <Mark />
          <div>
            ATC <strong>GUARDIAN</strong>
            <span>CONTINUOUS AWARENESS. HUMAN AUTHORITY.</span>
          </div>
        </div>
        <nav aria-label="Main navigation">
          {[
            ["scope", "Live simulation"],
            ["lab", "Scenario lab"],
            ["notes", "Project notes"],
          ].map(([id, name]) => (
            <button
              key={id}
              className={tab === id ? "nav-active" : ""}
              onClick={() => setTab(id)}
            >
              {name}
            </button>
          ))}
        </nav>
        <div className="version">
          RESEARCH BUILD <b>v0.1.0</b>
        </div>
      </header>
      <div className="notice">
        <span className="amber">◇</span> SIMULATION ONLY{" "}
        <span className="notice-detail">
          — Not certified. Never use to direct, separate, navigate, or control
          real aircraft.
        </span>
      </div>
      <main>
        <div className="page-title">
          <div>
            <div className="eyebrow">GUARDIAN RESEARCH / SECTOR 01</div>
            <h1>Every aircraft. Always in view.</h1>
            <p>A persistent safety monitor, with a human in command.</p>
          </div>
          <div
            className={`connection ${connected && !state?.system_fault ? "online" : ""}`}
          >
            <i />
            {state?.system_fault
              ? "ENGINE FAULT"
              : connected
                ? "SIMULATOR CONNECTED"
                : "CONNECTION UNAVAILABLE"}
          </div>
        </div>
        {(!connected || state?.system_fault) && (
          <div className="error" role="alert">
            {state?.system_fault ??
              "Waiting for the local simulator. Controls and assessment are unavailable until connection is restored."}
          </div>
        )}
        {error && (
          <div className="error" role="alert">
            {error}
            <button onClick={() => setError("")} aria-label="Dismiss error">
              ×
            </button>
          </div>
        )}
        {tab === "notes" && (
          <section className="notes panel">
            <div className="eyebrow">A FIRST RELEASE, BUILT TO GROW</div>
            <h2>From a pilot’s perspective.</h2>
            <p>
              ATC Guardian explores a question: what if an active clearance
              always had a persistent digital memory? This prototype gives every
              simulated aircraft a state, checks developing risks, and keeps
              human ownership explicit.
            </p>
            <div className="notes-grid">
              <article>
                <h3>Implemented in v0.1</h3>
                <p>
                  Deterministic aircraft motion, missed-turn monitoring,
                  altitude deviations, structured text readbacks, traffic
                  prediction, synthetic weather volumes, human requests, and a
                  SQLite event recorder.
                </p>
              </article>
              <article>
                <h3>Know the boundaries</h3>
                <p>
                  No live aircraft or weather feeds. No AI model, speech
                  recognition, radio transmission, terrain, wake,
                  runway-incursion checks, or regulatory separation assurance.
                  Prediction assumes constant observed velocity; headings equal
                  track in this no-wind model.
                </p>
              </article>
              <article>
                <h3>Human control stays visible</h3>
                <p>
                  Takeover changes simulated communication ownership. The
                  scripted pilot continues flying; ownership is not a
                  flight-control command. Restoring a feed never automatically
                  restores assistance.
                </p>
              </article>
              <article>
                <h3>Your next experiment</h3>
                <p>
                  Open Scenario lab. Reproduce a missed turn, acknowledge its
                  warning, then restore pilot response. Acknowledgement leaves
                  the condition active; only resolution removes it.
                </p>
              </article>
            </div>
            <button className="primary" onClick={() => setTab("lab")}>
              Open scenario lab →
            </button>
          </section>
        )}
        {tab === "lab" && (
          <section className="panel lab">
            <div className="section-title">
              <div>
                <div className="eyebrow">REPRODUCIBLE EXPERIMENTS</div>
                <h2>One scenario. One safety question.</h2>
              </div>
              <span>5 PRESETS</span>
            </div>
            <div className="scenario-grid">
              {scenarios.map((s, i) => (
                <button
                  key={s.id}
                  disabled={disabled}
                  onClick={async () => {
                    if (await post("scenario", { scenario: s.id }))
                      setTab("scope");
                  }}
                >
                  <span className="scenario-index">0{i + 1}</span>
                  <h3>{s.name}</h3>
                  <p>{s.description}</p>
                  <span className="amber">Load paused scenario ↗</span>
                </button>
              ))}
            </div>
            <p className="muted">
              Loading a preset starts a new session. Earlier event records
              remain in the local database.
            </p>
          </section>
        )}
        {tab === "scope" && state && (
          <>
            <section className="metrics" aria-label="Sector overview">
              <div>
                <span>TRACKED AIRCRAFT</span>
                <b>
                  {String(state.aircraft.length).padStart(2, "0")}
                  <small>synthetic tracks</small>
                </b>
              </div>
              <div>
                <span>ACTIVE ALERTS</span>
                <b className={state.alerts.length ? "amber" : ""}>
                  {String(state.alerts.length).padStart(2, "0")}
                  <small>
                    {trafficUnknown
                      ? "traffic assessment incomplete"
                      : "across monitored conditions"}
                  </small>
                </b>
              </div>
              <div>
                <span>HUMAN OWNERSHIP</span>
                <b>
                  {String(
                    state.aircraft.filter((a) => a.control === "HUMAN").length,
                  ).padStart(2, "0")}
                  <small>of {state.aircraft.length} aircraft</small>
                </b>
              </div>
              <div>
                <span>WEATHER STATUS</span>
                <b className="metric-label">
                  {state.weather_stale
                    ? "UNAVAILABLE"
                    : !state.weather_available
                      ? "INTERRUPTED"
                      : "SYNTHETIC"}
                  <small>
                    observation age {Math.round(state.weather_age_s)}s
                  </small>
                </b>
              </div>
            </section>
            <div className="workspace">
              <div className="workspace-main">
                <section className="panel radar-panel">
                  <div className="section-title">
                    <div>
                      <span className="live-dot" />
                      <h2>Sector overview</h2>
                      <span className="subtle">FICTIONAL AIRSPACE</span>
                    </div>
                    <div className="layers">
                      <label>
                        <input
                          type="checkbox"
                          checked={wx}
                          onChange={(e) => setWx(e.target.checked)}
                        />{" "}
                        Weather
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={vectors}
                          onChange={(e) => setVectors(e.target.checked)}
                        />{" "}
                        Paths
                      </label>
                    </div>
                  </div>
                  <Radar
                    state={state}
                    selected={selectedAircraft?.callsign ?? selected}
                    select={setSelected}
                    weather={wx}
                    vectors={vectors}
                  />
                  <div className="scope-legend">
                    <span>
                      <i className="legend-dot" /> Aircraft
                    </span>
                    <span>
                      <i className="legend-dot selected" /> Selected
                    </span>
                    <span>
                      <i className="legend-wx" /> Weather volume
                    </span>
                    <span>Paths: current velocity · 5 min</span>
                  </div>
                  <div className="playback">
                    <div className="playback-time">
                      <span>SIM TIME</span>
                      <b data-testid="sim-time">{time(state.time_s)}</b>
                    </div>
                    <button
                      className="primary"
                      disabled={disabled}
                      onClick={() => sim(state.running ? "pause" : "play")}
                    >
                      {state.running ? "Ⅱ Pause" : "▶ Run"}
                    </button>
                    <button disabled={disabled} onClick={() => sim("step", 30)}>
                      +30 sec
                    </button>
                    <select
                      aria-label="Playback speed"
                      disabled={disabled}
                      value={state.speed}
                      onChange={(e) => sim("speed", Number(e.target.value))}
                    >
                      <option value="1">1× speed</option>
                      <option value="2">2× speed</option>
                      <option value="4">4× speed</option>
                    </select>
                    <button
                      className="reset"
                      disabled={disabled}
                      onClick={() =>
                        post("scenario", { scenario: state.scenario })
                      }
                    >
                      ↺ Reset
                    </button>
                  </div>
                </section>
                <div className="active-scenario">
                  <span className="scenario-number">
                    {String(
                      scenarios.findIndex((s) => s.id === state.scenario) + 1,
                    ).padStart(2, "0")}
                  </span>
                  <div>
                    <span className="eyebrow">CURRENT EXPERIMENT</span>
                    <h3>{state.scenario_name}</h3>
                    <p>{state.description}</p>
                  </div>
                  <button
                    onClick={() => setTab("lab")}
                    aria-label="Change scenario"
                  >
                    ↗
                  </button>
                </div>
                <section className="panel traffic-table">
                  <div className="section-title">
                    <h2>Aircraft register</h2>
                    <span>ALL TRACKS</span>
                  </div>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>CALLSIGN</th>
                          <th>ALTITUDE</th>
                          <th>HEADING</th>
                          <th>SPEED</th>
                          <th>OWNERSHIP</th>
                        </tr>
                      </thead>
                      <tbody>
                        {state.aircraft.map((a) => (
                          <tr
                            key={a.callsign}
                            className={
                              selectedAircraft?.callsign === a.callsign
                                ? "selected-row"
                                : ""
                            }
                          >
                            <td>
                              <button onClick={() => setSelected(a.callsign)}>
                                {a.callsign}
                              </button>
                              {a.stale && <span className="amber"> STALE</span>}
                            </td>
                            <td>{fmt(a.altitude_ft)} ft</td>
                            <td>{hdg(a.heading_deg)}</td>
                            <td>{a.speed_kt} kt</td>
                            <td>
                              {a.control === "HUMAN" ? "Human" : "Assisted"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>
              <aside>
                <section className="panel alerts-panel">
                  <div className="section-title">
                    <h2>Safety monitor</h2>
                    <span className="counter">{state.alerts.length}</span>
                  </div>
                  <div className="alert-list" aria-live="polite">
                    {state.alerts.length === 0 ? (
                      <div className="no-alerts">
                        {trafficUnknown
                          ? "Assessment incomplete"
                          : "No modeled conflicts detected"}
                        <small>Limited to enabled research checks.</small>
                      </div>
                    ) : (
                      state.alerts.map((a) => (
                        <article
                          key={a.id}
                          className={`alert ${a.severity.toLowerCase()}`}
                        >
                          <div className="alert-top">
                            <span>
                              {a.severity} / {a.kind}
                            </span>
                            {a.evidence.entry_s !== undefined && (
                              <b>{time(Number(a.evidence.entry_s))}</b>
                            )}
                          </div>
                          <h3>{a.title}</h3>
                          <strong>
                            {a.aircraft.join(" / ") || "SECTOR-WIDE"}
                          </strong>
                          <p>{a.detail}</p>
                          <button
                            disabled={disabled || a.acknowledged}
                            onClick={() =>
                              post(
                                `alerts/${encodeURIComponent(a.id)}/acknowledge`,
                                {},
                              )
                            }
                          >
                            {a.acknowledged
                              ? "✓ Acknowledged · still active"
                              : "Acknowledge"}
                          </button>
                        </article>
                      ))
                    )}
                  </div>
                </section>
                {selectedAircraft && (
                  <section className="panel aircraft-panel">
                    <div className="section-title">
                      <h2>Aircraft detail</h2>
                      <span>SELECTED</span>
                    </div>
                    <div className="aircraft-heading">
                      <div>
                        <h2>{selectedAircraft.callsign}</h2>
                        <span>{selectedAircraft.aircraft_type}</span>
                      </div>
                      <span
                        className={`ownership ${selectedAircraft.control === "HUMAN" ? "human" : ""}`}
                      >
                        {selectedAircraft.control}
                      </span>
                    </div>
                    <div className="telemetry">
                      <div>
                        <span>ALTITUDE</span>
                        <b>
                          {fmt(selectedAircraft.altitude_ft)} <small>ft</small>
                        </b>
                        <small>
                          Assigned{" "}
                          {selectedAircraft.clearance
                            ? fmt(selectedAircraft.clearance.altitude_ft)
                            : "—"}
                        </small>
                      </div>
                      <div>
                        <span>HEADING / TRUE</span>
                        <b>{hdg(selectedAircraft.heading_deg)}</b>
                        <small>
                          Assigned{" "}
                          {selectedAircraft.clearance
                            ? hdg(selectedAircraft.clearance.heading_deg)
                            : "—"}
                        </small>
                      </div>
                      <div>
                        <span>GROUND SPEED</span>
                        <b>
                          {selectedAircraft.speed_kt} <small>kt</small>
                        </b>
                      </div>
                      <div>
                        <span>VERTICAL RATE</span>
                        <b>
                          {Math.round(selectedAircraft.vertical_rate_fpm)}{" "}
                          <small>ft/min</small>
                        </b>
                      </div>
                    </div>
                    <div className="clearance-status">
                      <span>CLEARANCE MEMORY</span>
                      <b>
                        {selectedAircraft.clearance?.status ??
                          "NO ACTIVE CLEARANCE"}
                      </b>
                      <small>
                        Readback: {selectedAircraft.clearance?.readback ?? "—"}{" "}
                        · Squawk: {selectedAircraft.squawk}
                      </small>
                    </div>
                    {selectedAircraft.human_reason && (
                      <div className="human-reason">
                        Human review: {selectedAircraft.human_reason}
                      </div>
                    )}
                    <div className="ownership-actions">
                      <button
                        disabled={disabled}
                        className="primary"
                        onClick={() =>
                          control(
                            selectedAircraft.control === "HUMAN"
                              ? "resume"
                              : "takeover",
                          )
                        }
                      >
                        {selectedAircraft.control === "HUMAN"
                          ? "Restore assistance"
                          : "Take human control"}
                      </button>
                      <button
                        disabled={disabled}
                        onClick={() => control("request_human")}
                      >
                        Pilot requests human
                      </button>
                    </div>
                    <details className="clearance-editor">
                      <summary>
                        Propose a simulated clearance <span>+</span>
                      </summary>
                      <p>Human review required. No real transmission.</p>
                      <div className="form-grid">
                        <label>
                          Heading °
                          <input
                            aria-label="Proposed heading"
                            type="number"
                            min="0"
                            max="359"
                            value={heading}
                            onChange={(e) =>
                              change(() => setHeading(e.target.value))
                            }
                          />
                        </label>
                        <label>
                          Altitude ft
                          <input
                            aria-label="Proposed altitude"
                            type="number"
                            min="0"
                            max="20000"
                            step="100"
                            value={altitude}
                            onChange={(e) =>
                              change(() => setAltitude(e.target.value))
                            }
                          />
                        </label>
                        <label>
                          Direction
                          <select
                            value={turn}
                            onChange={(e) =>
                              change(() => setTurn(e.target.value))
                            }
                          >
                            <option value="right">Right</option>
                            <option value="left">Left</option>
                          </select>
                        </label>
                      </div>
                      <button
                        disabled={disabled || heading === "" || altitude === ""}
                        onClick={async () =>
                          setPreview(
                            await post(
                              `aircraft/${selectedAircraft.callsign}/preview`,
                              command,
                            ),
                          )
                        }
                      >
                        Screen proposal
                      </button>
                      {preview && (
                        <div className="preview">
                          <strong>{preview.status}</strong>
                          <p>{preview.unknown.join(". ")}</p>
                          {preview.findings.map((f) => (
                            <p key={f.id}>
                              {f.title} · {f.aircraft.join(" / ")}
                            </p>
                          ))}
                          <small>{preview.assumptions}</small>
                          <label className="review">
                            <input
                              type="checkbox"
                              checked={reviewed}
                              onChange={(e) => setReviewed(e.target.checked)}
                            />
                            I reviewed these assumptions and findings.
                          </label>
                          <button
                            disabled={
                              disabled ||
                              !reviewed ||
                              preview.status === "UNAVAILABLE"
                            }
                            onClick={async () => {
                              if (
                                await post(
                                  `aircraft/${selectedAircraft.callsign}/clearance`,
                                  command,
                                )
                              ) {
                                setPreview(null);
                                setReviewed(false);
                              }
                            }}
                          >
                            Approve in simulation
                          </button>
                        </div>
                      )}
                      {selectedAircraft.clearance && (
                        <div className="readback">
                          <label>
                            Text readback
                            <input
                              aria-label="Text readback"
                              value={readback}
                              maxLength={200}
                              onChange={(e) => setReadback(e.target.value)}
                              placeholder={`${selectedAircraft.callsign} heading 310 altitude 5000`}
                            />
                          </label>
                          <small>
                            Supported format: CALLSIGN heading DIGITS altitude
                            DIGITS
                          </small>
                          <div className="button-row">
                            <button
                              disabled={disabled}
                              onClick={() =>
                                setReadback(
                                  `${selectedAircraft.callsign} heading ${selectedAircraft.clearance!.heading_deg} altitude ${selectedAircraft.clearance!.altitude_ft}`,
                                )
                              }
                            >
                              Fill matching text
                            </button>
                            <button
                              disabled={disabled || !readback.trim()}
                              onClick={() =>
                                post(
                                  `aircraft/${selectedAircraft.callsign}/readback`,
                                  { text: readback },
                                )
                              }
                            >
                              Verify
                            </button>
                          </div>
                        </div>
                      )}
                    </details>
                    <details className="faults">
                      <summary>
                        Simulation fault controls <span>+</span>
                      </summary>
                      <button
                        disabled={disabled}
                        onClick={() =>
                          control(
                            selectedAircraft.pilot_follows_turn
                              ? "miss_turn"
                              : "follow_turn",
                          )
                        }
                      >
                        {selectedAircraft.pilot_follows_turn
                          ? "Simulate missed turn"
                          : "Restore pilot turn response"}
                      </button>
                      <button
                        disabled={disabled}
                        onClick={() =>
                          control(
                            selectedAircraft.feed_available
                              ? "lose_track"
                              : "restore_track",
                          )
                        }
                      >
                        {selectedAircraft.feed_available
                          ? "Interrupt surveillance"
                          : "Restore surveillance"}
                      </button>
                      <button
                        disabled={disabled}
                        onClick={() =>
                          sim(
                            state.weather_available
                              ? "weather_fail"
                              : "weather_restore",
                          )
                        }
                      >
                        {state.weather_available
                          ? "Interrupt weather feed"
                          : "Restore weather feed"}
                      </button>
                      <small>
                        Restoring a feed keeps human ownership until explicitly
                        released.
                      </small>
                    </details>
                  </section>
                )}
                <button
                  className="sector-takeover"
                  disabled={disabled}
                  onClick={() => sim("takeover_all")}
                >
                  <Mark small /> Take control of entire sector
                </button>
              </aside>
            </div>
            <section className="panel events-panel">
              <div className="section-title">
                <div>
                  <h2>Event recorder</h2>
                  <span className="subtle">PERSISTENT / SQLITE</span>
                </div>
                <a href="/api/export" download>
                  Export session ↓
                </a>
              </div>
              <div className="events-scroll">
                {state.events.map((e) => (
                  <div className="event" key={e.id}>
                    <time>{time(e.sim_s)}</time>
                    <span
                      className={`event-kind ${e.kind === "ALERT" ? "amber" : ""}`}
                    >
                      {e.kind}
                    </span>
                    <b>{e.callsign ?? "SYSTEM"}</b>
                    <p>{e.message}</p>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
        <footer>
          <span>
            ATC GUARDIAN <b>v0.1</b> / Aviation software research
          </span>
          <span>Synthetic data. Deterministic checks. Human oversight.</span>
        </footer>
      </main>
    </>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
