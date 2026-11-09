# Requirements Checklist

Missing more than 2 site requirements = zero credit. After each phase, check
off what is done and name the exact function or field that satisfies it.

## Site

- [x] At least 7 routes — _where:_ 11 routes: `index`, `start_game`,
      `company_page`, `business_page`, `save_goods`, `save_policies`,
      `set_buy_amount`, `buy_item`, `raise_markup`, `lower_markup`, `tick`
- [ ] At least 5 pages — _where:_ 3 so far: start page (`index`), company page
      (`company_page`), Business page (`business_page`)
- [x] `State` dataclass with at least 4 fields — _where:_ `State` (17 fields)
- [x] At least one State field is a list/dict of a second dataclass —
      _where:_ `State.buy_items: list[BuyItem]`,
      `State.goods_types: list[GoodsType]`, `State.policies: list[Policy]`
- [x] At least 4 State fields, including that list/dict, are meaningfully
      modified in at least one route — _where:_ `buy_items` (`.owned`, in
      `buy_item`), `money` (`buy_item`, `tick`), `markup` (`raise_markup`,
      `lower_markup`), `loyalty` (`tick`), `goods_types` and
      `sells_war_supplies` (`save_goods`), `policies` (`save_policies`),
      `strike_ticks_left` and `news_feed` (`tick`, through `run_strikes`)
- [x] At least 3 input fields (TextBox, CheckBox, SelectBox, TextArea)
      — _where:_ `TextBox("company_name")` in `build_start_content`, one
      `CheckBox` per goods type in `build_goods_form`, one `CheckBox` per
      policy in `build_policy_form`
- [x] At least 3 meaningful if statements — _where:_ `buy_item` (can afford),
      `build_buy_list` (`is_item_visible` unlock check), `build_buy_action`
      (sold out / can't afford), `clean_company_name` (blank name),
      `run_strikes` (strike running / new strike), `build_live_content`
      (which page is showing), `policy_label` (locked policy)
- [x] At least 1 loop over the list/dict of dataclass instances, used in a
      meaningful way — _where:_ `total_item_effect` (loops over
      `state.buy_items` to total each stat), `build_buy_list`,
      `total_goods_bonus` (`state.goods_types`), `total_strike_risk` and the
      other `total_policy_...` helpers (`state.policies`)
- [x] Legitimate purpose (entertainment: it's a game) — _where:_ the whole site
- [x] No global variables; only ALL_CAPS constants, never mutated — _where:_
      constants block; `make_starting_items`, `make_starting_goods`,
      `make_starting_policies`, and `make_new_state` copy them
- [x] Uses Drafter — _where:_ `main.py`, `start_server(make_new_state())`
- [x] Any technique not covered in the course is explained in a comment or
      docstring — _where:_ `ADVANCED:` notes in `build_game_clock` (Clock),
      `tick` (Fragment), and `roll_strike` (`random.random`)

## Code quality

- [x] Good, descriptive variable and function names
- [x] Every route has at least one `assert_equal` unit test, unless it uses
      randomness (and its docstring says so) — _where:_ directly below each
      route in `main.py`; `tick` uses randomness (its docstring says so) but
      is still tested with zero-risk States
- [x] Lines under 80 characters (hard limit 120)
- [x] Type hints on every function header
- [x] A docstring as the first line of every function body
- [x] Long functions broken into helper functions

## Repository

- [x] `set_site_information(...)` called in `main.py` — _where:_ top of
      `main.py` (`author` is still "TODO: your name")
- [ ] Planning document in the repo (`docs/`) — _where:_
- [ ] Linked demo video — _where:_
- [ ] All AI conversations in the repo (`ai_conversations/`) — _where:_
