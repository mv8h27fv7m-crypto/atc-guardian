# Research boundaries and authoritative references

Reviewed 2026-10-05. This file records design distinctions, not operational instructions or a compliance finding. The original project brief is aspirational. The implementation inventory in README.md is authoritative for v0.1.

## Important distinctions

**Weather age and use.** FAA describes FIS-B as advisory information for planning and decision-making, with resolution/update limits that prevent tactical maneuvering around local weather. A radar-looking display must not imply an immediately safe route through weather. Guardian therefore uses explicitly synthetic volumes and does not ingest FIS-B or produce avoidance clearances. [FAA ADS-B In applications](https://www.faa.gov/air_traffic/technology/adsb/pilot).

**Traffic completeness.** FAA's ADS-B In guidance describes equipment, coverage, and client limitations; a traffic picture is not automatically complete. A future adapter needs coverage and quality metadata, not merely coordinates. Guardian has no real surveillance connection. [FAA ADS-B In applications](https://www.faa.gov/air_traffic/technology/adsb/pilot).

**Minimum fuel.** The original brief includes minimum fuel in a list of potential emergency phrases. FAA distinguishes minimum fuel as an advisory; it does not by itself confer emergency status or traffic priority. A future parser must preserve that distinction and escalate uncertainty to a qualified human. v0.1 implements no emergency-phrase detector. [FAA JO 7110.65, 2-1-8](https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap2_section_1.html).

**Collision and terrain avoidance.** FAA instructs controllers not to issue instructions contrary to reported TCAS resolution-advisory or TAWS maneuvers, with specific surrounding responsibilities. A future research module must not treat a justified avoidance maneuver as permission to direct an aircraft back into a conflict. No TCAS, ACAS, or TAWS logic is implemented here. [FAA JO 7110.65, General Control](https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap2_section_1.html).

**Surveillance fields.** A squawk, callsign, and ICAO address serve different purposes; they are not interchangeable identity proofs. Track and heading also differ, and barometric/pressure/geometric altitude require explicit treatment. v0.1 uses fictional callsigns and one synthetic altitude reference; its no-wind heading/track equality must not be carried into an operational adapter without redesign.

## Assurance research, not certification

FAA AC 20-115D concerns **airborne software** and recognizes DO-178C/ED-12C and associated documents. It does not automatically establish the approval path for a ground ATC research platform. Use it to learn about requirements, verification, traceability, configuration control, and assurance evidence, then determine the actual applicable framework with qualified specialists. [FAA AC 20-115D](https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentID/1032046).

FAA AC 20-174 addresses development assurance for civil aircraft and systems and recognizes ARP4754A in that context. Referencing it is not evidence that this repository meets it, that it applies directly to ground ATC, or that it is the only/current applicable standard for a future deployment. Standards editions and acceptance must be verified for the exact program. [FAA AC 20-174](https://www.faa.gov/airports/resources/advisory_circulars/index.cfm/go/document.information/documentNumber/20-174).

Research questions before any operational proposal: Who is the responsible authority? What ground-system requirements apply? What are the operational design domain and safety objectives? Who independently validates hazards and requirements? What human-factors evidence and contingency staffing are needed? How are source integrity, latency, redundancy, cyber risks, and configuration controlled? What approval is required for communication automation?

No answers to those questions are presumed by a successful demo, a polished interface, or passing tests.

## Other primary implementation references

- [FastAPI WebSocket testing](https://fastapi.tiangolo.com/advanced/testing-websockets/)
- [Vite getting started and supported Node versions](https://vite.dev/guide/)
- [GitHub: adding locally hosted code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)

The safety architecture is a project design choice, not an FAA endorsement or an inference that a particular implementation is safe.
