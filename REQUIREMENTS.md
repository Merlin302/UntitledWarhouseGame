# Requirements Checklist

Missing more than 2 site requirements = zero credit. After each phase, check
off what is done and name the exact function or field that satisfies it.

## Site

- [x] At least 7 routes — _where:_ 20 routes: `index`, `start_game`,
      `company_page`, `business_page`, `research_page`, `buy_research`,
      `artifacts_page`, `organize_page`,
      `casino_page`, `start_typing_round`, `submit_typing_round`,
      `save_goods`, `save_policies`, `run_expedition`, `save_artifact_grid`,
      `set_buy_amount`, `buy_item`, `raise_markup`, `lower_markup`, `tick`
- [x] At least 5 pages — _where:_ start page (`index`), company page
      (`company_page`), Business page (`business_page`), Research page
      (`research_page`), Artifacts page
      (`artifacts_page`), Organize page (`organize_page`), Casino page
      (`casino_page`)
- [x] `State` dataclass with at least 4 fields — _where:_ `State` (25 fields)
- [x] At least one State field is a list/dict of a second dataclass —
      _where:_ `State.owned_artifacts: list[Artifact]`,
      `State.buy_items: list[BuyItem]`,
      `State.goods_types: list[GoodsType]`, `State.policies: list[Policy]`,
      `State.research: list[Research]`
- [x] At least 4 State fields, including that list/dict, are meaningfully
      modified in at least one route — _where:_ `buy_items` (`.owned`, in
      `buy_item`), `money` (`buy_item`, `tick`), `markup` (`raise_markup`,
      `lower_markup`), `loyalty` (`tick`), `goods_types` and
      `sells_war_supplies` (`save_goods`), `policies` (`save_policies`),
      `strike_ticks_left` and `news_feed` (`tick`, through `run_strikes`),
      `owned_artifacts` (`run_expedition`, `save_artifact_grid`),
      `expeditions_bought` and `last_expedition_finds` (`run_expedition`),
      `tick_count` (`tick`), `typing_round` and `last_casino_result`
      (`start_typing_round`, `submit_typing_round`), `research` (`.is_done`),
      `money`, and `news_feed` (`buy_research`, through `complete_research`)
- [x] At least 3 input fields (TextBox, CheckBox, SelectBox, TextArea)
      — _where:_ `TextBox("company_name")` in `build_start_content`, one
      `CheckBox` per goods type in `build_goods_form`, one `CheckBox` per
      policy in `build_policy_form`, one `SelectBox` per grid slot in
      `build_organize_form`, `SelectBox("difficulty")` and `TextBox("bet")` in
      `build_casino_setup_form`, `TextArea("typed_text")` in
      `build_typing_form`
- [x] At least 3 meaningful if statements — _where:_ `buy_item` (can afford),
      `build_buy_list` (`is_item_visible` unlock check), `build_buy_action`
      (sold out), `build_nav` (which tab is current), `build_policy_chips`
      (only nonzero effects, strike warning), `clean_company_name` (blank
      name),
      `run_strikes` (strike running / new strike), `build_live_content`
      (which page is showing), `policy_label` (locked policy),
      `total_artifact_bonus` (placed or not), `add_artifact_copy` (duplicate
      or new), `run_expedition` (can afford), `can_place_bet` (bet limits),
      `roll_prompt` (difficulty), `start_typing_round` (bet accepted),
      `buy_research` (can buy), `is_requirement_met` (research needed),
      `nav_label` (research badge), `build_research_list` (available or
      none), `policy_label` (which lock applies)
- [x] At least 1 loop over the list/dict of dataclass instances, used in a
      meaningful way — _where (main answer):_ `total_artifact_bonus` loops
      over `state.owned_artifacts`, skips unplaced artifacts, and totals the
      bonuses that feed `calculate_total_bonus` and income. _Also:_
      `total_item_effect` (loops over
      `state.buy_items` to total each stat), `build_buy_list`,
      `total_goods_bonus` (`state.goods_types`), `total_strike_risk` and the
      other `total_policy_...` helpers (`state.policies`),
      `count_available_research`, `is_research_done` (linear search), and
      the `total_research_...` helpers (`state.research`)
- [x] Legitimate purpose (entertainment: it's a game) — _where:_ the whole site
- [x] No global variables; only ALL_CAPS constants, never mutated — _where:_
      constants block; `make_starting_items`, `make_starting_goods`,
      `make_starting_policies`, `make_starting_research`,
      `artifact_from_row`, and `make_new_state` copy them
- [x] Uses Drafter — _where:_ `main.py`, `start_server(make_new_state())`
- [x] Any technique not covered in the course is explained in a comment or
      docstring — _where:_ `# ADVANCED:` comments at the top of `main.py`
      (Drafter site settings, `set_browser_history`), `THEME_CSS` (CSS
      styling), `build_chip` (`classes=`), `build_game_clock`
      (Clock), `tick` (Fragment), `build_start_content` (RemovePersistent),
      `build_top_bar` (Div ids), `build_buy_amount_controls` (Argument),
      `roll_strike` (`random.random`), `roll_rarity`, `roll_artifact_row`,
      `roll_prompt` (`random.randint`), `parse_bet` (`.isascii`), and
      `save_goods` / `save_policies` (default parameter values `= False`)

## Code quality

- [x] Good, descriptive variable and function names
- [x] Every route has at least one `assert_equal` unit test, unless it uses
      randomness (and its docstring says so) — _where:_ directly below each
      route in `main.py`, with sample-data functions in the "Test helpers"
      section; `tick` uses randomness (its docstring says so) but
      is still tested with zero-risk States; `run_expedition` uses randomness
      (its docstring says so) and only its "can't afford" path is tested;
      `roll_rarity`, `roll_artifact_row`, and `collect_expedition_finds` are
      random helpers, exempt, and say so in their docstrings;
      `start_typing_round` uses randomness (its docstring says so) and only
      its rejected-bet paths are tested; `roll_prompt` is exempt; the scoring
      function `calculate_payout` is pure and tested
- [x] Lines under 80 characters (hard limit 120)
- [x] Type hints on every function header
- [x] A Google-format docstring as the first line of every function body
- [x] Long functions broken into helper functions

## Repository

- [x] `set_site_information(...)` called in `main.py` — _where:_ top of
      `main.py` (`author` is the GitHub username; `links` is still empty
      until the demo video exists)
- [ ] Planning document in the repo (`docs/`) — _where:_
- [ ] Linked demo video — _where:_
- [ ] All AI conversations in the repo (`ai_conversations/`) — _where:_
