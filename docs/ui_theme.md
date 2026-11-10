# UI theme and layout guide

This is the reference for how Untitled Warehouse Inc. looks. Read it before
designing or building any new page or panel. The code is in `main.py`
(the Theme section holds `THEME_CSS` and `NAV_ROWS`; the Page helpers
section holds the builders named below).

Screenshots: `docs/screenshots/theme_company_desktop.jpg` and
`docs/screenshots/theme_company_phone.jpg`.

## Look

- **Palette** (CSS variables at the top of `THEME_CSS`):
  slate `--slate #1f2a37` (top bar, normal buttons),
  amber `--amber #f5b301` (accent: money chip, current tab, buy and
  expedition buttons, bar underline), light gray page `--paper #eef0f2`,
  white cards `--card`, gray text `--muted`, red `--warn` (strikes).
- **Type**: the system font, 15 px body, small uppercase gray card titles
  (`Header(title, 2)`), bold numbers.
- **Shape**: 6 px rounded buttons and chips, 10 px rounded cards with a
  thin border and no shadows.

## Layout

```
┌─ top bar (sticky, slate, amber underline) ──────────────────────────┐
│ Company Name        [Company] Business  Artifacts  Casino           │
│ [MONEY Ŧ825.00] [STOCKED 5/5] [SOLD 5/6] [INCOME ...] [WAREHOUSE] … │
│ (effect tags: 📺 Electronics +15% income  🧾 Receipt +1.5% income)   │
└─────────────────────────────────────────────────────────────────────┘
  Company page: two columns (stack into one below 760 px)
  ┌─ Buy List ────────── [x1][x5][x10] ┐  ┌─ Pricing ─────────────┐
  │ 🧑‍💼 Procurement Agent  [Buy x1 for …] │  │ Markup x1.5  ▼ ▲      │
  │ 🚐 Fordov Delivery Van [Buy x1 for …] │  ├─ World News ──────────┤
  └────────────────────────────────────┘  └───────────────────────┘
```

- **Top bar** (`build_top_bar`): name, tabs (`build_nav`, current tab is
  amber), then `#live_numbers`. Money is always the first chip, on every
  page. On the Company page the stat chips (`build_stat_chips`), nonzero
  policy chips and strike warning (`build_policy_chips`), and effect tags
  (`build_effect_tags`) follow.
- **Pages**: content sits in `Div(..., classes="page")` (centered, at most
  1100 px wide). Company uses `.dashboard` (3:2 columns), Business uses
  `.two-col` (1:1), and the other pages use one column of cards.
- **Cards**: `Div(build_card_head(title, [controls]), ..., classes="card")`.
  Controls in the head sit on the right (e.g. x1/x5/x10, Organize, Save
  Layout).
- **Rows**: `.buy-row` (emoji | name + muted details | button),
  `.check-row` (checkbox | label | muted effect), `.button-row`,
  `.form-row`, `.slot-grid` (6 × 2 like the artifact grid).

## Rules for new UI

1. Style only with `classes="..."` and rules added to `THEME_CSS`. Reuse
   the palette variables and existing classes before adding new ones.
2. Put new live numbers in `#live_numbers` as `build_chip(label, value,
   "chip")`. Never put buttons there; a tick replaces it every time.
3. Keep buttons stable: show them even when the player can't afford the
   action, and have the route refuse it. `controls_signature` only tracks
   news and which items are visible, never money.
4. Forms (checkboxes, select boxes, text boxes) go outside `#live_area`,
   so ticks can't reset them.
5. Test every new page at phone width (375 px) and check there is no
   sideways scrolling.

## Change log

- 2026-11-09: First custom theme. It replaced the plain Drafter look with
  the slate/amber dashboard, a sticky top bar with money chips, a
  two-column Company page, and stable Buy and expedition buttons.
