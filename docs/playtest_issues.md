# Playtest Issues

A running list of problems noticed while play-testing. Add new issues at the
bottom of "Open" with the date and phase. When one is fixed, move it to
"Resolved" and note the commit.

Status: **open** = not fixed, **deferred** = known, saved for the balancing
pass.

## Open

| # | Found | Area | Issue | Status |
|---|-------|------|-------|--------|
| 1 | 2026-11-10, Research | Pacing | Early research appears too fast: the Business badge reached 3 within about 10 seconds of a new game. `unlock_at_earned` values in `RESEARCH_ROWS` are probably too low. | deferred |
| 2 | 2026-11-10, Research (seen again in W2 and W3) | UI | Clicks can be lost when a tick redraws `#live_area` at the same moment. This happens whenever `controls_signature` changes (a new buy item, a research unlock, or a news headline), which is often in the first minute of a game. In testing, nav clicks (especially 🐞) failed several times in a row early on, then worked once the badge settled. | open |
| 3 | 2026-11-11, W1 | Pacing | Threat meter pacing not tuned yet (`THREAT_PER_SECOND`, `THREAT_PER_WAR_UNIT`, `MAX_THREAT_PER_SECOND`). Intermissions are about 50 s at the base rate. | deferred |
| 4 | 2026-11-11, W2 | Balance | Failed waves barely hurt: stock is usually 0 because every unit sells each tick, so `STOCK_LOSS_PER_SURVIVOR` rarely matters; only the production penalty (`raid_ms_left`) has an effect. | open |
| 5 | 2026-11-11, W2 | Balance | Wave 1 is trivial: the 2 starting MANPADS clear it in about 3 seconds. | deferred |
| 6 | 2026-11-11, W2 | Balance | Dire wave equipment loss rounds down (`int(owned * 0.25)`), so owning 3 or fewer of a defense type means a failed dire wave destroys none of it. | open |
| 7 | 2026-11-11, W2 | Balance | Air defense has a flat cost (no cost growth), so it may get very cheap compared with late-game income. | deferred |
| 8 | 2026-11-11, W2 | Drafter | On page load, Drafter 2.1.4 shows "Unhandled configuration update event" errors in its debug panel for each `set_site_information` field. The game works; this looks like Drafter noise, not our code. | open |
| 9 | 2026-11-11, W3 | Balance | `WAR_VICTORY_GOODS = 30000` is a guess. It needs real numbers for how many war goods a typical player sells over 35 waves. | deferred |
| 10 | 2026-11-11, W3 | Debug | "End the war (lose)" sets war goods sold to 0 and counts all 35 waves as broken through, so a defeat demo shows extreme numbers. | open |

## Resolved

| # | Found | Area | Issue | Fix |
|---|-------|------|-------|-----|
| R1 | 2026-11-11, W1 | Business | Unsure whether goods selected before the war lose their bonus when sanctioned. Checked: `start_war` switches off every sanctioned goods type, so its bonus stops counting. A test was added (`make_veteran_electronics_state`). | 4278116 |
| R2 | 2026-11-11, W2 | War | A failed dire wave reported "air defenses damaged" even when the 25% loss rounded down to 0 units. It now reports the real number lost. | 4278116 |
| R3 | 2026-11-11, W3 | Debug | "End the war (win)" showed "Waves defended: 0 of 35". A debug win now counts every wave as defended. | W3 commit |
