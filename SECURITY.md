# Security scope

ATC Guardian v0.1 is a local single-user simulation. Its default launcher binds to `127.0.0.1`; there is no supported public or multi-user deployment mode.

Implemented: bounded Pydantic command fields, rejected unknown fields, a scenario-name allowlist, controlled browser origins, hostname checks, same-origin WebSocket access, parameterized SQLite statements, rendered text through React, and no shell/model/radio/remote-feed commands in the application.

Not implemented: user authentication, role separation, rate limiting, encrypted remote transport, signed updates, tamper-evident events, intrusion detection, hardened process isolation, redundant storage, or an independent watchdog. Trusted JSON fixtures are developer inputs; they are not a safe ingestion interface for arbitrary files.

Local software with access to the port or database can manipulate the simulation. Browser origin checks do not protect against a malicious local process. Multiple tabs share full simulation authority. A clock-loop exception stops progression and requests human ownership, but database failure recovery is incomplete. Do not make safety or security claims from this prototype's controls.

No secrets are required. Do not commit `.env` files, local database files, API credentials, or private flight/voice recordings. Dependencies are recorded in the lock files but have not received an independent supply-chain review.

For this research repository, report ordinary defects as reproducible synthetic scenarios and tests. If a future maintainer adds a security-reporting contact, use a private report for an exploitable issue; do not upload sensitive real-world data to a public issue.
