# Requirements Checklist

Missing more than 2 site requirements = zero credit. After each phase, check
off what is done and name the exact function or field that satisfies it.

## Site

- [x] At least 7 routes — _where:_ 34 routes: `index`, `start_game`,
      `company_page`, `business_page`, `research_page`, `buy_research`,
      `artifacts_page`, `organize_page`,
      `casino_page`, `start_typing_round`, `submit_typing_round`,
      `save_goods`, `save_policies`, `run_expedition`, `save_artifact_grid`,
      `set_buy_amount`, `buy_item`, `raise_markup`, `lower_markup`, `tick`,
      `debug_page`, `debug_add_money`, `debug_jump`, `war_page`,
      `buy_defense`, `start_next_wave`, `war_victory_page`,
      `war_defeat_page`,
      `inbox_page`, `open_email`, `acquisitions_page`, `buy_company`,
      `make_contribution`, `toggle_government_supply`
- [x] At least 5 pages — _where:_ start page (`index`), company page
      (`company_page`), Business page (`business_page`), Research page
      (`research_page`), Artifacts page
      (`artifacts_page`), Organize page (`organize_page`), Casino page
      (`casino_page`), War page (`war_page`), victory page
      (`war_victory_page`), defeat page (`war_defeat_page`), Inbox page
      (`inbox_page`), opened email page (`open_email`), Acquisitions
      page (`acquisitions_page`), Debug page
      (`debug_page`, demo tool)
- [x] `State` dataclass with at least 4 fields — _where:_ `State` (43 fields)
- [x] At least one State field is a list/dict of a second dataclass —
      _where:_ `State.owned_artifacts: list[Artifact]`,
      `State.buy_items: list[BuyItem]`,
      `State.goods_types: list[GoodsType]`, `State.policies: list[Policy]`,
      `State.research: list[Research]`, `State.attackers: list[Attacker]`,
      `State.next_wave: list[Attacker]`,
      `State.defenses: list[DefenseEquipment]`,
      `State.inbox: list[Email]`, `State.companies: list[Company]`
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
      `money`, and `news_feed` (`buy_research`, through `complete_research`),
      `game_phase`, `war_goods_sold`, and `threat` (`tick`, through
      `run_war_economy`; also `debug_jump`), `attackers` (`.hp`, in `tick`
      through `run_wave` / `damage_attackers`; spawned attackers added
      by `run_spawners`), `next_wave` and `attackers` (`start_next_wave`
      through `start_wave`; `tick` through `end_wave` /
      `generate_next_wave`), `defenses` (`.owned`, in `buy_defense`; taken
      in `tick` through `confiscate_defenses`), `buy_items` (`.owned`
      lost in `tick` through `lose_company_items`), `wave_number`,
      `wave_ms_left`, `threat` (`start_next_wave`), `waves_defended`,
      `war_won`, `raid_ms_left`, `last_wave_report` (`tick`), `inbox` and
      `sent_email_keys` (`start_game` and `tick`, through `send_email`;
      `.is_read` in `open_email`), `companies` (`.is_owned`, in
      `buy_company` through `acquire_company`), `government_opinion`
      (`make_contribution`, `buy_item`, `buy_research`, and `tick`),
      `contributions_made` (`make_contribution`), `supplies_government`
      (`toggle_government_supply`), `money` (`tick`,
      through `end_wave` / `confiscate`)
- [x] At least 3 input fields (TextBox, CheckBox, SelectBox, TextArea)
      — _where:_ `TextBox("company_name")` in `build_start_content`, one
      `CheckBox` per goods type in `build_goods_form`, one `CheckBox` per
      policy in `build_policy_form`, one `SelectBox` per grid slot in
      `build_organize_form`, `SelectBox("difficulty")` and `TextBox("bet")` in
      `build_casino_setup_form`, `TextArea("typed_text")` in
      `build_typing_form`
- [x] At least 3 meaningful if statements — _where:_ `buy_item` (can afford),
      `build_buy_list` (`is_item_visible` research check),
      `build_buy_action`
      (sold out), `build_nav` (which tab is current), `build_policy_chips`
      (only nonzero effects, strike warning), `clean_company_name` (blank
      name),
      `run_strikes` (strike running / new strike), `build_live_content`
      (which page is showing), `policy_label` (locked policy),
      `total_artifact_bonus` (placed or not), `add_artifact_copy` (duplicate
      or new), `run_expedition` (can afford), `can_place_bet` (bet limits),
      `roll_prompt` (difficulty), `start_typing_round` (bet accepted),
      `buy_research` (can buy), `is_requirement_met` (research needed),
      `nav_label` (War badge), `build_research_chips` (research
      available), `controls_signature` (Research page open),
      `build_research_list` (available or
      none), `policy_label` (which lock applies), `run_war_economy` (war
      starts / threat full), `build_goods_row` (sanctioned goods),
      `sanctions_multiplier` (peace or war), `percent_text` (negative),
      `describe_research_effect` (sanction recovery, parallel imports),
      `active_effect_lines` (wartime sanctions tag),
      `apply_debug_jump` (which shortcut), `run_intermission` (meter full,
      briefing unread), `wave_blocker` (why a wave can't start: no war,
      wave running, briefing, boss war goods), `start_next_wave`
      (nothing blocks the wave), `is_boss_wave`, `boss_requirement`,
      `era_for_wave` (era limits), `pick_row_index` (weighted roll),
      `run_spawners` (spawner alive and timer up), `spawn_attackers`
      (attacker cap), `waiting_penalty` (cap), `penalty_reduction`
      (research done / artifact placed), `most_owned_item_index`
      (repeatable and owned most), `buy_defense` (foreign costs
      opinion), `defense_origin_text` (foreign or domestic), `run_wave` (wave won or out of time), `end_wave` (won
      or broke through; last wave ends the war), `finish_war` (won or
      lost), `war_page` (war over: which report), `damage_attackers` (same
      altitude and alive),
      `defense_dps` (which altitude), `buy_defense` (can afford),
      `send_email` (once only unless repeatable), `run_email_triggers`
      (research first available), `open_email` (email exists),
      `build_email_row` (read or unread icon), `buy_company` (can
      buy), `is_company_for_sale` (owned or research missing),
      `describe_company_effect` (which sector), `goods_detail_text`
      (no supplier owned), `clamp_opinion` (out of range),
      `foreign_purchase_opinion_loss` (foreign item in wartime),
      `government_supply_units` (opinion maxed), `run_government_supply`
      (switched on in wartime), `build_government_card` (supply
      unlocked, on or off), `toggle_government_supply` (unlocked),
      `describe_policy` (opinion drain), `acquire_company` (arms
      bailout warning), `is_company_for_sale` (required company),
      `opinion_cost_text` (Government grateful), `upkeep_text`
      (bailout), `upkeep_payment` (reserve), `end_wave`
      (confiscation wave), `make_contribution` (can contribute),
      `build_opinion_chip` (low opinion), `is_food_empire_complete`
      (missing supplier or research), `run_email_triggers` (food
      empire, low opinion)
- [x] At least 1 loop over the list/dict of dataclass instances, used in a
      meaningful way — _where (main answer):_ `total_artifact_bonus` loops
      over `state.owned_artifacts`, skips unplaced artifacts, and totals the
      bonuses that feed `calculate_total_bonus` and income. _Also:_
      `total_item_effect` (loops over
      `state.buy_items` to total each stat), `build_buy_list`,
      `total_goods_bonus` (`state.goods_types`), `total_strike_risk` and the
      other `total_policy_...` helpers (`state.policies`),
      `count_available_research`, `is_research_done` (linear search), and
      the `total_research_...` helpers (`state.research`), `war_units_sold`
      (`state.goods_types`, counts war goods being sold);
      `damage_attackers` loops over `state.attackers` and carries leftover
      damage to the next attacker (`enemy_hp`, `count_survivors` too);
      `run_spawners` loops over `state.attackers` to count down spawner
      timers and launch new attackers; `count_attacker_kinds` loops over
      `state.next_wave` for the preview; `total_dps` and
      `confiscate_defenses` loop over `state.defenses`;
      `lose_company_items` / `most_owned_item_index` loop over
      `state.buy_items`; `penalty_reduction` loops over `state.research`
      and `state.owned_artifacts`; `count_unread`,
      `is_email_unread`, and `build_inbox_list` loop over `state.inbox`;
      `supplier_bonus` and `total_company_effect` loop over
      `state.companies` to total the bonuses of owned companies;
      `sanctions_multiplier` loops over `state.research` to add the
      income each completed workaround wins back;
      `is_food_empire_complete` loops over `state.companies` and
      `state.research` to check every canned food source is owned;
      `total_policy_opinion_drain` loops over `state.policies`;
      `total_company_upkeep` and `is_company_owned` loop over
      `state.companies`
- [x] Legitimate purpose (entertainment: it's a game) — _where:_ the whole site
- [x] No global variables; only ALL_CAPS constants, never mutated — _where:_
      constants block; `make_starting_items`, `make_starting_goods`,
      `make_starting_policies`, `make_starting_research`,
      `make_starting_companies`,
      `artifact_from_row`, and `make_new_state` copy them
- [x] Uses Drafter — _where:_ `main.py`, `start_server(make_new_state())`
- [x] Any technique not covered in the course is explained in a comment or
      docstring — _where:_ the full list, with one explanation each, is
      `docs/advanced_techniques.md`. Each technique has exactly one
      `# ADVANCED:` comment in `main.py`: top of the file (Drafter site
      settings, `set_browser_history`), `THEME_CSS` (CSS, `classes=`),
      `build_top_bar` (Div / Span, `id=`), `tick` (Fragment),
      `build_game_clock` (Clock), `build_start_content` (RemovePersistent),
      `build_buy_amount_controls` (Argument), `roll_strike`
      (`random.random`), `roll_wave_choices` (`random.randint`),
      `parse_bet` (`.isascii`), `research_summary` (`.capitalize`),
      `save_goods` (default parameter values), and the test below
      `add_news` (list repetition)

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
      function `calculate_payout` is pure and tested;
      `roll_wave_choices` and `generate_next_wave` are random helpers
      (docstrings say so); `build_wave` is pure and tested with fixed
      rolls, and `start_next_wave` is tested with a stored wave
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
