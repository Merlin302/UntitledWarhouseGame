# CLAUDE.md — Untitled Warehouse Inc. (CISC-106 Final Project)

You are helping a beginner Python student (CISC-106, University of Delaware)
build their final project: an incremental/idle management game that runs as a
website using the **Drafter** library. The student's professors encouraged
vibecoding, but the student must be able to explain the code in a video and
to a TA. Read this whole file before every task.

## How to work with me

- **Plan before coding.** For every phase, propose a short plan first: the
  dataclasses/fields, routes, and helper functions you will add or change.
  Wait for my OK.
- **Build one phase at a time.** Don't add features I didn't ask for. If you
  think something is missing, suggest it in one line at the end.
- **Keep explanations short.** After each phase, give me: (1) what you built in
  3-5 bullets, (2) a brief explanation of any technique I haven't seen before
  (see "Course concepts" below), (3) how to run and test it, (4) anything I
  should check by playing the game. No long recaps.
- **Save tokens.** Don't re-read or reprint whole files unnecessarily. Make
  targeted edits. Don't paste large code blocks into chat that are already in
  the file.
- **Run the tests** after every change and fix failures before reporting done.
- **Commit** at the end of each phase with a concise, descriptive message
  (e.g. "Add artifact expeditions and grid placement"), never
  "Update main.py".
- **Keep `REQUIREMENTS.md` updated**: a checklist mapping each assignment
  requirement to the exact function/field that satisfies it. I'll use it for my
  video and to double-check before submitting.
- **Keep `docs/playtest_issues.md` updated**: add issues noticed while
  play-testing (yours or mine), and move fixed ones to "Resolved".

## Assignment requirements (missing more than 2 = zero credit)

Site:
- At least 7 routes and at least 5 pages.
- `State` dataclass with at least 4 fields. At least one field is a list (or
  dict) of instances of a second dataclass. At least 4 State fields, including
  that list/dict, must be meaningfully modified in at least one route (not
  constants).
- At least 3 input fields (TextBox, CheckBox, SelectBox, TextArea).
- At least 3 meaningful if statements.
- At least 1 loop that iterates over the list/dict of dataclass instances in a
  meaningful way.
- Legitimate purpose (it's a game — entertainment).
- **No global variables.** Global CONSTANTS (ALL_CAPS, never mutated) are fine.
  Never mutate a global constant list/dataclass — copy it into State instead.
- Must use Drafter.
- Any technique not covered in the course must be explained in a comment or
  docstring.

Code quality (graded by a TA):
- Good, descriptive variable and function names.
- Every route has at least one unit test using Drafter's `assert_equal`, unless
  it uses randomness — then say so in its docstring.
- Lines under 80 characters (hard limit 120).
- Type hints on every function header.
- A docstring as the first line of every function body, in Google format: a
  description, then `Args:` and `Returns:` sections. Leave out `Args:` only if
  the function has no parameters, and `Returns:` only if it returns `None`.
- Each function's `assert_equal` tests go directly below that function, not
  in a separate tests section. Sample data shared by tests goes in the "Test
  helpers" section, above the code that uses it.
- Long functions broken into helper functions.

Repository:
- `set_site_information(...)` called in `main.py`.
- Planning document, a linked demo video, and all AI conversations in the repo
  (I'll handle those; keep a `docs/` and `ai_conversations/` folder ready).

## Course concepts (stick to these when possible)

Covered: variables, int/float/str/bool, arithmetic incl. `//` and `%`,
comparisons, `and`/`or`/`not`, string indexing/slicing, `in`, string methods
(`.split`, `.strip`, `.replace`, `.isdigit`), functions with type hints and
docstrings, `assert_equal` testing, if/elif/else, truthiness, dataclasses,
nested dataclasses, lists, lists of dataclasses, 2D lists, `for` loops,
`range(len(...))`, `enumerate`, `while` loops, `.append`, file reading,
recursion, bubble/insertion sort, linear/binary search, basic dictionaries
(JSON is being covered now). String building with `+` and `str()`.

Not covered (use only when it clearly helps, and mark it with a comment that
starts `# ADVANCED:` plus a 1-2 line plain-English explanation): f-strings,
list comprehensions, lambdas, `random` module functions beyond the basics,
`min`/`max` with keys, Drafter's `Clock`, `Fragment`, `Timer`, CSS/HTML
styling, default dataclass fields via `field(...)`.

Avoid entirely unless I ask: classes with methods, inheritance, decorators
other than `@dataclass` and `@route`, try/except, generators, JavaScript.

## Drafter notes

- Docs: https://drafter-edu.github.io/drafter/ — check the docs (especially
  the Components, Timers, Testing, and Deploy pages) instead of guessing APIs.
- **The game tick:** use one Drafter `Clock` that calls a `tick` route. The
  tick route updates State and returns a `Fragment` targeting the stats area,
  so the page (and the clock) isn't re-rendered every tick. Per the docs:
  re-rendering a page restarts a non-persistent clock, and a persistent clock
  plus a re-rendered copy can run at the same time. Make sure exactly ONE
  clock is ever ticking, including when the player switches pages. Verify
  this works before building more on top of it.
- Base tick interval: 1 tick every 3000 ms (the Admin upgrade will speed this
  up later, so read the interval from State/a helper, not a hard-coded value).
- Keep all code in `main.py` unless you confirm that Drafter's GitHub Pages
  deployment supports importing other local `.py` files.
- No libraries other than Drafter and the Python standard library (`random`,
  `dataclasses`). The site must work when deployed to GitHub Pages.
- Images: use emoji placeholders. Don't generate images.

## Architecture rules

1. **All balance numbers are global constants in one block at the top of
   `main.py`** (prices, rates, bonuses, cost growth, tick interval). I will
   tune these later without touching logic.
2. **`make_new_state() -> State`** builds the starting state. Use it in
   `start_server(...)` and in tests, so adding a State field later only means
   editing one place.
3. **Routes stay thin.** Game math lives in small pure helper functions
   (inputs in, value out, no randomness) so they're easy to unit test.
4. **Isolate randomness** in tiny functions (e.g. `roll_rarity()`), so
   everything else stays testable.
5. **Group code by system** with section comments: constants, dataclasses,
   economy, purchases, business (goods/policies), artifacts, casino, page
   helpers, routes. Each future system (research, invest, decisions,
   war, an ending) should be addable without rewriting existing systems.
6. **Shared page helpers**: one helper builds the top navigation bar
   (Company / Business / Artifacts / Casino) and the money display, used by
   every page.
7. **Bounded State, small ticks.** Every list (or dict) stored in State must
   have a maximum size, set by a constant (e.g. `MAX_NEWS_ITEMS`) or by a
   fixed catalog (e.g. one entry per artifact type), and must be trimmed
   wherever it grows. Per-tick work must stay small: `tick` may loop only
   over those bounded lists, must not loop over a player-chosen count, and
   should update `#live_numbers` rather than redraw `#live_area` whenever
   no button has changed. The game runs in the browser (Pyodide), where
   Python is much slower than on a desktop.
8. **UI theme and layout** (see `docs/ui_theme.md` for the full guide).
   - All styling lives in `THEME_CSS` (Theme section of `main.py`), added
     with `add_website_css`. Components get styles only through
     `classes="..."`; no inline styles, no other CSS files.
   - Colors come from the CSS variables at the top of `THEME_CSS` (slate
     top bar, amber accent, light gray page, white cards). Reuse them
     rather than adding new colors.
   - Reuse the existing building blocks: `build_top_bar` (sticky, holds
     nav + money), `build_chip` (one labelled number), `build_card_head`
     plus a `Div(..., classes="card")`, `.page`, `.dashboard`/`.two-col`
     grids, `.buy-row`, `.check-row`, `.button-row`, `.muted`.
   - Money must stay visible on every page (it is the first chip in
     `#live_numbers`). New per-tick numbers go into `#live_numbers` as
     chips; never put buttons there.
   - Action buttons stay on screen even when unaffordable; the route
     refuses the action. `controls_signature` must not depend on money.
   - Keep frequently clicked buttons outside `#live_area` when a page has
     per-tick content besides the top bar (the Company page puts the Buy
     list and Pricing cards in `build_company_controls`, after
     `#live_area`). A tick that redraws `#live_area` replaces every button
     inside it, which can swallow a click in progress. `#live_area` uses
     `display: contents` so the sticky top bar still sticks.
   - Check new pages at phone width (375 px): no sideways scrolling.

## Game design (current understanding — numbers are placeholders)

Theme: "Untitled Warehouse Inc." — an e-commerce warehouse company operating
in the middle of a war (a loose reference to the Russian company Wildberries).
Currency symbol: Ŧ.

**Core loop (every tick):**
1. Stocking: procurement agents buy goods into the warehouse.
   Cost per unit: 15. Limited by warehouse capacity and money.
2. Selling: units sold = the smallest of goods in stock, delivery capacity
   (vans), and customer demand.
3. Customer demand comes directly from customer loyalty (e.g.
   demand = MARKET_SIZE * loyalty / 100). Loyalty is raised by marketing,
   artifacts, upgrades, policies; lowered by high markup. Loyalty should drift
   gradually toward a target each tick rather than jump, and stay in 0-100.
4. Income = units sold * sale price * (1 + total bonus), where
   sale price = unit cost * markup, and total bonus adds goods-type bonuses,
   artifact bonuses, and policy effects.

**Company page (main dashboard):** money, goods stocked/sold per tick,
delivery capacity, warehouse capacity %, customer loyalty, a bonus summary
panel, the buy list, markup controls, and a World News feed (a list of recent
flavor-text strings).
- Buy list items (examples): Procurement Agent (+5 goods stocked/tick),
  Fordov Delivery Van (+1 delivery capacity), Short Form Marketing Campaign
  (+loyalty), Warehouse Expansion (+capacity), plus one-time unlocks like
  "Next Generation Corporate Organization" (unlocks a policy).
- Each repeat purchase costs more (cost * COST_GROWTH ** owned).
- X1 / X5 / X10 buttons set how many units one Buy click purchases.
- New items appear only through research (`required_research`), never
  from earnings alone, so a tick never has to redraw the Buy list.
- Increase/lower markup buttons.

**Business page:** checkboxes for which goods types to sell (each adds an
income bonus; "War supplies" gives a huge bonus and will later attract the
war), and checkboxes for policies (each has an upside and a downside, e.g.
unpaid overtime: +stocking, -loyalty, raises strike risk). Strikes (labor
unrest from policies) cause temporary penalties.

**Research page (sub-page of Business):** reached from the "Open
Research Lab" button on the Business page. A "🔬 Research" chip in
`#live_numbers` (`build_research_chips`) counts research that is available
(prerequisite done and unlocked by total_earned; money is ignored, per
rule 8). It is a chip rather than a nav badge so it can update without
redrawing the nav buttons. Each
`Research` (catalog: `RESEARCH_ROWS`) is bought once with money and takes
effect instantly, posting a World News headline. Categories: stat (%
stocking/delivery), equipment (unlocks a buy item), unlock (unlocks a goods
type or policy), world (market size, or a goods type's bonus). Buy items,
goods types, and policies have a `required_research` field ("" = none):
locked buy items and goods are hidden, locked policies are shown locked.
Research bonuses feed `total_stocking_bonus` / `total_delivery_bonus` (into
`apply_rate_modifiers`), `current_market_size` (into `calculate_demand`), and
`total_research_goods_bonus` (into `calculate_total_bonus`). The Better
Conveyor Belt uses `EFFECT_DELIVERY_BOOST` (a % per unit).

**The War (phase W1 built: war economy):** `State.game_phase` goes
peace -> war -> war_over (`PHASE_` constants). The war starts when
total_earned reaches `WAR_START_EARNED` (`start_war`, run by
`run_war_economy` in the tick), posting headlines. The Kalyxian Federation
invades the Republic of Varnia (fictional). In wartime, sanctioned goods
(`GoodsType.is_sanctioned`: Electronics, Imported Luxuries) are shown as
"🚫 Sanctioned" and forced off, and goods with a `war_bonus` (Household,
Canned Food) earn more as the only supplier (both feed
`goods_income_bonus`). War research (`Research.requires_war`): Defense
Procurement License (unlocks the war goods Body Armor and Drone
Components), and world research that buys out fleeing competitors (ParcelPro,
then Ozonix). `war_goods_sold` adds the war goods' share of each tick's
sales (`war_units_sold`). `threat` fills per real second (scaled by the tick
length, x `DEBUG_WAR_SPEED`), faster with more war goods sold, capped at
`MAX_THREAT_PER_SECOND`.

**War page (phase W2 built: air defense):** the War nav button appears once
the war starts (badge ❗ until the briefing is read, ⚠️ during a wave). A
one-time briefing (`seen_war_tutorial`) must be dismissed before wave 1.
Between waves the threat meter fills; when full, `start_wave` generates the
next wave with `make_wave(wave_number)` (count, HP, and attacker mix grow;
dire waves every `DIRE_WAVE_EVERY` and the last; capped at `MAX_ATTACKERS`)
and empties the meter. `ATTACKER_ROWS`: Pengvin drones (low), Kalibar cruise
missiles (medium/low), Mishka bombers (high). `DEFENSE_ROWS` (bought any
time, kept between waves, flat cost): Zhalo MANPADS (medium/low), LoM-16SM
fighter (mixed), MIN-400 Loyalist SAM (high); 2 MANPADS at the start. A
wave lasts `WAVE_DURATION_MS / DEBUG_WAR_SPEED` real ms (`wave_ms_left` minus
`tick_interval` each tick). `run_wave`: each altitude's damage hits the first
living attacker there, leftovers carry over. Failing a wave (`end_wave` /
`apply_raid_damage`): each survivor destroys stock and adds to
`raid_ms_left`, a production penalty applied with strikes through
`rate_penalty` -> `apply_rate_modifiers`; failing a dire wave also destroys
`DIRE_EQUIPMENT_LOSS_FRACTION` of each defense. On the War page the top bar
is not sticky and `#live_numbers` holds the whole battle board (Drafter
2.1.4 Fragments update one element); the briefing and shop sit outside it.
**End of the war (phase W3 built):** when wave `WAVE_COUNT` ends,
`end_wave` calls `finish_war`: `game_phase` becomes war_over and a ceasefire
headline is posted. The war is won if `war_goods_sold >= WAR_VICTORY_GOODS`
(`is_war_won`); failed waves matter because their production penalty means
fewer war goods sold. The War button becomes "War 📜", and `war_page` then
shows `war_victory_page` or `war_defeat_page` (waves defended, waves that
broke through, war goods sold, and an Epilogue placeholder for the ending
that comes later). The economy keeps running after the war.

**Debug page (🐞 in the nav, hidden when `DEBUG_TOOLS = False`):** buttons
that add money and jump ahead (restart in peace, unlock peacetime research,
start the war, fill the threat meter, start the next wave now, skip to
dire wave 10, skip to the last wave, end the war with a win or a loss), for
demos and play-testing.

**Artifacts page (gacha):** pay for expeditions (buttons for X1, X5, X10,
X100; price grows only slightly) to get random artifacts with rarity tiers
(e.g. common / rare / legendary with weighted odds). Artifacts are NOT
equally good. Duplicates increase that artifact's copy count/level. Only
artifacts placed in the 6x2 grid (12 slots) give bonuses. An "Organize" page
uses one SelectBox per slot to choose which owned artifact goes there.
Adjacency bonuses come in a later phase.

**Casino page:** deliberately silly games of chance/skill using in-game money.
First game: a typing test — pick a difficulty (SelectBox), type the prompt
(TextArea), reward based on accuracy and speed (time measured with the tick
or a Drafter timer). Easy = lowercase common words; hard = full quotes with
character swaps (a→@, and→&, 0↔O).

**Later phases (don't build yet, but don't block them):** Invest → Company
upgrades (Admin = tick speed, Input = stocking multiplier, Output = sales
multiplier), more research projects, HOI4-style
decisions (pay a cost now, effect lands N ticks later), more casino games
(pick-a-color pixel game on a code-generated colored grid, AI-image
geoguessr parody), stock market, artifact adjacency bonuses, the war
mechanic's later phases (air defense waves, the end of the war) that
eventually change
how the game is played (like Universal Paperclips' phases), and a game
ending.
