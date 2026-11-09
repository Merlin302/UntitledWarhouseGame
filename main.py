from dataclasses import dataclass
from drafter import *


hide_debug_information()
set_website_title("Untitled Warehouse Inc.")
set_website_framed(False)
# ADVANCED: Stops Drafter copying each route into the URL. Otherwise a browser
# refresh would rerun the "tick" route on a blank page and crash.
set_browser_history(False)
set_site_information(
    author="TODO: your name",
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
TICK_INTERVAL_MS = 3000

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

# Each row: name, emoji, base cost, effect kind, effect amount,
# lifetime earnings needed to appear, and whether it is a one-time buy.
STARTING_ITEM_ROWS = [
    ["Procurement Agent", "🧑‍💼", 100.0, EFFECT_STOCKING, 5, 0.0, False],
    ["Fordov Delivery Van", "🚐", 50.0, EFFECT_DELIVERY, 1, 0.0, False],
    ["Short Form Marketing Campaign", "📱", 150.0, EFFECT_LOYALTY, 2, 200.0,
     False],
    ["Warehouse Expansion", "🏗️", 200.0, EFFECT_CAPACITY, 50, 500.0, False],
    ["Next Generation Corporate Organization", "🏢", 2000.0, EFFECT_UNLOCK, 1,
     1500.0, True],
]

STARTING_NEWS = [
    "Local warehouse opens; neighbors report increased forklift noise.",
    "Economists agree that boxes remain popular.",
    "Front line reported to be 'somewhere over there'.",
]


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
        owned: How many units the player has bought.
    """
    name: str
    emoji: str
    base_cost: float
    effect_kind: str
    effect_amount: int
    unlock_at_earned: float
    is_one_time: bool
    owned: int


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
        news_feed: Recent World News headlines.
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


def make_starting_items() -> list[BuyItem]:
    """Build fresh BuyItems so the global rows are never modified."""
    items = []
    for row in STARTING_ITEM_ROWS:
        items.append(BuyItem(row[0], row[1], row[2], row[3], row[4], row[5],
                             row[6], 0))
    return items


def make_new_state() -> State:
    """Build the State that a brand new game starts with."""
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
    )


# ---------------------------------------------------------------------------
# Economy: pure helper functions
# ---------------------------------------------------------------------------

def tick_interval(state: State) -> int:
    """Return the milliseconds between ticks (upgrades will change this)."""
    return TICK_INTERVAL_MS


def total_item_effect(items: list[BuyItem], effect_kind: str) -> int:
    """Add up the effect of every owned item of the given kind."""
    total = 0
    for item in items:
        if item.effect_kind == effect_kind:
            total = total + item.owned * item.effect_amount
    return total


def calculate_stocking_rate(items: list[BuyItem]) -> int:
    """Return how many goods can be bought per tick."""
    return BASE_STOCKING_RATE + total_item_effect(items, EFFECT_STOCKING)


def calculate_delivery_capacity(items: list[BuyItem]) -> int:
    """Return how many goods can be delivered per tick."""
    return BASE_DELIVERY_CAPACITY + total_item_effect(items, EFFECT_DELIVERY)


def calculate_warehouse_capacity(items: list[BuyItem]) -> int:
    """Return how many goods the warehouse can hold."""
    return BASE_WAREHOUSE_CAPACITY + total_item_effect(items, EFFECT_CAPACITY)


def calculate_units_stocked(stocking_rate: int, goods_in_stock: int,
                            warehouse_capacity: int, money: float) -> int:
    """Return units bought, limited by rate, free space, and money."""
    free_space = warehouse_capacity - goods_in_stock
    affordable_units = int(money // UNIT_COST)
    return min(stocking_rate, free_space, affordable_units)


def calculate_demand(loyalty: float) -> int:
    """Return how many units customers want to buy this tick."""
    return int(MARKET_SIZE * loyalty // 100)


def calculate_units_sold(goods_in_stock: int, delivery_capacity: int,
                         demand: int) -> int:
    """Return units sold: the smallest of stock, delivery, and demand."""
    return min(goods_in_stock, delivery_capacity, demand)


def calculate_sale_price(markup: float) -> float:
    """Return the price customers pay for one unit."""
    return UNIT_COST * markup


def calculate_total_bonus(state: State) -> float:
    """Return the income bonus (goods, artifacts, policies add to it later)."""
    return 0.0


def calculate_income(units_sold: int, sale_price: float,
                     total_bonus: float) -> float:
    """Return the money earned from a tick's sales."""
    return units_sold * sale_price * (1 + total_bonus)


def clamp_loyalty(loyalty: float) -> float:
    """Keep a loyalty value between MIN_LOYALTY and MAX_LOYALTY."""
    if loyalty < MIN_LOYALTY:
        return MIN_LOYALTY
    if loyalty > MAX_LOYALTY:
        return MAX_LOYALTY
    return loyalty


def calculate_loyalty_target(markup: float, items: list[BuyItem]) -> float:
    """Return the loyalty that the current markup and marketing lead to."""
    marketing = total_item_effect(items, EFFECT_LOYALTY)
    penalty = (markup - MIN_MARKUP) * MARKUP_LOYALTY_PENALTY
    return clamp_loyalty(BASE_LOYALTY_TARGET + marketing - penalty)


def drift_loyalty(loyalty: float, target: float) -> float:
    """Move loyalty part of the way toward its target."""
    return clamp_loyalty(loyalty + (target - loyalty) * LOYALTY_DRIFT_FRACTION)


def change_markup(markup: float, change: float) -> float:
    """Apply a markup change, rounded and kept within the allowed range."""
    new_markup = round(markup + change, 2)
    if new_markup < MIN_MARKUP:
        return MIN_MARKUP
    if new_markup > MAX_MARKUP:
        return MAX_MARKUP
    return new_markup


def clean_company_name(company_name: str) -> str:
    """Strip spaces from a name, using the default if it is blank."""
    cleaned_name = company_name.strip()
    if not cleaned_name:
        return DEFAULT_COMPANY_NAME
    return cleaned_name


def run_stocking(state: State) -> None:
    """Buy goods into the warehouse and pay for them."""
    units = calculate_units_stocked(
        calculate_stocking_rate(state.buy_items),
        state.goods_in_stock,
        calculate_warehouse_capacity(state.buy_items),
        state.money,
    )
    state.goods_in_stock = state.goods_in_stock + units
    state.money = state.money - units * UNIT_COST
    state.goods_stocked_last_tick = units


def run_selling(state: State) -> None:
    """Sell goods to customers and collect the income."""
    units = calculate_units_sold(
        state.goods_in_stock,
        calculate_delivery_capacity(state.buy_items),
        calculate_demand(state.loyalty),
    )
    income = calculate_income(units, calculate_sale_price(state.markup),
                              calculate_total_bonus(state))
    state.goods_in_stock = state.goods_in_stock - units
    state.money = state.money + income
    state.total_earned = state.total_earned + income
    state.goods_sold_last_tick = units
    state.income_last_tick = income


def run_loyalty_drift(state: State) -> None:
    """Move customer loyalty toward its target."""
    target = calculate_loyalty_target(state.markup, state.buy_items)
    state.loyalty = drift_loyalty(state.loyalty, target)


# ---------------------------------------------------------------------------
# Purchases: pure helper functions
# ---------------------------------------------------------------------------

def item_cost(item: BuyItem, owned_offset: int) -> float:
    """Return the price of a unit, owned_offset units after those owned."""
    return item.base_cost * COST_GROWTH ** (item.owned + owned_offset)


def purchase_quantity(item: BuyItem, buy_amount: int) -> int:
    """Return how many units one click buys (one-time items buy 1)."""
    if item.is_one_time:
        return 1
    return buy_amount


def batch_cost(item: BuyItem, quantity: int) -> float:
    """Return the total price of buying several units in a row."""
    total = 0.0
    for offset in range(quantity):
        total = total + item_cost(item, offset)
    return total


def is_sold_out(item: BuyItem) -> bool:
    """Return whether a one-time item has already been bought."""
    return item.is_one_time and item.owned > 0


def can_afford(item: BuyItem, quantity: int, money: float) -> bool:
    """Return whether the full batch can be purchased right now."""
    return not is_sold_out(item) and batch_cost(item, quantity) <= money


def is_item_visible(item: BuyItem, total_earned: float) -> bool:
    """Return whether the item has unlocked or was already purchased."""
    return item.owned > 0 or total_earned >= item.unlock_at_earned


# ---------------------------------------------------------------------------
# Page helpers
# ---------------------------------------------------------------------------

def format_money(amount: float) -> str:
    """Turn an amount into text with the currency and two decimals."""
    cents = round(amount * 100)
    leftover_cents = cents % 100
    cents_text = str(leftover_cents)
    if leftover_cents < 10:
        cents_text = "0" + cents_text
    return CURRENCY_SYMBOL + str(cents // 100) + "." + cents_text


def describe_effect(item: BuyItem) -> str:
    """Return a short description of what one unit does."""
    amount_text = "+" + str(item.effect_amount)
    if item.effect_kind == EFFECT_STOCKING:
        return amount_text + " goods stocked/tick"
    if item.effect_kind == EFFECT_DELIVERY:
        return amount_text + " delivery capacity"
    if item.effect_kind == EFFECT_LOYALTY:
        return amount_text + " loyalty target"
    if item.effect_kind == EFFECT_CAPACITY:
        return amount_text + " warehouse capacity"
    return "Unlocks a new corporate policy"


def build_top_bar(state: State) -> Div:
    """Build the navigation bar and money display used by every page."""
    return Div(
        Header(state.company_name, 1),
        Button("Company", "company_page"),
        " Money: " + format_money(state.money),
    )


def build_stats_panel(state: State) -> Div:
    """Build the panel of current company statistics."""
    capacity = calculate_warehouse_capacity(state.buy_items)
    capacity_percent = state.goods_in_stock * 100 // capacity
    bonus_percent = round(calculate_total_bonus(state) * 100)
    return Div(
        Header("Company Stats", 2),
        BulletedList([
            "Goods stocked last tick: " + str(state.goods_stocked_last_tick),
            "Goods sold last tick: " + str(state.goods_sold_last_tick),
            "Income last tick: " + format_money(state.income_last_tick),
            "Delivery capacity: "
            + str(calculate_delivery_capacity(state.buy_items)),
            "Warehouse: " + str(state.goods_in_stock) + " / " + str(capacity)
            + " (" + str(capacity_percent) + "%)",
            "Customer loyalty: " + str(round(state.loyalty, 1)) + " / 100",
            "Customer demand: " + str(calculate_demand(state.loyalty)),
            "Total bonus: +" + str(bonus_percent) + "%",
        ]),
    )


def build_markup_controls(state: State) -> Div:
    """Build the markup display and its raise and lower buttons."""
    return Div(
        Header("Pricing", 2),
        "Markup: x" + str(state.markup) + " (sale price "
        + format_money(calculate_sale_price(state.markup)) + ") ",
        Button("Lower Markup", "lower_markup"),
        Button("Increase Markup", "raise_markup"),
    )


def build_buy_amount_controls(state: State) -> Div:
    """Build the X1, X5, and X10 buttons that set the buy amount."""
    buttons = ["Buying x" + str(state.buy_amount) + " per click: "]
    for amount in BUY_AMOUNTS:
        buttons.append(Button("X" + str(amount), "set_buy_amount",
                              [Argument("amount", amount)]))
    return Div(buttons)


def build_buy_action(item: BuyItem, item_index: int, state: State) -> Div:
    """Build the Buy button, or the reason the item can't be bought."""
    quantity = purchase_quantity(item, state.buy_amount)
    if is_sold_out(item):
        return Div("Purchased")
    price_text = format_money(batch_cost(item, quantity))
    if not can_afford(item, quantity, state.money):
        return Div("Need " + price_text)
    return Div(Button("Buy x" + str(quantity) + " for " + price_text,
                      "buy_item", [Argument("item_index", item_index)]))


def build_buy_list(state: State) -> Div:
    """Build a row for each item the player has unlocked."""
    rows = [Header("Buy List", 2)]
    for item_index, item in enumerate(state.buy_items):
        if is_item_visible(item, state.total_earned):
            rows.append(Div(
                item.emoji + " " + item.name + " (owned: " + str(item.owned)
                + ") - " + describe_effect(item),
                build_buy_action(item, item_index, state),
            ))
    return Div(rows)


def build_news_feed(state: State) -> Div:
    """Build the World News section."""
    return Div(Header("World News", 2), BulletedList(state.news_feed))


def build_live_content(state: State) -> list:
    """Build everything that the tick refreshes on the company page."""
    return [
        build_top_bar(state),
        build_stats_panel(state),
        build_markup_controls(state),
        build_buy_amount_controls(state),
        build_buy_list(state),
    ]


def build_company_content(state: State) -> list:
    """Build the company page's content, without any Clock."""
    return [
        Div(build_live_content(state), id="live_area"),
        build_news_feed(state),
    ]


def build_start_content(state: State) -> list:
    """Build the start page, removing any clock from an earlier game."""
    return [
        RemovePersistent(GAME_CLOCK_ID),
        Header("Untitled Warehouse Inc.", 1),
        "Every empire starts with a warehouse. What is yours called?",
        TextBox("company_name", state.company_name),
        Button("Open for Business", "start_game"),
    ]


def build_game_clock(state: State) -> Clock:
    """Build the game's one persistent Clock.

    ADVANCED: A Clock calls a route repeatedly. persistent=True keeps it
    running across page changes, so only start_game should ever add it.
    """
    return Clock(tick_interval(state), "tick", show=False, persistent=True,
                 id=GAME_CLOCK_ID)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@route
def index(state: State) -> Page:
    """Show the start page where the player names their company."""
    return Page(state, build_start_content(state))


@route
def start_game(state: State, company_name: str) -> Page:
    """Save the company name, start the Clock, and show the company page."""
    state.company_name = clean_company_name(company_name)
    return Page(state, [build_game_clock(state)]
                + build_company_content(state))


@route
def company_page(state: State) -> Page:
    """Show the main company dashboard."""
    return Page(state, build_company_content(state))


@route
def set_buy_amount(state: State, amount: int) -> Page:
    """Choose how many units one Buy click purchases."""
    state.buy_amount = amount
    return company_page(state)


@route
def buy_item(state: State, item_index: int) -> Page:
    """Buy the current amount of an item if the whole batch is affordable."""
    item = state.buy_items[item_index]
    quantity = purchase_quantity(item, state.buy_amount)
    if can_afford(item, quantity, state.money):
        state.money = state.money - batch_cost(item, quantity)
        item.owned = item.owned + quantity
    return company_page(state)


@route
def raise_markup(state: State) -> Page:
    """Raise the markup by one step."""
    state.markup = change_markup(state.markup, MARKUP_STEP)
    return company_page(state)


@route
def lower_markup(state: State) -> Page:
    """Lower the markup by one step."""
    state.markup = change_markup(state.markup, -MARKUP_STEP)
    return company_page(state)


@route
def tick(state: State) -> Fragment:
    """Run one game tick and refresh only the live part of the page.

    ADVANCED: A Fragment replaces one element instead of rebuilding the
    whole page, which keeps the Clock from being restarted.
    """
    run_stocking(state)
    run_selling(state)
    run_loyalty_drift(state)
    return Fragment(state, build_live_content(state), target="#live_area")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def make_test_item(effect_kind: str, effect_amount: int,
                   owned: int) -> BuyItem:
    """Build a simple 100-cost item for the helper tests."""
    return BuyItem("Test", "T", 100.0, effect_kind, effect_amount, 50.0,
                   False, owned)


def make_one_time_item(owned: int) -> BuyItem:
    """Build a simple one-time item for the helper tests."""
    return BuyItem("Once", "O", 100.0, EFFECT_UNLOCK, 1, 0.0, True, owned)


# Economy helpers
assert_equal(tick_interval(make_new_state()), TICK_INTERVAL_MS)
assert_equal(total_item_effect([], EFFECT_STOCKING), 0)
assert_equal(total_item_effect([make_test_item(EFFECT_STOCKING, 5, 2),
                                make_test_item(EFFECT_DELIVERY, 9, 9),
                                make_test_item(EFFECT_STOCKING, 1, 3)],
                               EFFECT_STOCKING), 13)
assert_equal(calculate_stocking_rate([make_test_item(EFFECT_STOCKING, 5, 2)]),
             BASE_STOCKING_RATE + 10)
assert_equal(calculate_delivery_capacity(
    [make_test_item(EFFECT_DELIVERY, 1, 3)]), BASE_DELIVERY_CAPACITY + 3)
assert_equal(calculate_warehouse_capacity(
    [make_test_item(EFFECT_CAPACITY, 50, 2)]), BASE_WAREHOUSE_CAPACITY + 100)
assert_equal(calculate_units_stocked(5, 0, 100, 500.0), 5)
assert_equal(calculate_units_stocked(5, 98, 100, 500.0), 2)
assert_equal(calculate_units_stocked(5, 0, 100, 44.0), 2)
assert_equal(calculate_units_stocked(5, 100, 100, 500.0), 0)
assert_equal(calculate_demand(50.0), 50)
assert_equal(calculate_demand(0.0), 0)
assert_equal(calculate_units_sold(3, 5, 50), 3)
assert_equal(calculate_units_sold(30, 5, 50), 5)
assert_equal(calculate_units_sold(30, 50, 7), 7)
assert_equal(calculate_sale_price(2.0), 30.0)
assert_equal(calculate_total_bonus(make_new_state()), 0.0)
assert_equal(calculate_income(4, 10.0, 0.0), 40.0)
assert_equal(calculate_income(4, 10.0, 0.5), 60.0)
assert_equal(clamp_loyalty(-5.0), MIN_LOYALTY)
assert_equal(clamp_loyalty(105.0), MAX_LOYALTY)
assert_equal(clamp_loyalty(42.0), 42.0)
assert_equal(calculate_loyalty_target(1.0, []), BASE_LOYALTY_TARGET)
assert_equal(calculate_loyalty_target(1.5, []), 50.0)
assert_equal(calculate_loyalty_target(5.0, []), 0.0)
assert_equal(calculate_loyalty_target(
    1.0, [make_test_item(EFFECT_LOYALTY, 2, 3)]), 66.0)
assert_equal(drift_loyalty(50.0, 60.0), 51.0)
assert_equal(drift_loyalty(50.0, 40.0), 49.0)
assert_equal(drift_loyalty(50.0, 50.0), 50.0)
assert_equal(change_markup(1.5, 0.1), 1.6)
assert_equal(change_markup(1.0, -0.1), MIN_MARKUP)
assert_equal(change_markup(5.0, 0.1), MAX_MARKUP)
assert_equal(clean_company_name("  Boxes  "), "Boxes")
assert_equal(clean_company_name("   "), DEFAULT_COMPANY_NAME)

# Purchase helpers
assert_equal(item_cost(make_test_item(EFFECT_STOCKING, 1, 0), 0), 100.0)
assert_equal(item_cost(make_test_item(EFFECT_STOCKING, 1, 1), 0),
             100.0 * COST_GROWTH)
assert_equal(item_cost(make_test_item(EFFECT_STOCKING, 1, 1), 1),
             100.0 * COST_GROWTH ** 2)
assert_equal(purchase_quantity(make_test_item(EFFECT_STOCKING, 1, 0), 5), 5)
assert_equal(purchase_quantity(make_one_time_item(0), 5), 1)
assert_equal(batch_cost(make_test_item(EFFECT_STOCKING, 1, 0), 0), 0.0)
assert_equal(batch_cost(make_test_item(EFFECT_STOCKING, 1, 0), 2),
             100.0 + 100.0 * COST_GROWTH)
assert_equal(is_sold_out(make_one_time_item(0)), False)
assert_equal(is_sold_out(make_one_time_item(1)), True)
assert_equal(is_sold_out(make_test_item(EFFECT_STOCKING, 1, 4)), False)
assert_equal(can_afford(make_test_item(EFFECT_STOCKING, 1, 0), 1, 100.0), True)
assert_equal(can_afford(make_test_item(EFFECT_STOCKING, 1, 0), 2, 100.0),
             False)
assert_equal(can_afford(make_one_time_item(1), 1, 9999.0), False)
assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 0), 49.0),
             False)
assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 0), 50.0),
             True)
assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 1), 0.0), True)

# Page helpers
assert_equal(format_money(5.0), "Ŧ5.00")
assert_equal(format_money(22.5), "Ŧ22.50")
assert_equal(format_money(3.07), "Ŧ3.07")
assert_equal(describe_effect(make_test_item(EFFECT_DELIVERY, 1, 0)),
             "+1 delivery capacity")
assert_equal(describe_effect(make_one_time_item(0)),
             "Unlocks a new corporate policy")


# Routes
def expected_after_named_start() -> State:
    """Build the State expected after starting a company named Boxes."""
    state = make_new_state()
    state.company_name = "Boxes"
    return state


def expected_after_first_tick() -> State:
    """Build the State expected after one tick of a brand new game."""
    state = make_new_state()
    state.money = 537.5
    state.total_earned = 112.5
    state.goods_stocked_last_tick = 5
    state.goods_sold_last_tick = 5
    state.income_last_tick = 112.5
    return state


def expected_after_buying_van() -> State:
    """Build the State expected after buying one Delivery Van."""
    state = make_new_state()
    state.money = 450.0
    state.buy_items[1].owned = 1
    return state


def expected_with_buy_amount(amount: int) -> State:
    """Build a new-game State that has the given buy amount."""
    state = make_new_state()
    state.buy_amount = amount
    return state


def expected_with_markup(markup: float) -> State:
    """Build a new-game State that has the given markup."""
    state = make_new_state()
    state.markup = markup
    return state


def make_expected_company_page(state: State) -> Page:
    """Build the company page expected for a given State."""
    return Page(state, build_company_content(state))


def make_broke_state() -> State:
    """Build a new-game State that cannot afford anything."""
    state = make_new_state()
    state.money = 1.0
    return state


assert_equal(index(make_new_state()),
             Page(make_new_state(), build_start_content(make_new_state())))
assert_equal(start_game(make_new_state(), "  Boxes "),
             Page(expected_after_named_start(),
                  [build_game_clock(expected_after_named_start())]
                  + build_company_content(expected_after_named_start())))
assert_equal(company_page(make_new_state()),
             make_expected_company_page(make_new_state()))
assert_equal(set_buy_amount(make_new_state(), 10),
             make_expected_company_page(expected_with_buy_amount(10)))
assert_equal(buy_item(make_new_state(), 1),
             make_expected_company_page(expected_after_buying_van()))
assert_equal(buy_item(make_broke_state(), 1),
             make_expected_company_page(make_broke_state()))
assert_equal(raise_markup(make_new_state()),
             make_expected_company_page(expected_with_markup(1.6)))
assert_equal(lower_markup(make_new_state()),
             make_expected_company_page(expected_with_markup(1.4)))
assert_equal(tick(make_new_state()),
             Fragment(expected_after_first_tick(),
                      build_live_content(expected_after_first_tick()),
                      target="#live_area"))

start_server(make_new_state())
