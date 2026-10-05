# A three-minute project demonstration

The default preset is **The forgotten turn**. All timestamps below are simulated time, not wall-clock time.

1. Start the app. Select **N123AB** on the radar or in the aircraft register. It is at 3,500 ft, heading 270°, with a correctly read back clearance for heading 310° and 5,000 ft.
2. Click **+30 sec**. The aircraft climbs but retains heading 270°. **Turn not detected** appears. Weather monitoring can already predict entry into the synthetic convective cell.
3. Acknowledge the missed-turn alert. It stays in the list because acknowledging a warning does not change what the aircraft is doing.
4. Click **Pilot requests human**. Its ownership becomes **HUMAN**. Monitoring continues; flight does not freeze.
5. Open **Propose a simulated clearance**. Enter heading **020**, altitude **5000**, turn **Right**, and click **Screen proposal**. Read the current findings and model assumptions. This screening cannot establish operational safety.
6. Check the review box and click **Approve in simulation**. The previous clearance is retained as superseded history. The new one waits for a readback.
7. Click **Fill matching text**, then **Verify**. The parser confirms those exact structured values.
8. Open **Simulation fault controls**, click **Restore pilot turn response**, and click **+30 sec** twice. The scripted pilot now follows the revised heading and the relevant warnings update. Verify the remaining findings rather than assuming all conditions cleared.
9. Human ownership remains until you explicitly click **Restore assistance**. Restoring the pilot's response does not silently hand authority back.
10. Click **Export session** to download the timestamped event record. This is not a full motion replay.

For the simplest missed-turn recovery, skip the revised-clearance steps: restore pilot turn response and advance 30 seconds. Heading 310° is reached and its missed-turn warning resolves.

## Four other experiments

| Preset | What to demonstrate |
| --- | --- |
| Crossing paths | Two converging tracks enter a synthetic protected volume. Compare entry time with horizontal CPA. |
| One thousand feet off | Wrong altitude readback requires human ownership. Correct it with matching text; ownership stays human. |
| Weather ahead | One projected path enters an icing band; the other aircraft is above that volume. |
| A disappearing track | Advance 30 seconds. The frozen last observation becomes stale, its vector disappears, and human review is required. |

## Short explanation you can give

“ATC Guardian is my aviation safety simulation project, inspired by my experience as a private pilot. The Python backend retains each aircraft's clearance and checks for missed turns, altitude deviations, traffic conflicts, and weather intersections. The React interface makes the findings and human ownership visible. I used AI assistance for the initial implementation and am learning and extending the code. It does not direct real aircraft.”
