# Advanced Techniques

A running list of every technique the course hasn't covered. Each technique
used in the project is explained **once**: here, and in one `# ADVANCED:`
comment in `main.py` (at the place named in "Explained at"). Other uses of
the same technique get no extra comment. When a new technique is added,
add a row here and one `# ADVANCED:` comment.

## Used in the project

| # | Technique | What it does (plain English) | Explained at | Also used in |
|---|-----------|------------------------------|--------------|--------------|
| 1 | Drafter site settings (`hide_debug_information`, `set_website_title`, `set_website_framed`) | Hide Drafter's debug panel, name the browser tab, and let the game fill the whole window instead of a small frame. | top of `main.py` | — |
| 2 | `set_browser_history(False)` | Stops Drafter copying each route into the URL, so refreshing the browser can't rerun the `tick` route on a blank page and crash. | top of `main.py` | — |
| 3 | CSS styling (`THEME_CSS`, `add_website_css`, `classes="..."`) | CSS is the language browsers use to style a page. Each rule names a class (like `.card`) and sets its colors, spacing, and layout. Components get those class names through `classes="..."`. | `THEME_CSS` | `add_website_css(THEME_CSS)`, `build_chip` and every page helper (`classes=`) |
| 4 | `Div` / `Span` and `id=` | A `Div` groups components into a block; a `Span` groups them inside one line. An `id` names a `Div` so a `Fragment` can find it and replace just that part. | `build_top_bar` (`#live_numbers`) | every page helper; `#live_area` in each page |
| 5 | `Fragment` | Replaces one element of the page instead of rebuilding the whole page, so the `Clock` isn't restarted and buttons outside it aren't redrawn mid-click. | `tick` | — |
| 6 | `Clock` (persistent) | Calls a route over and over (here `tick`). `persistent=True` keeps it running when the player changes pages. | `build_game_clock` | — |
| 7 | `RemovePersistent` | Stops the persistent `Clock` with a given id, so a new game never has two clocks ticking. | `build_start_content` | — |
| 8 | `Argument` | Lets a `Button` send an extra value to its route, so one route can serve many buttons. | `build_buy_amount_controls` | `buy_item`, `buy_research`, `buy_company`, `buy_defense`, `run_expedition`, `open_email`, `debug_add_money`, `debug_jump` buttons |
| 9 | `random.random()` | Gives a decimal from 0 up to (not including) 1; comparing it with a chance (like 0.1) is true that often. | `roll_strike` | — |
| 10 | `random.randint(a, b)` | Picks a whole number from `a` to `b`, including both ends. | `roll_wave_choices` | `roll_rarity`, `roll_artifact_row`, `roll_prompt` |
| 11 | `.isascii()` | True only if every character is a plain keyboard character, so symbols like a superscript ² can't sneak into `int(...)`. | `parse_bet` | — |
| 12 | `.capitalize()` | Returns a copy of a string with its first letter in upper case (`"stat"` → `"Stat"`). | `research_summary` | `build_altitude_summary`, `build_company_row` |
| 13 | Default parameter values (`= False`) | A parameter with `= False` uses `False` when no value is sent. A locked goods type has no CheckBox, so the browser sends nothing for it. | `save_goods` | `save_policies` |
| 14 | List repetition (`[x] * n`) | A list times a number repeats it: `["x"] * 3` is `["x", "x", "x"]`. Used in tests to build long sample lists. | test below `add_news` | tests for `state_after_emails`, `build_wave`, `spawn_attackers` |

## On the course's "not covered" list, but not used

f-strings, list comprehensions, lambdas, `min`/`max` with keys, Drafter's
`Timer`, and default dataclass fields (`field(...)`). The project builds
strings with `+` and `str()`, uses plain `for` loops, and calls `min`/`max`
only on two numbers.
