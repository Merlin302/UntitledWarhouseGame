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
| 2 | 2026-11-10, Research (seen again in W2 and W3) | UI | Lost clicks, what remains after R4: a tick that redraws `#live_area` (a headline, a war phase or War badge change, or new research while on the Research page) can still swallow a click on the nav buttons, the Research page's buy buttons, or the Artifacts expedition buttons if it lands between mouse-down and mouse-up. Harmless (nothing happens; click again). **Don't worry about it during bug testing.** | won't fix |
| 3 | 2026-11-11, W1 | Pacing | Threat meter pacing not tuned yet (`THREAT_PER_SECOND`, `THREAT_PER_WAR_UNIT`, `MAX_THREAT_PER_SECOND`). Intermissions are about 50 s at the base rate. | deferred |
| 4 | 2026-11-11, W2 | Balance | Failed waves barely hurt: stock is usually 0 because every unit sells each tick, so `STOCK_LOSS_PER_SURVIVOR` rarely matters; only the production penalty (`raid_ms_left`) has an effect. | open |
| 5 | 2026-11-11, W2 | Balance | Wave 1 is trivial: the 2 starting MANPADS clear it in about 3 seconds. | deferred |
| 7 | 2026-11-11, W2 | Balance | Air defense has a flat cost (no cost growth), so it may get very cheap compared with late-game income. | deferred |
| 8 | 2026-11-11, W2 | Drafter | On page load, Drafter 2.1.4 shows "Unhandled configuration update event" errors in its debug panel for each `set_site_information` field. The game works; this looks like Drafter noise, not our code. | open |
| 10 | 2026-11-11, W3 | Debug | "End the war (lose)" (and "Skip to the last wave") count every skipped wave as broken through, so a defeat demo shows extreme numbers (e.g. 29 of 30). It no longer zeroes war goods sold. | open |
| 11 | 2026-11-12, lost-click fix | Pacing | The marketing campaign, warehouse expansion, and corporate organization items now need research (Social Media Playbook, Warehouse Zoning Permit, Corporate Restructuring Study), so the research chip shows 3 available within seconds of a new game (see #1). Their costs (100 / 250 / 750) are guesses. | deferred |
| 12 | 2026-11-13, Emails | Pacing | The research email arrives on tick 1, right after the welcome email, because some research is available almost at once (see #1 and #11). Raising the early `unlock_at_earned` values would space them out. | deferred |
| 14 | 2026-11-13, E1 | Balance | Company costs and bonuses in `COMPANY_ROWS` are guesses. Supplier bonuses match the old free goods bonuses, so early income is lower than before until suppliers are bought. | deferred |
| 16 | 2026-11-13, E2 | Balance | Sanctions now cut profit (not revenue) by 80%. Every workaround plus the war goods suppliers gets to about 1.15x pre-war income at markup 1.5; the 1.5x target relies on artifacts, food acquisitions, and policies, which isn't measured yet. Workaround costs (8000 / 12000 / 18000) are guesses. | deferred |
| 17 | 2026-11-13, E2 | UI | The "Income bonus" chip doesn't include the sanctions cut; it shows only in the "🚫 Sanctions" effect tag. | open |
| 18 | 2026-11-13, E3 | Balance | Opinion numbers are guesses: start 60, company costs -15 to 25 opinion (all 16 cost 152 in total), contributions +10 for Ŧ2000 (x1.5 each), Government supply 2 units/tick for +0.1 each, policy drains 0.05-0.15/s. | deferred |
| 20 | 2026-11-13, E3 | UI | The Government Relations card and the Acquisitions note are drawn on click, so they don't show live opinion; the chip does. | open |
| 21 | 2026-11-13, opinion rework | Balance | Government supply takes its units before selling, so it competes with sales for stock, and it is per tick, so a faster tick speed (Admin upgrade) will also speed it up. | open |
| 22 | 2026-11-13, arms bailouts | Balance | Bailout upkeep (Bronik Ŧ8/s, Zhuzh Ŧ12/s, Kovalev Ŧ10/s) and the cheaper bailout prices are guesses, and wartime income is low after the 80% sanctions cut. Upkeep that can't be paid is skipped (no debt, no penalty), so it can never ruin the player. | deferred |

| 23 | 2026-11-13, war rework | Balance | Era numbers are guesses. Wave 30 (boss, era 3) holds about 45,000 HP across 23 attackers plus up to 7 MIRV warheads, so it needs about 1,500 DPS per altitude, which is roughly Ŧ200k-Ŧ300k of flat-cost defenses. `BOSS_WAR_GOODS` (2000 / 10000 / 25000), `ERA_PENALTY_PER_THREAT`, the penalty cap (50%), and the reduction values are untested guesses too. | deferred |
| 24 | 2026-11-13, war rework | Pacing | The waiting penalty keeps growing while a boss wave is locked behind its war goods requirement, so a player who is short of war goods earns less while trying to catch up. This is intended pressure, but it could feel unfair if war goods come slowly. | open |
| 25 | 2026-11-13, war rework | Balance | Losing a wave takes items from the repeatable item owned the most (usually Procurement Agents), and each lost unit makes the next one cheaper to rebuy, so the loss is mild. | open |

## Resolved

| # | Found | Area | Issue | Fix |
|---|-------|------|-------|-----|
| R1 | 2026-11-11, W1 | Business | Unsure whether goods selected before the war lose their bonus when sanctioned. Checked: `start_war` switches off every sanctioned goods type, so its bonus stops counting. A test was added (`make_veteran_electronics_state`). | 4278116 |
| R2 | 2026-11-11, W2 | War | A failed dire wave reported "air defenses damaged" even when the 25% loss rounded down to 0 units. It now reports the real number lost. | 4278116 |
| R3 | 2026-11-11, W3 | Debug | "End the war (win)" showed "Waves defended: 0 of 35". A debug win now counts every wave as defended. | ddd0672 |
| R4 | 2026-11-10, Research | UI | Lost clicks on the Company page (part of #2): a tick that redrew `#live_area` rebuilt the Buy, X1/X5/X10, and markup buttons, swallowing a click held across the redraw. Fixed: those buttons moved outside `#live_area` (`build_company_controls`), World News moved above them, the research count became a chip in `#live_numbers` instead of a nav badge, and new buy items appear only through research, so no tick ever redraws them. Checked in the browser: a wave-start tick redrew the header while all 7 Company buttons stayed the same elements. | this commit |
| R5 | 2026-11-12, lost-click fix | UI | The sticky top bar scrolled away on pages where `#live_area` held only the top bar (e.g. Business at phone width), because a sticky element only sticks inside its parent. Fixed with `#live_area {display: contents}`. | this commit |
| R6 | 2026-11-13, E1 | Balance | Household Goods and Canned Food got a free wartime bonus (`war_bonus`) without a supplier. Removed: `GoodsType.war_bonus` and `goods_war_bonus` are gone. | E2 commit |
| R7 | 2026-11-13, Emails | Emails | The confiscation notice had no real trigger. Now `end_wave` calls `confiscate` every `CONFISCATION_EVERY_WAVES` waves, which sends it. | E3 commit |
| R8 | 2026-11-13, E3 | Balance | A player who sold no goods types counted as selling no war goods, so opinion drained from the first second of the war. Removed: opinion no longer falls for too few war goods. | opinion rework commit |
| R9 | 2026-11-13, war start | Balance | Softlock after the war started: sanctions cut all revenue by 80%, so a sale earned less than the Ŧ15 unit cost (Ŧ5.04 at markup 1.4 with +20% bonus). Money drained below Ŧ15, agents could not restock, and income stopped. Fixed: sanctions now cut only the profit, and every sale earns back `UNIT_COST` (tested in `calculate_income`). | sanctions profit fix commit |
| R10 | 2026-11-11, W2 | War | Dire wave equipment loss rounded down (#6). Removed in the war rework: failed waves destroy Company page items instead, and confiscations take air defenses. | war rework commit |
| R11 | 2026-11-11, W3 | Balance | `WAR_VICTORY_GOODS = 30000` was a guess (#9). Removed in the war rework: the war is won by repelling wave 30, and war goods now gate the boss waves (`BOSS_WAR_GOODS`). | war rework commit |
