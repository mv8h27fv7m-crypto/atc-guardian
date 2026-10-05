# Verification record

Verified in the handoff environment on 2026-10-05: Linux, Python 3.12.14, Node 24.19.0, Chromium 141 through Playwright 1.56.1. Python and JavaScript dependencies are captured in `requirements.txt` and `frontend/package-lock.json`.

| Check | Result |
| --- | --- |
| Geometry, engine and API tests | 44 passed |
| Browser interaction tests | 7 passed |
| TypeScript check and production build | Passed |
| Desktop visual inspection | Passed at 1520 px width |
| Mobile visual inspection and overflow test | Passed at 390 px width; detailed radar work is intended for a desktop |
| Windows execution | Not run in this environment; Windows scripts provided and Windows CI configured |
| GitHub Actions | Workflow provided; no remote run claimed |
| Aviation assurance / real-world validation | Not performed; simulation only |

One dependency emits a Starlette test-client deprecation warning recommending a future migration away from its `httpx` compatibility path. The pinned integration passes; this is not treated as evidence of long-term dependency support.

## Behaviors exercised

Geometry: knots/seconds/feet conversion; heading wrap; crossing, parallel and diverging motion; stationary and tangent boundaries; altitude-band weather rejection; limited prediction horizon; and a case where vertical convergence occurs away from horizontal CPA.

Engine: missed turn after its grace period; warning persistence after acknowledgement; resolution after pilot response; altitude progress versus deviation; wrong identity/value and unrecognized readbacks; preserved readback timer; stale surveillance and weather; withheld rather than false resolved conditions; explicit human resumption; read-only screening; clearance history; turn direction at 360°; deduplicated events; retained sessions; severity escalation; and every preset through 300 seconds.

API: invalid and fractional command values, unknown fields/targets, unreviewed clearance rejection, cross-origin command rejection, WebSocket snapshots/origin handling, event export, and sector takeover.

Browser: missed-turn acknowledgement/recovery; scenario loading and readback correction; reviewed proposal approval; stale-track restoration without authority increase; layer toggles; event export; mobile document overflow; and connection loss disabling controls.

## Coverage boundary

These are selected behavior tests, not exhaustive state-space exploration or evidence of operational safety. No coverage percentage is claimed. No tests use real aircraft or weather.

| Failure family | v0.1 scope |
| --- | --- |
| Missing/stale position or weather | Injected in simulation and tested |
| Browser connection loss | Tested |
| Wrong or unsupported readback | Tested with structured text |
| Incorrect controller command fields | Validated and tested |
| Turn/climb response | Scripted model and selected deviation tests |
| Packet delay, duplication, reordering, identity collision, position jumps | Future observation adapter work |
| GNSS spoofing / sensor disagreement | Not implemented |
| Database/disk corruption or outage | Recovery incomplete; not fault-injection tested |
| Server/process/power outage and redundancy | Connection warning exists; resilience architecture not implemented |
| AI/speech failure or prompt injection | No model/speech subsystem exists yet |
| Terrain, runway, wake, real weather/performance, TCAS/ACAS | Not implemented |

## Running the checks

```bash
python -m pytest
cd frontend
npm ci
npm run build
npx playwright install chromium
npm run test:e2e
```

Use the project virtual environment's Python. For browser tests, either leave the local server running or activate that environment before `npm run test:e2e`; the test configuration launches `python -m uvicorn` when no server is present. The tests intentionally reset the active scenario.

The CI workflow runs the same checks on Ubuntu and Windows. Dependency installation and downloading the test browser need network access. Ordinary simulation after setup does not.
