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
- Items unlock/appear as the player progresses (if statements).
- Increase/lower markup buttons.

**Business page:** checkboxes for which goods types to sell (each adds an
income bonus; "War supplies" gives a huge bonus and will later attract the
war), and checkboxes for policies (each has an upside and a downside, e.g.
unpaid overtime: +stocking, -loyalty, raises strike risk). Strikes (labor
unrest from policies) cause temporary penalties.

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
multiplier), research (one-time permanent bonuses/unlocks), HOI4-style
decisions (pay a cost now, effect lands N ticks later), more casino games
(pick-a-color pixel game on a code-generated colored grid, AI-image
geoguessr parody), stock market, artifact adjacency bonuses, the war
mechanic (missile strikes, air defense, the front) that eventually changes
how the game is played (like Universal Paperclips' phases), and a game
ending.
