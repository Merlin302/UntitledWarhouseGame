import random
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
MAX_NEWS_ITEMS = 8

# Which page is showing, so the tick refreshes the right content.
PAGE_COMPANY = "company"
PAGE_BUSINESS = "business"

# Each row: name, emoji, CheckBox name (must match a save_goods parameter),
# and income bonus as a fraction.
STARTING_GOODS_ROWS = [
    ["Household Goods", "🧺", "sell_household", 0.05],
    ["Canned Food", "🥫", "sell_canned_food", 0.10],
    ["Electronics", "📺", "sell_electronics", 0.15],
    ["War Supplies", "💣", "sell_war_supplies", 1.00],
]

# Each row: name, emoji, CheckBox name (must match a save_policies parameter),
# stocking bonus, delivery bonus, income bonus, loyalty target change,
# strike risk per tick, and whether it needs an unlock purchase.
STARTING_POLICY_ROWS = [
    ["Unpaid Overtime", "⏰", "unpaid_overtime",
     0.5, 0.0, 0.0, -5.0, 0.03, False],
    ["Aggressive Upselling", "💬", "aggressive_upselling",
     0.0, 0.0, 0.15, -8.0, 0.0, False],
    ["Algorithmic Route Quotas", "🗺️", "route_quotas",
     0.0, 0.5, 0.0, -3.0, 0.05, True],
]

STRIKE_DURATION_TICKS = 5
# Stocking and delivery are multiplied by this during a strike.
STRIKE_PENALTY_MULTIPLIER = 0.5
STRIKE_NEWS = "Warehouse staff walk out! Management calls it 'unplanned rest'."


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
class GoodsType:
    """One kind of goods the company can choose to sell.

    Attributes:
        name: The goods type's display name.
        emoji: A placeholder picture for the goods type.
        input_name: The name of its CheckBox on the Business page.
        income_bonus: The income bonus as a fraction while selling it.
        is_selling: Whether the company currently sells it.
    """
    name: str
    emoji: str
    input_name: str
    income_bonus: float
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
    is_active: bool


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


def make_starting_items() -> list[BuyItem]:
    """Build fresh BuyItems so the global rows are never modified.

    Returns:
        A new list with one unowned BuyItem per row of STARTING_ITEM_ROWS.
    """
    items = []
    for row in STARTING_ITEM_ROWS:
        items.append(BuyItem(row[0], row[1], row[2], row[3], row[4], row[5],
                             row[6], 0))
    return items


def make_starting_goods() -> list[GoodsType]:
    """Build fresh GoodsTypes so the global rows are never modified.

    Returns:
        A new list with one unselected GoodsType per goods row.
    """
    goods_types = []
    for row in STARTING_GOODS_ROWS:
        goods_types.append(GoodsType(row[0], row[1], row[2], row[3], False))
    return goods_types


def make_starting_policies() -> list[Policy]:
    """Build fresh Policies so the global rows are never modified.

    Returns:
        A new list with one inactive Policy per policy row.
    """
    policies = []
    for row in STARTING_POLICY_ROWS:
        policies.append(Policy(row[0], row[1], row[2], row[3], row[4], row[5],
                               row[6], row[7], row[8], False))
    return policies


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
                   False, owned)


def make_one_time_item(owned: int) -> BuyItem:
    """Build a simple one-time item for the helper tests.

    Args:
        owned: How many units are already owned (0 or 1).

    Returns:
        A one-time BuyItem that is always unlocked.
    """
    return BuyItem("Once", "O", 100.0, EFFECT_UNLOCK, 1, 0.0, True, owned)


def make_test_goods(income_bonus: float, is_selling: bool) -> GoodsType:
    """Build a simple goods type for the helper tests.

    Args:
        income_bonus: The income bonus as a fraction.
        is_selling: Whether it is being sold.

    Returns:
        A GoodsType with those values.
    """
    return GoodsType("Test", "T", "sell_test", income_bonus, is_selling)


def make_test_policy(is_active: bool) -> Policy:
    """Build a policy with one known value for every effect.

    Args:
        is_active: Whether the policy is in force.

    Returns:
        A Policy that does not need an unlock.
    """
    return Policy("Test", "T", "test_policy", 0.5, 0.25, 0.1, -5.0, 0.03,
                  False, is_active)


def make_locked_policy() -> Policy:
    """Build an inactive policy that needs an unlock purchase.

    Returns:
        A locked Policy with no effects.
    """
    return Policy("Locked", "L", "locked_policy", 0.0, 0.0, 0.0, 0.0, 0.0,
                  True, False)


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
                             False, True)]
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


def set_goods_choices(goods_types: list[GoodsType],
                      choices: list[bool]) -> None:
    """Record which goods types the player chose to sell.

    Args:
        goods_types: The goods types to update.
        choices: One True or False per goods type, in the same order.
    """
    for index, goods in enumerate(goods_types):
        goods.is_selling = choices[index]


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

    ADVANCED: random.random() gives a decimal from 0 up to (but not
    including) 1, so it lands below strike_risk with that probability.

    Args:
        strike_risk: The chance of a strike, from 0 to 1.

    Returns:
        True if a strike begins.
    """
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


def apply_rate_modifiers(base_rate: int, policy_bonus: float,
                         strike_ticks_left: int) -> int:
    """Apply policy bonuses and any strike penalty to a per-tick rate.

    Args:
        base_rate: The rate before modifiers.
        policy_bonus: The policy bonus as a fraction.
        strike_ticks_left: Ticks until the current strike ends.

    Returns:
        The final rate, rounded down to a whole number of units.
    """
    multiplier = (1 + policy_bonus) * strike_multiplier(strike_ticks_left)
    return int(round(base_rate * multiplier, 2))


assert_equal(apply_rate_modifiers(10, 0.0, 0), 10)
assert_equal(apply_rate_modifiers(10, 0.5, 0), 15)
assert_equal(apply_rate_modifiers(10, 0.5, 2), 7)


def effective_stocking_rate(state: State) -> int:
    """Calculate the most goods that can be stocked each tick right now.

    Args:
        state: The current game state.

    Returns:
        The stocking rate after policies and strikes.
    """
    return apply_rate_modifiers(calculate_stocking_rate(state.buy_items),
                                total_policy_stocking_bonus(state.policies),
                                state.strike_ticks_left)


assert_equal(effective_stocking_rate(make_new_state()), BASE_STOCKING_RATE)
assert_equal(effective_stocking_rate(make_striking_state(1)),
             BASE_STOCKING_RATE // 2)


def effective_delivery_capacity(state: State) -> int:
    """Calculate the most goods that can be delivered each tick right now.

    Args:
        state: The current game state.

    Returns:
        The delivery capacity after policies and strikes.
    """
    return apply_rate_modifiers(calculate_delivery_capacity(state.buy_items),
                                total_policy_delivery_bonus(state.policies),
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


def calculate_demand(loyalty: float) -> int:
    """Calculate how many units customers want to buy this tick.

    Args:
        loyalty: Customer loyalty from 0 to 100.

    Returns:
        The number of units customers want, rounded down.
    """
    # Drifting loyalty stops just short of its target (like 59.9999), so
    # round first or // would drop a whole unit of demand.
    return int(MARKET_SIZE * round(loyalty, 2) // 100)


assert_equal(calculate_demand(50.0), 50)
assert_equal(calculate_demand(0.0), 0)
assert_equal(calculate_demand(59.9999), 60)
assert_equal(calculate_demand(59.5), 59)


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
    """Add the income bonuses from goods types and policies.

    Args:
        state: The current game state.

    Returns:
        The bonus as a fraction, where 0.5 means +50%.
    """
    return (total_goods_bonus(state.goods_types)
            + total_policy_income_bonus(state.policies))


def make_state_with_income_bonuses() -> State:
    """Build a State selling Electronics with Aggressive Upselling active.

    Returns:
        A new-game State with +15% from goods and +15% from policy.
    """
    state = make_new_state()
    state.goods_types[2].is_selling = True
    state.policies[1].is_active = True
    return state


assert_equal(calculate_total_bonus(make_new_state()), 0.0)
assert_equal(round(calculate_total_bonus(make_state_with_income_bonuses()), 2),
             0.3)


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


def state_after_strikes(state: State) -> State:
    """Run the strike step and hand back the State so tests can check it.

    Args:
        state: The game state to update.

    Returns:
        The same State after run_strikes.
    """
    run_strikes(state)
    return state


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


def is_item_visible(item: BuyItem, total_earned: float) -> bool:
    """Check whether the item has unlocked or was already purchased.

    Args:
        item: The item to check.
        total_earned: The player's lifetime earnings.

    Returns:
        True if the item should appear in the buy list.
    """
    return item.owned > 0 or total_earned >= item.unlock_at_earned


assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 0), 49.0),
             False)
assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 0), 50.0),
             True)
assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 1), 0.0), True)


def is_policy_unlocked(policy: Policy, items: list[BuyItem]) -> bool:
    """Check whether a policy can be used yet.

    Args:
        policy: The policy to check.
        items: The player's buy items.

    Returns:
        True if it needs no unlock or an unlock item has been bought.
    """
    return not policy.needs_unlock or total_item_effect(items,
                                                        EFFECT_UNLOCK) > 0


assert_equal(is_policy_unlocked(make_test_policy(False), []), True)
assert_equal(is_policy_unlocked(make_locked_policy(),
                                [make_one_time_item(0)]), False)
assert_equal(is_policy_unlocked(make_locked_policy(),
                                [make_one_time_item(1)]), True)


def set_policy_choices(policies: list[Policy], choices: list[bool],
                       items: list[BuyItem]) -> None:
    """Record the player's policies, keeping locked ones switched off.

    Args:
        policies: The policies to update.
        choices: One True or False per policy, in the same order.
        items: The player's buy items.
    """
    for index, policy in enumerate(policies):
        policy.is_active = (choices[index]
                            and is_policy_unlocked(policy, items))


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
    return "Unlocks a new corporate policy"


assert_equal(describe_effect(make_test_item(EFFECT_DELIVERY, 1, 0)),
             "+1 delivery capacity")
assert_equal(describe_effect(make_one_time_item(0)),
             "Unlocks a new corporate policy")


def build_top_bar(state: State) -> Div:
    """Build the navigation bar and money display used by every page.

    Args:
        state: The current game state.

    Returns:
        A Div holding the company name, navigation, and money.
    """
    return Div(
        Header(state.company_name, 1),
        Button("Company", "company_page"),
        Button("Business", "business_page"),
        " Money: " + format_money(state.money),
    )


def build_stats_panel(state: State) -> Div:
    """Build the panel of current company statistics.

    Args:
        state: The current game state.

    Returns:
        A Div holding a heading and the list of stats.
    """
    capacity = calculate_warehouse_capacity(state.buy_items)
    capacity_percent = state.goods_in_stock * 100 // capacity
    delivery_capacity = effective_delivery_capacity(state)
    return Div(
        Header("Company Stats", 2),
        "Numbers in parentheses are the most possible per tick.",
        BulletedList([
            "Goods stocked last tick: " + str(state.goods_stocked_last_tick)
            + " (" + str(effective_stocking_rate(state)) + ")",
            "Goods sold last tick: " + str(state.goods_sold_last_tick)
            + " (" + str(delivery_capacity) + ")",
            "Income last tick: " + format_money(state.income_last_tick)
            + " (" + format_money(max_income_per_tick(state)) + ")",
            "Delivery capacity: " + str(delivery_capacity),
            "Warehouse: " + str(state.goods_in_stock) + " / " + str(capacity)
            + " (" + str(capacity_percent) + "%)",
            "Customer loyalty: " + str(round(state.loyalty, 1)) + " / 100",
            "Customer demand: " + str(calculate_demand(state.loyalty)),
        ]),
    )


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


def active_effect_lines(state: State) -> list[str]:
    """List each goods type being sold and each active policy.

    Args:
        state: The current game state.

    Returns:
        One line of text per active bonus source.
    """
    lines = []
    for goods in state.goods_types:
        if goods.is_selling:
            lines.append(goods.emoji + " " + goods.name + ": "
                         + percent_text(goods.income_bonus) + " income")
    for policy in state.policies:
        if policy.is_active:
            lines.append(policy.emoji + " " + policy.name + ": "
                         + describe_policy(policy))
    return lines


assert_equal(active_effect_lines(make_new_state()), [])
assert_equal(active_effect_lines(make_state_with_income_bonuses()),
             ["📺 Electronics: +15% income",
              "💬 Aggressive Upselling: +15% income, -8 loyalty target"])


def build_bonus_panel(state: State) -> Div:
    """Build the summary of goods, policy, and strike effects.

    Args:
        state: The current game state.

    Returns:
        A Div holding a heading and the list of effects.
    """
    policies = state.policies
    return Div(
        Header("Bonus Summary", 2),
        BulletedList(active_effect_lines(state) + [
            "Total income bonus: "
            + percent_text(calculate_total_bonus(state)),
            "Policy stocking bonus: "
            + percent_text(total_policy_stocking_bonus(policies)),
            "Policy delivery bonus: "
            + percent_text(total_policy_delivery_bonus(policies)),
            "Policy loyalty target change: "
            + str(round(total_policy_loyalty_change(policies))),
            "Strike risk per tick: "
            + percent_text(total_strike_risk(policies)),
            strike_status_text(state.strike_ticks_left),
        ]),
    )


def build_markup_controls(state: State) -> Div:
    """Build the markup display and its raise and lower buttons.

    Args:
        state: The current game state.

    Returns:
        A Div holding the current markup and its buttons.
    """
    return Div(
        Header("Pricing", 2),
        "Markup: x" + str(state.markup) + " (sale price "
        + format_money(calculate_sale_price(state.markup)) + ") ",
        Button("Lower Markup", "lower_markup"),
        Button("Increase Markup", "raise_markup"),
    )


def build_buy_amount_controls(state: State) -> Div:
    """Build the X1, X5, and X10 buttons that set the buy amount.

    Args:
        state: The current game state.

    Returns:
        A Div holding the current amount and one button per choice.
    """
    buttons = ["Buying x" + str(state.buy_amount) + " per click: "]
    for amount in BUY_AMOUNTS:
        buttons.append(Button("X" + str(amount), "set_buy_amount",
                              [Argument("amount", amount)]))
    return Div(buttons)


def build_buy_action(item: BuyItem, item_index: int, state: State) -> Div:
    """Build the Buy button, or the reason the item can't be bought.

    Args:
        item: The item this row is for.
        item_index: The item's position in state.buy_items.
        state: The current game state.

    Returns:
        A Div holding a Buy button or a short message.
    """
    quantity = purchase_quantity(item, state.buy_amount)
    if is_sold_out(item):
        return Div("Purchased")
    if not can_afford(item, quantity, state.money, state.goods_in_stock):
        required = money_required(item, quantity, state.goods_in_stock)
        return Div("Need " + format_money(required))
    price_text = format_money(batch_cost(item, quantity))
    return Div(Button("Buy x" + str(quantity) + " for " + price_text,
                      "buy_item", [Argument("item_index", item_index)]))


def build_buy_list(state: State) -> Div:
    """Build a row for each item the player has unlocked.

    Args:
        state: The current game state.

    Returns:
        A Div holding a heading and the visible item rows.
    """
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
    """Build the World News section.

    Args:
        state: The current game state.

    Returns:
        A Div holding a heading and the list of headlines.
    """
    return Div(Header("World News", 2), BulletedList(state.news_feed))


def build_live_content(state: State) -> list:
    """Build everything that the tick refreshes on the current page.

    Args:
        state: The current game state.

    Returns:
        A list of the components inside the live area.
    """
    if state.current_page == PAGE_BUSINESS:
        return [build_top_bar(state)]
    return [
        build_top_bar(state),
        build_stats_panel(state),
        build_bonus_panel(state),
        build_markup_controls(state),
        build_buy_amount_controls(state),
        build_buy_list(state),
        build_news_feed(state),
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
        A Div holding the goods choices.
    """
    rows = [Header("Goods to Sell", 2)]
    for goods in state.goods_types:
        rows.append(Div(
            CheckBox(goods.input_name, goods.is_selling),
            " " + goods.emoji + " " + goods.name + " - "
            + percent_text(goods.income_bonus) + " income",
        ))
    rows.append(Button("Save Goods", "save_goods"))
    return Div(rows)


def policy_label(policy: Policy, items: list[BuyItem]) -> str:
    """Build the text shown beside a policy's CheckBox.

    Args:
        policy: The policy to label.
        items: The player's buy items.

    Returns:
        The policy's effects, or a note saying that it is locked.
    """
    text = policy.emoji + " " + policy.name + " - " + describe_policy(policy)
    if is_policy_unlocked(policy, items):
        return text
    return ("🔒 " + text
            + " (locked: buy Next Generation Corporate Organization)")


assert_equal(policy_label(make_test_policy(False), [])[:6], "T Test")
assert_equal(policy_label(make_locked_policy(), [make_one_time_item(0)])[:1],
             "🔒")


def build_policy_form(state: State) -> Div:
    """Build one CheckBox per policy and the button that saves them.

    Args:
        state: The current game state.

    Returns:
        A Div holding the policy choices.
    """
    rows = [Header("Corporate Policies", 2)]
    for policy in state.policies:
        rows.append(Div(
            CheckBox(policy.input_name, policy.is_active),
            " " + policy_label(policy, state.buy_items),
        ))
    rows.append(Button("Save Policies", "save_policies"))
    return Div(rows)


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
        build_goods_form(state),
        build_policy_form(state),
    ]


def build_start_content(state: State) -> list:
    """Build the start page, removing any clock from an earlier game.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
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

    Args:
        state: The current game state.

    Returns:
        A hidden Clock that calls the tick route.
    """
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


def expected_after_named_start() -> State:
    """Build the State expected after starting a company named Boxes.

    Returns:
        A new-game State with the company name set.
    """
    state = make_new_state()
    state.company_name = "Boxes"
    return state


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


def make_expected_company_page(state: State) -> Page:
    """Build the company page expected for a given State.

    Args:
        state: The State the page should show.

    Returns:
        The expected company page.
    """
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


assert_equal(business_page(make_new_state()),
             make_expected_business_page(make_business_state()))


@route
def save_goods(state: State, sell_household: bool, sell_canned_food: bool,
               sell_electronics: bool, sell_war_supplies: bool) -> Page:
    """Save which goods types the company sells.

    Args:
        state: The current game state.
        sell_household: Whether Household Goods is checked.
        sell_canned_food: Whether Canned Food is checked.
        sell_electronics: Whether Electronics is checked.
        sell_war_supplies: Whether War Supplies is checked.

    Returns:
        The refreshed Business page.
    """
    set_goods_choices(state.goods_types, [sell_household, sell_canned_food,
                                          sell_electronics, sell_war_supplies])
    state.sells_war_supplies = sell_war_supplies
    return business_page(state)


def expected_after_selling_war_supplies() -> State:
    """Build the State expected after choosing only War Supplies.

    Returns:
        A Business page State selling only War Supplies, with the flag set.
    """
    state = make_business_state()
    state.goods_types[3].is_selling = True
    state.sells_war_supplies = True
    return state


assert_equal(save_goods(make_new_state(), False, False, False, True),
             make_expected_business_page(
                 expected_after_selling_war_supplies()))


@route
def save_policies(state: State, unpaid_overtime: bool,
                  aggressive_upselling: bool, route_quotas: bool) -> Page:
    """Save which corporate policies are active.

    Args:
        state: The current game state.
        unpaid_overtime: Whether Unpaid Overtime is checked.
        aggressive_upselling: Whether Aggressive Upselling is checked.
        route_quotas: Whether Algorithmic Route Quotas is checked.

    Returns:
        The refreshed Business page.
    """
    set_policy_choices(state.policies,
                       [unpaid_overtime, aggressive_upselling, route_quotas],
                       state.buy_items)
    return business_page(state)


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


assert_equal(save_policies(make_new_state(), True, False, False),
             make_expected_business_page(expected_after_overtime()))
# The locked policy stays off until the unlock item is bought.
assert_equal(save_policies(make_new_state(), False, False, True),
             make_expected_business_page(make_business_state()))
assert_equal(save_policies(make_unlocked_state(), False, False, True),
             make_expected_business_page(expected_after_quotas()))


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

    ADVANCED: A Fragment replaces one element instead of rebuilding the
    whole page, which keeps the Clock from being restarted.

    Uses randomness through run_strikes, but with no strike risk (as in a
    new game) the result is predictable, so the tests use zero-risk States.

    Args:
        state: The current game state.

    Returns:
        A Fragment that replaces the contents of #live_area.
    """
    run_strikes(state)
    run_stocking(state)
    run_selling(state)
    run_loyalty_drift(state)
    return Fragment(state, build_live_content(state), target="#live_area")


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
    return state


assert_equal(tick(make_new_state()),
             Fragment(expected_after_first_tick(),
                      build_live_content(expected_after_first_tick()),
                      target="#live_area"))


def expected_business_tick() -> State:
    """Build the State expected after one tick on the Business page.

    Returns:
        The first-tick State, with the Business page showing.
    """
    state = expected_after_first_tick()
    state.current_page = PAGE_BUSINESS
    return state


# On the Business page, the tick must refresh only the top bar.
assert_equal(tick(make_business_state()),
             Fragment(expected_business_tick(),
                      [build_top_bar(expected_business_tick())],
                      target="#live_area"))

start_server(make_new_state())
