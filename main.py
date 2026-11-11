import random
from dataclasses import dataclass
from drafter import *


# ADVANCED: These Drafter settings hide the debug panel, name the browser tab,
# and let the game fill the whole window instead of a small frame.
hide_debug_information()
set_website_title("Untitled Warehouse Inc.")
set_website_framed(False)
# ADVANCED: Stops Drafter copying each route into the URL. Otherwise a browser
# refresh would rerun the "tick" route on a blank page and crash.
set_browser_history(False)
set_site_information(
    author="Merlin302",
    description="An incremental warehouse management game.",
    sources=["Drafter documentation"],
    planning=["docs/"],
    links=[],
)


# ---------------------------------------------------------------------------
# Constants: every balance number lives here
# ---------------------------------------------------------------------------

CURRENCY_SYMBOL = "Ŧ"
DEFAULT_COMPANY_NAME = "Untitled Warehouse Inc."

# The id shared by the one persistent Clock and its RemovePersistent.
GAME_CLOCK_ID = "game_clock"
# A Clock needs whole milliseconds; 667 ms is about 1.5 ticks per second.
TICK_INTERVAL_MS = 667

STARTING_MONEY = 500.0
UNIT_COST = 15

STARTING_MARKUP = 1.5
MARKUP_STEP = 0.1
MIN_MARKUP = 1.0
MAX_MARKUP = 5.0

BASE_STOCKING_RATE = 5
BASE_DELIVERY_CAPACITY = 5
BASE_WAREHOUSE_CAPACITY = 100

MARKET_SIZE = 100
STARTING_LOYALTY = 50.0
MIN_LOYALTY = 0.0
MAX_LOYALTY = 100.0
BASE_LOYALTY_TARGET = 60.0
# Loyalty target lost for each 1.0 of markup above MIN_MARKUP.
MARKUP_LOYALTY_PENALTY = 20.0
# Each tick, loyalty moves this fraction of the way to its target.
LOYALTY_DRIFT_FRACTION = 0.1

COST_GROWTH = 1.15
BUY_AMOUNTS = [1, 5, 10]
STARTING_BUY_AMOUNT = 1

EFFECT_STOCKING = "stocking"
EFFECT_DELIVERY = "delivery"
EFFECT_LOYALTY = "loyalty"
EFFECT_CAPACITY = "capacity"
EFFECT_UNLOCK = "unlock"
# Each owned unit adds effect_amount percent to delivery capacity.
EFFECT_DELIVERY_BOOST = "delivery boost"

# Research names, used by the rows that require them.
LEAN_PROCUREMENT = "Lean Procurement"
ROUTE_OPTIMIZATION = "Route Optimization Software"
PICKUP_TRUCK_STUDY = "Pickup Truck Feasibility Study"
CONVEYOR_RESEARCH = "Conveyor Belt R&D"
IMPORT_LICENSES = "Import Licenses"
LABOR_CONSULTANCY = "Labor Relations Consultancy"
TUSHONKA_BUYOUT = "Buy Out Tushonka Canning Co."
BOXLY_ACQUISITION = "Acquire Rival: Boxly Logistics"
NO_REQUIREMENT = ""

# Each row: name, emoji, base cost, effect kind, effect amount,
# lifetime earnings needed to appear, whether it is a one-time buy, and
# the research it requires (NO_REQUIREMENT if none).
STARTING_ITEM_ROWS = [
    ["Procurement Agent", "🧑‍💼", 100.0, EFFECT_STOCKING, 5, 0.0, False,
     NO_REQUIREMENT],
    ["Fordov Delivery Van", "🚐", 50.0, EFFECT_DELIVERY, 1, 0.0, False,
     NO_REQUIREMENT],
    ["Short Form Marketing Campaign", "📱", 150.0, EFFECT_LOYALTY, 2, 200.0,
     False, NO_REQUIREMENT],
    ["Warehouse Expansion", "🏗️", 200.0, EFFECT_CAPACITY, 50, 500.0, False,
     NO_REQUIREMENT],
    ["Next Generation Corporate Organization", "🏢", 2000.0, EFFECT_UNLOCK, 1,
     1500.0, True, NO_REQUIREMENT],
    ["Upgraded Pickup Truck", "🛻", 300.0, EFFECT_DELIVERY, 4, 0.0, False,
     PICKUP_TRUCK_STUDY],
    ["Better Conveyor Belt", "⚙️", 600.0, EFFECT_DELIVERY_BOOST, 5, 0.0,
     False, CONVEYOR_RESEARCH],
]

STARTING_NEWS = [
    "Local warehouse opens; neighbors report increased forklift noise.",
    "Economists agree that boxes remain popular.",
    "Front line reported to be 'somewhere over there'.",
]
MAX_NEWS_ITEMS = 8

# Which page is showing, so the tick refreshes the right content.
PAGE_COMPANY = "company"
PAGE_BUSINESS = "business"
PAGE_ARTIFACTS = "artifacts"
PAGE_ORGANIZE = "organize"
PAGE_RESEARCH = "research"

CANNED_FOOD = "Canned Food"

# Each row: name, emoji, CheckBox name (must match a save_goods parameter),
# income bonus as a fraction, and the research it requires.
STARTING_GOODS_ROWS = [
    ["Household Goods", "🧺", "sell_household", 0.05, NO_REQUIREMENT],
    [CANNED_FOOD, "🥫", "sell_canned_food", 0.10, NO_REQUIREMENT],
    ["Electronics", "📺", "sell_electronics", 0.15, NO_REQUIREMENT],
    ["War Supplies", "💣", "sell_war_supplies", 1.00, NO_REQUIREMENT],
    ["Imported Luxuries", "💎", "sell_imported_luxuries", 0.25,
     IMPORT_LICENSES],
]

# Each row: name, emoji, CheckBox name (must match a save_policies parameter),
# stocking bonus, delivery bonus, income bonus, loyalty target change,
# strike risk per tick, whether it needs an unlock purchase, and the
# research it requires.
STARTING_POLICY_ROWS = [
    ["Unpaid Overtime", "⏰", "unpaid_overtime",
     0.5, 0.0, 0.0, -5.0, 0.03, False, NO_REQUIREMENT],
    ["Aggressive Upselling", "💬", "aggressive_upselling",
     0.0, 0.0, 0.15, -8.0, 0.0, False, NO_REQUIREMENT],
    ["Algorithmic Route Quotas", "🗺️", "route_quotas",
     0.0, 0.5, 0.0, -3.0, 0.05, True, NO_REQUIREMENT],
    ["Gig Worker Reclassification", "📋", "gig_reclassification",
     0.0, 0.0, 0.20, -6.0, 0.02, False, LABOR_CONSULTANCY],
]

CATEGORY_STAT = "stat"
CATEGORY_EQUIPMENT = "equipment"
CATEGORY_UNLOCK = "unlock"
CATEGORY_WORLD = "world"

# Each row: name, emoji, description, category, cost, stocking bonus,
# delivery bonus (both fractions), market size bonus, the goods type it
# boosts ("" for none) and that goods bonus, the prerequisite research
# (NO_REQUIREMENT if none), lifetime earnings needed to appear, and the
# World News headline posted when it is completed.
RESEARCH_ROWS = [
    [LEAN_PROCUREMENT, "📉",
     "Consultants remove three chairs and call it a methodology.",
     CATEGORY_STAT, 800.0, 0.10, 0.0, 0, "", 0.0, NO_REQUIREMENT, 500.0,
     "Procurement team goes lean; snacks reclassified as 'waste'."],
    [ROUTE_OPTIMIZATION, "🧭",
     "An app that tells drivers the road is shorter than they think.",
     CATEGORY_STAT, 1000.0, 0.0, 0.10, 0, "", 0.0, NO_REQUIREMENT, 800.0,
     "Drivers report the app keeps routing them through a lake."],
    [PICKUP_TRUCK_STUDY, "🛻",
     "A 40-page study concludes that bigger trucks hold more boxes.",
     CATEGORY_EQUIPMENT, 1500.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT,
     1500.0, "Study confirms trucks are 'like vans, but more so'."],
    [CONVEYOR_RESEARCH, "⚙️",
     "Engineers discover that belts can move boxes without lunch breaks.",
     CATEGORY_EQUIPMENT, 2500.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT,
     3000.0, "New conveyor belt prototype eats only one intern."],
    [IMPORT_LICENSES, "📜",
     "Paperwork so thick it is itself a taxable import.",
     CATEGORY_UNLOCK, 3000.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT, 3000.0,
     "Customs office approves licenses after a 'gift basket'."],
    [LABOR_CONSULTANCY, "🤝",
     "Experts in making 'no' sound like 'great question'.",
     CATEGORY_UNLOCK, 4000.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT, 5000.0,
     "Consultants rename workers 'independent box partners'."],
    [TUSHONKA_BUYOUT, "🥫",
     "Own the cans, own the soup, own the supply chain of soup.",
     CATEGORY_WORLD, 8000.0, 0.0, 0.0, 0, CANNED_FOOD, 0.15,
     IMPORT_LICENSES, 8000.0,
     "Tushonka Canning Co. acquired; stew prices 'stable for now'."],
    [BOXLY_ACQUISITION, "📦",
     "Buy the competition, then politely forget it ever existed.",
     CATEGORY_WORLD, 25000.0, 0.0, 0.0, 50, "", 0.0, NO_REQUIREMENT,
     15000.0, "Boxly Logistics absorbed; its customers 'welcomed home'."],
]

STRIKE_DURATION_TICKS = 5
# Stocking and delivery are multiplied by this during a strike.
STRIKE_PENALTY_MULTIPLIER = 0.5
STRIKE_NEWS = "Warehouse staff walk out! Management calls it 'unplanned rest'."

RARITY_COMMON = "common"
RARITY_RARE = "rare"
RARITY_LEGENDARY = "legendary"
# Each row: rarity and its weight. Weights add up to 100, so they read as %.
RARITY_WEIGHTS = [
    [RARITY_COMMON, 70],
    [RARITY_RARE, 25],
    [RARITY_LEGENDARY, 5],
]

# Each row: emoji, name, rarity, income bonus as a fraction, and description.
ARTIFACT_ROWS = [
    ["📎", "Ceremonial Paperclip", RARITY_COMMON, 0.01,
     "Held the Q3 merger together. Also some receipts."],
    ["🧾", "Infinite Receipt", RARITY_COMMON, 0.015,
     "Legal confirms that it is, technically, still printing."],
    ["☕", "Mug of Eternal Lukewarmness", RARITY_COMMON, 0.02,
     "Never hot, never cold. Much like the benefits package."],
    ["🪑", "Ergonomic Stool of Compliance", RARITY_COMMON, 0.02,
     "Designed so that nobody sits for longer than policy allows."],
    ["🏷️", "Clearance Sticker of Destiny", RARITY_COMMON, 0.025,
     "Everything must go. Including, eventually, you."],
    ["🖊️", "Pen Chained to the Desk", RARITY_COMMON, 0.03,
     "Our most trusted long-term asset retention program."],
    ["🗿", "Head of Human Resources", RARITY_RARE, 0.05,
     "Stone-faced and unmoved by your complaint. Exceeds expectations."],
    ["📠", "Fax Machine of the Ancients", RARITY_RARE, 0.06,
     "Still the only device approved by the accounting department."],
    ["🦆", "Senior Rubber Duck Consultant", RARITY_RARE, 0.07,
     "Bills by the hour to listen. Has never once disagreed."],
    ["📊", "Upward-Only Chart", RARITY_RARE, 0.08,
     "The axes are unlabeled, so the investors are thrilled."],
    ["🧿", "Eye of the Shift Supervisor", RARITY_RARE, 0.10,
     "Sees every bathroom break. Forgives none of them."],
    ["👑", "Crown of Synergy", RARITY_LEGENDARY, 0.20,
     "Whoever wears it may say 'circle back' without consequence."],
    ["🏆", "Employee of the Millennium", RARITY_LEGENDARY, 0.30,
     "Awarded to the only worker who never requested a day off."],
    ["💼", "Golden Parachute", RARITY_LEGENDARY, 0.40,
     "Opens automatically the moment anyone asks about the audit."],
]

# Each duplicate adds this fraction of the artifact's base bonus.
COPY_BONUS_FRACTION = 0.10

EXPEDITION_AMOUNTS = [1, 5, 10, 100]
EXPEDITION_BASE_COST = 500.0
EXPEDITION_COST_GROWTH = 1.01

GRID_ROWS = 2
GRID_COLUMNS = 6
GRID_SLOT_COUNT = GRID_ROWS * GRID_COLUMNS
EMPTY_SLOT = "(empty)"
# Artifact.slot holds this when the artifact isn't in the grid.
NOT_PLACED = -1
# What the linear search returns when it finds nothing.
NOT_FOUND = -1

PAGE_CASINO = "casino"
DIFFICULTY_EASY = "easy"
DIFFICULTY_HARD = "hard"
DIFFICULTY_OPTIONS = [DIFFICULTY_EASY, DIFFICULTY_HARD]
DIFFICULTY_MULTIPLIERS = {DIFFICULTY_EASY: 1.0, DIFFICULTY_HARD: 2.0}

# A bet can be at most this fraction of the player's current money.
CASINO_MAX_BET_FRACTION = 0.8
CHARACTERS_PER_WORD = 5
INVALID_BET_MESSAGE = "The casino rejects that bet. Check the limit."

# Each row: lowest value that earns the tier, and its payout multiplier.
# Rows must go from lowest to highest.
ACCURACY_TIERS = [[0.0, 0.0], [0.8, 0.5], [0.95, 1.0], [1.0, 1.5]]
# The values here are words per minute.
SPEED_TIERS = [[0.0, 0.5], [20.0, 1.0], [40.0, 1.5], [70.0, 2.0]]

EASY_PROMPTS = [
    "the box is on the big truck and the van is out",
    "we move the goods to the store and then go back",
    "please pack each order and put it near the door",
    "all of our workers are happy and that is a rule",
]
# Hard prompts also go through swap_hard_characters before they are shown.
HARD_PROMPTS = [
    "Our Q4 Outlook is 100% positive and 0% audited.",
    "Overtime is Optional, and Optional means 60 hours.",
    "Our Office has an Open door policy and 0 doors.",
    "Profits rose 200% Once we stopped buying chairs and desks.",
]


# ---------------------------------------------------------------------------
# Theme: colors and layout for every page
# ---------------------------------------------------------------------------

# Each row: button text, route, and the page it shows.
NAV_ROWS = [
    ["Company", "company_page", PAGE_COMPANY],
    ["Business", "business_page", PAGE_BUSINESS],
    ["Artifacts", "artifacts_page", PAGE_ARTIFACTS],
    ["Casino", "casino_page", PAGE_CASINO],
]

# ADVANCED: This is CSS, the language browsers use to style a page. Each
# rule names a CSS class (".card") and sets its colors, spacing, and layout.
# Components get those class names through classes="..." in the page
# helpers. "display: grid" and "display: flex" line things up in rows and
# columns; the @media rule stacks the columns on narrow (phone) screens.
THEME_CSS = """
:root {
  --ink: #1f2933;
  --muted: #5f6b7a;
  --paper: #eef0f2;
  --card: #ffffff;
  --line: #d8dde3;
  --slate: #1f2a37;
  --slate-light: #2d3b4d;
  --amber: #f5b301;
  --amber-dark: #c98f00;
  --warn: #c0392b;
}
html, body {
  background: var(--paper);
}
body .drafter-frame-- {
  max-width: none;
  margin: 0;
}
body .drafter-body-- {
  font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 15px;
  line-height: 1.4;
  color: var(--ink);
  padding: 0 0 24px 0;
}
body .drafter-body-- h1 {
  font-size: 1.2rem !important;
  letter-spacing: 0 !important;
  margin: 0;
}
body .drafter-body-- h2 {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  margin: 0;
}
body .drafter-body-- button {
  font: inherit;
  font-size: 0.9rem;
  padding: 5px 11px;
  margin: 2px;
  border-radius: 6px;
  border: 1px solid var(--slate);
  background: var(--slate);
  color: #ffffff;
  box-shadow: none;
}
body .drafter-body-- button:hover {
  background: var(--slate-light);
}
body .drafter-body-- input,
body .drafter-body-- select,
body .drafter-body-- textarea {
  font: inherit;
  padding: 5px 8px;
  margin: 2px 0;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #ffffff;
  color: var(--ink);
}
body .drafter-body-- input[type=checkbox] {
  transform: none;
  width: 18px;
  height: 18px;
  margin: 0;
  accent-color: var(--amber-dark);
}
body .drafter-body-- ul {
  margin: 0;
  padding-left: 18px;
}
body .drafter-body-- li {
  margin: 3px 0;
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--slate);
  color: #ffffff;
  padding: 8px 16px 10px 16px;
  border-bottom: 4px solid var(--amber);
}
.topbar-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  max-width: 1100px;
  margin: 0 auto;
}
.topbar-row h1 {
  color: #ffffff;
  margin-right: auto;
}
body .drafter-body-- .nav button {
  background: transparent;
  border-color: transparent;
  color: #c9d2dc;
}
body .drafter-body-- .nav button:hover {
  background: var(--slate-light);
}
body .drafter-body-- .nav button.current {
  background: var(--amber);
  border-color: var(--amber);
  color: var(--slate);
  font-weight: 600;
}
#live_numbers {
  max-width: 1100px;
  margin: 0 auto;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.chip {
  display: flex;
  flex-direction: column;
  min-width: 88px;
  padding: 3px 9px;
  border-radius: 6px;
  background: var(--slate-light);
}
.chip-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #a9b4c1;
}
.chip-value {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.chip.money {
  background: var(--amber);
  color: var(--slate);
}
.chip.money .chip-label {
  color: var(--slate);
}
.chip.money .chip-value {
  font-size: 1.15rem;
}
.chip.warn {
  background: var(--warn);
}
.chip.warn .chip-label {
  color: #ffd7d2;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}
.tag {
  font-size: 0.8rem;
  padding: 1px 8px;
  border-radius: 999px;
  border: 1px solid var(--amber);
  color: var(--amber);
}
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px 16px 0 16px;
}
.dashboard,
.two-col {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  gap: 16px;
  align-items: start;
}
.two-col {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 16px;
}
.card.narrow {
  max-width: 640px;
}
.card-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}
.muted {
  color: var(--muted);
  font-size: 0.85rem;
}
.big-number {
  font-size: 1.5rem;
  font-weight: 600;
}
.button-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}
body .drafter-body-- .segmented button {
  background: #ffffff;
  border-color: var(--line);
  color: var(--ink);
  min-width: 44px;
}
body .drafter-body-- .segmented button.current {
  background: var(--slate);
  border-color: var(--slate);
  color: #ffffff;
}
.buy-row {
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  border-top: 1px solid var(--line);
}
.emoji {
  font-size: 1.4rem;
  text-align: center;
}
.item-name {
  font-weight: 600;
}
body .drafter-body-- .buy-row button,
body .drafter-body-- .expedition button {
  background: var(--amber);
  border-color: var(--amber-dark);
  color: var(--slate);
  font-weight: 600;
  min-width: 150px;
}
body .drafter-body-- .buy-row button:hover,
body .drafter-body-- .expedition button:hover {
  background: var(--amber-dark);
}
body .drafter-body-- .check-row input[type=checkbox] {
  flex-shrink: 0;
}
.check-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  border-top: 1px solid var(--line);
}
body .drafter-body-- .artifact-grid table {
  width: 100%;
  table-layout: fixed;
  margin: 4px 0 0 0;
  box-shadow: none;
}
body .drafter-body-- .artifact-grid td {
  padding: 8px 4px;
  text-align: center;
  font-size: 0.8rem;
  border: 1px solid var(--line);
}
.slot-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 8px;
}
body .drafter-body-- .slot-grid select {
  width: 100%;
}
.form-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: 6px 0;
}
.prompt {
  font-family: ui-monospace, Consolas, monospace;
  background: var(--paper);
  border-left: 4px solid var(--amber);
  padding: 8px 10px;
  margin: 6px 0;
}
body .drafter-body-- textarea {
  width: 100%;
  min-height: 90px;
  box-sizing: border-box;
}
.result:empty {
  display: none;
}
.result {
  font-weight: 600;
  margin-bottom: 8px;
}
.card.start {
  max-width: 460px;
  margin: 12vh auto 0 auto;
  text-align: center;
}
body .drafter-body-- .card.start h1 {
  font-size: 1.7rem !important;
  margin-bottom: 6px;
}
@media (max-width: 760px) {
  .dashboard,
  .two-col {
    grid-template-columns: minmax(0, 1fr);
  }
  .slot-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .chip {
    min-width: 0;
    padding: 2px 7px;
  }
  .chip-label {
    font-size: 0.6rem;
  }
  .chip-value,
  .chip.money .chip-value {
    font-size: 0.85rem;
  }
  .tag {
    font-size: 0.72rem;
  }
  body .drafter-body-- .buy-row button {
    min-width: 0;
    font-size: 0.82rem;
  }
  .topbar {
    padding: 6px 10px 8px 10px;
  }
  .page {
    padding: 12px 10px 0 10px;
  }
}
"""
add_website_css(THEME_CSS)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class BuyItem:
    """One thing the player can purchase on the company page.

    Attributes:
        name: The item's display name.
        emoji: A placeholder picture for the item.
        base_cost: The price of the first unit.
        effect_kind: Which stat it improves (an EFFECT_ constant).
        effect_amount: How much each owned unit improves that stat.
        unlock_at_earned: Lifetime earnings needed for it to appear.
        is_one_time: Whether it can only be bought once.
        required_research: Research needed for it to appear ("" = none).
        owned: How many units the player has bought.
    """
    name: str
    emoji: str
    base_cost: float
    effect_kind: str
    effect_amount: int
    unlock_at_earned: float
    is_one_time: bool
    required_research: str
    owned: int


@dataclass
class GoodsType:
    """One kind of goods the company can choose to sell.

    Attributes:
        name: The goods type's display name.
        emoji: A placeholder picture for the goods type.
        input_name: The name of its CheckBox on the Business page.
        income_bonus: The income bonus as a fraction while selling it.
        required_research: Research needed for it to appear ("" = none).
        is_selling: Whether the company currently sells it.
    """
    name: str
    emoji: str
    input_name: str
    income_bonus: float
    required_research: str
    is_selling: bool


@dataclass
class Policy:
    """One corporate policy with upsides and downsides.

    Attributes:
        name: The policy's display name.
        emoji: A placeholder picture for the policy.
        input_name: The name of its CheckBox on the Business page.
        stocking_bonus: Extra stocking rate as a fraction.
        delivery_bonus: Extra delivery capacity as a fraction.
        income_bonus: Extra income as a fraction.
        loyalty_change: Amount added to the loyalty target.
        strike_risk: Added chance of a strike each tick, from 0 to 1.
        needs_unlock: Whether an unlock purchase is required first.
        required_research: Research needed before it can be used ("" =
            none).
        is_active: Whether the policy is currently in force.
    """
    name: str
    emoji: str
    input_name: str
    stocking_bonus: float
    delivery_bonus: float
    income_bonus: float
    loyalty_change: float
    strike_risk: float
    needs_unlock: bool
    required_research: str
    is_active: bool


@dataclass
class Research:
    """One research project the player can pay for once.

    Attributes:
        name: The research's display name.
        emoji: A placeholder picture for the research.
        description: The funny corporate flavor text.
        category: One of the CATEGORY_ constants.
        cost: The money it costs to complete.
        stocking_bonus: Extra stocking rate as a fraction once done.
        delivery_bonus: Extra delivery capacity as a fraction once done.
        market_bonus: Customers added to the market size once done.
        goods_name: The goods type whose bonus it raises ("" for none).
        goods_bonus: The income bonus it adds to that goods type.
        prerequisite: Research that must be done first ("" for none).
        unlock_at_earned: Lifetime earnings needed for it to appear.
        headline: The World News headline posted when it is done.
        is_done: Whether the player has completed it.
    """
    name: str
    emoji: str
    description: str
    category: str
    cost: float
    stocking_bonus: float
    delivery_bonus: float
    market_bonus: int
    goods_name: str
    goods_bonus: float
    prerequisite: str
    unlock_at_earned: float
    headline: str
    is_done: bool


@dataclass
class Artifact:
    """An artifact the player owns.

    Attributes:
        emoji: The placeholder picture.
        name: The artifact's name.
        rarity: One of the RARITY_ constants.
        income_bonus: The income bonus of one copy, as a fraction.
        description: The funny corporate flavor text.
        copies: How many copies the player has found.
        slot: The grid slot it sits in (0-11), or NOT_PLACED.
    """
    emoji: str
    name: str
    rarity: str
    income_bonus: float
    description: str
    copies: int
    slot: int


@dataclass
class TypingRound:
    """One typing test, from when it starts until it is submitted.

    Attributes:
        prompt: The text to type; empty when no round is running.
        difficulty: One of the DIFFICULTY_ constants.
        bet: The money already paid to enter this round.
        start_tick: The value of State.tick_count when the round began.
    """
    prompt: str
    difficulty: str
    bet: int
    start_tick: int


@dataclass
class State:
    """Holds everything the website remembers between pages.

    Attributes:
        company_name: The name the player chose.
        money: Spendable money.
        total_earned: All income ever earned; used to unlock items.
        goods_in_stock: Units currently in the warehouse.
        loyalty: Customer loyalty from 0 to 100; sets demand.
        markup: Sale price multiplier applied to the unit cost.
        buy_amount: How many units one Buy click purchases.
        buy_items: Every purchasable item and how many are owned.
        goods_stocked_last_tick: Units bought in the latest tick.
        goods_sold_last_tick: Units sold in the latest tick.
        income_last_tick: Money earned in the latest tick.
        news_feed: Recent World News headlines, newest first.
        goods_types: Every goods type and whether it is being sold.
        policies: Every corporate policy and whether it is active.
        sells_war_supplies: Whether War Supplies are being sold.
        strike_ticks_left: Ticks until the current strike ends (0 = none).
        current_page: Which PAGE_ constant the player is viewing.
        owned_artifacts: Every artifact found so far.
        expeditions_bought: Expeditions ever bought; raises their price.
        last_expedition_finds: One line per artifact from the last batch.
        controls_signature: Summary of the buttons the last tick drew.
        tick_count: Ticks since the game began; times the typing test.
        typing_round: The casino typing test in progress, if any.
        last_casino_result: The message from the latest casino action.
        research: Every research project and whether it is done.
    """
    company_name: str
    money: float
    total_earned: float
    goods_in_stock: int
    loyalty: float
    markup: float
    buy_amount: int
    buy_items: list[BuyItem]
    goods_stocked_last_tick: int
    goods_sold_last_tick: int
    income_last_tick: float
    news_feed: list[str]
    goods_types: list[GoodsType]
    policies: list[Policy]
    sells_war_supplies: bool
    strike_ticks_left: int
    current_page: str
    owned_artifacts: list[Artifact]
    expeditions_bought: int
    last_expedition_finds: list[str]
    controls_signature: str
    tick_count: int
    typing_round: TypingRound
    last_casino_result: str
    research: list[Research]


def make_no_typing_round() -> TypingRound:
    """Build the placeholder that means no typing test is running.

    Returns:
        A TypingRound with an empty prompt.
    """
    return TypingRound("", DIFFICULTY_EASY, 0, 0)


def make_starting_items() -> list[BuyItem]:
    """Build fresh BuyItems so the global rows are never modified.

    Returns:
        A new list with one unowned BuyItem per row of STARTING_ITEM_ROWS.
    """
    items = []
    for row in STARTING_ITEM_ROWS:
        items.append(BuyItem(row[0], row[1], row[2], row[3], row[4], row[5],
                             row[6], row[7], 0))
    return items


def make_starting_goods() -> list[GoodsType]:
    """Build fresh GoodsTypes so the global rows are never modified.

    Returns:
        A new list with one unselected GoodsType per goods row.
    """
    goods_types = []
    for row in STARTING_GOODS_ROWS:
        goods_types.append(GoodsType(row[0], row[1], row[2], row[3], row[4],
                                     False))
    return goods_types


def make_starting_policies() -> list[Policy]:
    """Build fresh Policies so the global rows are never modified.

    Returns:
        A new list with one inactive Policy per policy row.
    """
    policies = []
    for row in STARTING_POLICY_ROWS:
        policies.append(Policy(row[0], row[1], row[2], row[3], row[4], row[5],
                               row[6], row[7], row[8], row[9], False))
    return policies


def make_starting_research() -> list[Research]:
    """Build fresh Research so the global rows are never modified.

    Returns:
        A new list with one unfinished Research per row of RESEARCH_ROWS.
    """
    research = []
    for row in RESEARCH_ROWS:
        research.append(Research(row[0], row[1], row[2], row[3], row[4],
                                 row[5], row[6], row[7], row[8], row[9],
                                 row[10], row[11], row[12], False))
    return research


def make_new_state() -> State:
    """Build the State that a brand new game starts with.

    Returns:
        A new State holding the starting values.
    """
    return State(
        company_name=DEFAULT_COMPANY_NAME,
        money=STARTING_MONEY,
        total_earned=0.0,
        goods_in_stock=0,
        loyalty=STARTING_LOYALTY,
        markup=STARTING_MARKUP,
        buy_amount=STARTING_BUY_AMOUNT,
        buy_items=make_starting_items(),
        goods_stocked_last_tick=0,
        goods_sold_last_tick=0,
        income_last_tick=0.0,
        news_feed=STARTING_NEWS[:],
        goods_types=make_starting_goods(),
        policies=make_starting_policies(),
        sells_war_supplies=False,
        strike_ticks_left=0,
        current_page=PAGE_COMPANY,
        owned_artifacts=[],
        expeditions_bought=0,
        last_expedition_finds=[],
        controls_signature="",
        tick_count=0,
        typing_round=make_no_typing_round(),
        last_casino_result="",
        research=make_starting_research(),
    )


# ---------------------------------------------------------------------------
# Test helpers: sample data shared by the tests below
# ---------------------------------------------------------------------------

def make_test_item(effect_kind: str, effect_amount: int,
                   owned: int) -> BuyItem:
    """Build a simple 100-cost item for the helper tests.

    Args:
        effect_kind: Which stat the item improves.
        effect_amount: How much each owned unit improves that stat.
        owned: How many units are already owned.

    Returns:
        A repeatable BuyItem that unlocks at 50 earned.
    """
    return BuyItem("Test", "T", 100.0, effect_kind, effect_amount, 50.0,
                   False, NO_REQUIREMENT, owned)


def make_one_time_item(owned: int) -> BuyItem:
    """Build a simple one-time item for the helper tests.

    Args:
        owned: How many units are already owned (0 or 1).

    Returns:
        A one-time BuyItem that is always unlocked.
    """
    return BuyItem("Once", "O", 100.0, EFFECT_UNLOCK, 1, 0.0, True,
                   NO_REQUIREMENT, owned)


def make_test_goods(income_bonus: float, is_selling: bool) -> GoodsType:
    """Build a simple goods type for the helper tests.

    Args:
        income_bonus: The income bonus as a fraction.
        is_selling: Whether it is being sold.

    Returns:
        A GoodsType with those values.
    """
    return GoodsType("Test", "T", "sell_test", income_bonus, NO_REQUIREMENT,
                     is_selling)


def make_test_policy(is_active: bool) -> Policy:
    """Build a policy with one known value for every effect.

    Args:
        is_active: Whether the policy is in force.

    Returns:
        A Policy that does not need an unlock.
    """
    return Policy("Test", "T", "test_policy", 0.5, 0.25, 0.1, -5.0, 0.03,
                  False, NO_REQUIREMENT, is_active)


def make_locked_policy() -> Policy:
    """Build an inactive policy that needs an unlock purchase.

    Returns:
        A locked Policy with no effects.
    """
    return Policy("Locked", "L", "locked_policy", 0.0, 0.0, 0.0, 0.0, 0.0,
                  True, NO_REQUIREMENT, False)


def make_striking_state(ticks_left: int) -> State:
    """Build a new-game State in the middle of a strike.

    Args:
        ticks_left: How many strike ticks remain.

    Returns:
        A new-game State with that strike.
    """
    state = make_new_state()
    state.strike_ticks_left = ticks_left
    return state


def make_certain_strike_state() -> State:
    """Build a State whose only policy makes a strike certain.

    Returns:
        A new-game State whose next strike roll must succeed.
    """
    state = make_new_state()
    state.policies = [Policy("Riot", "R", "riot", 0.0, 0.0, 0.0, 0.0, 1.0,
                             False, NO_REQUIREMENT, True)]
    return state


def make_test_artifact(name: str, income_bonus: float, copies: int,
                       slot: int) -> Artifact:
    """Build a simple common Artifact for tests.

    Args:
        name: The artifact's name.
        income_bonus: The income bonus of one copy.
        copies: How many copies are owned.
        slot: The grid slot, or NOT_PLACED.

    Returns:
        A new common Artifact with the emoji "A".
    """
    return Artifact("A", name, RARITY_COMMON, income_bonus, "Test", copies,
                    slot)


def make_typing_state() -> State:
    """Build a Casino page State three ticks into a typing round.

    Returns:
        A State with Ŧ400 left after betting 100 on the easy prompt "hello".
    """
    state = make_new_state()
    state.current_page = PAGE_CASINO
    state.money = 400.0
    state.tick_count = 3
    state.typing_round = TypingRound("hello", DIFFICULTY_EASY, 100, 0)
    return state


def make_rich_state() -> State:
    """Build a new-game State that can afford anything.

    Returns:
        A new-game State with a huge amount of money.
    """
    state = make_new_state()
    state.money = 1000000000.0
    return state


def make_artifact_state() -> State:
    """Build a State owning two artifacts, with only Alpha placed.

    Returns:
        A new-game State where Alpha (+10%) is in slot 0 and Beta (+50%)
        is not placed.
    """
    state = make_new_state()
    state.owned_artifacts = [make_test_artifact("Alpha", 0.1, 1, 0),
                             make_test_artifact("Beta", 0.5, 1, NOT_PLACED)]
    return state


def make_state_with_income_bonuses() -> State:
    """Build a State selling Electronics with Aggressive Upselling active.

    Returns:
        A new-game State with +15% from goods and +15% from policy.
    """
    state = make_new_state()
    state.goods_types[2].is_selling = True
    state.policies[1].is_active = True
    return state


def state_after_strikes(state: State) -> State:
    """Run the strike step and hand back the State so tests can check it.

    Args:
        state: The game state to update.

    Returns:
        The same State after run_strikes.
    """
    run_strikes(state)
    return state


def expected_after_named_start() -> State:
    """Build the State expected after starting a company named Boxes.

    Returns:
        A new-game State with the company name set.
    """
    state = make_new_state()
    state.company_name = "Boxes"
    return state


def make_expected_company_page(state: State) -> Page:
    """Build the company page expected for a given State.

    Args:
        state: The State the page should show.

    Returns:
        The expected company page.
    """
    return Page(state, build_company_content(state))


def make_business_state() -> State:
    """Build a new-game State that is viewing the Business page.

    Returns:
        A new-game State whose current page is the Business page.
    """
    state = make_new_state()
    state.current_page = PAGE_BUSINESS
    return state


def make_expected_business_page(state: State) -> Page:
    """Build the Business page expected for a given State.

    Args:
        state: The State the page should show.

    Returns:
        The expected Business page.
    """
    return Page(state, build_business_content(state))


def expected_after_selling_war_supplies() -> State:
    """Build the State expected after choosing only War Supplies.

    Returns:
        A Business page State selling only War Supplies, with the flag set.
    """
    state = make_business_state()
    state.goods_types[3].is_selling = True
    state.sells_war_supplies = True
    return state


def expected_after_overtime() -> State:
    """Build the State expected after choosing only Unpaid Overtime.

    Returns:
        A Business page State with Unpaid Overtime active.
    """
    state = make_business_state()
    state.policies[0].is_active = True
    return state


def make_unlocked_state() -> State:
    """Build a new-game State that owns the policy unlock item.

    Returns:
        A new-game State with Next Generation Corporate Organization.
    """
    state = make_new_state()
    state.buy_items[4].owned = 1
    return state


def expected_after_quotas() -> State:
    """Build the State expected after enabling the unlocked policy.

    Returns:
        A Business page State with Algorithmic Route Quotas active.
    """
    state = make_unlocked_state()
    state.current_page = PAGE_BUSINESS
    state.policies[2].is_active = True
    return state


def make_artifacts_view_state() -> State:
    """Build the artifact test State while it views the Artifacts page.

    Returns:
        The artifact test State with the Artifacts page showing.
    """
    state = make_artifact_state()
    state.current_page = PAGE_ARTIFACTS
    return state


def make_expected_artifacts_page(state: State) -> Page:
    """Build the Artifacts page expected for a given State.

    Args:
        state: The State the page should show.

    Returns:
        The expected Artifacts page.
    """
    return Page(state, build_artifacts_content(state))


def make_organize_view_state() -> State:
    """Build the artifact test State while it views the Organize page.

    Returns:
        The artifact test State with the Organize page showing.
    """
    state = make_artifact_state()
    state.current_page = PAGE_ORGANIZE
    return state


def expected_after_moving_beta() -> State:
    """Build the State expected after swapping Alpha out for Beta.

    Returns:
        An Artifacts page State with only Beta placed, in slot 12.
    """
    state = make_artifacts_view_state()
    state.owned_artifacts[0].slot = NOT_PLACED
    state.owned_artifacts[1].slot = 11
    return state


def make_expected_casino_page(state: State) -> Page:
    """Build the Casino page expected for a given State.

    Args:
        state: The State the page should show.

    Returns:
        The expected Casino page.
    """
    return Page(state, build_casino_content(state))


def make_casino_view_state(message: str) -> State:
    """Build a new-game State viewing the Casino page.

    Args:
        message: The casino result message to show.

    Returns:
        A new-game State with the Casino page showing and that message.
    """
    state = make_new_state()
    state.current_page = PAGE_CASINO
    state.last_casino_result = message
    return state


def expected_after_typing(payout: float, message: str) -> State:
    """Build the State expected after finishing the test typing round.

    Args:
        payout: The money the round should pay.
        message: The result message that should be shown.

    Returns:
        The typing State with the payout added and the round finished.
    """
    state = make_typing_state()
    state.money = state.money + payout
    state.typing_round = make_no_typing_round()
    state.last_casino_result = message
    return state


def expected_with_buy_amount(amount: int) -> State:
    """Build a new-game State that has the given buy amount.

    Args:
        amount: The buy amount to set.

    Returns:
        A new-game State with that buy amount.
    """
    state = make_new_state()
    state.buy_amount = amount
    return state


def expected_after_buying_van() -> State:
    """Build the State expected after buying one Delivery Van.

    Returns:
        A new-game State with one van bought and paid for.
    """
    state = make_new_state()
    state.money = 450.0
    state.buy_items[1].owned = 1
    return state


def make_broke_state() -> State:
    """Build a new-game State that cannot afford anything.

    Returns:
        A new-game State with almost no money.
    """
    state = make_new_state()
    state.money = 1.0
    return state


def make_nearly_stranded_state() -> State:
    """Build a State where buying a van would leave too little to stock.

    Returns:
        A new-game State with an empty warehouse and 60 money.
    """
    state = make_new_state()
    state.money = 60.0
    return state


def expected_with_markup(markup: float) -> State:
    """Build a new-game State that has the given markup.

    Args:
        markup: The markup to set.

    Returns:
        A new-game State with that markup.
    """
    state = make_new_state()
    state.markup = markup
    return state


def expected_after_first_tick() -> State:
    """Build the State expected after one tick of a brand new game.

    Returns:
        A new-game State updated by one tick's stocking and selling.
    """
    state = make_new_state()
    state.money = 537.5
    state.total_earned = 112.5
    state.goods_stocked_last_tick = 5
    state.goods_sold_last_tick = 5
    state.income_last_tick = 112.5
    state.tick_count = 1
    state.controls_signature = controls_signature(state)
    return state


def make_settled_state() -> State:
    """Build a new game whose buttons already match the next tick's.

    Returns:
        A new-game State holding the signature its first tick will produce.
    """
    state = make_new_state()
    state.controls_signature = expected_after_first_tick().controls_signature
    return state


def expected_business_tick() -> State:
    """Build the State expected after one tick on the Business page.

    Returns:
        The first-tick State, with the Business page showing.
    """
    state = expected_after_first_tick()
    state.current_page = PAGE_BUSINESS
    return state


def make_veteran_state() -> State:
    """Build a new-game State that has earned enough to unlock every item.

    Returns:
        A new-game State with huge lifetime earnings.
    """
    state = make_new_state()
    state.total_earned = 1000000000.0
    return state


def make_test_research(name: str, prerequisite: str,
                       is_done: bool) -> Research:
    """Build a research project with one known value for every effect.

    Args:
        name: The research's name.
        prerequisite: The research needed first ("" for none).
        is_done: Whether it is already completed.

    Returns:
        A 100-cost Research that appears at 100 earned and boosts "Test".
    """
    return Research(name, "R", "Testing.", CATEGORY_STAT, 100.0, 0.1, 0.2,
                    10, "Test", 0.5, prerequisite, 100.0, "Test done.",
                    is_done)


def make_research_state() -> State:
    """Build a State viewing the Research page with 2000 money, 1000 earned.

    Returns:
        A State that can afford the first research (Lean Procurement).
    """
    state = make_new_state()
    state.money = 2000.0
    state.total_earned = 1000.0
    state.goods_in_stock = 10
    state.current_page = PAGE_RESEARCH
    return state


def make_poor_research_state() -> State:
    """Build the research State with too little money for any research.

    Returns:
        The research State holding only 100 money.
    """
    state = make_research_state()
    state.money = 100.0
    return state


def make_expected_research_page(state: State) -> Page:
    """Build the Research page expected for a given State.

    Args:
        state: The State the page should show.

    Returns:
        The expected Research page.
    """
    return Page(state, build_research_content(state))


def expected_after_lean_procurement() -> State:
    """Build the State expected after buying Lean Procurement.

    Returns:
        The research State with Lean Procurement done and paid for.
    """
    state = make_research_state()
    state.money = 2000.0 - RESEARCH_ROWS[0][4]
    state.research[0].is_done = True
    state.news_feed = add_news(state.news_feed, RESEARCH_ROWS[0][12])
    return state


def make_finished_research_state(research_index: int) -> State:
    """Build a new-game State with one research already completed.

    Args:
        research_index: The position of the research in state.research.

    Returns:
        A new-game State where that research is done.
    """
    state = make_new_state()
    state.research[research_index].is_done = True
    return state


def expected_after_luxuries() -> State:
    """Build the State expected after selling the unlocked luxuries.

    Returns:
        A Business page State with Import Licenses done, selling luxuries.
    """
    state = make_finished_research_state(4)
    state.current_page = PAGE_BUSINESS
    state.goods_types[4].is_selling = True
    return state


def expected_after_gig_policy() -> State:
    """Build the State expected after enabling the researched policy.

    Returns:
        A Business page State with Gig Worker Reclassification active.
    """
    state = make_finished_research_state(5)
    state.current_page = PAGE_BUSINESS
    state.policies[3].is_active = True
    return state


# ---------------------------------------------------------------------------
# Business: goods and policy helper functions
# ---------------------------------------------------------------------------

def total_goods_bonus(goods_types: list[GoodsType]) -> float:
    """Add up the income bonus of every goods type being sold.

    Args:
        goods_types: The goods types to add up.

    Returns:
        The combined income bonus as a fraction.
    """
    total = 0.0
    for goods in goods_types:
        if goods.is_selling:
            total = total + goods.income_bonus
    return total


assert_equal(total_goods_bonus([]), 0.0)
assert_equal(total_goods_bonus([make_test_goods(0.25, True),
                                make_test_goods(0.5, False),
                                make_test_goods(1.0, True)]), 1.25)


def total_policy_stocking_bonus(policies: list[Policy]) -> float:
    """Add up the stocking bonus of every active policy.

    Args:
        policies: The policies to add up.

    Returns:
        The combined stocking bonus as a fraction.
    """
    total = 0.0
    for policy in policies:
        if policy.is_active:
            total = total + policy.stocking_bonus
    return total


assert_equal(total_policy_stocking_bonus(
    [make_test_policy(True), make_test_policy(False)]), 0.5)


def total_policy_delivery_bonus(policies: list[Policy]) -> float:
    """Add up the delivery bonus of every active policy.

    Args:
        policies: The policies to add up.

    Returns:
        The combined delivery bonus as a fraction.
    """
    total = 0.0
    for policy in policies:
        if policy.is_active:
            total = total + policy.delivery_bonus
    return total


assert_equal(total_policy_delivery_bonus(
    [make_test_policy(True), make_test_policy(False)]), 0.25)


def total_policy_income_bonus(policies: list[Policy]) -> float:
    """Add up the income bonus of every active policy.

    Args:
        policies: The policies to add up.

    Returns:
        The combined income bonus as a fraction.
    """
    total = 0.0
    for policy in policies:
        if policy.is_active:
            total = total + policy.income_bonus
    return total


assert_equal(total_policy_income_bonus(
    [make_test_policy(True), make_test_policy(False)]), 0.1)


def total_policy_loyalty_change(policies: list[Policy]) -> float:
    """Add up the loyalty target change of every active policy.

    Args:
        policies: The policies to add up.

    Returns:
        The combined change to the loyalty target.
    """
    total = 0.0
    for policy in policies:
        if policy.is_active:
            total = total + policy.loyalty_change
    return total


assert_equal(total_policy_loyalty_change(
    [make_test_policy(True), make_test_policy(False)]), -5.0)


def total_strike_risk(policies: list[Policy]) -> float:
    """Add up the strike risk of every active policy.

    Args:
        policies: The policies to add up.

    Returns:
        The chance of a strike each tick, from 0 to 1.
    """
    total = 0.0
    for policy in policies:
        if policy.is_active:
            total = total + policy.strike_risk
    return total


assert_equal(total_strike_risk(
    [make_test_policy(True), make_test_policy(False)]), 0.03)


def set_goods_choices(goods_types: list[GoodsType], choices: list[bool],
                      research: list[Research]) -> None:
    """Record which goods types the player chose to sell.

    Goods whose required research isn't done stay unsold.

    Args:
        goods_types: The goods types to update.
        choices: One True or False per goods type, in the same order.
        research: Every research project.
    """
    for index, goods in enumerate(goods_types):
        goods.is_selling = (choices[index]
                            and is_requirement_met(goods.required_research,
                                                   research))


def strike_multiplier(strike_ticks_left: int) -> float:
    """Find the multiplier a strike applies to stocking and delivery.

    Args:
        strike_ticks_left: Ticks until the current strike ends.

    Returns:
        The strike penalty during a strike, otherwise 1.0.
    """
    if strike_ticks_left > 0:
        return STRIKE_PENALTY_MULTIPLIER
    return 1.0


assert_equal(strike_multiplier(0), 1.0)
assert_equal(strike_multiplier(3), STRIKE_PENALTY_MULTIPLIER)


def roll_strike(strike_risk: float) -> bool:
    """Randomly decide whether a strike begins this tick.

    Args:
        strike_risk: The chance of a strike, from 0 to 1.

    Returns:
        True if a strike begins.
    """
    # ADVANCED: random.random() gives a decimal from 0 up to (but not
    # including) 1, so it lands below strike_risk with that probability.
    return random.random() < strike_risk


# Risks of exactly 0 and 1 give the same answer on every roll.
assert_equal(roll_strike(0.0), False)
assert_equal(roll_strike(1.0), True)


def add_news(news_feed: list[str], headline: str) -> list[str]:
    """Put a headline first, dropping the oldest if the feed is full.

    Args:
        news_feed: The current headlines, newest first.
        headline: The new headline.

    Returns:
        A new list of at most MAX_NEWS_ITEMS headlines.
    """
    return [headline] + news_feed[:MAX_NEWS_ITEMS - 1]


assert_equal(add_news(["old"], "new"), ["new", "old"])
assert_equal(len(add_news(["x"] * MAX_NEWS_ITEMS, "new")), MAX_NEWS_ITEMS)


# ---------------------------------------------------------------------------
# Research: one-time projects that add bonuses and unlock new options
# ---------------------------------------------------------------------------

def is_research_done(research: list[Research], name: str) -> bool:
    """Search the research list for a project and check if it is done.

    Args:
        research: Every research project.
        name: The name of the project to look for.

    Returns:
        True if a project with that name exists and is completed.
    """
    for project in research:
        if project.name == name:
            return project.is_done
    return False


assert_equal(is_research_done([make_test_research("A", "", True)], "A"),
             True)
assert_equal(is_research_done([make_test_research("A", "", False)], "A"),
             False)
assert_equal(is_research_done([make_test_research("A", "", True)], "B"),
             False)


def is_requirement_met(required_research: str,
                       research: list[Research]) -> bool:
    """Check whether a required research (if any) has been completed.

    Args:
        required_research: The research needed, or NO_REQUIREMENT.
        research: Every research project.

    Returns:
        True if nothing is required or the required research is done.
    """
    if required_research == NO_REQUIREMENT:
        return True
    return is_research_done(research, required_research)


assert_equal(is_requirement_met(NO_REQUIREMENT, []), True)
assert_equal(is_requirement_met("A", [make_test_research("A", "", True)]),
             True)
assert_equal(is_requirement_met("A", [make_test_research("A", "", False)]),
             False)


def is_research_available(project: Research, research: list[Research],
                          total_earned: float) -> bool:
    """Check whether a project can be researched now, ignoring money.

    Args:
        project: The project to check.
        research: Every research project, to look up the prerequisite.
        total_earned: The player's lifetime earnings.

    Returns:
        True if it is unfinished, its prerequisite is done, and the
        player has earned enough for it to appear.
    """
    return (not project.is_done
            and total_earned >= project.unlock_at_earned
            and is_requirement_met(project.prerequisite, research))


assert_equal(is_research_available(make_test_research("A", "", False), [],
                                   99.0), False)
assert_equal(is_research_available(make_test_research("A", "", False), [],
                                   100.0), True)
assert_equal(is_research_available(make_test_research("A", "", True), [],
                                   100.0), False)
assert_equal(is_research_available(
    make_test_research("B", "A", False),
    [make_test_research("A", "", False)], 100.0), False)


def count_available_research(research: list[Research],
                             total_earned: float) -> int:
    """Count the projects that can be researched now, ignoring money.

    The Business nav badge shows this number. It ignores money so the
    badge (and the buttons around it) never redraw when money changes.

    Args:
        research: Every research project.
        total_earned: The player's lifetime earnings.

    Returns:
        How many projects are available.
    """
    count = 0
    for project in research:
        if is_research_available(project, research, total_earned):
            count = count + 1
    return count


assert_equal(count_available_research(make_new_state().research, 0.0), 0)
assert_equal(count_available_research(make_new_state().research, 1000.0), 2)


def research_money_required(cost: float, goods_in_stock: int) -> float:
    """Calculate the money needed to safely pay for a research project.

    Like money_required, it keeps enough money to restock an empty
    warehouse, so research can never end the game.

    Args:
        cost: The research's price.
        goods_in_stock: Units currently in the warehouse.

    Returns:
        The price, plus one unit's cost if the warehouse is empty.
    """
    if goods_in_stock == 0:
        return cost + UNIT_COST
    return cost


assert_equal(research_money_required(800.0, 5), 800.0)
assert_equal(research_money_required(800.0, 0), 800.0 + UNIT_COST)


def can_buy_research(state: State, research_index: int) -> bool:
    """Check whether a research project can be bought right now.

    Args:
        state: The current game state.
        research_index: The project's position in state.research.

    Returns:
        True if it is available and the player can afford it.
    """
    project = state.research[research_index]
    required = research_money_required(project.cost, state.goods_in_stock)
    return (is_research_available(project, state.research, state.total_earned)
            and required <= state.money)


assert_equal(can_buy_research(make_research_state(), 0), True)
assert_equal(can_buy_research(make_poor_research_state(), 0), False)
assert_equal(can_buy_research(make_new_state(), 0), False)


def complete_research(state: State, research_index: int) -> None:
    """Pay for a research project, mark it done, and post its headline.

    Args:
        state: The game state to update.
        research_index: The project's position in state.research.
    """
    project = state.research[research_index]
    state.money = state.money - project.cost
    project.is_done = True
    state.news_feed = add_news(state.news_feed, project.headline)


def total_research_stocking_bonus(research: list[Research]) -> float:
    """Add up the stocking bonus of every completed research.

    Args:
        research: Every research project.

    Returns:
        The combined stocking bonus as a fraction.
    """
    total = 0.0
    for project in research:
        if project.is_done:
            total = total + project.stocking_bonus
    return total


assert_equal(total_research_stocking_bonus(
    [make_test_research("A", "", True), make_test_research("B", "", False)]),
    0.1)


def total_research_delivery_bonus(research: list[Research]) -> float:
    """Add up the delivery bonus of every completed research.

    Args:
        research: Every research project.

    Returns:
        The combined delivery bonus as a fraction.
    """
    total = 0.0
    for project in research:
        if project.is_done:
            total = total + project.delivery_bonus
    return total


assert_equal(total_research_delivery_bonus(
    [make_test_research("A", "", True), make_test_research("B", "", False)]),
    0.2)


def total_research_market_bonus(research: list[Research]) -> int:
    """Add up the customers every completed research adds to the market.

    Args:
        research: Every research project.

    Returns:
        The number of extra customers.
    """
    total = 0
    for project in research:
        if project.is_done:
            total = total + project.market_bonus
    return total


assert_equal(total_research_market_bonus(
    [make_test_research("A", "", True), make_test_research("B", "", True)]),
    20)


def goods_income_bonus(goods: GoodsType, research: list[Research]) -> float:
    """Find a goods type's income bonus, including research boosts.

    Args:
        goods: The goods type.
        research: Every research project.

    Returns:
        Its own bonus plus the bonus of each completed research for it.
    """
    total = goods.income_bonus
    for project in research:
        if project.is_done and project.goods_name == goods.name:
            total = total + project.goods_bonus
    return total


assert_equal(goods_income_bonus(make_test_goods(0.25, True),
                                [make_test_research("A", "", True)]), 0.75)
assert_equal(goods_income_bonus(make_test_goods(0.25, True),
                                [make_test_research("A", "", False)]), 0.25)


def total_research_goods_bonus(research: list[Research],
                               goods_types: list[GoodsType]) -> float:
    """Add up the research boosts for every goods type being sold.

    total_goods_bonus already counts each goods type's own bonus, so this
    adds only the extra part that research gives.

    Args:
        research: Every research project.
        goods_types: Every goods type.

    Returns:
        The extra income bonus from research, as a fraction.
    """
    total = 0.0
    for goods in goods_types:
        if goods.is_selling:
            total = (total + goods_income_bonus(goods, research)
                     - goods.income_bonus)
    return total


assert_equal(total_research_goods_bonus([make_test_research("A", "", True)],
                                        [make_test_goods(0.25, True)]), 0.5)
assert_equal(total_research_goods_bonus([make_test_research("A", "", True)],
                                        [make_test_goods(0.25, False)]), 0.0)


# ---------------------------------------------------------------------------
# Artifacts: expeditions, copies, and the grid
# ---------------------------------------------------------------------------

def artifact_bonus(artifact: Artifact) -> float:
    """Calculate an artifact's income bonus, including its duplicates.

    Args:
        artifact: The artifact to measure.

    Returns:
        The bonus as a fraction, where 0.5 means +50%.
    """
    extra_copies = artifact.copies - 1
    return artifact.income_bonus * (1 + COPY_BONUS_FRACTION * extra_copies)


assert_equal(artifact_bonus(make_test_artifact("A", 0.1, 1, 0)), 0.1)
assert_equal(round(artifact_bonus(make_test_artifact("A", 0.1, 6, 0)), 3),
             0.15)


def total_artifact_bonus(owned_artifacts: list[Artifact]) -> float:
    """Total the income bonuses of the artifacts placed in the grid.

    REQUIREMENT: This is the project's main loop over a list of dataclass
    instances. It visits each Artifact in state.owned_artifacts, skips any
    that aren't in the grid, and adds the rest into the income bonus.

    Args:
        owned_artifacts: Every artifact the player owns.

    Returns:
        The combined bonus as a fraction.
    """
    total = 0.0
    for artifact in owned_artifacts:
        if artifact.slot != NOT_PLACED:
            total = total + artifact_bonus(artifact)
    return total


assert_equal(total_artifact_bonus([]), 0.0)
# Only Alpha is placed, so Beta's +50% must not count.
assert_equal(total_artifact_bonus(make_artifact_state().owned_artifacts), 0.1)


def expedition_cost(expeditions_bought: int) -> float:
    """Calculate the price of the next single expedition.

    Args:
        expeditions_bought: Expeditions bought before this one.

    Returns:
        The price of one expedition.
    """
    return EXPEDITION_BASE_COST * EXPEDITION_COST_GROWTH ** expeditions_bought


assert_equal(expedition_cost(0), EXPEDITION_BASE_COST)
assert_equal(round(expedition_cost(1), 2), 505.0)


def expedition_batch_cost(expeditions_bought: int, count: int) -> float:
    """Add up the price of several expeditions bought together.

    Args:
        expeditions_bought: Expeditions bought before this batch.
        count: How many expeditions are in the batch.

    Returns:
        The total price of the batch.
    """
    total = 0.0
    for index in range(count):
        total = total + expedition_cost(expeditions_bought + index)
    return total


assert_equal(expedition_batch_cost(0, 0), 0.0)
assert_equal(round(expedition_batch_cost(0, 2), 2), 1005.0)


def expedition_money_required(expeditions_bought: int, count: int,
                              goods_in_stock: int) -> float:
    """Calculate the money needed to safely buy an expedition batch.

    Like money_required, this stops the player spending the last of their
    money with an empty warehouse, which would end the game.

    Args:
        expeditions_bought: Expeditions bought before this batch.
        count: How many expeditions are in the batch.
        goods_in_stock: Units currently in the warehouse.

    Returns:
        The batch price, plus one unit's cost if the warehouse is empty.
    """
    price = expedition_batch_cost(expeditions_bought, count)
    if goods_in_stock == 0:
        return price + UNIT_COST
    return price


assert_equal(expedition_money_required(0, 1, 5), 500.0)
assert_equal(expedition_money_required(0, 1, 0), 500.0 + UNIT_COST)


def can_afford_expedition(state: State, count: int) -> bool:
    """Check whether a whole expedition batch can be bought right now.

    Args:
        state: The current game state.
        count: How many expeditions are in the batch.

    Returns:
        True if the player has enough money for the batch.
    """
    required = expedition_money_required(state.expeditions_bought, count,
                                         state.goods_in_stock)
    return required <= state.money


# A new game has 500 money and an empty warehouse, so it is 15 short.
assert_equal(can_afford_expedition(make_new_state(), 1), False)


def total_rarity_weight() -> int:
    """Add up the weights of every rarity.

    Returns:
        The sum of the weights in RARITY_WEIGHTS.
    """
    total = 0
    for row in RARITY_WEIGHTS:
        total = total + row[1]
    return total


assert_equal(total_rarity_weight(), 100)


def rarity_for_roll(roll: int) -> str:
    """Turn a number from 1 to the total weight into a rarity.

    Args:
        roll: The number rolled.

    Returns:
        The rarity whose share of the weights contains the roll.
    """
    weight_so_far = 0
    for row in RARITY_WEIGHTS:
        weight_so_far = weight_so_far + row[1]
        if roll <= weight_so_far:
            return row[0]
    return RARITY_COMMON


assert_equal(rarity_for_roll(1), RARITY_COMMON)
assert_equal(rarity_for_roll(70), RARITY_COMMON)
assert_equal(rarity_for_roll(71), RARITY_RARE)
assert_equal(rarity_for_roll(95), RARITY_RARE)
assert_equal(rarity_for_roll(96), RARITY_LEGENDARY)
assert_equal(rarity_for_roll(100), RARITY_LEGENDARY)


def roll_rarity() -> str:
    """Randomly choose a rarity using the weighted odds.

    Uses randomness, so it has no unit test (rarity_for_roll is tested).

    Returns:
        One of the RARITY_ constants.
    """
    # ADVANCED: random.randint(a, b) picks a whole number from a to b,
    # including both ends.
    return rarity_for_roll(random.randint(1, total_rarity_weight()))


def artifact_rows_of_rarity(rarity: str) -> list[list]:
    """Find the catalog rows with a given rarity.

    Args:
        rarity: The rarity to look for.

    Returns:
        A list of the matching rows from ARTIFACT_ROWS.
    """
    matching_rows = []
    for row in ARTIFACT_ROWS:
        if row[2] == rarity:
            matching_rows.append(row)
    return matching_rows


assert_equal(len(artifact_rows_of_rarity(RARITY_COMMON)), 6)
assert_equal(len(artifact_rows_of_rarity(RARITY_RARE)), 5)
assert_equal(len(artifact_rows_of_rarity(RARITY_LEGENDARY)), 3)
assert_equal(artifact_rows_of_rarity("imaginary"), [])


def roll_artifact_row(rarity: str) -> list:
    """Randomly choose one catalog row of the given rarity.

    Uses randomness, so it has no unit test.

    Args:
        rarity: The rarity to choose from.

    Returns:
        One row from ARTIFACT_ROWS.
    """
    rows = artifact_rows_of_rarity(rarity)
    # ADVANCED: random.randint picks a random valid index into rows.
    return rows[random.randint(0, len(rows) - 1)]


def artifact_label(artifact: Artifact) -> str:
    """Build the text that identifies an artifact in menus and the grid.

    Args:
        artifact: The artifact to label.

    Returns:
        The artifact's emoji and name.
    """
    return artifact.emoji + " " + artifact.name


assert_equal(artifact_label(make_test_artifact("Alpha", 0.1, 1, 0)), "A Alpha")


def find_artifact_index(owned_artifacts: list[Artifact], label: str) -> int:
    """Linear search for the artifact with a given label.

    Args:
        owned_artifacts: Every artifact the player owns.
        label: The artifact_label to look for.

    Returns:
        The artifact's position in the list, or NOT_FOUND.
    """
    for index in range(len(owned_artifacts)):
        if artifact_label(owned_artifacts[index]) == label:
            return index
    return NOT_FOUND


assert_equal(find_artifact_index(make_artifact_state().owned_artifacts,
                                 "A Beta"), 1)
assert_equal(find_artifact_index([], "A Beta"), NOT_FOUND)


def artifact_from_row(row: list) -> Artifact:
    """Build a one-copy, unplaced Artifact from a catalog row.

    Args:
        row: One row of ARTIFACT_ROWS.

    Returns:
        A new Artifact, so the global row is never modified.
    """
    return Artifact(row[0], row[1], row[2], row[3], row[4], 1, NOT_PLACED)


assert_equal(artifact_from_row(["A", "Alpha", RARITY_COMMON, 0.1, "Test"]),
             make_test_artifact("Alpha", 0.1, 1, NOT_PLACED))


def add_artifact_copy(owned_artifacts: list[Artifact], row: list) -> None:
    """Add a found artifact, or one more copy if it is a duplicate.

    Args:
        owned_artifacts: Every artifact the player owns; updated here.
        row: The catalog row that was found.
    """
    found = artifact_from_row(row)
    index = find_artifact_index(owned_artifacts, artifact_label(found))
    if index == NOT_FOUND:
        owned_artifacts.append(found)
    else:
        owned_artifacts[index].copies = owned_artifacts[index].copies + 1


def added_twice_artifacts() -> list[Artifact]:
    """Add the same catalog row to an empty collection twice.

    Returns:
        The resulting list of owned artifacts.
    """
    owned_artifacts = []
    row = ["A", "Alpha", RARITY_COMMON, 0.1, "Test"]
    add_artifact_copy(owned_artifacts, row)
    add_artifact_copy(owned_artifacts, row)
    return owned_artifacts


assert_equal(added_twice_artifacts(),
             [make_test_artifact("Alpha", 0.1, 2, NOT_PLACED)])


def summarize_finds(find_texts: list[str]) -> list[str]:
    """Combine repeated expedition finds into one line each.

    Args:
        find_texts: One line of text for every artifact found.

    Returns:
        One line per different find, such as "A Alpha x3".
    """
    counts = {}
    for text in find_texts:
        if text in counts:
            counts[text] = counts[text] + 1
        else:
            counts[text] = 1
    lines = []
    for text in counts:
        lines.append(text + " x" + str(counts[text]))
    return lines


assert_equal(summarize_finds([]), [])
assert_equal(summarize_finds(["A", "B", "A"]), ["A x2", "B x1"])


def collect_expedition_finds(state: State, count: int) -> None:
    """Roll each expedition in a batch and record what was found.

    Uses randomness, so it has no unit test.

    Args:
        state: The current game state; its artifacts and finds are updated.
        count: How many expeditions to roll.
    """
    find_texts = []
    for expedition in range(count):
        rarity = roll_rarity()
        row = roll_artifact_row(rarity)
        add_artifact_copy(state.owned_artifacts, row)
        find_texts.append(row[0] + " " + row[1] + " (" + rarity + ")")
    state.last_expedition_finds = summarize_finds(find_texts)


def slot_choice(owned_artifacts: list[Artifact], slot: int) -> str:
    """Find the label of whatever occupies a grid slot.

    Args:
        owned_artifacts: Every artifact the player owns.
        slot: The grid slot number.

    Returns:
        The artifact's label, or EMPTY_SLOT if nothing is there.
    """
    for artifact in owned_artifacts:
        if artifact.slot == slot:
            return artifact_label(artifact)
    return EMPTY_SLOT


assert_equal(slot_choice(make_artifact_state().owned_artifacts, 0), "A Alpha")
assert_equal(slot_choice(make_artifact_state().owned_artifacts, 1), EMPTY_SLOT)


def slot_options(owned_artifacts: list[Artifact]) -> list[str]:
    """List the choices shown in each grid slot's SelectBox.

    Args:
        owned_artifacts: Every artifact the player owns.

    Returns:
        EMPTY_SLOT followed by the label of each owned artifact.
    """
    options = [EMPTY_SLOT]
    for artifact in owned_artifacts:
        options.append(artifact_label(artifact))
    return options


assert_equal(slot_options(make_artifact_state().owned_artifacts),
             [EMPTY_SLOT, "A Alpha", "A Beta"])


def place_artifacts(owned_artifacts: list[Artifact],
                    choices: list[str]) -> None:
    """Rearrange the grid to match the player's SelectBox choices.

    Each artifact fits in one slot, so if it was chosen more than once,
    the earliest slot keeps it and the later ones stay empty.

    Args:
        owned_artifacts: Every artifact the player owns; updated here.
        choices: The label chosen for each slot, in slot order.
    """
    for artifact in owned_artifacts:
        artifact.slot = NOT_PLACED
    for slot in range(len(choices)):
        index = find_artifact_index(owned_artifacts, choices[slot])
        if index != NOT_FOUND and owned_artifacts[index].slot == NOT_PLACED:
            owned_artifacts[index].slot = slot


def artifacts_after_placing(choices: list[str]) -> list[Artifact]:
    """Apply slot choices to the test artifacts.

    Args:
        choices: The label chosen for each slot, in slot order.

    Returns:
        The rearranged test artifacts.
    """
    owned_artifacts = make_artifact_state().owned_artifacts
    place_artifacts(owned_artifacts, choices)
    return owned_artifacts


# Choosing Beta moves it in, and Alpha is taken out of the grid.
assert_equal(artifacts_after_placing(["A Beta", EMPTY_SLOT]),
             [make_test_artifact("Alpha", 0.1, 1, NOT_PLACED),
              make_test_artifact("Beta", 0.5, 1, 0)])
# An artifact chosen twice stays in the earliest slot.
assert_equal(artifacts_after_placing([EMPTY_SLOT, "A Beta", "A Beta"]),
             [make_test_artifact("Alpha", 0.1, 1, NOT_PLACED),
              make_test_artifact("Beta", 0.5, 1, 1)])


# ---------------------------------------------------------------------------
# Economy: pure helper functions
# ---------------------------------------------------------------------------

def tick_interval(state: State) -> int:
    """Find the time between ticks (upgrades will change this later).

    Args:
        state: The current game state.

    Returns:
        The number of milliseconds between ticks.
    """
    return TICK_INTERVAL_MS


assert_equal(tick_interval(make_new_state()), TICK_INTERVAL_MS)


def total_item_effect(items: list[BuyItem], effect_kind: str) -> int:
    """Add up the effect of every owned item of the given kind.

    Args:
        items: The items to add up.
        effect_kind: The EFFECT_ constant to count.

    Returns:
        The combined effect of all owned units of that kind.
    """
    total = 0
    for item in items:
        if item.effect_kind == effect_kind:
            total = total + item.owned * item.effect_amount
    return total


assert_equal(total_item_effect([], EFFECT_STOCKING), 0)
assert_equal(total_item_effect([make_test_item(EFFECT_STOCKING, 5, 2),
                                make_test_item(EFFECT_DELIVERY, 9, 9),
                                make_test_item(EFFECT_STOCKING, 1, 3)],
                               EFFECT_STOCKING), 13)


def calculate_stocking_rate(items: list[BuyItem]) -> int:
    """Calculate how many goods can be bought per tick.

    Args:
        items: The player's buy items.

    Returns:
        The base stocking rate plus the bonus from owned items.
    """
    return BASE_STOCKING_RATE + total_item_effect(items, EFFECT_STOCKING)


assert_equal(calculate_stocking_rate([make_test_item(EFFECT_STOCKING, 5, 2)]),
             BASE_STOCKING_RATE + 10)


def calculate_delivery_capacity(items: list[BuyItem]) -> int:
    """Calculate how many goods can be delivered per tick.

    Args:
        items: The player's buy items.

    Returns:
        The base delivery capacity plus the bonus from owned items.
    """
    return BASE_DELIVERY_CAPACITY + total_item_effect(items, EFFECT_DELIVERY)


assert_equal(calculate_delivery_capacity(
    [make_test_item(EFFECT_DELIVERY, 1, 3)]), BASE_DELIVERY_CAPACITY + 3)


def calculate_warehouse_capacity(items: list[BuyItem]) -> int:
    """Calculate how many goods the warehouse can hold.

    Args:
        items: The player's buy items.

    Returns:
        The base warehouse capacity plus the bonus from owned items.
    """
    return BASE_WAREHOUSE_CAPACITY + total_item_effect(items, EFFECT_CAPACITY)


assert_equal(calculate_warehouse_capacity(
    [make_test_item(EFFECT_CAPACITY, 50, 2)]), BASE_WAREHOUSE_CAPACITY + 100)


def apply_rate_modifiers(base_rate: int, bonus_fraction: float,
                         strike_ticks_left: int) -> int:
    """Apply percentage bonuses and any strike penalty to a per-tick rate.

    Args:
        base_rate: The rate before modifiers.
        bonus_fraction: The combined policy, research, and item bonus.
        strike_ticks_left: Ticks until the current strike ends.

    Returns:
        The final rate, rounded down to a whole number of units.
    """
    multiplier = (1 + bonus_fraction) * strike_multiplier(strike_ticks_left)
    return int(round(base_rate * multiplier, 2))


assert_equal(apply_rate_modifiers(10, 0.0, 0), 10)
assert_equal(apply_rate_modifiers(10, 0.5, 0), 15)
assert_equal(apply_rate_modifiers(10, 0.5, 2), 7)


def item_delivery_boost(items: list[BuyItem]) -> float:
    """Add up the percentage delivery boost from owned items.

    Args:
        items: The player's buy items.

    Returns:
        The boost as a fraction (each effect_amount is a percent).
    """
    return total_item_effect(items, EFFECT_DELIVERY_BOOST) / 100


assert_equal(item_delivery_boost(
    [make_test_item(EFFECT_DELIVERY_BOOST, 5, 2)]), 0.1)


def total_stocking_bonus(state: State) -> float:
    """Add the percentage stocking bonuses from policies and research.

    Args:
        state: The current game state.

    Returns:
        The combined stocking bonus as a fraction.
    """
    return (total_policy_stocking_bonus(state.policies)
            + total_research_stocking_bonus(state.research))


assert_equal(total_stocking_bonus(make_new_state()), 0.0)
assert_equal(total_stocking_bonus(make_finished_research_state(0)), 0.1)


def total_delivery_bonus(state: State) -> float:
    """Add the percentage delivery bonuses from policies, research, items.

    Args:
        state: The current game state.

    Returns:
        The combined delivery bonus as a fraction.
    """
    return (total_policy_delivery_bonus(state.policies)
            + total_research_delivery_bonus(state.research)
            + item_delivery_boost(state.buy_items))


assert_equal(total_delivery_bonus(make_new_state()), 0.0)
assert_equal(total_delivery_bonus(make_finished_research_state(1)), 0.1)


def effective_stocking_rate(state: State) -> int:
    """Calculate the most goods that can be stocked each tick right now.

    Args:
        state: The current game state.

    Returns:
        The stocking rate after policies, research, and strikes.
    """
    return apply_rate_modifiers(calculate_stocking_rate(state.buy_items),
                                total_stocking_bonus(state),
                                state.strike_ticks_left)


assert_equal(effective_stocking_rate(make_new_state()), BASE_STOCKING_RATE)
assert_equal(effective_stocking_rate(make_striking_state(1)),
             BASE_STOCKING_RATE // 2)


def effective_delivery_capacity(state: State) -> int:
    """Calculate the most goods that can be delivered each tick right now.

    Args:
        state: The current game state.

    Returns:
        The delivery capacity after policies, research, items, and strikes.
    """
    return apply_rate_modifiers(calculate_delivery_capacity(state.buy_items),
                                total_delivery_bonus(state),
                                state.strike_ticks_left)


assert_equal(effective_delivery_capacity(make_new_state()),
             BASE_DELIVERY_CAPACITY)
assert_equal(effective_delivery_capacity(make_striking_state(1)),
             BASE_DELIVERY_CAPACITY // 2)


def calculate_units_stocked(stocking_rate: int, goods_in_stock: int,
                            warehouse_capacity: int, money: float) -> int:
    """Calculate units bought, limited by rate, free space, and money.

    Args:
        stocking_rate: The most goods that can be bought per tick.
        goods_in_stock: Units already in the warehouse.
        warehouse_capacity: The most units the warehouse can hold.
        money: The money available to spend.

    Returns:
        The number of units bought this tick.
    """
    free_space = warehouse_capacity - goods_in_stock
    affordable_units = int(money // UNIT_COST)
    return min(stocking_rate, free_space, affordable_units)


assert_equal(calculate_units_stocked(5, 0, 100, 500.0), 5)
assert_equal(calculate_units_stocked(5, 98, 100, 500.0), 2)
assert_equal(calculate_units_stocked(5, 0, 100, 44.0), 2)
assert_equal(calculate_units_stocked(5, 100, 100, 500.0), 0)


def current_market_size(state: State) -> int:
    """Find how many customers the market holds, including research.

    Args:
        state: The current game state.

    Returns:
        MARKET_SIZE plus the customers added by completed research.
    """
    return MARKET_SIZE + total_research_market_bonus(state.research)


assert_equal(current_market_size(make_new_state()), MARKET_SIZE)
assert_equal(current_market_size(make_finished_research_state(7)),
             MARKET_SIZE + RESEARCH_ROWS[7][7])


def calculate_demand(loyalty: float, market_size: int) -> int:
    """Calculate how many units customers want to buy this tick.

    Args:
        loyalty: Customer loyalty from 0 to 100.
        market_size: How many customers the market holds.

    Returns:
        The number of units customers want, rounded down.
    """
    # Drifting loyalty stops just short of its target (like 59.9999), so
    # round first or // would drop a whole unit of demand.
    return int(market_size * round(loyalty, 2) // 100)


assert_equal(calculate_demand(50.0, 100), 50)
assert_equal(calculate_demand(0.0, 100), 0)
assert_equal(calculate_demand(59.9999, 100), 60)
assert_equal(calculate_demand(59.5, 100), 59)
assert_equal(calculate_demand(50.0, 150), 75)


def calculate_units_sold(goods_in_stock: int, delivery_capacity: int,
                         demand: int) -> int:
    """Calculate units sold: the smallest of stock, delivery, and demand.

    Args:
        goods_in_stock: Units available in the warehouse.
        delivery_capacity: The most units that can be delivered.
        demand: The number of units customers want.

    Returns:
        The number of units sold this tick.
    """
    return min(goods_in_stock, delivery_capacity, demand)


assert_equal(calculate_units_sold(3, 5, 50), 3)
assert_equal(calculate_units_sold(30, 5, 50), 5)
assert_equal(calculate_units_sold(30, 50, 7), 7)


def calculate_sale_price(markup: float) -> float:
    """Calculate the price customers pay for one unit.

    Args:
        markup: The multiplier applied to the unit cost.

    Returns:
        The sale price of one unit.
    """
    return UNIT_COST * markup


assert_equal(calculate_sale_price(2.0), 30.0)


def calculate_total_bonus(state: State) -> float:
    """Add the income bonuses from goods, policies, artifacts, and research.

    Args:
        state: The current game state.

    Returns:
        The bonus as a fraction, where 0.5 means +50%.
    """
    return (total_goods_bonus(state.goods_types)
            + total_research_goods_bonus(state.research, state.goods_types)
            + total_policy_income_bonus(state.policies)
            + total_artifact_bonus(state.owned_artifacts))


assert_equal(calculate_total_bonus(make_new_state()), 0.0)
assert_equal(round(calculate_total_bonus(make_state_with_income_bonuses()), 2),
             0.3)
assert_equal(calculate_total_bonus(make_artifact_state()), 0.1)


def calculate_income(units_sold: int, sale_price: float,
                     total_bonus: float) -> float:
    """Calculate the money earned from a tick's sales.

    Args:
        units_sold: The number of units sold.
        sale_price: The price of one unit.
        total_bonus: The income bonus as a fraction.

    Returns:
        The income from these sales.
    """
    return units_sold * sale_price * (1 + total_bonus)


assert_equal(calculate_income(4, 10.0, 0.0), 40.0)
assert_equal(calculate_income(4, 10.0, 0.5), 60.0)


def max_income_per_tick(state: State) -> float:
    """Calculate the income if every delivery slot sold a unit.

    Args:
        state: The current game state.

    Returns:
        The income from a tick at full delivery capacity.
    """
    return calculate_income(effective_delivery_capacity(state),
                            calculate_sale_price(state.markup),
                            calculate_total_bonus(state))


assert_equal(max_income_per_tick(make_new_state()),
             BASE_DELIVERY_CAPACITY * UNIT_COST * STARTING_MARKUP)


def clamp_loyalty(loyalty: float) -> float:
    """Keep a loyalty value between MIN_LOYALTY and MAX_LOYALTY.

    Args:
        loyalty: The value to limit.

    Returns:
        The value, moved inside the allowed range if needed.
    """
    if loyalty < MIN_LOYALTY:
        return MIN_LOYALTY
    if loyalty > MAX_LOYALTY:
        return MAX_LOYALTY
    return loyalty


assert_equal(clamp_loyalty(-5.0), MIN_LOYALTY)
assert_equal(clamp_loyalty(105.0), MAX_LOYALTY)
assert_equal(clamp_loyalty(42.0), 42.0)


def calculate_loyalty_target(markup: float, items: list[BuyItem],
                             policies: list[Policy]) -> float:
    """Calculate the loyalty that markup, marketing, and policies lead to.

    Args:
        markup: The current markup.
        items: The player's buy items.
        policies: The player's corporate policies.

    Returns:
        The loyalty value that customers drift toward.
    """
    marketing = total_item_effect(items, EFFECT_LOYALTY)
    penalty = (markup - MIN_MARKUP) * MARKUP_LOYALTY_PENALTY
    policy_change = total_policy_loyalty_change(policies)
    return clamp_loyalty(BASE_LOYALTY_TARGET + marketing - penalty
                         + policy_change)


assert_equal(calculate_loyalty_target(1.0, [], []), BASE_LOYALTY_TARGET)
assert_equal(calculate_loyalty_target(1.5, [], []), 50.0)
assert_equal(calculate_loyalty_target(5.0, [], []), 0.0)
assert_equal(calculate_loyalty_target(
    1.0, [make_test_item(EFFECT_LOYALTY, 2, 3)], []), 66.0)
assert_equal(calculate_loyalty_target(1.0, [], [make_test_policy(True)]),
             BASE_LOYALTY_TARGET - 5.0)


def drift_loyalty(loyalty: float, target: float) -> float:
    """Move loyalty part of the way toward its target.

    Args:
        loyalty: The current loyalty.
        target: The loyalty being drifted toward.

    Returns:
        The new loyalty after one tick of drifting.
    """
    return clamp_loyalty(loyalty + (target - loyalty) * LOYALTY_DRIFT_FRACTION)


assert_equal(drift_loyalty(50.0, 60.0), 51.0)
assert_equal(drift_loyalty(50.0, 40.0), 49.0)
assert_equal(drift_loyalty(50.0, 50.0), 50.0)


def change_markup(markup: float, change: float) -> float:
    """Apply a markup change, keeping the result in the allowed range.

    Args:
        markup: The current markup.
        change: The amount to add (negative to lower it).

    Returns:
        The new markup, rounded to two decimal places.
    """
    new_markup = round(markup + change, 2)
    if new_markup < MIN_MARKUP:
        return MIN_MARKUP
    if new_markup > MAX_MARKUP:
        return MAX_MARKUP
    return new_markup


assert_equal(change_markup(1.5, 0.1), 1.6)
assert_equal(change_markup(1.0, -0.1), MIN_MARKUP)
assert_equal(change_markup(5.0, 0.1), MAX_MARKUP)


def clean_company_name(company_name: str) -> str:
    """Strip spaces from a name, using the default if it is blank.

    Args:
        company_name: The name the player typed.

    Returns:
        The cleaned name, or DEFAULT_COMPANY_NAME if nothing was typed.
    """
    cleaned_name = company_name.strip()
    if not cleaned_name:
        return DEFAULT_COMPANY_NAME
    return cleaned_name


assert_equal(clean_company_name("  Boxes  "), "Boxes")
assert_equal(clean_company_name("   "), DEFAULT_COMPANY_NAME)


def run_stocking(state: State) -> None:
    """Buy goods into the warehouse and pay for them.

    Args:
        state: The game state to update.
    """
    units = calculate_units_stocked(
        effective_stocking_rate(state),
        state.goods_in_stock,
        calculate_warehouse_capacity(state.buy_items),
        state.money,
    )
    state.goods_in_stock = state.goods_in_stock + units
    state.money = state.money - units * UNIT_COST
    state.goods_stocked_last_tick = units


def run_selling(state: State) -> None:
    """Sell goods to customers and collect the income.

    Args:
        state: The game state to update.
    """
    units = calculate_units_sold(
        state.goods_in_stock,
        effective_delivery_capacity(state),
        calculate_demand(state.loyalty, current_market_size(state)),
    )
    income = calculate_income(units, calculate_sale_price(state.markup),
                              calculate_total_bonus(state))
    state.goods_in_stock = state.goods_in_stock - units
    state.money = state.money + income
    state.total_earned = state.total_earned + income
    state.goods_sold_last_tick = units
    state.income_last_tick = income


def run_loyalty_drift(state: State) -> None:
    """Move customer loyalty toward its target.

    Args:
        state: The game state to update.
    """
    target = calculate_loyalty_target(state.markup, state.buy_items,
                                      state.policies)
    state.loyalty = drift_loyalty(state.loyalty, target)


def run_strikes(state: State) -> None:
    """Count down the current strike, or roll for a new one.

    Args:
        state: The game state to update.
    """
    if state.strike_ticks_left > 0:
        state.strike_ticks_left = state.strike_ticks_left - 1
    elif roll_strike(total_strike_risk(state.policies)):
        state.strike_ticks_left = STRIKE_DURATION_TICKS
        state.news_feed = add_news(state.news_feed, STRIKE_NEWS)


assert_equal(state_after_strikes(make_striking_state(3)).strike_ticks_left, 2)
assert_equal(state_after_strikes(make_new_state()).strike_ticks_left, 0)
assert_equal(state_after_strikes(
    make_certain_strike_state()).strike_ticks_left, STRIKE_DURATION_TICKS)
assert_equal(state_after_strikes(make_certain_strike_state()).news_feed[0],
             STRIKE_NEWS)


# ---------------------------------------------------------------------------
# Purchases: pure helper functions
# ---------------------------------------------------------------------------

def item_cost(item: BuyItem, owned_offset: int) -> float:
    """Calculate the price of one unit of an item.

    Args:
        item: The item being priced.
        owned_offset: How many units past those already owned to price.

    Returns:
        The price of that unit after cost growth.
    """
    return item.base_cost * COST_GROWTH ** (item.owned + owned_offset)


assert_equal(item_cost(make_test_item(EFFECT_STOCKING, 1, 0), 0), 100.0)
assert_equal(item_cost(make_test_item(EFFECT_STOCKING, 1, 1), 0),
             100.0 * COST_GROWTH)
assert_equal(item_cost(make_test_item(EFFECT_STOCKING, 1, 1), 1),
             100.0 * COST_GROWTH ** 2)


def purchase_quantity(item: BuyItem, buy_amount: int) -> int:
    """Find how many units one click buys.

    Args:
        item: The item being bought.
        buy_amount: The player's chosen X1, X5, or X10 amount.

    Returns:
        1 for a one-time item, otherwise buy_amount.
    """
    if item.is_one_time:
        return 1
    return buy_amount


assert_equal(purchase_quantity(make_test_item(EFFECT_STOCKING, 1, 0), 5), 5)
assert_equal(purchase_quantity(make_one_time_item(0), 5), 1)


def batch_cost(item: BuyItem, quantity: int) -> float:
    """Calculate the total price of buying several units in a row.

    Args:
        item: The item being bought.
        quantity: How many units to buy.

    Returns:
        The combined price of all the units.
    """
    total = 0.0
    for offset in range(quantity):
        total = total + item_cost(item, offset)
    return total


assert_equal(batch_cost(make_test_item(EFFECT_STOCKING, 1, 0), 0), 0.0)
assert_equal(batch_cost(make_test_item(EFFECT_STOCKING, 1, 0), 2),
             100.0 + 100.0 * COST_GROWTH)


def money_required(item: BuyItem, quantity: int,
                   goods_in_stock: int) -> float:
    """Calculate the money needed to safely buy a batch.

    With an empty warehouse, the player must keep enough money to stock one
    unit. Otherwise nothing could be stocked or sold ever again.

    Args:
        item: The item being bought.
        quantity: How many units to buy.
        goods_in_stock: Units currently in the warehouse.

    Returns:
        The batch price, plus one unit's cost if the warehouse is empty.
    """
    if goods_in_stock == 0:
        return batch_cost(item, quantity) + UNIT_COST
    return batch_cost(item, quantity)


assert_equal(money_required(make_test_item(EFFECT_STOCKING, 1, 0), 1, 3),
             100.0)
assert_equal(money_required(make_test_item(EFFECT_STOCKING, 1, 0), 1, 0),
             100.0 + UNIT_COST)


def is_sold_out(item: BuyItem) -> bool:
    """Check whether a one-time item has already been bought.

    Args:
        item: The item to check.

    Returns:
        True if the item can never be bought again.
    """
    return item.is_one_time and item.owned > 0


assert_equal(is_sold_out(make_one_time_item(0)), False)
assert_equal(is_sold_out(make_one_time_item(1)), True)
assert_equal(is_sold_out(make_test_item(EFFECT_STOCKING, 1, 4)), False)


def can_afford(item: BuyItem, quantity: int, money: float,
               goods_in_stock: int) -> bool:
    """Check whether the full batch can be purchased right now.

    Args:
        item: The item being bought.
        quantity: How many units to buy.
        money: The money available to spend.
        goods_in_stock: Units currently in the warehouse.

    Returns:
        True if the item is for sale and the whole batch is affordable.
    """
    required = money_required(item, quantity, goods_in_stock)
    return not is_sold_out(item) and required <= money


assert_equal(can_afford(make_test_item(EFFECT_STOCKING, 1, 0), 1, 100.0, 5),
             True)
assert_equal(can_afford(make_test_item(EFFECT_STOCKING, 1, 0), 2, 100.0, 5),
             False)
assert_equal(can_afford(make_test_item(EFFECT_STOCKING, 1, 0), 1, 100.0, 0),
             False)
assert_equal(can_afford(make_test_item(EFFECT_STOCKING, 1, 0), 1, 115.0, 0),
             True)
assert_equal(can_afford(make_one_time_item(1), 1, 9999.0, 5), False)


def is_item_visible(item: BuyItem, total_earned: float,
                    research: list[Research]) -> bool:
    """Check whether the item has unlocked or was already purchased.

    Args:
        item: The item to check.
        total_earned: The player's lifetime earnings.
        research: Every research project.

    Returns:
        True if its research is done and it was bought or has unlocked.
    """
    return ((item.owned > 0 or total_earned >= item.unlock_at_earned)
            and is_requirement_met(item.required_research, research))


assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 0), 49.0, []),
             False)
assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 0), 50.0, []),
             True)
assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 1), 0.0, []),
             True)
# The pickup truck stays hidden until its research is done.
assert_equal(is_item_visible(make_new_state().buy_items[5], 0.0,
                             make_new_state().research), False)
assert_equal(is_item_visible(make_new_state().buy_items[5], 0.0,
                             make_finished_research_state(2).research), True)


def is_unlock_item_owned(policy: Policy, items: list[BuyItem]) -> bool:
    """Check whether a policy's unlock purchase (if any) has been made.

    Args:
        policy: The policy to check.
        items: The player's buy items.

    Returns:
        True if it needs no unlock or an unlock item has been bought.
    """
    return not policy.needs_unlock or total_item_effect(items,
                                                        EFFECT_UNLOCK) > 0


assert_equal(is_unlock_item_owned(make_locked_policy(),
                                  [make_one_time_item(0)]), False)
assert_equal(is_unlock_item_owned(make_locked_policy(),
                                  [make_one_time_item(1)]), True)


def is_policy_unlocked(policy: Policy, items: list[BuyItem],
                       research: list[Research]) -> bool:
    """Check whether a policy can be used yet.

    Args:
        policy: The policy to check.
        items: The player's buy items.
        research: Every research project.

    Returns:
        True if its unlock item (if any) is owned and its research is done.
    """
    return (is_unlock_item_owned(policy, items)
            and is_requirement_met(policy.required_research, research))


assert_equal(is_policy_unlocked(make_test_policy(False), [], []), True)
assert_equal(is_policy_unlocked(make_locked_policy(),
                                [make_one_time_item(0)], []), False)
assert_equal(is_policy_unlocked(make_locked_policy(),
                                [make_one_time_item(1)], []), True)
assert_equal(is_policy_unlocked(make_new_state().policies[3], [],
                                make_new_state().research), False)
assert_equal(is_policy_unlocked(make_new_state().policies[3], [],
                                make_finished_research_state(5).research),
             True)


def set_policy_choices(policies: list[Policy], choices: list[bool],
                       items: list[BuyItem],
                       research: list[Research]) -> None:
    """Record the player's policies, keeping locked ones switched off.

    Args:
        policies: The policies to update.
        choices: One True or False per policy, in the same order.
        items: The player's buy items.
        research: Every research project.
    """
    for index, policy in enumerate(policies):
        policy.is_active = (choices[index]
                            and is_policy_unlocked(policy, items, research))


# ---------------------------------------------------------------------------
# Casino: the typing test
# ---------------------------------------------------------------------------

def swap_hard_characters(text: str) -> str:
    """Apply the hard difficulty's character swaps.

    "and" must become "&" before "a" becomes "@", or "and" would be broken
    up first. 0 and O trade places, so they are swapped one at a time.

    Args:
        text: The original prompt.

    Returns:
        The prompt with and->&, a->@, 0->O, and O->0 applied.
    """
    swapped = text.replace("and", "&").replace("a", "@")
    result = ""
    for character in swapped:
        if character == "0":
            result = result + "O"
        elif character == "O":
            result = result + "0"
        else:
            result = result + character
    return result


assert_equal(swap_hard_characters("sand a 0 O"), "s& @ O 0")
assert_equal(swap_hard_characters(""), "")


def roll_prompt(difficulty: str) -> str:
    """Randomly choose a prompt for a difficulty.

    Uses randomness, so it has no unit test.

    Args:
        difficulty: One of the DIFFICULTY_ constants.

    Returns:
        The prompt the player must type.
    """
    # ADVANCED: random.randint picks a random valid index into a prompt list.
    if difficulty == DIFFICULTY_HARD:
        index = random.randint(0, len(HARD_PROMPTS) - 1)
        return swap_hard_characters(HARD_PROMPTS[index])
    return EASY_PROMPTS[random.randint(0, len(EASY_PROMPTS) - 1)]


def score_accuracy(prompt: str, typed: str) -> float:
    """Compare typed text to the prompt, one position at a time.

    Spaces at the ends of the typed text are ignored. Missing or extra
    characters count as wrong.

    Args:
        prompt: The text the player was asked to type.
        typed: What the player typed.

    Returns:
        The fraction of positions that are correct, from 0 to 1.
    """
    cleaned = typed.strip()
    total = max(len(prompt), len(cleaned))
    if total == 0:
        return 0.0
    correct = 0
    for index in range(min(len(prompt), len(cleaned))):
        if prompt[index] == cleaned[index]:
            correct = correct + 1
    return correct / total


assert_equal(score_accuracy("abcd", "abcd"), 1.0)
assert_equal(score_accuracy("abcd", "  abcd\n"), 1.0)
assert_equal(score_accuracy("abcd", "abXd"), 0.75)
assert_equal(score_accuracy("abcd", "ab"), 0.5)
assert_equal(score_accuracy("abcd", "abcdefgh"), 0.5)
assert_equal(score_accuracy("abcd", "ABCD"), 0.0)
assert_equal(score_accuracy("", ""), 0.0)


def elapsed_seconds(ticks_passed: int, interval_ms: int) -> float:
    """Convert a number of game ticks into seconds.

    Args:
        ticks_passed: How many ticks went by.
        interval_ms: The milliseconds between ticks.

    Returns:
        The elapsed time in seconds.
    """
    return ticks_passed * interval_ms / 1000


assert_equal(elapsed_seconds(3, 1000), 3.0)
assert_equal(elapsed_seconds(0, 667), 0.0)


def words_per_minute(character_count: int, seconds: float) -> float:
    """Calculate typing speed using the standard 5 characters per word.

    Args:
        character_count: How many characters were typed.
        seconds: How long the typing took.

    Returns:
        The speed in words per minute, or 0 if no time was measured.
    """
    if seconds <= 0:
        return 0.0
    return (character_count / CHARACTERS_PER_WORD) / (seconds / 60)


assert_equal(words_per_minute(50, 60.0), 10.0)
assert_equal(words_per_minute(5, 2.0), 30.0)
assert_equal(words_per_minute(50, 0.0), 0.0)


def tier_multiplier(value: float, tiers: list[list[float]]) -> float:
    """Find the multiplier of the highest tier a value reaches.

    Args:
        value: The score to look up.
        tiers: Rows of [lowest value, multiplier], lowest tier first.

    Returns:
        The multiplier for that value.
    """
    multiplier = tiers[0][1]
    for row in tiers:
        if value >= row[0]:
            multiplier = row[1]
    return multiplier


assert_equal(tier_multiplier(0.79, ACCURACY_TIERS), 0.0)
assert_equal(tier_multiplier(0.8, ACCURACY_TIERS), 0.5)
assert_equal(tier_multiplier(1.0, ACCURACY_TIERS), 1.5)
assert_equal(tier_multiplier(0.0, SPEED_TIERS), 0.5)
assert_equal(tier_multiplier(45.0, SPEED_TIERS), 1.5)
assert_equal(tier_multiplier(200.0, SPEED_TIERS), 2.0)


def calculate_payout(bet: int, accuracy: float, speed_wpm: float,
                     difficulty: str) -> float:
    """Calculate a typing test's winnings; this is the scoring function.

    Args:
        bet: The money that was bet.
        accuracy: The fraction of characters correct.
        speed_wpm: The typing speed in words per minute.
        difficulty: One of the DIFFICULTY_ constants.

    Returns:
        The bet times the accuracy, speed, and difficulty multipliers.
    """
    return (bet * tier_multiplier(accuracy, ACCURACY_TIERS)
            * tier_multiplier(speed_wpm, SPEED_TIERS)
            * DIFFICULTY_MULTIPLIERS[difficulty])


assert_equal(calculate_payout(100, 1.0, 30.0, DIFFICULTY_EASY), 150.0)
assert_equal(calculate_payout(100, 1.0, 30.0, DIFFICULTY_HARD), 300.0)
assert_equal(calculate_payout(100, 1.0, 75.0, DIFFICULTY_HARD), 600.0)
assert_equal(calculate_payout(100, 0.96, 10.0, DIFFICULTY_EASY), 50.0)
# Poor accuracy loses the whole bet, however fast the typing was.
assert_equal(calculate_payout(100, 0.5, 200.0, DIFFICULTY_HARD), 0.0)


def parse_bet(bet_text: str) -> int:
    """Turn the text from the bet box into a number.

    .isascii() rejects symbols such as a superscript 2, which .isdigit()
    accepts but int() cannot convert.

    Args:
        bet_text: What the player typed.

    Returns:
        The whole-number bet, or 0 if the text isn't a whole number.
    """
    cleaned = bet_text.strip()
    # ADVANCED: .isascii() is True only if every character is a plain
    # keyboard character, which keeps symbols like a superscript 2 out of int.
    if cleaned.isdigit() and cleaned.isascii():
        return int(cleaned)
    return 0


assert_equal(parse_bet("250"), 250)
assert_equal(parse_bet(" 7 "), 7)
assert_equal(parse_bet("abc"), 0)
assert_equal(parse_bet("-5"), 0)
assert_equal(parse_bet("1.5"), 0)
assert_equal(parse_bet(""), 0)
assert_equal(parse_bet("²"), 0)


def can_place_bet(bet: int, money: float, goods_in_stock: int) -> bool:
    """Check that a bet is positive, under the cap, and safe.

    With an empty warehouse the player must also keep enough to stock one
    unit, or nothing could be stocked or sold ever again.

    Args:
        bet: The whole-number bet.
        money: The money available.
        goods_in_stock: Units currently in the warehouse.

    Returns:
        True if the bet is allowed.
    """
    if bet <= 0 or bet > money * CASINO_MAX_BET_FRACTION:
        return False
    return goods_in_stock > 0 or bet + UNIT_COST <= money


assert_equal(can_place_bet(0, 500.0, 5), False)
assert_equal(can_place_bet(400, 500.0, 5), True)
assert_equal(can_place_bet(401, 500.0, 5), False)
# Within the 80% cap, but only 10 would be left for restocking.
assert_equal(can_place_bet(40, 50.0, 0), False)
assert_equal(can_place_bet(35, 50.0, 0), True)


def settle_typing_round(state: State, typed_text: str) -> None:
    """Score the running round, pay the player, and end the round.

    Tested through the submit_typing_round route.

    Args:
        state: The current game state; its money and round are updated.
        typed_text: What the player typed.
    """
    typing_round = state.typing_round
    seconds = elapsed_seconds(state.tick_count - typing_round.start_tick,
                              tick_interval(state))
    accuracy = score_accuracy(typing_round.prompt, typed_text)
    speed = words_per_minute(len(typed_text.strip()), seconds)
    payout = calculate_payout(typing_round.bet, accuracy, speed,
                              typing_round.difficulty)
    state.money = state.money + payout
    state.last_casino_result = describe_typing_result(
        accuracy, speed, typing_round.bet, payout)
    state.typing_round = make_no_typing_round()


# ---------------------------------------------------------------------------
# Page helpers
# ---------------------------------------------------------------------------

def format_money(amount: float) -> str:
    """Turn an amount into text with the currency and two decimals.

    Args:
        amount: The amount of money.

    Returns:
        The formatted text, such as "Ŧ22.50".
    """
    cents = round(amount * 100)
    leftover_cents = cents % 100
    cents_text = str(leftover_cents)
    if leftover_cents < 10:
        cents_text = "0" + cents_text
    return CURRENCY_SYMBOL + str(cents // 100) + "." + cents_text


assert_equal(format_money(5.0), "Ŧ5.00")
assert_equal(format_money(22.5), "Ŧ22.50")
assert_equal(format_money(3.07), "Ŧ3.07")


def percent_text(fraction: float) -> str:
    """Turn a fraction into signed percent text.

    Args:
        fraction: The fraction, where 0.5 means 50%.

    Returns:
        The text, such as "+50%".
    """
    return "+" + str(round(fraction * 100)) + "%"


assert_equal(percent_text(0.5), "+50%")
assert_equal(percent_text(0.0), "+0%")


def artifact_percent_text(fraction: float) -> str:
    """Turn a small bonus into percent text with one decimal place.

    One decimal is needed because a duplicate can add as little as +0.1%.

    Args:
        fraction: The fraction, where 0.011 means 1.1%.

    Returns:
        The text, such as "+1.1%".
    """
    return "+" + str(round(fraction * 100, 1)) + "%"


assert_equal(artifact_percent_text(0.011), "+1.1%")
assert_equal(artifact_percent_text(0.4), "+40.0%")


def describe_policy(policy: Policy) -> str:
    """Describe every upside and downside of a policy.

    Args:
        policy: The policy to describe.

    Returns:
        The policy's nonzero effects, separated by commas.
    """
    text = ""
    if policy.stocking_bonus != 0:
        text = text + percent_text(policy.stocking_bonus) + " stocking, "
    if policy.delivery_bonus != 0:
        text = text + percent_text(policy.delivery_bonus) + " delivery, "
    if policy.income_bonus != 0:
        text = text + percent_text(policy.income_bonus) + " income, "
    if policy.loyalty_change != 0:
        text = text + str(round(policy.loyalty_change)) + " loyalty target, "
    if policy.strike_risk != 0:
        text = text + percent_text(policy.strike_risk) + " strike risk/tick, "
    return text[:-2]


assert_equal(describe_policy(make_test_policy(False)),
             "+50% stocking, +25% delivery, +10% income, -5 loyalty target, "
             + "+3% strike risk/tick")


def describe_effect(item: BuyItem) -> str:
    """Describe what one unit of an item does.

    Args:
        item: The item to describe.

    Returns:
        A short description for the buy list.
    """
    amount_text = "+" + str(item.effect_amount)
    if item.effect_kind == EFFECT_STOCKING:
        return amount_text + " goods stocked/tick"
    if item.effect_kind == EFFECT_DELIVERY:
        return amount_text + " delivery capacity"
    if item.effect_kind == EFFECT_LOYALTY:
        return amount_text + " loyalty target"
    if item.effect_kind == EFFECT_CAPACITY:
        return amount_text + " warehouse capacity"
    if item.effect_kind == EFFECT_DELIVERY_BOOST:
        return amount_text + "% delivery capacity"
    return "Unlocks a new corporate policy"


assert_equal(describe_effect(make_test_item(EFFECT_DELIVERY, 1, 0)),
             "+1 delivery capacity")
assert_equal(describe_effect(make_one_time_item(0)),
             "Unlocks a new corporate policy")
assert_equal(describe_effect(make_test_item(EFFECT_DELIVERY_BOOST, 5, 0)),
             "+5% delivery capacity")


def describe_research_effect(project: Research) -> str:
    """Describe the number bonuses a research project gives.

    Args:
        project: The research to describe.

    Returns:
        Its nonzero bonuses separated by commas ("" if it has none).
    """
    text = ""
    if project.stocking_bonus != 0:
        text = text + percent_text(project.stocking_bonus) + " stocking, "
    if project.delivery_bonus != 0:
        text = text + percent_text(project.delivery_bonus) + " delivery, "
    if project.market_bonus != 0:
        text = text + "+" + str(project.market_bonus) + " market size, "
    if project.goods_name != "":
        text = (text + percent_text(project.goods_bonus) + " "
                + project.goods_name + " income, ")
    return text[:-2]


assert_equal(describe_research_effect(make_test_research("A", "", False)),
             "+10% stocking, +20% delivery, +10 market size, "
             + "+50% Test income")
assert_equal(describe_research_effect(make_new_state().research[4]), "")


def research_unlock_text(project: Research, state: State) -> str:
    """List the buy items, goods, and policies a research unlocks.

    Args:
        project: The research to look up.
        state: The current game state.

    Returns:
        "Unlocks: " and their names, or "" if it unlocks nothing.
    """
    names = ""
    for item in state.buy_items:
        if item.required_research == project.name:
            names = names + item.name + ", "
    for goods in state.goods_types:
        if goods.required_research == project.name:
            names = names + goods.name + " (goods), "
    for policy in state.policies:
        if policy.required_research == project.name:
            names = names + policy.name + " (policy), "
    if names == "":
        return ""
    return "Unlocks: " + names[:-2]


assert_equal(research_unlock_text(make_new_state().research[2],
                                  make_new_state()),
             "Unlocks: Upgraded Pickup Truck")
assert_equal(research_unlock_text(make_new_state().research[0],
                                  make_new_state()), "")


def research_summary(project: Research, state: State) -> str:
    """Build the one-line effect summary shown under a research's name.

    Args:
        project: The research to summarize.
        state: The current game state.

    Returns:
        Its category followed by its bonuses or what it unlocks.
    """
    effect = describe_research_effect(project)
    if effect == "":
        effect = research_unlock_text(project, state)
    return project.category.capitalize() + " · " + effect


assert_equal(research_summary(make_new_state().research[0], make_new_state()),
             "Stat · +10% stocking")
assert_equal(research_summary(make_new_state().research[4], make_new_state()),
             "Unlock · Unlocks: Imported Luxuries (goods)")


def controls_signature(state: State) -> str:
    """Summarize what decides whether a tick must redraw the buttons.

    Buy and expedition buttons stay on screen whether or not the player
    can afford them (buy_item and run_expedition refuse what can't be
    afforded), so money changes never redraw them. Only a newly visible
    item or a new headline does. The tick compares this text with the
    previous tick's and leaves the buttons alone if they match, so a
    tick can't interrupt a click.

    Args:
        state: The current game state.

    Returns:
        Text recording the news, which items are visible, and how many
        research projects are available (the Business badge).
    """
    signature = (str(state.news_feed) + str(count_available_research(
        state.research, state.total_earned)))
    for item in state.buy_items:
        signature = signature + str(is_item_visible(item, state.total_earned,
                                                    state.research))
    return signature


# Money alone never changes the signature; unlocking an item does.
assert_equal(controls_signature(make_new_state()),
             controls_signature(make_rich_state()))
assert_equal(controls_signature(make_new_state())
             == controls_signature(make_veteran_state()), False)
# New research becoming available changes the badge, so it redraws.
assert_equal(controls_signature(make_new_state())
             == controls_signature(make_research_state()), False)


def build_chip(label: str, value: str, chip_classes: str) -> Div:
    """Build one small labelled number for the top bar.

    Args:
        label: The small caption above the number.
        value: The number, already formatted as text.
        chip_classes: The CSS classes, such as "chip" or "chip money".

    Returns:
        A Div holding the label and the value.
    """
    # ADVANCED: classes= gives a component CSS class names. THEME_CSS uses
    # those names to pick its colors, size, and position.
    return Div(Span(label, classes="chip-label"),
               Span(value, classes="chip-value"), classes=chip_classes)


def per_tick_text(actual: int, most: int) -> str:
    """Show what happened last tick next to the most that was possible.

    Args:
        actual: The amount last tick.
        most: The most possible in one tick.

    Returns:
        Text such as "5 / 10".
    """
    return str(actual) + " / " + str(most)


assert_equal(per_tick_text(5, 10), "5 / 10")


def build_stat_chips(state: State) -> list[Div]:
    """Build the company statistics shown in the top bar.

    Args:
        state: The current game state.

    Returns:
        One chip per statistic.
    """
    capacity = calculate_warehouse_capacity(state.buy_items)
    capacity_percent = state.goods_in_stock * 100 // capacity
    income_text = (format_money(state.income_last_tick) + " / "
                   + format_money(max_income_per_tick(state)))
    warehouse_text = (str(state.goods_in_stock) + " / " + str(capacity)
                      + " (" + str(capacity_percent) + "%)")
    return [
        build_chip("Stocked / tick",
                   per_tick_text(state.goods_stocked_last_tick,
                                 effective_stocking_rate(state)), "chip"),
        build_chip("Sold / tick",
                   per_tick_text(state.goods_sold_last_tick,
                                 effective_delivery_capacity(state)), "chip"),
        build_chip("Income / tick", income_text, "chip"),
        build_chip("Warehouse", warehouse_text, "chip"),
        build_chip("Loyalty", str(round(state.loyalty, 1)), "chip"),
        build_chip("Demand", str(calculate_demand(
            state.loyalty, current_market_size(state))), "chip"),
        build_chip("Income bonus",
                   percent_text(calculate_total_bonus(state)), "chip"),
    ]


def strike_status_text(strike_ticks_left: int) -> str:
    """Describe whether a strike is happening.

    Args:
        strike_ticks_left: Ticks until the current strike ends.

    Returns:
        A line for the bonus summary.
    """
    if strike_ticks_left > 0:
        return ("⚠️ STRIKE: stocking and delivery x"
                + str(STRIKE_PENALTY_MULTIPLIER) + " for "
                + str(strike_ticks_left) + " more ticks")
    return "No strike in progress"


assert_equal(strike_status_text(0), "No strike in progress")
assert_equal(strike_status_text(2),
             "⚠️ STRIKE: stocking and delivery x0.5 for 2 more ticks")


def build_policy_chips(state: State) -> list[Div]:
    """Build chips for policy effects and strikes, skipping any that are 0.

    Args:
        state: The current game state.

    Returns:
        A chip for each nonzero policy total, and a warning during a strike.
    """
    policies = state.policies
    chips = []
    stocking = total_policy_stocking_bonus(policies)
    if stocking != 0:
        chips.append(build_chip("Stocking bonus", percent_text(stocking),
                                "chip"))
    delivery = total_policy_delivery_bonus(policies)
    if delivery != 0:
        chips.append(build_chip("Delivery bonus", percent_text(delivery),
                                "chip"))
    loyalty_change = total_policy_loyalty_change(policies)
    if loyalty_change != 0:
        chips.append(build_chip("Loyalty target", str(round(loyalty_change)),
                                "chip"))
    strike_risk = total_strike_risk(policies)
    if strike_risk != 0:
        chips.append(build_chip("Strike risk / tick",
                                percent_text(strike_risk), "chip"))
    if state.strike_ticks_left > 0:
        chips.append(build_chip("Labor unrest",
                                strike_status_text(state.strike_ticks_left),
                                "chip warn"))
    return chips


assert_equal(build_policy_chips(make_new_state()), [])
assert_equal(len(build_policy_chips(make_striking_state(2))), 1)


def active_effect_lines(state: State) -> list[str]:
    """List each goods type sold, active policy, artifact, and research.

    Args:
        state: The current game state.

    Returns:
        One line of text per active bonus source.
    """
    lines = []
    for goods in state.goods_types:
        if goods.is_selling:
            lines.append(goods.emoji + " " + goods.name + ": "
                         + percent_text(goods_income_bonus(goods,
                                                           state.research))
                         + " income")
    for policy in state.policies:
        if policy.is_active:
            lines.append(policy.emoji + " " + policy.name + ": "
                         + describe_policy(policy))
    for artifact in state.owned_artifacts:
        if artifact.slot != NOT_PLACED:
            lines.append(artifact_label(artifact) + ": "
                         + artifact_percent_text(artifact_bonus(artifact))
                         + " income")
    for project in state.research:
        effect = describe_research_effect(project)
        if project.is_done and effect != "":
            lines.append(project.emoji + " " + project.name + ": " + effect)
    return lines


assert_equal(active_effect_lines(make_new_state()), [])
assert_equal(active_effect_lines(make_finished_research_state(0)),
             ["📉 Lean Procurement: +10% stocking"])
assert_equal(active_effect_lines(make_artifact_state()),
             ["A Alpha: +10.0% income"])
assert_equal(active_effect_lines(make_state_with_income_bonuses()),
             ["📺 Electronics: +15% income",
              "💬 Aggressive Upselling: +15% income, -8 loyalty target"])


def build_effect_tags(state: State) -> Div:
    """Build one small tag for each active goods type, policy, and artifact.

    Args:
        state: The current game state.

    Returns:
        A Div holding the tags (empty if nothing is active).
    """
    tags = []
    for line in active_effect_lines(state):
        tags.append(Span(line, classes="tag"))
    return Div(tags, classes="tags")


def build_live_numbers(state: State) -> list:
    """Build the numbers that change every tick; they contain no buttons.

    Args:
        state: The current game state.

    Returns:
        A list of the components inside the #live_numbers element.
    """
    chips = [build_chip("Money", format_money(state.money), "chip money")]
    if state.current_page != PAGE_COMPANY:
        return [Div(chips, classes="chips")]
    chips = chips + build_stat_chips(state) + build_policy_chips(state)
    return [Div(chips, classes="chips"), build_effect_tags(state)]


def nav_section(current_page: str) -> str:
    """Find which nav button a page belongs to.

    Args:
        current_page: One of the PAGE_ constants.

    Returns:
        PAGE_BUSINESS for the Research sub-page, otherwise the page itself.
    """
    if current_page == PAGE_RESEARCH:
        return PAGE_BUSINESS
    return current_page


assert_equal(nav_section(PAGE_RESEARCH), PAGE_BUSINESS)
assert_equal(nav_section(PAGE_CASINO), PAGE_CASINO)


def nav_label(row: list, available_research: int) -> str:
    """Build a nav button's text, adding the research badge to Business.

    Args:
        row: One row of NAV_ROWS.
        available_research: How many research projects are available.

    Returns:
        The button text, like "Business 🔬2".
    """
    if row[2] == PAGE_BUSINESS and available_research > 0:
        return row[0] + " 🔬" + str(available_research)
    return row[0]


assert_equal(nav_label(NAV_ROWS[1], 2), "Business 🔬2")
assert_equal(nav_label(NAV_ROWS[1], 0), "Business")
assert_equal(nav_label(NAV_ROWS[0], 2), "Company")


def build_nav(state: State) -> Div:
    """Build the navigation buttons, marking the page being shown.

    Args:
        state: The current game state.

    Returns:
        A Div holding one Button per main page.
    """
    available = count_available_research(state.research, state.total_earned)
    buttons = []
    for row in NAV_ROWS:
        label = nav_label(row, available)
        if row[2] == nav_section(state.current_page):
            buttons.append(Button(label, row[1], classes="current"))
        else:
            buttons.append(Button(label, row[1]))
    return Div(buttons, classes="nav")


def build_top_bar(state: State) -> Div:
    """Build the navigation bar and live numbers used by every page.

    Args:
        state: The current game state.

    Returns:
        A Div holding the company name, navigation, and live numbers.
    """
    return Div(
        Div(Header(state.company_name, 1), build_nav(state),
            classes="topbar-row"),
        # ADVANCED: A Div groups components. Its id is the name a Fragment
        # uses to find and replace just this part of the page.
        Div(build_live_numbers(state), id="live_numbers"),
        classes="topbar",
    )


def build_card_head(title: str, controls: list) -> Div:
    """Build a card's title row, with any controls on the right.

    Args:
        title: The card's title.
        controls: Components to show beside the title (may be empty).

    Returns:
        A Div holding the title and controls.
    """
    return Div([Header(title, 2)] + controls, classes="card-head")


def build_markup_controls(state: State) -> Div:
    """Build the markup display and its raise and lower buttons.

    Args:
        state: The current game state.

    Returns:
        A card holding the current markup and its buttons.
    """
    return Div(
        build_card_head("Pricing", []),
        Div("Markup x" + str(state.markup), classes="big-number"),
        Div("Each unit sells for "
            + format_money(calculate_sale_price(state.markup)),
            classes="muted"),
        Div(Button("▼ Lower", "lower_markup"),
            Button("▲ Raise", "raise_markup"), classes="button-row"),
        classes="card",
    )


def build_buy_amount_controls(state: State) -> Div:
    """Build the x1, x5, and x10 buttons, marking the chosen amount.

    Args:
        state: The current game state.

    Returns:
        A Div holding one button per choice.
    """
    buttons = []
    for amount in BUY_AMOUNTS:
        label = "x" + str(amount)
        # ADVANCED: An Argument makes a Button pass an extra value to its
        # route, so one route can serve many Buttons.
        arguments = [Argument("amount", amount)]
        if amount == state.buy_amount:
            buttons.append(Button(label, "set_buy_amount", arguments,
                                  classes="current"))
        else:
            buttons.append(Button(label, "set_buy_amount", arguments))
    return Div(buttons, classes="segmented")


def build_buy_action(item: BuyItem, item_index: int, state: State) -> Div:
    """Build the Buy button, or a note if a one-time item is bought.

    The button is shown even when the player can't afford the batch;
    buy_item then refuses the purchase. Keeping the button means a tick
    never has to redraw it just because money went up or down.

    Args:
        item: The item this row is for.
        item_index: The item's position in state.buy_items.
        state: The current game state.

    Returns:
        A Div holding a Buy button or a short message.
    """
    quantity = purchase_quantity(item, state.buy_amount)
    if is_sold_out(item):
        return Div("Purchased", classes="muted")
    price_text = format_money(batch_cost(item, quantity))
    return Div(Button("Buy x" + str(quantity) + " for " + price_text,
                      "buy_item", [Argument("item_index", item_index)]))


def build_buy_list(state: State) -> Div:
    """Build a row for each item the player has unlocked.

    Args:
        state: The current game state.

    Returns:
        A card holding the buy amount buttons and the visible item rows.
    """
    rows = [build_card_head("Buy List", [build_buy_amount_controls(state)])]
    for item_index, item in enumerate(state.buy_items):
        if is_item_visible(item, state.total_earned, state.research):
            rows.append(Div(
                Span(item.emoji, classes="emoji"),
                Div(Div(item.name, classes="item-name"),
                    Div(describe_effect(item) + " · owned: "
                        + str(item.owned), classes="muted")),
                build_buy_action(item, item_index, state),
                classes="buy-row",
            ))
    return Div(rows, classes="card")


def build_news_feed(state: State) -> Div:
    """Build the World News section.

    Args:
        state: The current game state.

    Returns:
        A card holding the list of headlines.
    """
    return Div(build_card_head("World News", []),
               BulletedList(state.news_feed), classes="card")


def build_live_content(state: State) -> list:
    """Build everything a full tick refresh replaces on the current page.

    Args:
        state: The current game state.

    Returns:
        A list of the components inside the live area.
    """
    if state.current_page == PAGE_BUSINESS:
        return [build_top_bar(state)]
    if state.current_page == PAGE_ORGANIZE:
        return [build_top_bar(state)]
    if state.current_page == PAGE_CASINO:
        return [build_top_bar(state)]
    if state.current_page == PAGE_ARTIFACTS:
        return [build_top_bar(state),
                Div(build_expedition_controls(state), classes="page")]
    if state.current_page == PAGE_RESEARCH:
        return [build_top_bar(state),
                Div(build_research_list(state),
                    build_completed_research(state),
                    classes="page two-col")]
    return [
        build_top_bar(state),
        Div(Div(build_buy_list(state)),
            Div(build_markup_controls(state), build_news_feed(state)),
            classes="page dashboard"),
    ]


def build_company_content(state: State) -> list:
    """Build the company page's content, without any Clock.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    return [Div(build_live_content(state), id="live_area")]


def build_goods_form(state: State) -> Div:
    """Build one CheckBox per goods type and the button that saves them.

    Args:
        state: The current game state.

    Returns:
        A card holding the goods choices.
    """
    rows = [build_card_head("Goods to Sell", [])]
    for goods in state.goods_types:
        if is_requirement_met(goods.required_research, state.research):
            rows.append(Div(
                CheckBox(goods.input_name, goods.is_selling),
                Span(goods.emoji + " " + goods.name),
                Span(percent_text(goods_income_bonus(goods, state.research))
                     + " income", classes="muted"),
                classes="check-row",
            ))
    rows.append(Button("Save Goods", "save_goods"))
    return Div(rows, classes="card")


def policy_label(policy: Policy, items: list[BuyItem],
                 research: list[Research]) -> str:
    """Build the text shown beside a policy's CheckBox.

    Args:
        policy: The policy to label.
        items: The player's buy items.
        research: Every research project.

    Returns:
        The policy's effects, or a note saying what unlocks it.
    """
    text = policy.emoji + " " + policy.name + " - " + describe_policy(policy)
    if is_policy_unlocked(policy, items, research):
        return text
    if not is_unlock_item_owned(policy, items):
        return ("🔒 " + text
                + " (locked: buy Next Generation Corporate Organization)")
    return ("🔒 " + text + " (locked: research " + policy.required_research
            + ")")


assert_equal(policy_label(make_test_policy(False), [], [])[:6], "T Test")
assert_equal(policy_label(make_locked_policy(), [make_one_time_item(0)],
                          [])[:1], "🔒")
assert_equal("(locked: research Labor Relations Consultancy)"
             in policy_label(make_new_state().policies[3], [],
                             make_new_state().research), True)


def build_policy_form(state: State) -> Div:
    """Build one CheckBox per policy and the button that saves them.

    Args:
        state: The current game state.

    Returns:
        A card holding the policy choices.
    """
    rows = [build_card_head("Corporate Policies", [])]
    for policy in state.policies:
        rows.append(Div(
            CheckBox(policy.input_name, policy.is_active),
            Span(policy_label(policy, state.buy_items, state.research)),
            classes="check-row",
        ))
    rows.append(Button("Save Policies", "save_policies"))
    return Div(rows, classes="card")


def build_business_content(state: State) -> list:
    """Build the Business page's content.

    The forms sit outside the live area so ticks can't reset the
    CheckBoxes while the player is choosing.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    return [
        Div(build_live_content(state), id="live_area"),
        Div(build_research_link(), classes="page"),
        Div(build_goods_form(state), build_policy_form(state),
            classes="page two-col"),
    ]


def build_research_link() -> Div:
    """Build the Business page card that opens the Research page.

    Returns:
        A card holding a short note and the Research Lab button.
    """
    return Div(
        build_card_head("Research", [Button("🔬 Open Research Lab",
                                            "research_page")]),
        Div("One-time projects that boost the company or unlock new "
            + "goods, policies, and equipment.", classes="muted"),
        classes="card",
    )


def build_research_row(project: Research, research_index: int,
                       state: State) -> Div:
    """Build one available research project and its Research button.

    The button stays even when the player can't afford it; buy_research
    refuses the purchase, so money changes never redraw the button.

    Args:
        project: The research to show.
        research_index: Its position in state.research.
        state: The current game state.

    Returns:
        A buy row for the project.
    """
    return Div(
        Span(project.emoji, classes="emoji"),
        Div(Div(project.name, classes="item-name"),
            Div(project.description, classes="muted"),
            Div(research_summary(project, state), classes="muted")),
        Button("Research for " + format_money(project.cost), "buy_research",
               [Argument("research_index", research_index)]),
        classes="buy-row",
    )


def build_research_list(state: State) -> Div:
    """Build the card listing every research project available now.

    Args:
        state: The current game state.

    Returns:
        A card with one row per available project, or a short note.
    """
    rows = [build_card_head("Research Lab", [Button("← Business",
                                                    "business_page")])]
    for research_index, project in enumerate(state.research):
        if is_research_available(project, state.research, state.total_earned):
            rows.append(build_research_row(project, research_index, state))
    if len(rows) == 1:
        rows.append(Div("No research available. Earn more to attract "
                        + "consultants.", classes="muted"))
    return Div(rows, classes="card")


def build_completed_research(state: State) -> Div:
    """Build the card listing every completed research project.

    Args:
        state: The current game state.

    Returns:
        A card with one line per completed project, or a short note.
    """
    lines = []
    for project in state.research:
        if project.is_done:
            lines.append(project.emoji + " " + project.name)
    if len(lines) == 0:
        return Div(build_card_head("Completed", []),
                   Div("Nothing researched yet.", classes="muted"),
                   classes="card")
    return Div(build_card_head("Completed", []), BulletedList(lines),
               classes="card")


def build_research_content(state: State) -> list:
    """Build the Research page's content.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    return [Div(build_live_content(state), id="live_area")]


def build_expedition_action(state: State, count: int) -> Button:
    """Build one expedition button showing its price.

    Like the Buy buttons, it is shown even when the player can't afford
    the batch (run_expedition then refuses), so ticks never redraw it.

    Args:
        state: The current game state.
        count: How many expeditions this button buys.

    Returns:
        The button for this batch size.
    """
    price = expedition_batch_cost(state.expeditions_bought, count)
    return Button("X" + str(count) + " for " + format_money(price),
                  "run_expedition", [Argument("count", count)])


def build_expedition_controls(state: State) -> Div:
    """Build the expedition buttons, one for each batch size.

    Args:
        state: The current game state.

    Returns:
        A card holding the expedition buttons.
    """
    buttons = []
    for count in EXPEDITION_AMOUNTS:
        buttons.append(build_expedition_action(state, count))
    return Div(build_card_head("Expeditions", []),
               Div(buttons, classes="button-row expedition"),
               classes="card")


def build_grid_rows(owned_artifacts: list[Artifact]) -> list[list[str]]:
    """Lay out the artifact grid as a 2D list of cell text.

    Args:
        owned_artifacts: Every artifact the player owns.

    Returns:
        GRID_ROWS rows, each holding GRID_COLUMNS labels.
    """
    rows = []
    for row_number in range(GRID_ROWS):
        cells = []
        for column in range(GRID_COLUMNS):
            slot = row_number * GRID_COLUMNS + column
            cells.append(slot_choice(owned_artifacts, slot))
        rows.append(cells)
    return rows


assert_equal(len(build_grid_rows([])), GRID_ROWS)
assert_equal(len(build_grid_rows([])[0]), GRID_COLUMNS)
# Slot 7 is the second row, second column.
assert_equal(build_grid_rows([make_test_artifact("Alpha", 0.1, 1, 7)])[1][1],
             "A Alpha")


def describe_artifact(artifact: Artifact) -> str:
    """Describe an owned artifact in one line.

    Args:
        artifact: The artifact to describe.

    Returns:
        Its label, rarity, copies, bonus, and flavor text.
    """
    return (artifact_label(artifact) + " (" + artifact.rarity + ") x"
            + str(artifact.copies) + ": "
            + artifact_percent_text(artifact_bonus(artifact))
            + " income when placed. " + artifact.description)


assert_equal(describe_artifact(make_test_artifact("Alpha", 0.1, 1, 0)),
             "A Alpha (common) x1: +10.0% income when placed. Test")


def build_owned_artifact_list(state: State) -> Div:
    """Build the list of every artifact the player owns.

    Args:
        state: The current game state.

    Returns:
        A card holding the artifact descriptions.
    """
    head = build_card_head("Owned Artifacts", [])
    if len(state.owned_artifacts) == 0:
        return Div(head, Div("Nothing yet. Fund an expedition!",
                             classes="muted"), classes="card")
    lines = []
    for artifact in state.owned_artifacts:
        lines.append(describe_artifact(artifact))
    return Div(head, BulletedList(lines), classes="card")


def build_expedition_finds(state: State) -> Div:
    """Build the list of what the latest expedition batch found.

    Args:
        state: The current game state.

    Returns:
        A card holding the finds, or an empty Div if there are none.
    """
    if len(state.last_expedition_finds) == 0:
        return Div()
    return Div(build_card_head("Latest Finds", []),
               BulletedList(state.last_expedition_finds), classes="card")


def build_artifacts_content(state: State) -> list:
    """Build the Artifacts page's content.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    grid_card = Div(
        build_card_head("Artifact Grid",
                        [Button("Organize", "organize_page")]),
        Table(build_grid_rows(state.owned_artifacts)),
        classes="card artifact-grid",
    )
    return [
        Div(build_live_content(state), id="live_area"),
        Div(build_expedition_finds(state), grid_card,
            build_owned_artifact_list(state), classes="page"),
    ]


def build_organize_form(state: State) -> Div:
    """Build one SelectBox for each slot in the grid.

    Each SelectBox name must match a save_artifact_grid parameter. The
    slots are laid out like the grid itself (6 across, 2 down).

    Args:
        state: The current game state.

    Returns:
        A card holding the SelectBoxes and the save button.
    """
    options = slot_options(state.owned_artifacts)
    slots = []
    for slot in range(GRID_SLOT_COUNT):
        slot_number = str(slot + 1)
        slots.append(Div(
            Div("Slot " + slot_number, classes="muted"),
            SelectBox("slot_" + slot_number, options,
                      slot_choice(state.owned_artifacts, slot)),
        ))
    return Div(
        build_card_head("Organize Artifacts",
                        [Button("Save Layout", "save_artifact_grid")]),
        Div(slots, classes="slot-grid"),
        classes="card",
    )


def build_organize_content(state: State) -> list:
    """Build the Organize page's content.

    The form sits outside the live area so ticks can't reset a SelectBox
    while the player is choosing.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    return [
        Div(build_live_content(state), id="live_area"),
        Div(build_organize_form(state), classes="page"),
    ]


def describe_typing_result(accuracy: float, speed_wpm: float, bet: int,
                           payout: float) -> str:
    """Write the message shown after a typing test.

    Args:
        accuracy: The fraction of characters correct.
        speed_wpm: The typing speed in words per minute.
        bet: The money that was bet.
        payout: The money won.

    Returns:
        One line summarizing the round.
    """
    return ("Accuracy " + str(round(accuracy * 100)) + "%, "
            + str(round(speed_wpm)) + " WPM. Bet " + format_money(bet)
            + ", paid " + format_money(payout) + ".")


assert_equal(describe_typing_result(0.5, 30.0, 100, 150.0),
             "Accuracy 50%, 30 WPM. Bet Ŧ100.00, paid Ŧ150.00.")


def build_casino_setup_form() -> Div:
    """Build the form that starts a typing test.

    Returns:
        A Div holding the difficulty and bet inputs and the start button.
    """
    cap_text = str(round(CASINO_MAX_BET_FRACTION * 100))
    return Div(
        build_card_head("Typing Test", []),
        Div("Difficulty",
            SelectBox("difficulty", DIFFICULTY_OPTIONS, DIFFICULTY_EASY),
            classes="form-row"),
        Div("Bet (up to " + cap_text + "% of your money)",
            TextBox("bet", ""), classes="form-row"),
        Button("Start Typing", "start_typing_round"),
    )


def build_typing_form(typing_round: TypingRound) -> Div:
    """Build the prompt and the box the player types into.

    Args:
        typing_round: The round in progress.

    Returns:
        A Div holding the prompt, the TextArea, and the submit button.
    """
    return Div(
        build_card_head("Type this exactly", []),
        Div(typing_round.prompt, classes="prompt"),
        TextArea("typed_text", ""),
        Button("Submit", "submit_typing_round"),
    )


def build_casino_content(state: State) -> list:
    """Build the Casino page's content.

    The forms sit outside the live area so ticks can't erase typing.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    if state.typing_round.prompt == "":
        form = build_casino_setup_form()
    else:
        form = build_typing_form(state.typing_round)
    return [
        Div(build_live_content(state), id="live_area"),
        Div(Div(Div(state.last_casino_result, classes="result"), form,
                classes="card narrow"), classes="page"),
    ]


def build_start_content(state: State) -> list:
    """Build the start page, removing any clock from an earlier game.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    return [
        # ADVANCED: RemovePersistent stops the persistent Clock with this id,
        # so a new game never has two clocks ticking at once.
        RemovePersistent(GAME_CLOCK_ID),
        Div(Div(
            Header("Untitled Warehouse Inc.", 1),
            Div("Every empire starts with a warehouse. What is yours called?",
                classes="muted"),
            TextBox("company_name", state.company_name),
            Button("Open for Business", "start_game"),
            classes="card start",
        ), classes="page"),
    ]


def build_game_clock(state: State) -> Clock:
    """Build the game's one persistent Clock.

    Args:
        state: The current game state.

    Returns:
        A hidden Clock that calls the tick route.
    """
    # ADVANCED: A Clock calls a route repeatedly. persistent=True keeps it
    # running across page changes, so only start_game should ever add it.
    return Clock(tick_interval(state), "tick", show=False, persistent=True,
                 id=GAME_CLOCK_ID)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@route
def index(state: State) -> Page:
    """Show the start page where the player names their company.

    Args:
        state: The current game state.

    Returns:
        The start page.
    """
    return Page(state, build_start_content(state))


assert_equal(index(make_new_state()),
             Page(make_new_state(), build_start_content(make_new_state())))


@route
def start_game(state: State, company_name: str) -> Page:
    """Save the company name, start the Clock, and show the company page.

    Args:
        state: The current game state.
        company_name: The name typed into the TextBox.

    Returns:
        The company page, including the game's Clock.
    """
    state.company_name = clean_company_name(company_name)
    return Page(state, [build_game_clock(state)]
                + build_company_content(state))


assert_equal(start_game(make_new_state(), "  Boxes "),
             Page(expected_after_named_start(),
                  [build_game_clock(expected_after_named_start())]
                  + build_company_content(expected_after_named_start())))


@route
def company_page(state: State) -> Page:
    """Show the main company dashboard.

    Args:
        state: The current game state.

    Returns:
        The company page, without a Clock.
    """
    state.current_page = PAGE_COMPANY
    return Page(state, build_company_content(state))


assert_equal(company_page(make_new_state()),
             make_expected_company_page(make_new_state()))


@route
def business_page(state: State) -> Page:
    """Show the goods and policy choices.

    Args:
        state: The current game state.

    Returns:
        The Business page.
    """
    state.current_page = PAGE_BUSINESS
    return Page(state, build_business_content(state))


assert_equal(business_page(make_new_state()),
             make_expected_business_page(make_business_state()))


# ADVANCED: "= False" gives a parameter a default value. A goods type that
# is still locked has no CheckBox on the page, so the browser sends no value
# for it, and Drafter uses the default instead.
@route
def save_goods(state: State, sell_household: bool, sell_canned_food: bool,
               sell_electronics: bool, sell_war_supplies: bool,
               sell_imported_luxuries: bool = False) -> Page:
    """Save which goods types the company sells.

    Args:
        state: The current game state.
        sell_household: Whether Household Goods is checked.
        sell_canned_food: Whether Canned Food is checked.
        sell_electronics: Whether Electronics is checked.
        sell_war_supplies: Whether War Supplies is checked.
        sell_imported_luxuries: Whether Imported Luxuries is checked.

    Returns:
        The refreshed Business page.
    """
    set_goods_choices(state.goods_types,
                      [sell_household, sell_canned_food, sell_electronics,
                       sell_war_supplies, sell_imported_luxuries],
                      state.research)
    state.sells_war_supplies = sell_war_supplies
    return business_page(state)


assert_equal(save_goods(make_new_state(), False, False, False, True),
             make_expected_business_page(
                 expected_after_selling_war_supplies()))
# Imported Luxuries stays unsold until Import Licenses is researched.
assert_equal(save_goods(make_new_state(), False, False, False, False, True),
             make_expected_business_page(make_business_state()))
assert_equal(save_goods(make_finished_research_state(4), False, False, False,
                        False, True),
             make_expected_business_page(expected_after_luxuries()))


# ADVANCED: "= False" is a default value, as in save_goods, in case the
# page ever leaves this CheckBox out.
@route
def save_policies(state: State, unpaid_overtime: bool,
                  aggressive_upselling: bool, route_quotas: bool,
                  gig_reclassification: bool = False) -> Page:
    """Save which corporate policies are active.

    Args:
        state: The current game state.
        unpaid_overtime: Whether Unpaid Overtime is checked.
        aggressive_upselling: Whether Aggressive Upselling is checked.
        route_quotas: Whether Algorithmic Route Quotas is checked.
        gig_reclassification: Whether Gig Worker Reclassification is
            checked.

    Returns:
        The refreshed Business page.
    """
    set_policy_choices(state.policies,
                       [unpaid_overtime, aggressive_upselling, route_quotas,
                        gig_reclassification],
                       state.buy_items, state.research)
    return business_page(state)


assert_equal(save_policies(make_new_state(), True, False, False),
             make_expected_business_page(expected_after_overtime()))
# The locked policy stays off until the unlock item is bought.
assert_equal(save_policies(make_new_state(), False, False, True),
             make_expected_business_page(make_business_state()))
assert_equal(save_policies(make_unlocked_state(), False, False, True),
             make_expected_business_page(expected_after_quotas()))
# Gig Worker Reclassification needs Labor Relations Consultancy first.
assert_equal(save_policies(make_new_state(), False, False, False, True),
             make_expected_business_page(make_business_state()))
assert_equal(save_policies(make_finished_research_state(5), False, False,
                           False, True),
             make_expected_business_page(expected_after_gig_policy()))


@route
def research_page(state: State) -> Page:
    """Show the Research page, a sub-page of Business.

    Args:
        state: The current game state.

    Returns:
        The Research page.
    """
    state.current_page = PAGE_RESEARCH
    return Page(state, build_research_content(state))


assert_equal(research_page(make_research_state()),
             make_expected_research_page(make_research_state()))


@route
def buy_research(state: State, research_index: int) -> Page:
    """Complete a research project if it is available and affordable.

    Args:
        state: The current game state.
        research_index: The project's position in state.research.

    Returns:
        The refreshed Research page.
    """
    if can_buy_research(state, research_index):
        complete_research(state, research_index)
    return research_page(state)


assert_equal(buy_research(make_research_state(), 0),
             make_expected_research_page(expected_after_lean_procurement()))
# Too poor: nothing changes.
assert_equal(buy_research(make_poor_research_state(), 0),
             make_expected_research_page(make_poor_research_state()))
# Not unlocked yet (Boxly needs 15000 earned): nothing changes.
assert_equal(buy_research(make_research_state(), 7),
             make_expected_research_page(make_research_state()))


@route
def artifacts_page(state: State) -> Page:
    """Show the expeditions, the artifact grid, and owned artifacts.

    Args:
        state: The current game state.

    Returns:
        The Artifacts page.
    """
    state.current_page = PAGE_ARTIFACTS
    return Page(state, build_artifacts_content(state))


assert_equal(artifacts_page(make_artifact_state()),
             make_expected_artifacts_page(make_artifacts_view_state()))


@route
def organize_page(state: State) -> Page:
    """Show one SelectBox per grid slot.

    Args:
        state: The current game state.

    Returns:
        The Organize page.
    """
    state.current_page = PAGE_ORGANIZE
    return Page(state, build_organize_content(state))


assert_equal(organize_page(make_artifact_state()),
             Page(make_organize_view_state(),
                  build_organize_content(make_organize_view_state())))


@route
def run_expedition(state: State, count: int) -> Page:
    """Pay for a batch of expeditions and collect what they find.

    Uses randomness when the batch is bought, so only the "can't afford
    it" path, which rolls nothing, has a unit test.

    Args:
        state: The current game state.
        count: How many expeditions to buy.

    Returns:
        The refreshed Artifacts page.
    """
    if can_afford_expedition(state, count):
        state.money = state.money - expedition_batch_cost(
            state.expeditions_bought, count)
        state.expeditions_bought = state.expeditions_bought + count
        collect_expedition_finds(state, count)
    return artifacts_page(state)


# The artifact test State has no money for 100 expeditions: nothing changes.
assert_equal(run_expedition(make_artifact_state(), 100),
             make_expected_artifacts_page(make_artifacts_view_state()))


@route
def save_artifact_grid(state: State, slot_1: str, slot_2: str, slot_3: str,
                       slot_4: str, slot_5: str, slot_6: str, slot_7: str,
                       slot_8: str, slot_9: str, slot_10: str, slot_11: str,
                       slot_12: str) -> Page:
    """Save which owned artifact sits in each grid slot.

    Args:
        state: The current game state.
        slot_1: The label chosen for slot 1.
        slot_2: The label chosen for slot 2.
        slot_3: The label chosen for slot 3.
        slot_4: The label chosen for slot 4.
        slot_5: The label chosen for slot 5.
        slot_6: The label chosen for slot 6.
        slot_7: The label chosen for slot 7.
        slot_8: The label chosen for slot 8.
        slot_9: The label chosen for slot 9.
        slot_10: The label chosen for slot 10.
        slot_11: The label chosen for slot 11.
        slot_12: The label chosen for slot 12.

    Returns:
        The refreshed Artifacts page.
    """
    place_artifacts(state.owned_artifacts,
                    [slot_1, slot_2, slot_3, slot_4, slot_5, slot_6, slot_7,
                     slot_8, slot_9, slot_10, slot_11, slot_12])
    return artifacts_page(state)


assert_equal(save_artifact_grid(make_artifact_state(), EMPTY_SLOT, EMPTY_SLOT,
                                EMPTY_SLOT, EMPTY_SLOT, EMPTY_SLOT, EMPTY_SLOT,
                                EMPTY_SLOT, EMPTY_SLOT, EMPTY_SLOT, EMPTY_SLOT,
                                EMPTY_SLOT, "A Beta"),
             make_expected_artifacts_page(expected_after_moving_beta()))


@route
def casino_page(state: State) -> Page:
    """Show the typing test's setup form or the round in progress.

    Args:
        state: The current game state.

    Returns:
        The Casino page.
    """
    state.current_page = PAGE_CASINO
    return Page(state, build_casino_content(state))


assert_equal(casino_page(make_new_state()),
             make_expected_casino_page(make_casino_view_state("")))
# Coming back during a round must show that same round.
assert_equal(casino_page(make_typing_state()),
             make_expected_casino_page(make_typing_state()))


@route
def start_typing_round(state: State, difficulty: str, bet: str) -> Page:
    """Take the bet and begin a typing test with a random prompt.

    Uses randomness when the bet is accepted, so only the rejected bet
    path, which rolls nothing, has a unit test.

    Args:
        state: The current game state.
        difficulty: The chosen difficulty.
        bet: The text from the bet box.

    Returns:
        The refreshed Casino page.
    """
    bet_amount = parse_bet(bet)
    if state.typing_round.prompt != "":
        return casino_page(state)
    if can_place_bet(bet_amount, state.money, state.goods_in_stock):
        state.money = state.money - bet_amount
        state.typing_round = TypingRound(roll_prompt(difficulty), difficulty,
                                         bet_amount, state.tick_count)
        state.last_casino_result = ""
    else:
        state.last_casino_result = INVALID_BET_MESSAGE
    return casino_page(state)


assert_equal(start_typing_round(make_new_state(), DIFFICULTY_EASY, "abc"),
             make_expected_casino_page(
                 make_casino_view_state(INVALID_BET_MESSAGE)))
# 401 is over 80% of the starting 500.
assert_equal(start_typing_round(make_new_state(), DIFFICULTY_EASY, "401"),
             make_expected_casino_page(
                 make_casino_view_state(INVALID_BET_MESSAGE)))
# A second start during a round changes nothing.
assert_equal(start_typing_round(make_typing_state(), DIFFICULTY_HARD, "50"),
             make_expected_casino_page(make_typing_state()))


@route
def submit_typing_round(state: State, typed_text: str) -> Page:
    """Score the typing test and pay out the winnings.

    Args:
        state: The current game state.
        typed_text: What the player typed.

    Returns:
        The refreshed Casino page.
    """
    if state.typing_round.prompt != "":
        settle_typing_round(state, typed_text)
    return casino_page(state)


# 5 characters in 3 ticks (2.001 seconds) is about 30 WPM, the x1 tier.
assert_equal(submit_typing_round(make_typing_state(), "hello"),
             make_expected_casino_page(expected_after_typing(
                 150.0, "Accuracy 100%, 30 WPM. Bet Ŧ100.00, paid Ŧ150.00.")))
assert_equal(submit_typing_round(make_typing_state(), "nope"),
             make_expected_casino_page(expected_after_typing(
                 0.0, "Accuracy 0%, 24 WPM. Bet Ŧ100.00, paid Ŧ0.00.")))
# With no round running, a stray submit changes nothing.
assert_equal(submit_typing_round(make_casino_view_state(""), "hello"),
             make_expected_casino_page(make_casino_view_state("")))


@route
def set_buy_amount(state: State, amount: int) -> Page:
    """Choose how many units one Buy click purchases.

    Args:
        state: The current game state.
        amount: The new buy amount.

    Returns:
        The refreshed company page.
    """
    state.buy_amount = amount
    return company_page(state)


assert_equal(set_buy_amount(make_new_state(), 10),
             make_expected_company_page(expected_with_buy_amount(10)))


@route
def buy_item(state: State, item_index: int) -> Page:
    """Buy the current amount of an item if the whole batch is affordable.

    Args:
        state: The current game state.
        item_index: The item's position in state.buy_items.

    Returns:
        The refreshed company page.
    """
    item = state.buy_items[item_index]
    quantity = purchase_quantity(item, state.buy_amount)
    if can_afford(item, quantity, state.money, state.goods_in_stock):
        state.money = state.money - batch_cost(item, quantity)
        item.owned = item.owned + quantity
    return company_page(state)


assert_equal(buy_item(make_new_state(), 1),
             make_expected_company_page(expected_after_buying_van()))
assert_equal(buy_item(make_broke_state(), 1),
             make_expected_company_page(make_broke_state()))
assert_equal(buy_item(make_nearly_stranded_state(), 1),
             make_expected_company_page(make_nearly_stranded_state()))


@route
def raise_markup(state: State) -> Page:
    """Raise the markup by one step.

    Args:
        state: The current game state.

    Returns:
        The refreshed company page.
    """
    state.markup = change_markup(state.markup, MARKUP_STEP)
    return company_page(state)


assert_equal(raise_markup(make_new_state()),
             make_expected_company_page(expected_with_markup(1.6)))


@route
def lower_markup(state: State) -> Page:
    """Lower the markup by one step.

    Args:
        state: The current game state.

    Returns:
        The refreshed company page.
    """
    state.markup = change_markup(state.markup, -MARKUP_STEP)
    return company_page(state)


assert_equal(lower_markup(make_new_state()),
             make_expected_company_page(expected_with_markup(1.4)))


@route
def tick(state: State) -> Fragment:
    """Run one game tick and refresh only the live part of the page.

    Uses randomness through run_strikes, but with no strike risk (as in a
    new game) the result is predictable, so the tests use zero-risk States.

    Args:
        state: The current game state.

    Returns:
        A Fragment that replaces #live_numbers or, if the buttons or news
        changed, all of #live_area.
    """
    run_strikes(state)
    run_stocking(state)
    run_selling(state)
    run_loyalty_drift(state)
    state.tick_count = state.tick_count + 1
    new_signature = controls_signature(state)
    # ADVANCED: A Fragment replaces one element instead of rebuilding the
    # whole page, which keeps the Clock from being restarted. Replacing a
    # button mid-click loses the click, so most ticks target only the
    # button-free #live_numbers. #live_area is redrawn when buttons change.
    if new_signature == state.controls_signature:
        return Fragment(state, build_live_numbers(state),
                        target="#live_numbers")
    state.controls_signature = new_signature
    return Fragment(state, build_live_content(state), target="#live_area")


assert_equal(tick(make_new_state()),
             Fragment(expected_after_first_tick(),
                      build_live_content(expected_after_first_tick()),
                      target="#live_area"))


# When no button changes, the tick must leave the buttons alone.
assert_equal(tick(make_settled_state()),
             Fragment(expected_after_first_tick(),
                      build_live_numbers(expected_after_first_tick()),
                      target="#live_numbers"))


# On the Business page, the tick must refresh only the top bar.
assert_equal(tick(make_business_state()),
             Fragment(expected_business_tick(),
                      [build_top_bar(expected_business_tick())],
                      target="#live_area"))

start_server(make_new_state())
