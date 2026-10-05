# Roadmap

The long-term vision is preserved in `docs/PROJECT_VISION.txt`. Items below are research milestones, not promises of operational readiness.

## v0.1 — working baseline

- [x] Synthetic radar and aircraft state
- [x] Scripted turns/climbs, current-velocity prediction
- [x] Persistent clearance lifecycle, missed-turn and altitude monitoring
- [x] Structured text readback checking
- [x] Traffic-volume intersection and synthetic 3D weather checks
- [x] Human request, individual/sector takeover, explicit assistance restoration
- [x] Freshness handling, local event database and JSON export
- [x] Presets, automated checks, Windows launch scripts, architecture and learning guide

## v0.2 — evidence and data integrity

- [ ] Record every simulation input and tick for exact replay; historical-session browser
- [ ] Validate scenario schemas and reject duplicate identities, invalid timestamps, and impossible values
- [ ] Separate simulator truth from observed data; delay, packet loss, reordering, jumps, and recovery
- [ ] Test wrong-direction turns, transient altitude disturbances, compliance timeouts, and re-entry alert acknowledgement policy
- [ ] Add wind, heading/track distinction, altitude datums, intent-aware level-off, and uncertainty envelopes
- [ ] Add a user-facing scenario editor with validated bounds

Release gate: reproducible replay hashes, schema/invariant tests, no unknown-to-safe transitions, documented performance and false-alarm behavior.

## v0.3 — weather and environmental research

- [ ] Licensed recorded/test weather with source, timestamp, validity and quality
- [ ] Moving polygons, hazard buffers, weather evolution uncertainty
- [ ] Distinguish strategic weather planning from tactical avoidance
- [ ] Verified terrain/obstacle data and separately tested vertical references
- [ ] Synthetic runway occupancy/alignment and validated wake metadata
- [ ] Crosswind calculations only with verified runway orientation, wind reference and aircraft limitations

Release gate: independently reviewed data assumptions and a regression scenario for each new detector. No claims that all weather hazards are detected.

## v0.4 — constrained interpretation and voice simulation

- [ ] Text-to-structure AI proposals in an isolated, permission-limited adapter
- [ ] Callsign ambiguity, phonetic digits, conditional clearances, noisy readback datasets
- [ ] Calibrated confidence, reject/abstain handling, prompt-injection tests
- [ ] Controller-approved local voice playback; never operational radio transmission
- [ ] Human handoff acknowledgement and communication queue ownership

Release gate: compare with the deterministic baseline; incorrect/uncertain interpretations never silently update authoritative state.

## Longer-term engineering questions

Sensor fusion, ADS-B/Mode S recorded inputs, GNSS disagreement detection, emergency handling, TCAS/ACAS interaction, aircraft performance validation, human workload and alarm-fatigue studies, independent watchdogs, backups, authentication, audit integrity, signed releases, supply-chain controls, and carefully bounded supervision experiments.

Before any consideration of aviation deployment, engage qualified controllers, human-factors specialists, system-safety engineers, cybersecurity engineers, and the responsible authorities to establish the actual assurance and approval basis. This roadmap is not a route to permission to control aircraft.
