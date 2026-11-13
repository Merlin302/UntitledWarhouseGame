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
DEFENSE_LICENSE = "Defense Procurement License"
PARCELPRO_ABSORPTION = "Absorb Fleeing Rival: ParcelPro"
OZONIX_NATIONALIZATION = "Nationalize Ozonix Marketplace"
MARKETING_PLAYBOOK = "Social Media Playbook"
ZONING_PERMIT = "Warehouse Zoning Permit"
RESTRUCTURING_STUDY = "Corporate Restructuring Study"
NO_REQUIREMENT = ""

# Each row: name, emoji, base cost, effect kind, effect amount, whether
# it is a one-time buy, and the research it requires (NO_REQUIREMENT if
# none). New items only ever appear through research, which the player
# buys with a click, so a tick never has to redraw the Buy list.
STARTING_ITEM_ROWS = [
    ["Procurement Agent", "🧑‍💼", 100.0, EFFECT_STOCKING, 5, False,
     NO_REQUIREMENT],
    ["Fordov Delivery Van", "🚐", 50.0, EFFECT_DELIVERY, 1, False,
     NO_REQUIREMENT],
    ["Short Form Marketing Campaign", "📱", 150.0, EFFECT_LOYALTY, 2, False,
     MARKETING_PLAYBOOK],
    ["Warehouse Expansion", "🏗️", 200.0, EFFECT_CAPACITY, 50, False,
     ZONING_PERMIT],
    ["Next Generation Corporate Organization", "🏢", 2000.0, EFFECT_UNLOCK, 1,
     True, RESTRUCTURING_STUDY],
    ["Upgraded Pickup Truck", "🛻", 300.0, EFFECT_DELIVERY, 4, False,
     PICKUP_TRUCK_STUDY],
    ["Better Conveyor Belt", "⚙️", 600.0, EFFECT_DELIVERY_BOOST, 5, False,
     CONVEYOR_RESEARCH],
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
# income bonus as a fraction, the research it requires, whether it is a
# war good, whether wartime sanctions ban it, and the extra income bonus it
# gets during the war (when the company is the only supplier left).
STARTING_GOODS_ROWS = [
    ["Household Goods", "🧺", "sell_household", 0.05, NO_REQUIREMENT,
     False, False, 0.10],
    [CANNED_FOOD, "🥫", "sell_canned_food", 0.10, NO_REQUIREMENT,
     False, False, 0.25],
    ["Electronics", "📺", "sell_electronics", 0.15, NO_REQUIREMENT,
     False, True, 0.0],
    ["War Supplies", "💣", "sell_war_supplies", 1.00, NO_REQUIREMENT,
     True, False, 0.0],
    ["Imported Luxuries", "💎", "sell_imported_luxuries", 0.25,
     IMPORT_LICENSES, False, True, 0.0],
    ["Body Armor", "🦺", "sell_body_armor", 0.60, DEFENSE_LICENSE,
     True, False, 0.0],
    ["Drone Components", "🔧", "sell_drone_parts", 0.80, DEFENSE_LICENSE,
     True, False, 0.0],
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
# (NO_REQUIREMENT if none), lifetime earnings needed to appear, the World
# News headline posted when it is completed, and whether it only appears
# once the war has started.
RESEARCH_ROWS = [
    [LEAN_PROCUREMENT, "📉",
     "Consultants remove three chairs and call it a methodology.",
     CATEGORY_STAT, 800.0, 0.10, 0.0, 0, "", 0.0, NO_REQUIREMENT, 500.0,
     "Procurement team goes lean; snacks reclassified as 'waste'.", False],
    [ROUTE_OPTIMIZATION, "🧭",
     "An app that tells drivers the road is shorter than they think.",
     CATEGORY_STAT, 1000.0, 0.0, 0.10, 0, "", 0.0, NO_REQUIREMENT, 800.0,
     "Drivers report the app keeps routing them through a lake.", False],
    [PICKUP_TRUCK_STUDY, "🛻",
     "A 40-page study concludes that bigger trucks hold more boxes.",
     CATEGORY_EQUIPMENT, 1500.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT,
     1500.0, "Study confirms trucks are 'like vans, but more so'.", False],
    [CONVEYOR_RESEARCH, "⚙️",
     "Engineers discover that belts can move boxes without lunch breaks.",
     CATEGORY_EQUIPMENT, 2500.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT,
     3000.0, "New conveyor belt prototype eats only one intern.", False],
    [IMPORT_LICENSES, "📜",
     "Paperwork so thick it is itself a taxable import.",
     CATEGORY_UNLOCK, 3000.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT, 3000.0,
     "Customs office approves licenses after a 'gift basket'.", False],
    [LABOR_CONSULTANCY, "🤝",
     "Experts in making 'no' sound like 'great question'.",
     CATEGORY_UNLOCK, 4000.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT, 5000.0,
     "Consultants rename workers 'independent box partners'.", False],
    [TUSHONKA_BUYOUT, "🥫",
     "Own the cans, own the soup, own the supply chain of soup.",
     CATEGORY_WORLD, 8000.0, 0.0, 0.0, 0, CANNED_FOOD, 0.15,
     IMPORT_LICENSES, 8000.0,
     "Tushonka Canning Co. acquired; stew prices 'stable for now'.", False],
    [BOXLY_ACQUISITION, "📦",
     "Buy the competition, then politely forget it ever existed.",
     CATEGORY_WORLD, 25000.0, 0.0, 0.0, 50, "", 0.0, NO_REQUIREMENT,
     15000.0, "Boxly Logistics absorbed; its customers 'welcomed home'.",
     False],
    [DEFENSE_LICENSE, "🎖️",
     "A stamp that turns a warehouse into a 'strategic asset'.",
     CATEGORY_UNLOCK, 20000.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT, 0.0,
     "Ministry of Defense approves warehouse as 'basically a fort'.", True],
    [PARCELPRO_ABSORPTION, "🏃",
     "Its foreign owners left in a hurry. Their customers did not.",
     CATEGORY_WORLD, 30000.0, 0.0, 0.0, 40, "", 0.0, NO_REQUIREMENT, 0.0,
     "ParcelPro warehouses 'find a new home' after owners flee.", True],
    [OZONIX_NATIONALIZATION, "🏛️",
     "Patriotic duty requires that we own the second-biggest marketplace.",
     CATEGORY_WORLD, 60000.0, 0.0, 0.0, 60, "", 0.0, PARCELPRO_ABSORPTION,
     0.0, "Ozonix nationalized; shareholders thanked for their service.",
     True],
    [MARKETING_PLAYBOOK, "📱",
     "A guide to dancing in front of boxes until people buy them.",
     CATEGORY_EQUIPMENT, 100.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT, 200.0,
     "Warehouse staff now legally required to 'go viral' weekly.", False],
    [ZONING_PERMIT, "🏗️",
     "Permission to build more warehouse, signed in triplicate.",
     CATEGORY_EQUIPMENT, 250.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT, 500.0,
     "City approves expansion after warehouse promises 'fewer forklifts'.",
     False],
    [RESTRUCTURING_STUDY, "🏢",
     "Consultants draw boxes around boxes and call it an org chart.",
     CATEGORY_EQUIPMENT, 750.0, 0.0, 0.0, 0, "", 0.0, NO_REQUIREMENT, 1500.0,
     "Management restructured; everyone now reports to everyone.", False],
]

# ---------------------------------------------------------------------------
# War: numbers for the war (W1: the war economy)
# ---------------------------------------------------------------------------

PHASE_PEACE = "peace"
PHASE_WAR = "war"
PHASE_WAR_OVER = "war_over"

HOME_COUNTRY = "Republic of Varnia"
ENEMY_COUNTRY = "Kalyxian Federation"

# Lifetime earnings at which the war breaks out.
WAR_START_EARNED = 40000.0
WAR_START_NEWS = ("BREAKING: The " + ENEMY_COUNTRY + " invades the "
                  + HOME_COUNTRY + "! Markets 'mildly concerned'.")
SANCTIONS_NEWS = ("Sanctions ban electronics and luxury imports; the "
                  + "company is now the only supplier of soup.")
SIRENS_NEWS = ("Air raid sirens sound citywide. Read the briefing in your "
               + "Inbox before the first attack.")

WAVE_COUNT = 35
# Every 10th wave, and the last wave, is a dire wave.
DIRE_WAVE_EVERY = 10
# Raise this (e.g. to 10) to make waves and intermissions 10x shorter
# while testing. Keep it at 1 for the real game.
DEBUG_WAR_SPEED = 1

MAX_THREAT = 100.0
# Threat added per second, plus a little more for each war good sold in
# the latest tick. The cap keeps intermissions from getting too short.
THREAT_PER_SECOND = 2.0
THREAT_PER_WAR_UNIT = 0.05
MAX_THREAT_PER_SECOND = 5.0

# --- W2: air defense ---
PAGE_WAR = "war"
ALTITUDE_HIGH = "high"
ALTITUDE_MEDIUM = "medium"
ALTITUDE_LOW = "low"
ALTITUDES = [ALTITUDE_HIGH, ALTITUDE_MEDIUM, ALTITUDE_LOW]

# Attackers per wave: WAVE_BASE_ATTACKERS, plus one more every
# WAVES_PER_EXTRA_ATTACKER waves, plus DIRE_EXTRA_ATTACKERS on dire waves,
# never more than MAX_ATTACKERS.
MAX_ATTACKERS = 20
WAVE_BASE_ATTACKERS = 3
WAVES_PER_EXTRA_ATTACKER = 2
DIRE_EXTRA_ATTACKERS = 5
# Attacker HP grows by this fraction each wave; dire waves multiply it.
WAVE_HP_GROWTH = 0.10
DIRE_HP_MULTIPLIER = 1.5
# How long the defenders have to destroy a wave, in real time.
WAVE_DURATION_MS = 30000

# Each row: name, emoji, altitude, the altitude every second attacker of
# this kind flies at instead, base HP, and the first wave it appears in.
ATTACKER_ROWS = [
    ['9M456 "Pengvin" drone', "🛩️", ALTITUDE_LOW, ALTITUDE_LOW, 30.0, 1],
    ['BGM-14 "Kalibar" cruise missile', "🚀", ALTITUDE_MEDIUM, ALTITUDE_LOW,
     60.0, 4],
    ['B-95 "Mishka" bomber', "✈️", ALTITUDE_HIGH, ALTITUDE_HIGH, 200.0, 8],
]

# Each row: name, emoji, cost, damage per second against high, medium,
# and low altitude attackers, and how many the company owns at the start.
DEFENSE_ROWS = [
    ['9K92 "Zhalo" MANPADS', "🧍", 1500.0, 0.0, 8.0, 15.0, 2],
    ["LoM-16SM fighter", "🛫", 5000.0, 12.0, 12.0, 6.0, 0],
    ['MIN-400 "Loyalist" SAM', "🛡️", 8000.0, 40.0, 10.0, 0.0, 0],
]

# What a failed wave costs: each surviving attacker destroys some stock and
# adds time to an air raid penalty on stocking and delivery.
STOCK_LOSS_PER_SURVIVOR = 10
RAID_PENALTY_MS_PER_SURVIVOR = 3000
MAX_RAID_PENALTY_MS = 60000
RAID_PENALTY_MULTIPLIER = 0.6
# Failing a dire wave also destroys this fraction of each defense type.
DIRE_EQUIPMENT_LOSS_FRACTION = 0.25

# --- W3: the end of the war ---
PAGE_WAR_REPORT = "war_report"
# War goods that must be sold during the war to win it.
WAR_VICTORY_GOODS = 30000
WAR_WON_NEWS = ("CEASEFIRE: The " + ENEMY_COUNTRY + " withdraws! The "
                + "warehouse is declared a 'national hero'.")
WAR_LOST_NEWS = ("CEASEFIRE: The " + HOME_COUNTRY + " signs a humiliating "
                 + "treaty. The warehouse is blamed 'for vibes'.")

# ---------------------------------------------------------------------------
# Emails: the inbox and its catalog of templates
# ---------------------------------------------------------------------------

PAGE_INBOX = "inbox"
# The page that shows one opened email.
PAGE_EMAIL = "email"
# The inbox drops its oldest emails beyond this many.
MAX_INBOX_EMAILS = 20
# The air defense briefing is sent when the threat meter first gets here.
BRIEFING_THREAT = 50.0

SENDER_ADVISOR = "John Johnson, Senior Advisor"
SENDER_HQ = "Corporate HQ"
SENDER_GOVERNMENT = "Government of the " + HOME_COUNTRY

# Trigger keys: send_email(state, key) sends the template with that key.
EMAIL_WELCOME = "welcome"
EMAIL_RESEARCH = "research"
EMAIL_WAR = "war"
EMAIL_FIRST_WAVE = "first wave"
EMAIL_CONFISCATION = "confiscation"

# Each row: trigger key, sender, subject, body, and whether it can be sent
# more than once. "\n" in a body starts a new line on the page.
EMAIL_ROWS = [
    [EMAIL_WELCOME, SENDER_ADVISOR,
     "Welcome aboard (there is no orientation)",
     "Congratulations on your new warehouse. I am John Johnson, your "
     + "Senior Advisor. I advise; you are liable.\n\n"
     + "How the business works, every tick:\n"
     + "1. Procurement Agents buy goods into the warehouse at "
     + CURRENCY_SYMBOL + str(UNIT_COST) + " each, until it is full or you "
     + "are broke.\n"
     + "2. Delivery Vans carry goods to customers. You sell the smallest "
     + "of three numbers: goods in stock, delivery capacity, and customer "
     + "demand.\n"
     + "3. Demand comes from customer loyalty. A higher markup earns more "
     + "per sale and makes customers like you less. They get over it, "
     + "slowly.\n\n"
     + "Start on the Company page: buy an agent and a few vans. Then watch "
     + "which number is holding you back, and buy more of that.\n\n"
     + "Regards,\nJohn Johnson\n"
     + "Sent from my desk, which I am told is temporary",
     False],
    [EMAIL_RESEARCH, SENDER_HQ,
     "Memo: innovation is now permitted",
     "Following a successful quarter, the Board has approved the concept "
     + "of 'ideas'.\n\n"
     + "A Research Lab is open on the Business page. Each project is paid "
     + "for once and works immediately. Some raise stocking or delivery, "
     + "some unlock new equipment, goods, or policies, and some rearrange "
     + "the market in our favor.\n\n"
     + "The 🔬 Research chip at the top of every page counts the projects "
     + "you can start. More appear as lifetime earnings grow.\n\n"
     + "Innovation outside approved projects remains a disciplinary "
     + "matter.\n\nCorporate HQ",
     False],
    [EMAIL_WAR, SENDER_GOVERNMENT,
     "NOTICE: a state of war now exists",
     "Citizen-Enterprise,\n\n"
     + "The " + ENEMY_COUNTRY + " has invaded the " + HOME_COUNTRY
     + ". You are instructed to remain calm and operational.\n\n"
     + "Effective immediately:\n"
     + "- Goods marked 🚫 Sanctioned on the Business page may not be "
     + "sold.\n"
     + "- Essential goods now earn more, as your competitors have "
     + "relocated abroad. The Government has no comment on this.\n"
     + "- A Defense Procurement License is available in your Research "
     + "Lab. War goods sold decide who wins the war. They also make your "
     + "warehouse more interesting to the enemy.\n\n"
     + "A War page has been issued to you. Thank you for your continued "
     + "existence.",
     False],
    [EMAIL_FIRST_WAVE, SENDER_ADVISOR,
     "URGENT: things in the sky (read before wave 1)",
     "The threat meter is half full, so here is everything I know about "
     + "air defense. The enemy will not attack until you have opened this "
     + "email. I asked; they were surprisingly reasonable about it.\n\n"
     + "- The " + ENEMY_COUNTRY + " attacks in " + str(WAVE_COUNT)
     + " waves. A wave starts when the threat meter is full.\n"
     + "- Selling war goods fills the meter faster, but war goods sold "
     + "decide who wins the war.\n"
     + "- Attackers fly high, medium, or low. Each defense is good at "
     + "some altitudes and useless at others.\n"
     + "- Shoot down every attacker before the wave's timer runs out, or "
     + "the survivors destroy stock and cut production for a while.\n"
     + "- Every " + str(DIRE_WAVE_EVERY) + "th wave (and the last) is "
     + "dire: tougher, and losing it damages your defenses.\n"
     + "- Air defense is sold on the War page at any time, even "
     + "mid-wave.\n\n"
     + "I will be advising from the basement.\n\nJohn Johnson",
     False],
    [EMAIL_CONFISCATION, SENDER_GOVERNMENT,
     "Notice of Patriotic Contribution",
     "Citizen-Enterprise,\n\n"
     + "Under the Wartime Logistics Act, a portion of your property has "
     + "been reclassified as 'the State's'.\n\n"
     + "No action is required on your part. No action is possible on your "
     + "part. A receipt will be issued after the war, subject to the "
     + "outcome of the war.",
     True],
]

# ---------------------------------------------------------------------------
# Debug: shortcuts for demos and play-testing
# ---------------------------------------------------------------------------

# Set to False before submitting to hide the 🐞 Debug page.
DEBUG_TOOLS = True
PAGE_DEBUG = "debug"
DEBUG_MONEY_AMOUNTS = [10000, 100000, 1000000]
DEBUG_JUMP_PEACE = "peace"
DEBUG_JUMP_RESEARCH = "research"
DEBUG_JUMP_WAR = "war"
DEBUG_JUMP_THREAT = "threat"
DEBUG_JUMP_WAVE = "wave"
DEBUG_JUMP_DIRE = "dire"
DEBUG_JUMP_LAST = "last"
DEBUG_JUMP_WIN = "win"
DEBUG_JUMP_LOSE = "lose"
DEBUG_JUMP_CONFISCATION = "confiscation"
# Lifetime earnings that make every peacetime research appear.
DEBUG_RESEARCH_EARNED = 25000.0

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
    ["War", "war_page", PAGE_WAR],
    ["Inbox", "inbox_page", PAGE_INBOX],
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
.topbar.static {
  position: static;
}
.topbar .card {
  color: var(--ink);
}
.war-board {
  display: grid;
  gap: 10px;
  max-width: 1100px;
  margin: 10px auto 0 auto;
}
.scroll-list {
  max-height: 260px;
  overflow-y: auto;
}
.list-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 4px 0;
  border-bottom: 1px solid var(--line);
  font-variant-numeric: tabular-nums;
}
.list-row.destroyed {
  color: var(--muted);
  text-decoration: line-through;
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
/* #live_area is only a container for tick Fragments. display: contents
   removes its box from the layout, so the sticky top bar sticks to the
   whole page instead of only to #live_area. */
#live_area {
  display: contents;
}
.email-body {
  white-space: pre-line;
  margin: 10px 0;
}
.news-scroll {
  max-height: 7.5em;
  overflow-y: auto;
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
        is_one_time: Whether it can only be bought once.
        required_research: Research needed for it to appear ("" = none).
        owned: How many units the player has bought.
    """
    name: str
    emoji: str
    base_cost: float
    effect_kind: str
    effect_amount: int
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
        is_war_good: Whether its sales count as war goods sold.
        is_sanctioned: Whether wartime sanctions stop it being sold.
        war_bonus: Extra income bonus during the war.
        is_selling: Whether the company currently sells it.
    """
    name: str
    emoji: str
    input_name: str
    income_bonus: float
    required_research: str
    is_war_good: bool
    is_sanctioned: bool
    war_bonus: float
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
        requires_war: Whether it only appears once the war has started.
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
    requires_war: bool
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
class Attacker:
    """One enemy drone, missile, or bomber in the current wave.

    Attributes:
        name: The attacker's display name.
        emoji: A placeholder picture.
        altitude: One of the ALTITUDE_ constants.
        max_hp: Its starting HP.
        hp: HP left; 0 means it was shot down.
    """
    name: str
    emoji: str
    altitude: str
    max_hp: float
    hp: float


@dataclass
class DefenseEquipment:
    """One kind of air defense the company can buy and keep.

    Attributes:
        name: The equipment's display name.
        emoji: A placeholder picture.
        cost: The price of one unit.
        dps_high: Damage per second against high altitude attackers.
        dps_medium: Damage per second against medium altitude attackers.
        dps_low: Damage per second against low altitude attackers.
        owned: How many units the company owns.
    """
    name: str
    emoji: str
    cost: float
    dps_high: float
    dps_medium: float
    dps_low: float
    owned: int


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
class Email:
    """One email in the player's inbox, copied from a row of EMAIL_ROWS.

    Attributes:
        key: The EMAIL_ trigger key of the template it was built from.
        sender: Who the email is from.
        subject: The subject line.
        body: The full text; "\\n" starts a new line.
        tick_received: The value of State.tick_count when it arrived.
        is_read: Whether the player has opened it.
    """
    key: str
    sender: str
    subject: str
    body: str
    tick_received: int
    is_read: bool


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
        game_phase: One of the PHASE_ constants (peace, war, war over).
        war_goods_sold: War goods sold since the war started.
        threat: How close the next enemy attack is, from 0 to MAX_THREAT.
        attackers: The attackers in the current wave (empty between waves).
        defenses: Every kind of air defense and how many are owned.
        wave_number: The number of waves started so far.
        wave_ms_left: Milliseconds left in the current wave (0 = no wave).
        waves_defended: How many waves were destroyed in time.
        raid_ms_left: Milliseconds left of the air raid production penalty.
        last_wave_report: A summary of how the latest wave ended.
        inbox: The newest MAX_INBOX_EMAILS emails, newest first.
        sent_email_keys: The key of every template sent so far, so a
            once-only email is never sent twice (one entry per template).
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
    game_phase: str
    war_goods_sold: int
    threat: float
    attackers: list[Attacker]
    defenses: list[DefenseEquipment]
    wave_number: int
    wave_ms_left: int
    waves_defended: int
    raid_ms_left: int
    last_wave_report: str
    inbox: list[Email]
    sent_email_keys: list[str]


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
                             row[6], 0))
    return items


def make_starting_goods() -> list[GoodsType]:
    """Build fresh GoodsTypes so the global rows are never modified.

    Returns:
        A new list with one unselected GoodsType per goods row.
    """
    goods_types = []
    for row in STARTING_GOODS_ROWS:
        goods_types.append(GoodsType(row[0], row[1], row[2], row[3], row[4],
                                     row[5], row[6], row[7], False))
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
                                 row[10], row[11], row[12], row[13],
                                 False))
    return research


def make_starting_defenses() -> list[DefenseEquipment]:
    """Build fresh DefenseEquipment so the global rows are never modified.

    Returns:
        A new list with one DefenseEquipment per row of DEFENSE_ROWS.
    """
    defenses = []
    for row in DEFENSE_ROWS:
        defenses.append(DefenseEquipment(row[0], row[1], row[2], row[3],
                                         row[4], row[5], row[6]))
    return defenses


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
        game_phase=PHASE_PEACE,
        war_goods_sold=0,
        threat=0.0,
        attackers=[],
        defenses=make_starting_defenses(),
        wave_number=0,
        wave_ms_left=0,
        waves_defended=0,
        raid_ms_left=0,
        last_wave_report="",
        inbox=[],
        sent_email_keys=[],
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
        A repeatable BuyItem that needs no research.
    """
    return BuyItem("Test", "T", 100.0, effect_kind, effect_amount, False,
                   NO_REQUIREMENT, owned)


def make_one_time_item(owned: int) -> BuyItem:
    """Build a simple one-time item for the helper tests.

    Args:
        owned: How many units are already owned (0 or 1).

    Returns:
        A one-time BuyItem that is always unlocked.
    """
    return BuyItem("Once", "O", 100.0, EFFECT_UNLOCK, 1, True,
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
                     False, False, 0.0, is_selling)


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
        A new-game State with the company name set and the welcome email.
    """
    state = make_new_state()
    state.company_name = "Boxes"
    send_email(state, EMAIL_WELCOME)
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
                    False, is_done)


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


def make_veteran_electronics_state() -> State:
    """Build the veteran State while it sells Electronics, before the war.

    Returns:
        A peacetime State that will start the war and is selling
        Electronics.
    """
    state = make_veteran_state()
    state.goods_types[2].is_selling = True
    return state


def make_war_state() -> State:
    """Build a State in the war that sells War Supplies and Household Goods.

    Returns:
        A wartime State with 10 units sold in the latest tick.
    """
    state = make_new_state()
    state.game_phase = PHASE_WAR
    state.total_earned = WAR_START_EARNED
    state.goods_types[0].is_selling = True
    state.goods_types[3].is_selling = True
    state.goods_sold_last_tick = 10
    return state


def make_nearly_threatened_state() -> State:
    """Build the war State with the threat meter almost full.

    Returns:
        The war State with the threat one point below full.
    """
    state = make_war_state()
    state.threat = MAX_THREAT - 1
    return state


def make_test_attacker(altitude: str, hp: float) -> Attacker:
    """Build an attacker with the given altitude and HP for tests.

    Args:
        altitude: One of the ALTITUDE_ constants.
        hp: Its HP (also its max HP).

    Returns:
        An Attacker named "Test".
    """
    return Attacker("Test", "T", altitude, hp, hp)


def make_briefed_threat_state() -> State:
    """Build the nearly threatened war State after the War briefing.

    Returns:
        A war State whose next tick fills the meter and starts wave 1.
    """
    state = make_nearly_threatened_state()
    skip_briefing(state)
    return state


def make_unbriefed_war_state() -> State:
    """Build the war State with the air defense briefing still unread.

    Returns:
        A war State whose first wave is waiting for the player.
    """
    state = make_war_state()
    send_email(state, EMAIL_FIRST_WAVE)
    return state


def make_inbox_state() -> State:
    """Build a new-game State with two unread emails, viewing the Inbox.

    Returns:
        A State on the Inbox page: research email first, then welcome.
    """
    state = make_new_state()
    state.current_page = PAGE_INBOX
    send_email(state, EMAIL_WELCOME)
    send_email(state, EMAIL_RESEARCH)
    return state


def expected_after_opening_welcome() -> State:
    """Build the State expected after opening the older of two emails.

    Returns:
        The inbox State showing the welcome email, which is now read.
    """
    state = make_inbox_state()
    state.current_page = PAGE_EMAIL
    state.inbox[1].is_read = True
    return state


def make_wave_state() -> State:
    """Build a war State in wave 1 with one weak drone left.

    The 2 starting MANPADS deal 30 low damage per second.

    Returns:
        A war State whose next 1000 ms tick wins the wave.
    """
    state = make_war_state()
    skip_briefing(state)
    state.wave_number = 1
    state.wave_ms_left = 1000
    state.attackers = [make_test_attacker(ALTITUDE_LOW, 5.0)]
    return state


def make_losing_wave_state() -> State:
    """Build a war State in wave 1 that its defenses can't win.

    Returns:
        A war State with a strong bomber, 500 ms left, and 50 in stock.
    """
    state = make_wave_state()
    state.wave_ms_left = 500
    state.goods_in_stock = 50
    state.attackers = [make_test_attacker(ALTITUDE_HIGH, 500.0)]
    return state


def make_rich_war_state() -> State:
    """Build the war State with 10000 money and some stock.

    Returns:
        A war State that can afford any air defense.
    """
    state = make_war_state()
    state.money = 10000.0
    state.goods_in_stock = 10
    return state


def expected_after_buying_manpads() -> State:
    """Build the State expected after buying one MANPADS on the War page.

    Returns:
        The rich war State on the War page, with a third MANPADS.
    """
    state = make_rich_war_state()
    state.current_page = PAGE_WAR
    state.money = 10000.0 - DEFENSE_ROWS[0][2]
    state.defenses[0].owned = 3
    return state


def make_last_wave_state(war_goods_sold: int) -> State:
    """Build a war State fighting the last wave, about to win it.

    Args:
        war_goods_sold: War goods sold so far.

    Returns:
        A war State in wave WAVE_COUNT with one weak drone left.
    """
    state = make_wave_state()
    state.wave_number = WAVE_COUNT
    state.waves_defended = WAVE_COUNT - 1
    state.war_goods_sold = war_goods_sold
    return state


def make_finished_war_state(war_goods_sold: int) -> State:
    """Build a State whose war is over.

    Args:
        war_goods_sold: War goods sold during the war.

    Returns:
        A war-over State after all WAVE_COUNT waves.
    """
    state = make_war_state()
    state.game_phase = PHASE_WAR_OVER
    skip_briefing(state)
    state.wave_number = WAVE_COUNT
    state.waves_defended = 30
    state.war_goods_sold = war_goods_sold
    return state


def make_report_view_state(war_goods_sold: int) -> State:
    """Build the finished war State while it views the war report.

    Args:
        war_goods_sold: War goods sold during the war.

    Returns:
        The finished war State with the war report page showing.
    """
    state = make_finished_war_state(war_goods_sold)
    state.current_page = PAGE_WAR_REPORT
    return state


def make_war_view_state() -> State:
    """Build the war State while it views the War page.

    Returns:
        The war State with the War page showing.
    """
    state = make_war_state()
    state.current_page = PAGE_WAR
    return state


def make_expected_war_page(state: State) -> Page:
    """Build the War page expected for a given State.

    Args:
        state: The State the page should show.

    Returns:
        The expected War page.
    """
    return Page(state, build_war_content(state))


def make_debug_state() -> State:
    """Build a new-game State that is viewing the Debug page.

    Returns:
        A new-game State whose current page is the Debug page.
    """
    state = make_new_state()
    state.current_page = PAGE_DEBUG
    return state


def make_expected_debug_page(state: State) -> Page:
    """Build the Debug page expected for a given State.

    Args:
        state: The State the page should show.

    Returns:
        The expected Debug page.
    """
    return Page(state, build_debug_content(state))


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
                      research: list[Research], game_phase: str) -> None:
    """Record which goods types the player chose to sell.

    Goods whose required research isn't done, or that sanctions ban,
    stay unsold.

    Args:
        goods_types: The goods types to update.
        choices: One True or False per goods type, in the same order.
        research: Every research project.
        game_phase: One of the PHASE_ constants.
    """
    for index, goods in enumerate(goods_types):
        goods.is_selling = (choices[index]
                            and is_requirement_met(goods.required_research,
                                                   research)
                            and not is_sanctioned_now(goods, game_phase))


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
# Emails: sending, counting, and reading the inbox
# ---------------------------------------------------------------------------

def find_email_row(key: str) -> list:
    """Find the email template with a trigger key (a linear search).

    Args:
        key: One of the EMAIL_ trigger keys.

    Returns:
        The matching row of EMAIL_ROWS, or an empty list if none matches.
    """
    for row in EMAIL_ROWS:
        if row[0] == key:
            return row
    return []


assert_equal(find_email_row(EMAIL_WELCOME)[1], SENDER_ADVISOR)
assert_equal(find_email_row("no such key"), [])


def add_email(inbox: list[Email], email: Email) -> list[Email]:
    """Put an email first, dropping the oldest if the inbox is full.

    Args:
        inbox: The current emails, newest first.
        email: The new email.

    Returns:
        A new list of at most MAX_INBOX_EMAILS emails.
    """
    return [email] + inbox[:MAX_INBOX_EMAILS - 1]


assert_equal(add_email([], Email("k", "a", "b", "c", 0, False)),
             [Email("k", "a", "b", "c", 0, False)])
assert_equal(len(add_email([Email("k", "a", "b", "c", 0, False)]
                           * MAX_INBOX_EMAILS,
                           Email("new", "a", "b", "c", 1, False))),
             MAX_INBOX_EMAILS)


def send_email(state: State, key: str) -> None:
    """Add the email with a trigger key to the inbox, unread.

    A template is sent only once, unless its row marks it repeatable.

    Args:
        state: The game state to update.
        key: One of the EMAIL_ trigger keys.
    """
    row = find_email_row(key)
    was_sent = key in state.sent_email_keys
    if row and (row[4] or not was_sent):
        if not was_sent:
            state.sent_email_keys.append(key)
        state.inbox = add_email(state.inbox, Email(
            row[0], row[1], row[2], row[3], state.tick_count, False))


def state_after_emails(keys: list[str]) -> State:
    """Send several emails to a new-game State and return it.

    Args:
        keys: The EMAIL_ trigger keys to send, in order.

    Returns:
        A new-game State after send_email for each key.
    """
    state = make_new_state()
    for key in keys:
        send_email(state, key)
    return state


assert_equal(state_after_emails([EMAIL_WELCOME]).inbox[0].sender,
             SENDER_ADVISOR)
assert_equal(state_after_emails([EMAIL_WELCOME]).inbox[0].is_read, False)
# The newest email comes first.
assert_equal(state_after_emails(
    [EMAIL_WELCOME, EMAIL_RESEARCH]).inbox[0].key, EMAIL_RESEARCH)
# A once-only email is not sent twice; a repeatable one is.
assert_equal(len(state_after_emails([EMAIL_WELCOME, EMAIL_WELCOME]).inbox),
             1)
assert_equal(len(state_after_emails(
    [EMAIL_CONFISCATION, EMAIL_CONFISCATION]).inbox), 2)
assert_equal(state_after_emails(
    [EMAIL_CONFISCATION, EMAIL_CONFISCATION]).sent_email_keys,
    [EMAIL_CONFISCATION])
# The inbox never grows past its maximum size.
assert_equal(len(state_after_emails(
    [EMAIL_CONFISCATION] * (MAX_INBOX_EMAILS + 5)).inbox), MAX_INBOX_EMAILS)


def count_unread(inbox: list[Email]) -> int:
    """Count the emails the player hasn't opened.

    Args:
        inbox: The emails to count.

    Returns:
        How many are unread.
    """
    count = 0
    for email in inbox:
        if not email.is_read:
            count = count + 1
    return count


assert_equal(count_unread([]), 0)
assert_equal(count_unread(make_inbox_state().inbox), 2)
assert_equal(count_unread(expected_after_opening_welcome().inbox), 1)


def is_email_unread(inbox: list[Email], key: str) -> bool:
    """Check whether an email with a trigger key is waiting to be read.

    Args:
        inbox: The emails to search.
        key: One of the EMAIL_ trigger keys.

    Returns:
        True if the inbox holds an unread email with that key.
    """
    for email in inbox:
        if email.key == key and not email.is_read:
            return True
    return False


assert_equal(is_email_unread([], EMAIL_FIRST_WAVE), False)
assert_equal(is_email_unread(make_unbriefed_war_state().inbox,
                             EMAIL_FIRST_WAVE), True)


def skip_briefing(state: State) -> None:
    """Deliver the air defense briefing (if needed) and mark it read.

    Used by the debug jumps and by tests, so waves can start right away.

    Args:
        state: The game state to update.
    """
    send_email(state, EMAIL_FIRST_WAVE)
    for email in state.inbox:
        if email.key == EMAIL_FIRST_WAVE:
            email.is_read = True


# make_wave_state uses skip_briefing: its briefing is delivered and read.
assert_equal(len(make_wave_state().inbox), 1)
assert_equal(is_email_unread(make_wave_state().inbox, EMAIL_FIRST_WAVE),
             False)


def inbox_badge(inbox: list[Email]) -> str:
    """Build the unread count shown on the Inbox nav button.

    It depends only on the inbox (never on money), so the nav buttons are
    redrawn only when an email arrives or is opened.

    Args:
        inbox: The player's emails.

    Returns:
        Text like " (2)", or "" when everything is read.
    """
    unread = count_unread(inbox)
    if unread == 0:
        return ""
    return " (" + str(unread) + ")"


assert_equal(inbox_badge([]), "")
assert_equal(inbox_badge(make_inbox_state().inbox), " (2)")


def can_open_email(inbox: list[Email], email_index: int) -> bool:
    """Check that a position in the inbox holds an email.

    Args:
        inbox: The player's emails.
        email_index: The position to check.

    Returns:
        True if the index is inside the inbox.
    """
    return 0 <= email_index and email_index < len(inbox)


assert_equal(can_open_email(make_inbox_state().inbox, 1), True)
assert_equal(can_open_email(make_inbox_state().inbox, 2), False)
assert_equal(can_open_email([], 0), False)


# ---------------------------------------------------------------------------
# War: the war economy (sanctions, war goods, and the threat meter)
# ---------------------------------------------------------------------------

def is_wartime(game_phase: str) -> bool:
    """Check whether the war has started (it may already be over).

    Sanctions and wartime bonuses stay after the war ends.

    Args:
        game_phase: One of the PHASE_ constants.

    Returns:
        True unless the game is still at peace.
    """
    return game_phase != PHASE_PEACE


assert_equal(is_wartime(PHASE_PEACE), False)
assert_equal(is_wartime(PHASE_WAR), True)
assert_equal(is_wartime(PHASE_WAR_OVER), True)


def goods_war_bonus(goods: GoodsType, game_phase: str) -> float:
    """Find the extra income bonus a goods type gets during the war.

    Args:
        goods: The goods type.
        game_phase: One of the PHASE_ constants.

    Returns:
        Its war bonus in wartime, otherwise 0.
    """
    if is_wartime(game_phase):
        return goods.war_bonus
    return 0.0


assert_equal(goods_war_bonus(make_new_state().goods_types[1], PHASE_PEACE),
             0.0)
assert_equal(goods_war_bonus(make_new_state().goods_types[1], PHASE_WAR),
             0.25)


def is_sanctioned_now(goods: GoodsType, game_phase: str) -> bool:
    """Check whether sanctions stop a goods type from being sold.

    Args:
        goods: The goods type.
        game_phase: One of the PHASE_ constants.

    Returns:
        True if it is a sanctioned goods type and the war has started.
    """
    return goods.is_sanctioned and is_wartime(game_phase)


assert_equal(is_sanctioned_now(make_new_state().goods_types[2], PHASE_PEACE),
             False)
assert_equal(is_sanctioned_now(make_new_state().goods_types[2], PHASE_WAR),
             True)


def war_units_sold(units_sold: int, goods_types: list[GoodsType]) -> int:
    """Estimate how many of the units sold were war goods.

    Sales are one combined number, so the war goods' share is the number
    of war goods types being sold out of all goods types being sold.

    Args:
        units_sold: Units sold in a tick.
        goods_types: Every goods type.

    Returns:
        The war goods' share of the units, rounded down.
    """
    selling_count = 0
    war_count = 0
    for goods in goods_types:
        if goods.is_selling:
            selling_count = selling_count + 1
            if goods.is_war_good:
                war_count = war_count + 1
    if selling_count == 0:
        return 0
    return units_sold * war_count // selling_count


assert_equal(war_units_sold(10, make_war_state().goods_types), 5)
assert_equal(war_units_sold(10, make_new_state().goods_types), 0)


def threat_per_second(war_units: int) -> float:
    """Calculate how fast the threat meter fills.

    Args:
        war_units: War goods sold in the latest tick.

    Returns:
        Threat points per second, capped, times DEBUG_WAR_SPEED.
    """
    rate = THREAT_PER_SECOND + war_units * THREAT_PER_WAR_UNIT
    if rate > MAX_THREAT_PER_SECOND:
        rate = MAX_THREAT_PER_SECOND
    return rate * DEBUG_WAR_SPEED


assert_equal(threat_per_second(0), THREAT_PER_SECOND * DEBUG_WAR_SPEED)
assert_equal(threat_per_second(20),
             (THREAT_PER_SECOND + 1.0) * DEBUG_WAR_SPEED)
assert_equal(threat_per_second(100000),
             MAX_THREAT_PER_SECOND * DEBUG_WAR_SPEED)


def add_threat(threat: float, per_second: float, interval_ms: int) -> float:
    """Fill the threat meter for one tick, stopping at MAX_THREAT.

    Using the tick length in milliseconds keeps the fill speed the same
    in real seconds even if ticks get faster.

    Args:
        threat: The current threat.
        per_second: Threat points added per second.
        interval_ms: The length of one tick in milliseconds.

    Returns:
        The new threat value.
    """
    new_threat = threat + per_second * interval_ms / 1000
    if new_threat > MAX_THREAT:
        return MAX_THREAT
    return new_threat


assert_equal(add_threat(10.0, 2.0, 500), 11.0)
assert_equal(add_threat(99.5, 2.0, 1000), MAX_THREAT)


def is_dire_wave(wave_number: int) -> bool:
    """Check whether a wave is a dire wave (every 10th, and the last).

    Args:
        wave_number: The wave's number, starting at 1.

    Returns:
        True for a dire wave.
    """
    return wave_number % DIRE_WAVE_EVERY == 0 or wave_number == WAVE_COUNT


assert_equal(is_dire_wave(9), False)
assert_equal(is_dire_wave(10), True)
assert_equal(is_dire_wave(WAVE_COUNT), True)


def attacker_count(wave_number: int) -> int:
    """Calculate how many attackers a wave has.

    Args:
        wave_number: The wave's number, starting at 1.

    Returns:
        The number of attackers, never more than MAX_ATTACKERS.
    """
    count = WAVE_BASE_ATTACKERS + wave_number // WAVES_PER_EXTRA_ATTACKER
    if is_dire_wave(wave_number):
        count = count + DIRE_EXTRA_ATTACKERS
    return min(count, MAX_ATTACKERS)


assert_equal(attacker_count(1), 3)
assert_equal(attacker_count(10), 13)
assert_equal(attacker_count(WAVE_COUNT), MAX_ATTACKERS)


def wave_hp_multiplier(wave_number: int) -> float:
    """Calculate how much tougher a wave's attackers are than wave 1's.

    Args:
        wave_number: The wave's number, starting at 1.

    Returns:
        The HP multiplier, bigger on dire waves.
    """
    multiplier = 1 + WAVE_HP_GROWTH * (wave_number - 1)
    if is_dire_wave(wave_number):
        multiplier = multiplier * DIRE_HP_MULTIPLIER
    return multiplier


assert_equal(wave_hp_multiplier(1), 1.0)
assert_equal(round(wave_hp_multiplier(3), 2), 1.2)
assert_equal(round(wave_hp_multiplier(10), 2), 2.85)


def attacker_rows_for_wave(wave_number: int) -> list[list]:
    """Find the kinds of attackers that have appeared by this wave.

    Args:
        wave_number: The wave's number, starting at 1.

    Returns:
        The rows of ATTACKER_ROWS whose first wave has been reached.
    """
    rows = []
    for row in ATTACKER_ROWS:
        if row[5] <= wave_number:
            rows.append(row)
    return rows


assert_equal(len(attacker_rows_for_wave(1)), 1)
assert_equal(len(attacker_rows_for_wave(8)), 3)


def make_attacker(row: list, copy_number: int,
                  hp_multiplier: float) -> Attacker:
    """Build one attacker from a row of ATTACKER_ROWS.

    Args:
        row: The attacker's row.
        copy_number: How many of this kind are already in the wave; every
            second one flies at the row's second altitude.
        hp_multiplier: The wave's HP multiplier.

    Returns:
        A new Attacker at full HP.
    """
    altitude = row[2]
    if copy_number % 2 == 1:
        altitude = row[3]
    hp = float(round(row[4] * hp_multiplier))
    return Attacker(row[0], row[1], altitude, hp, hp)


assert_equal(make_attacker(ATTACKER_ROWS[1], 0, 2.0).altitude,
             ALTITUDE_MEDIUM)
assert_equal(make_attacker(ATTACKER_ROWS[1], 1, 2.0).altitude, ALTITUDE_LOW)
assert_equal(make_attacker(ATTACKER_ROWS[1], 1, 2.0).hp, 120.0)


def make_wave(wave_number: int) -> list[Attacker]:
    """Generate a wave's attackers from its number (no hand-written list).

    Kinds take turns: with drones and missiles unlocked, the wave goes
    drone, missile, drone, missile, and so on.

    Args:
        wave_number: The wave's number, starting at 1.

    Returns:
        The wave's attackers, at most MAX_ATTACKERS of them.
    """
    rows = attacker_rows_for_wave(wave_number)
    hp_multiplier = wave_hp_multiplier(wave_number)
    attackers = []
    for index in range(attacker_count(wave_number)):
        row = rows[index % len(rows)]
        attackers.append(make_attacker(row, index // len(rows),
                                       hp_multiplier))
    return attackers


assert_equal(make_wave(1), [Attacker(ATTACKER_ROWS[0][0], "🛩️", ALTITUDE_LOW,
                                     30.0, 30.0)] * 3)
assert_equal(len(make_wave(WAVE_COUNT)), MAX_ATTACKERS)


def wave_duration_ms() -> int:
    """Find how long a wave lasts, sped up by DEBUG_WAR_SPEED.

    Returns:
        The wave length in milliseconds.
    """
    return WAVE_DURATION_MS // DEBUG_WAR_SPEED


assert_equal(wave_duration_ms(), WAVE_DURATION_MS // DEBUG_WAR_SPEED)


def defense_dps(defense: DefenseEquipment, altitude: str) -> float:
    """Find one unit's damage per second against an altitude.

    Args:
        defense: The equipment.
        altitude: One of the ALTITUDE_ constants.

    Returns:
        Its damage per second at that altitude.
    """
    if altitude == ALTITUDE_HIGH:
        return defense.dps_high
    if altitude == ALTITUDE_MEDIUM:
        return defense.dps_medium
    return defense.dps_low


assert_equal(defense_dps(make_new_state().defenses[2], ALTITUDE_HIGH), 40.0)
assert_equal(defense_dps(make_new_state().defenses[0], ALTITUDE_LOW), 15.0)


def total_dps(defenses: list[DefenseEquipment], altitude: str) -> float:
    """Add up the damage per second of every owned defense at an altitude.

    Args:
        defenses: Every kind of air defense.
        altitude: One of the ALTITUDE_ constants.

    Returns:
        The combined damage per second.
    """
    total = 0.0
    for defense in defenses:
        total = total + defense.owned * defense_dps(defense, altitude)
    return total


# A new game owns 2 MANPADS: 2 x 15 low and 2 x 8 medium.
assert_equal(total_dps(make_new_state().defenses, ALTITUDE_LOW), 30.0)
assert_equal(total_dps(make_new_state().defenses, ALTITUDE_MEDIUM), 16.0)
assert_equal(total_dps(make_new_state().defenses, ALTITUDE_HIGH), 0.0)


def damage_attackers(attackers: list[Attacker], altitude: str,
                     damage: float) -> None:
    """Hit the first living attacker at an altitude, carrying over leftovers.

    Args:
        attackers: The wave's attackers.
        altitude: The altitude this damage can reach.
        damage: The damage to deal this tick.
    """
    for attacker in attackers:
        if damage <= 0:
            return
        if attacker.altitude == altitude and attacker.hp > 0:
            hit = min(attacker.hp, damage)
            attacker.hp = attacker.hp - hit
            damage = damage - hit


def attackers_after_damage(damage: float) -> list[Attacker]:
    """Deal low altitude damage to a small test wave.

    Args:
        damage: The damage to deal.

    Returns:
        The test wave (10 HP low, 50 HP high, 10 HP low) after the damage.
    """
    attackers = [make_test_attacker(ALTITUDE_LOW, 10.0),
                 make_test_attacker(ALTITUDE_HIGH, 50.0),
                 make_test_attacker(ALTITUDE_LOW, 10.0)]
    damage_attackers(attackers, ALTITUDE_LOW, damage)
    return attackers


# 15 damage kills the first drone and carries 5 to the next low one; the
# high attacker is out of reach.
assert_equal(attackers_after_damage(15.0)[0].hp, 0.0)
assert_equal(attackers_after_damage(15.0)[1].hp, 50.0)
assert_equal(attackers_after_damage(15.0)[2].hp, 5.0)


def enemy_hp(attackers: list[Attacker], altitude: str) -> float:
    """Add up the HP left of the attackers at an altitude.

    Args:
        attackers: The wave's attackers.
        altitude: One of the ALTITUDE_ constants.

    Returns:
        The total HP left at that altitude.
    """
    total = 0.0
    for attacker in attackers:
        if attacker.altitude == altitude:
            total = total + attacker.hp
    return total


assert_equal(enemy_hp(attackers_after_damage(15.0), ALTITUDE_LOW), 5.0)


def count_survivors(attackers: list[Attacker]) -> int:
    """Count the attackers that haven't been shot down.

    Args:
        attackers: The wave's attackers.

    Returns:
        How many have HP left.
    """
    count = 0
    for attacker in attackers:
        if attacker.hp > 0:
            count = count + 1
    return count


assert_equal(count_survivors(attackers_after_damage(15.0)), 2)
assert_equal(count_survivors([]), 0)


def is_wave_active(state: State) -> bool:
    """Check whether a wave is being fought right now.

    Args:
        state: The current game state.

    Returns:
        True if the current wave still has time left.
    """
    return state.wave_ms_left > 0


assert_equal(is_wave_active(make_new_state()), False)
assert_equal(is_wave_active(make_wave_state()), True)


def war_badge(state: State) -> str:
    """Build the badge for the War nav button.

    Args:
        state: The current game state.

    Returns:
        " ⚠️" during a wave, " 📜" after the war, else "".
    """
    if state.game_phase == PHASE_WAR_OVER:
        return " 📜"
    if is_wave_active(state):
        return " ⚠️"
    return ""


assert_equal(war_badge(make_new_state()), "")
assert_equal(war_badge(make_war_state()), "")
assert_equal(war_badge(make_wave_state()), " ⚠️")
assert_equal(war_badge(make_finished_war_state(0)), " 📜")


def wave_start_headline(wave_number: int, count: int) -> str:
    """Build the World News headline for a wave starting.

    Args:
        wave_number: The wave's number.
        count: How many attackers it has.

    Returns:
        The headline, louder for a dire wave.
    """
    text = ("Wave " + str(wave_number) + "/" + str(WAVE_COUNT) + ": "
            + str(count) + " attackers inbound from the " + ENEMY_COUNTRY
            + "!")
    if is_dire_wave(wave_number):
        return "☠️ DIRE " + text
    return "🚨 " + text


assert_equal(wave_start_headline(1, 3),
             "🚨 Wave 1/" + str(WAVE_COUNT) + ": 3 attackers inbound from the "
             + ENEMY_COUNTRY + "!")
assert_equal("DIRE Wave 10/" in wave_start_headline(10, 13), True)


def start_wave(state: State) -> None:
    """Start the next wave and empty the threat meter.

    Args:
        state: The game state to update.
    """
    state.wave_number = state.wave_number + 1
    state.attackers = make_wave(state.wave_number)
    state.wave_ms_left = wave_duration_ms()
    state.threat = 0.0
    state.news_feed = add_news(state.news_feed, wave_start_headline(
        state.wave_number, len(state.attackers)))


def is_war_won(war_goods_sold: int) -> bool:
    """Check whether enough war goods were sold to win the war.

    Args:
        war_goods_sold: War goods sold during the war.

    Returns:
        True if it reached WAR_VICTORY_GOODS.
    """
    return war_goods_sold >= WAR_VICTORY_GOODS


assert_equal(is_war_won(WAR_VICTORY_GOODS - 1), False)
assert_equal(is_war_won(WAR_VICTORY_GOODS), True)


def finish_war(state: State) -> None:
    """End the war: switch to the war-over phase and post the outcome.

    The economy keeps running afterwards.

    Args:
        state: The game state to update.
    """
    state.game_phase = PHASE_WAR_OVER
    state.attackers = []
    state.wave_ms_left = 0
    state.threat = 0.0
    if is_war_won(state.war_goods_sold):
        state.news_feed = add_news(state.news_feed, WAR_WON_NEWS)
    else:
        state.news_feed = add_news(state.news_feed, WAR_LOST_NEWS)


def raid_multiplier(raid_ms_left: int) -> float:
    """Find the multiplier air raid damage applies to stocking and delivery.

    Args:
        raid_ms_left: Milliseconds left of the air raid penalty.

    Returns:
        RAID_PENALTY_MULTIPLIER during the penalty, otherwise 1.0.
    """
    if raid_ms_left > 0:
        return RAID_PENALTY_MULTIPLIER
    return 1.0


assert_equal(raid_multiplier(0), 1.0)
assert_equal(raid_multiplier(500), RAID_PENALTY_MULTIPLIER)


def lose_dire_equipment(defenses: list[DefenseEquipment]) -> int:
    """Destroy part of each kind of air defense after a failed dire wave.

    Args:
        defenses: Every kind of air defense.

    Returns:
        How many units were destroyed in total.
    """
    total_lost = 0
    for defense in defenses:
        lost = int(defense.owned * DIRE_EQUIPMENT_LOSS_FRACTION)
        defense.owned = defense.owned - lost
        total_lost = total_lost + lost
    return total_lost


# 2 MANPADS lose int(0.5) = 0; 8 SAMs would lose 2.
assert_equal(lose_dire_equipment(make_new_state().defenses), 0)
assert_equal(lose_dire_equipment([DefenseEquipment("S", "S", 1.0, 1.0, 1.0,
                                                   1.0, 8)]), 2)


def apply_raid_damage(state: State, survivors: int) -> str:
    """Apply the damage done by attackers that got through.

    Each survivor destroys some stock and adds to the production penalty;
    a failed dire wave also destroys some air defense.

    Args:
        state: The game state to update.
        survivors: How many attackers got through.

    Returns:
        A short description of the damage.
    """
    stock_lost = min(state.goods_in_stock, survivors * STOCK_LOSS_PER_SURVIVOR)
    state.goods_in_stock = state.goods_in_stock - stock_lost
    state.raid_ms_left = min(MAX_RAID_PENALTY_MS, state.raid_ms_left
                             + survivors * RAID_PENALTY_MS_PER_SURVIVOR)
    text = (str(stock_lost) + " units destroyed, production cut for "
            + str(state.raid_ms_left // 1000) + "s")
    if is_dire_wave(state.wave_number):
        lost = lose_dire_equipment(state.defenses)
        if lost > 0:
            text = (text + ", " + str(lost)
                    + " air defense units destroyed")
    return text


def end_wave(state: State) -> None:
    """Finish the current wave: record a win, or apply the raid damage.

    After the last wave, this also ends the war.

    Args:
        state: The game state to update.
    """
    survivors = count_survivors(state.attackers)
    label = "Wave " + str(state.wave_number)
    if survivors == 0:
        state.waves_defended = state.waves_defended + 1
        state.last_wave_report = (label + " repelled: every attacker was "
                                  + "shot down.")
    else:
        damage = apply_raid_damage(state, survivors)
        state.last_wave_report = (label + " broke through: "
                                  + str(survivors) + " attackers hit the "
                                  + "warehouse (" + damage + ").")
    state.news_feed = add_news(state.news_feed, state.last_wave_report)
    state.attackers = []
    state.wave_ms_left = 0
    if state.wave_number >= WAVE_COUNT:
        finish_war(state)


def run_wave(state: State, interval_ms: int) -> None:
    """Fight the current wave for one tick.

    Each altitude's total damage this tick hits that altitude's attackers.
    The wave ends when all are shot down or its time runs out.

    Args:
        state: The game state to update.
        interval_ms: The length of one tick in milliseconds.
    """
    for altitude in ALTITUDES:
        damage = total_dps(state.defenses, altitude) * interval_ms / 1000
        damage_attackers(state.attackers, altitude, damage)
    state.wave_ms_left = state.wave_ms_left - interval_ms
    if count_survivors(state.attackers) == 0 or state.wave_ms_left <= 0:
        end_wave(state)


def state_after_wave_tick(state: State) -> State:
    """Fight one 1000 ms tick of a wave and return the State.

    Args:
        state: The State to update.

    Returns:
        The same State, after run_wave.
    """
    run_wave(state, 1000)
    return state


# The MANPADS shoot down the last drone: the wave is won.
assert_equal(state_after_wave_tick(make_wave_state()).waves_defended, 1)
assert_equal(state_after_wave_tick(make_wave_state()).wave_ms_left, 0)
# The bomber survives the time limit: stock is lost and production is cut.
assert_equal(state_after_wave_tick(make_losing_wave_state()).goods_in_stock,
             40)
assert_equal(state_after_wave_tick(make_losing_wave_state()).raid_ms_left,
             RAID_PENALTY_MS_PER_SURVIVOR)
assert_equal(state_after_wave_tick(make_losing_wave_state()).waves_defended,
             0)
# Ending the last wave ends the war; war goods sold decide the outcome.
assert_equal(state_after_wave_tick(
    make_last_wave_state(WAR_VICTORY_GOODS)).game_phase, PHASE_WAR_OVER)
assert_equal(state_after_wave_tick(
    make_last_wave_state(WAR_VICTORY_GOODS)).news_feed[0], WAR_WON_NEWS)
assert_equal(state_after_wave_tick(make_last_wave_state(0)).news_feed[0],
             WAR_LOST_NEWS)


def run_intermission(state: State, war_units: int, interval_ms: int) -> None:
    """Fill the threat meter between waves; start a wave when it is full.

    The air defense briefing email is sent once the meter reaches
    BRIEFING_THREAT. No wave starts while that email is unread, and no
    wave starts after the last one.

    Args:
        state: The game state to update.
        war_units: War goods sold in the latest tick.
        interval_ms: The length of one tick in milliseconds.
    """
    old_threat = state.threat
    state.threat = add_threat(old_threat, threat_per_second(war_units),
                              interval_ms)
    if state.threat >= BRIEFING_THREAT:
        send_email(state, EMAIL_FIRST_WAVE)
    if state.threat == MAX_THREAT:
        is_briefed = not is_email_unread(state.inbox, EMAIL_FIRST_WAVE)
        if is_briefed and state.wave_number < WAVE_COUNT:
            start_wave(state)
        elif old_threat < MAX_THREAT:
            state.news_feed = add_news(state.news_feed, SIRENS_NEWS)


def start_war(state: State) -> None:
    """Start the war: change the phase, apply sanctions, post the news.

    Args:
        state: The game state to update.
    """
    state.game_phase = PHASE_WAR
    for goods in state.goods_types:
        if goods.is_sanctioned:
            goods.is_selling = False
    state.news_feed = add_news(state.news_feed, SANCTIONS_NEWS)
    state.news_feed = add_news(state.news_feed, WAR_START_NEWS)
    send_email(state, EMAIL_WAR)


def run_war_economy(state: State, interval_ms: int) -> None:
    """Start the war when earnings are high enough, or run its economy.

    During the war, this counts war goods sold, then either fights the
    current wave or fills the threat meter between waves (it uses
    goods_sold_last_tick, so call it after run_selling). After the war,
    only the air raid penalty keeps counting down.

    Args:
        state: The game state to update.
        interval_ms: The length of one tick in milliseconds.
    """
    if state.game_phase == PHASE_PEACE:
        if state.total_earned >= WAR_START_EARNED:
            start_war(state)
    elif state.game_phase == PHASE_WAR_OVER:
        state.raid_ms_left = max(0, state.raid_ms_left - interval_ms)
    else:
        war_units = war_units_sold(state.goods_sold_last_tick,
                                   state.goods_types)
        state.war_goods_sold = state.war_goods_sold + war_units
        state.raid_ms_left = max(0, state.raid_ms_left - interval_ms)
        if is_wave_active(state):
            run_wave(state, interval_ms)
        else:
            run_intermission(state, war_units, interval_ms)


def state_after_war_economy(state: State) -> State:
    """Run the war economy for one 1000 ms tick and return the State.

    Args:
        state: The State to update.

    Returns:
        The same State, after run_war_economy.
    """
    run_war_economy(state, 1000)
    return state


# Too little earned: still at peace.
assert_equal(state_after_war_economy(make_new_state()).game_phase,
             PHASE_PEACE)
# Enough earned: war starts, Electronics is banned, and the news says so.
assert_equal(state_after_war_economy(make_veteran_state()).game_phase,
             PHASE_WAR)
assert_equal(state_after_war_economy(make_veteran_state()).news_feed[0],
             WAR_START_NEWS)
# During the war: 5 of 10 units were war goods, and the threat fills.
assert_equal(state_after_war_economy(make_war_state()).war_goods_sold, 5)
assert_equal(state_after_war_economy(make_war_state()).threat,
             threat_per_second(5))
# The meter tops out at MAX_THREAT and the sirens headline is posted once.
assert_equal(state_after_war_economy(make_nearly_threatened_state()).threat,
             MAX_THREAT)
assert_equal(state_after_war_economy(
    make_nearly_threatened_state()).news_feed[0], SIRENS_NEWS)
# The war email arrives when the war starts.
assert_equal(state_after_war_economy(make_veteran_state()).inbox[0].key,
             EMAIL_WAR)
# The briefing email arrives unread, and wave 1 waits for it to be read.
assert_equal(is_email_unread(state_after_war_economy(
    make_nearly_threatened_state()).inbox, EMAIL_FIRST_WAVE), True)
assert_equal(state_after_war_economy(
    make_nearly_threatened_state()).wave_number, 0)
# After the briefing, a full meter starts wave 1 and empties.
assert_equal(state_after_war_economy(make_briefed_threat_state()).wave_number,
             1)
assert_equal(state_after_war_economy(make_briefed_threat_state()).threat, 0.0)
# During a wave, the defenses fight it (here they win).
assert_equal(state_after_war_economy(make_wave_state()).waves_defended, 1)
# Sanctioned goods selected before the war stop being sold (and lose their
# bonus) the moment it starts.
assert_equal(state_after_war_economy(
    make_veteran_electronics_state()).goods_types[2].is_selling, False)


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
                          total_earned: float, game_phase: str) -> bool:
    """Check whether a project can be researched now, ignoring money.

    Args:
        project: The project to check.
        research: Every research project, to look up the prerequisite.
        total_earned: The player's lifetime earnings.
        game_phase: One of the PHASE_ constants.

    Returns:
        True if it is unfinished, its prerequisite is done, the player
        has earned enough, and (for war research) the war has started.
    """
    return (not project.is_done
            and total_earned >= project.unlock_at_earned
            and is_requirement_met(project.prerequisite, research)
            and (not project.requires_war or is_wartime(game_phase)))


assert_equal(is_research_available(make_test_research("A", "", False), [],
                                   99.0, PHASE_PEACE), False)
assert_equal(is_research_available(make_test_research("A", "", False), [],
                                   100.0, PHASE_PEACE), True)
assert_equal(is_research_available(make_test_research("A", "", True), [],
                                   100.0, PHASE_PEACE), False)
assert_equal(is_research_available(
    make_test_research("B", "A", False),
    [make_test_research("A", "", False)], 100.0, PHASE_PEACE), False)
# The Defense Procurement License only appears once the war starts.
assert_equal(is_research_available(make_new_state().research[8], [],
                                   WAR_START_EARNED, PHASE_PEACE), False)
assert_equal(is_research_available(make_new_state().research[8], [],
                                   WAR_START_EARNED, PHASE_WAR), True)


def count_available_research(research: list[Research], total_earned: float,
                             game_phase: str) -> int:
    """Count the projects that can be researched now, ignoring money.

    The Business nav badge shows this number. It ignores money so the
    badge (and the buttons around it) never redraw when money changes.

    Args:
        research: Every research project.
        total_earned: The player's lifetime earnings.
        game_phase: One of the PHASE_ constants.

    Returns:
        How many projects are available.
    """
    count = 0
    for project in research:
        if is_research_available(project, research, total_earned,
                                 game_phase):
            count = count + 1
    return count


assert_equal(count_available_research(make_new_state().research, 0.0,
                                      PHASE_PEACE), 0)
assert_equal(count_available_research(make_new_state().research, 1000.0,
                                      PHASE_PEACE), 4)


def run_email_triggers(state: State) -> None:
    """Send the emails that depend on game progress; called every tick.

    Only the research email is checked here. The war emails are sent by
    start_war and run_intermission, and the welcome email by start_game.

    Args:
        state: The game state to update.
    """
    if EMAIL_RESEARCH not in state.sent_email_keys:
        if count_available_research(state.research, state.total_earned,
                                    state.game_phase) > 0:
            send_email(state, EMAIL_RESEARCH)


def state_after_email_triggers(state: State) -> State:
    """Run the email triggers once and return the State.

    Args:
        state: The State to update.

    Returns:
        The same State, after run_email_triggers.
    """
    run_email_triggers(state)
    return state


# No research is available in a new game, so no email is sent.
assert_equal(state_after_email_triggers(make_new_state()).inbox, [])
# Once research is available, the research email arrives (only once).
assert_equal(state_after_email_triggers(
    make_research_state()).inbox[0].key, EMAIL_RESEARCH)
assert_equal(len(state_after_email_triggers(state_after_email_triggers(
    make_research_state())).inbox), 1)


def safe_money_required(cost: float, goods_in_stock: int) -> float:
    """Calculate the money needed to safely pay for research or defenses.

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


assert_equal(safe_money_required(800.0, 5), 800.0)
assert_equal(safe_money_required(800.0, 0), 800.0 + UNIT_COST)


def can_buy_research(state: State, research_index: int) -> bool:
    """Check whether a research project can be bought right now.

    Args:
        state: The current game state.
        research_index: The project's position in state.research.

    Returns:
        True if it is available and the player can afford it.
    """
    project = state.research[research_index]
    required = safe_money_required(project.cost, state.goods_in_stock)
    available = is_research_available(project, state.research,
                                      state.total_earned, state.game_phase)
    return available and required <= state.money


assert_equal(can_buy_research(make_research_state(), 0), True)
assert_equal(can_buy_research(make_poor_research_state(), 0), False)
assert_equal(can_buy_research(make_new_state(), 0), False)


def can_buy_defense(state: State, defense_index: int) -> bool:
    """Check whether one unit of air defense can be bought right now.

    Equipment can be bought during a wave as well as between waves.

    Args:
        state: The current game state.
        defense_index: The equipment's position in state.defenses.

    Returns:
        True if the war has started and the player can afford it.
    """
    cost = state.defenses[defense_index].cost
    required = safe_money_required(cost, state.goods_in_stock)
    return is_wartime(state.game_phase) and required <= state.money


assert_equal(can_buy_defense(make_rich_war_state(), 0), True)
assert_equal(can_buy_defense(make_war_state(), 0), False)
assert_equal(can_buy_defense(make_rich_state(), 0), False)


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


def goods_income_bonus(goods: GoodsType, research: list[Research],
                       game_phase: str) -> float:
    """Find a goods type's income bonus, including research and the war.

    Args:
        goods: The goods type.
        research: Every research project.
        game_phase: One of the PHASE_ constants.

    Returns:
        Its own bonus, plus each completed research for it, plus its
        wartime bonus.
    """
    total = goods.income_bonus + goods_war_bonus(goods, game_phase)
    for project in research:
        if project.is_done and project.goods_name == goods.name:
            total = total + project.goods_bonus
    return total


assert_equal(goods_income_bonus(make_test_goods(0.25, True),
                                [make_test_research("A", "", True)],
                                PHASE_PEACE), 0.75)
assert_equal(goods_income_bonus(make_test_goods(0.25, True),
                                [make_test_research("A", "", False)],
                                PHASE_PEACE), 0.25)
assert_equal(goods_income_bonus(make_new_state().goods_types[1], [],
                                PHASE_WAR), 0.35)


def total_extra_goods_bonus(research: list[Research],
                            goods_types: list[GoodsType],
                            game_phase: str) -> float:
    """Add up the research and wartime boosts for goods being sold.

    total_goods_bonus already counts each goods type's own bonus, so this
    adds only the extra part that research and the war give.

    Args:
        research: Every research project.
        goods_types: Every goods type.
        game_phase: One of the PHASE_ constants.

    Returns:
        The extra income bonus, as a fraction.
    """
    total = 0.0
    for goods in goods_types:
        if goods.is_selling:
            total = (total + goods_income_bonus(goods, research, game_phase)
                     - goods.income_bonus)
    return total


assert_equal(total_extra_goods_bonus([make_test_research("A", "", True)],
                                     [make_test_goods(0.25, True)],
                                     PHASE_PEACE), 0.5)
assert_equal(total_extra_goods_bonus([make_test_research("A", "", True)],
                                     [make_test_goods(0.25, False)],
                                     PHASE_PEACE), 0.0)
# War Supplies gets no war bonus; Household Goods gets +10%.
assert_equal(round(total_extra_goods_bonus([], make_war_state().goods_types,
                                           PHASE_WAR), 2), 0.1)


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
                         penalty_multiplier: float) -> int:
    """Apply percentage bonuses and any penalties to a per-tick rate.

    Args:
        base_rate: The rate before modifiers.
        bonus_fraction: The combined policy, research, and item bonus.
        penalty_multiplier: Strike and air raid penalties (1.0 = none).

    Returns:
        The final rate, rounded down to a whole number of units.
    """
    multiplier = (1 + bonus_fraction) * penalty_multiplier
    return int(round(base_rate * multiplier, 2))


assert_equal(apply_rate_modifiers(10, 0.0, 1.0), 10)
assert_equal(apply_rate_modifiers(10, 0.5, 1.0), 15)
assert_equal(apply_rate_modifiers(10, 0.5, 0.5), 7)


def rate_penalty(state: State) -> float:
    """Combine the strike and air raid penalties on stocking and delivery.

    Args:
        state: The current game state.

    Returns:
        The multiplier, from 1.0 (no penalty) down.
    """
    return (strike_multiplier(state.strike_ticks_left)
            * raid_multiplier(state.raid_ms_left))


assert_equal(rate_penalty(make_new_state()), 1.0)
assert_equal(rate_penalty(make_striking_state(1)), STRIKE_PENALTY_MULTIPLIER)


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
                                rate_penalty(state))


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
                                rate_penalty(state))


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
            + total_extra_goods_bonus(state.research, state.goods_types,
                                      state.game_phase)
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


def is_item_visible(item: BuyItem, research: list[Research]) -> bool:
    """Check whether the item's research is done or it was already bought.

    Items never unlock from earnings alone, only through research, which
    the player buys with a click. So a tick can never make one appear.

    Args:
        item: The item to check.
        research: Every research project.

    Returns:
        True if the item needs no research, its research is done, or it
        is already owned.
    """
    return (item.owned > 0
            or is_requirement_met(item.required_research, research))


assert_equal(is_item_visible(make_test_item(EFFECT_STOCKING, 1, 0), []), True)
# The marketing campaign and pickup truck stay hidden until researched.
assert_equal(is_item_visible(make_new_state().buy_items[2],
                             make_new_state().research), False)
assert_equal(is_item_visible(make_new_state().buy_items[5],
                             make_new_state().research), False)
assert_equal(is_item_visible(make_new_state().buy_items[5],
                             make_finished_research_state(2).research), True)
assert_equal(is_item_visible(make_new_state().buy_items[0],
                             make_new_state().research), True)


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
    """Summarize what decides whether a tick must redraw #live_area.

    The tick compares this text with the previous tick's. If they match,
    it replaces only #live_numbers, which holds no buttons, so it can't
    interrupt a click. Money never counts: buttons stay on screen whether
    or not the player can afford them. Neither do new buy items, which
    only appear through research (a click). The Company page's buttons
    sit outside #live_area, so even a redraw leaves them alone.

    Args:
        state: The current game state.

    Returns:
        Text recording the news, the game phase, the War badge, and the
        Inbox badge, plus the available research count when the Research
        page is open.
    """
    signature = (str(state.news_feed) + state.game_phase + war_badge(state)
                 + inbox_badge(state.inbox))
    # The Research page lists available projects inside #live_area.
    if state.current_page == PAGE_RESEARCH:
        signature = signature + str(count_available_research(
            state.research, state.total_earned, state.game_phase))
    return signature


# Money and lifetime earnings never change the signature.
assert_equal(controls_signature(make_new_state()),
             controls_signature(make_rich_state()))
assert_equal(controls_signature(make_new_state()),
             controls_signature(make_veteran_state()))
# The war's headlines and new phase do.
assert_equal(controls_signature(make_new_state())
             == controls_signature(make_war_state()), False)
# On the Research page, newly available research does too.
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
                         + percent_text(goods_income_bonus(
                             goods, state.research, state.game_phase))
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


def threat_text(state: State) -> str:
    """Describe the threat meter and how fast it is filling.

    Args:
        state: The current game state.

    Returns:
        Text like "40% (+2.5/s)".
    """
    war_units = war_units_sold(state.goods_sold_last_tick, state.goods_types)
    rate = threat_per_second(war_units)
    return (str(int(state.threat * 100 // MAX_THREAT)) + "% (+"
            + str(round(rate, 1)) + "/s)")


assert_equal(threat_text(make_nearly_threatened_state()),
             "99% (+" + str(round(threat_per_second(5), 1)) + "/s)")


def build_research_chips(state: State) -> list[Div]:
    """Build the chip counting research the player can start now.

    Args:
        state: The current game state.

    Returns:
        One "🔬 Research" chip, or none when nothing is available.
    """
    available = count_available_research(state.research, state.total_earned,
                                         state.game_phase)
    if available == 0:
        return []
    return [build_chip("🔬 Research", str(available) + " available",
                       "chip")]


assert_equal(build_research_chips(make_new_state()), [])
assert_equal(build_research_chips(make_research_state()),
             [build_chip("🔬 Research", "4 available", "chip")])


def build_war_chips(state: State) -> list[Div]:
    """Build the war chips shown on every page once the war starts.

    Args:
        state: The current game state.

    Returns:
        The threat and war goods chips (none during peace).
    """
    if not is_wartime(state.game_phase):
        return []
    chips = []
    if state.game_phase == PHASE_WAR:
        if state.threat >= MAX_THREAT:
            chips.append(build_chip("⚠️ Threat", threat_text(state),
                                    "chip warn"))
        else:
            chips.append(build_chip("⚠️ Threat", threat_text(state), "chip"))
    chips.append(build_chip("War goods sold", str(state.war_goods_sold),
                            "chip"))
    return chips


assert_equal(build_war_chips(make_new_state()), [])
assert_equal(len(build_war_chips(make_war_state())), 2)


def seconds_until_wave(state: State) -> int:
    """Estimate the seconds until the threat meter fills.

    Args:
        state: The current game state.

    Returns:
        Whole seconds left at the current fill speed.
    """
    war_units = war_units_sold(state.goods_sold_last_tick, state.goods_types)
    return int((MAX_THREAT - state.threat) / threat_per_second(war_units))


assert_equal(seconds_until_wave(make_war_state()),
             int(MAX_THREAT / threat_per_second(5)))


def wave_status_text(state: State) -> str:
    """Describe what the war is doing right now.

    Args:
        state: The current game state.

    Returns:
        The wave and its time left, or the countdown to the next wave.
    """
    if is_wave_active(state):
        return ("Wave " + str(state.wave_number) + "/" + str(WAVE_COUNT)
                + " · " + str((state.wave_ms_left + 999) // 1000) + "s left")
    if state.wave_number >= WAVE_COUNT:
        return "Last wave fought"
    if is_email_unread(state.inbox, EMAIL_FIRST_WAVE):
        return "Read your Inbox"
    return ("Wave " + str(state.wave_number + 1) + " in ~"
            + str(seconds_until_wave(state)) + "s")


assert_equal(wave_status_text(make_unbriefed_war_state()), "Read your Inbox")
assert_equal(wave_status_text(make_wave_state()),
             "Wave 1/" + str(WAVE_COUNT) + " · 1s left")


def build_wave_chips(state: State) -> list[Div]:
    """Build the War page chips: wave status, waves defended, raid damage.

    Args:
        state: The current game state.

    Returns:
        The War page's extra chips.
    """
    chips = []
    if is_wave_active(state):
        chips.append(build_chip("Status", wave_status_text(state),
                                "chip warn"))
    else:
        chips.append(build_chip("Status", wave_status_text(state), "chip"))
    chips.append(build_chip("Waves defended", str(state.waves_defended) + " / "
                            + str(state.wave_number), "chip"))
    if state.raid_ms_left > 0:
        penalty = round((1 - RAID_PENALTY_MULTIPLIER) * 100)
        chips.append(build_chip("Air raid damage",
                                "-" + str(penalty) + "% output for "
                                + str((state.raid_ms_left + 999) // 1000)
                                + "s", "chip warn"))
    return chips


assert_equal(len(build_wave_chips(make_war_state())), 2)


def build_attacker_row(attacker: Attacker) -> Div:
    """Build one line of the attacker list.

    Args:
        attacker: The attacker to show.

    Returns:
        A row with its name, altitude, and HP (crossed out if shot down).
    """
    name_text = attacker.emoji + " " + attacker.name
    if attacker.hp <= 0:
        return Div(Span(name_text), Span("💥 shot down"),
                   classes="list-row destroyed")
    return Div(Span(name_text),
               Span(attacker.altitude + " · " + str(round(attacker.hp)) + "/"
                    + str(round(attacker.max_hp)) + " HP"),
               classes="list-row")


def build_attacker_card(state: State) -> Div:
    """Build the scrollable list of the current wave's attackers.

    Args:
        state: The current game state.

    Returns:
        A card listing every attacker, or a note between waves.
    """
    title = ("Incoming (" + str(count_survivors(state.attackers))
             + " left)")
    rows = []
    for attacker in state.attackers:
        rows.append(build_attacker_row(attacker))
    if len(rows) == 0:
        rows.append(Div("Skies are clear.", classes="muted"))
    return Div(build_card_head(title, []), Div(rows, classes="scroll-list"),
               classes="card")


def dps_text(high: float, medium: float, low: float) -> str:
    """Describe damage per second at each altitude.

    Args:
        high: Damage per second against high altitude.
        medium: Damage per second against medium altitude.
        low: Damage per second against low altitude.

    Returns:
        Text like "H 40 · M 10 · L 0 DPS".
    """
    return ("H " + str(round(high)) + " · M " + str(round(medium)) + " · L "
            + str(round(low)) + " DPS")


assert_equal(dps_text(40.0, 10.0, 0.0), "H 40 · M 10 · L 0 DPS")


def build_defender_card(state: State) -> Div:
    """Build the list of owned air defense and its damage per second.

    Args:
        state: The current game state.

    Returns:
        A card with one row per kind of equipment owned.
    """
    rows = []
    for defense in state.defenses:
        if defense.owned > 0:
            rows.append(Div(
                Span(defense.emoji + " " + defense.name + " ×"
                     + str(defense.owned)),
                Span(dps_text(defense.owned * defense.dps_high,
                              defense.owned * defense.dps_medium,
                              defense.owned * defense.dps_low)),
                classes="list-row"))
    if len(rows) == 0:
        rows.append(Div("No air defense! Buy some below.", classes="muted"))
    return Div(build_card_head("Our Air Defense", []), Div(rows),
               classes="card")


def kill_time_text(hp: float, dps: float) -> str:
    """Describe how long our defenses need to clear an altitude.

    Args:
        hp: The enemy HP left at that altitude.
        dps: Our damage per second at that altitude.

    Returns:
        "clear", "out of reach!", or the seconds needed.
    """
    if hp <= 0:
        return "clear"
    if dps <= 0:
        return "out of reach!"
    return "~" + str(round(hp / dps, 1)) + "s"


assert_equal(kill_time_text(0.0, 0.0), "clear")
assert_equal(kill_time_text(50.0, 0.0), "out of reach!")
assert_equal(kill_time_text(50.0, 20.0), "~2.5s")


def build_altitude_summary(state: State) -> Div:
    """Build the enemy HP vs our damage per second for each altitude.

    Args:
        state: The current game state.

    Returns:
        A card with one row per altitude and the latest wave report.
    """
    rows = [build_card_head("Altitude Summary", [])]
    for altitude in ALTITUDES:
        hp = enemy_hp(state.attackers, altitude)
        dps = total_dps(state.defenses, altitude)
        rows.append(Div(
            Span(altitude.capitalize()),
            Span("enemy " + str(round(hp)) + " HP · ours " + str(round(dps))
                 + " DPS · " + kill_time_text(hp, dps)),
            classes="list-row"))
    if state.last_wave_report != "":
        rows.append(Div(state.last_wave_report, classes="muted"))
    return Div(rows, classes="card")


def build_war_board(state: State) -> Div:
    """Build the battle board that every tick refreshes on the War page.

    It holds no buttons, so a tick can't swallow a click.

    Args:
        state: The current game state.

    Returns:
        The attacker list, defender list, and altitude summary.
    """
    return Div(Div(build_attacker_card(state), build_defender_card(state),
                   classes="two-col"),
               build_altitude_summary(state), classes="war-board")


def build_defense_row(defense: DefenseEquipment, defense_index: int) -> Div:
    """Build one row of the air defense shop.

    Args:
        defense: The equipment to sell.
        defense_index: Its position in state.defenses.

    Returns:
        A buy row with the equipment's damage and a Buy button.
    """
    return Div(
        Span(defense.emoji, classes="emoji"),
        Div(Div(defense.name, classes="item-name"),
            Div("Each: " + dps_text(defense.dps_high, defense.dps_medium,
                                    defense.dps_low), classes="muted")),
        Button("Buy for " + format_money(defense.cost), "buy_defense",
               [Argument("defense_index", defense_index)]),
        classes="buy-row",
    )


def build_defense_shop(state: State) -> Div:
    """Build the card for buying air defense.

    Args:
        state: The current game state.

    Returns:
        A card with one buy row per kind of equipment.
    """
    rows = [build_card_head("Air Defense Shop", [])]
    for defense_index, defense in enumerate(state.defenses):
        rows.append(build_defense_row(defense, defense_index))
    return Div(rows, classes="card")


def war_report_lines(state: State) -> list[str]:
    """Summarize the war for the victory and defeat pages.

    Args:
        state: The current game state.

    Returns:
        One line each for waves defended, waves lost, and war goods sold.
    """
    return [
        "Waves defended: " + str(state.waves_defended) + " of "
        + str(state.wave_number),
        "Waves that broke through: "
        + str(state.wave_number - state.waves_defended),
        "War goods sold: " + str(state.war_goods_sold) + " (needed "
        + str(WAR_VICTORY_GOODS) + " to win)",
    ]


assert_equal(war_report_lines(make_finished_war_state(100))[1],
             "Waves that broke through: 5")


def build_war_report_content(state: State, is_victory: bool) -> list:
    """Build the victory or defeat page.

    Args:
        state: The current game state.
        is_victory: Whether to show the victory page.

    Returns:
        A list of the page's components.
    """
    if is_victory:
        title = "🏆 Victory"
        message = ("The " + ENEMY_COUNTRY + " ran out of patience before "
                   + "the warehouse ran out of war goods.")
    else:
        title = "🏳️ Defeat"
        message = ("The front collapsed for lack of supplies. Somewhere, a "
                   + "spreadsheet says it was not our fault.")
    return [
        Div(build_live_content(state), id="live_area"),
        Div(Div(build_card_head(title, []), Div(message),
                BulletedList(war_report_lines(state)), classes="card"),
            Div(build_card_head("Epilogue", []),
                Div("The ending of Untitled Warehouse Inc. arrives in a "
                    + "later update. The warehouse keeps running.",
                    classes="muted"),
                Button("Back to the Company", "company_page"),
                classes="card"),
            classes="page two-col"),
    ]


def build_war_content(state: State) -> list:
    """Build the War page's content.

    The shop sits outside the live area, so ticks never redraw its
    buttons. (The briefing is an email in the Inbox.)

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    live_area = Div(build_live_content(state), id="live_area")
    if not is_wartime(state.game_phase):
        return [live_area, Div(Div(build_card_head("War", []),
                                   Div("All quiet... for now.",
                                       classes="muted"), classes="card"),
                               classes="page")]
    return [live_area, Div(build_defense_shop(state), classes="page")]


def build_live_numbers(state: State) -> list:
    """Build the numbers that change every tick; they contain no buttons.

    Args:
        state: The current game state.

    Returns:
        A list of the components inside the #live_numbers element.
    """
    chips = ([build_chip("Money", format_money(state.money), "chip money")]
             + build_research_chips(state) + build_war_chips(state))
    if state.current_page == PAGE_WAR:
        return [Div(chips + build_wave_chips(state), classes="chips"),
                build_war_board(state)]
    if state.current_page != PAGE_COMPANY:
        return [Div(chips, classes="chips")]
    chips = chips + build_stat_chips(state) + build_policy_chips(state)
    return [Div(chips, classes="chips"), build_effect_tags(state)]


def nav_section(current_page: str) -> str:
    """Find which nav button a page belongs to.

    Args:
        current_page: One of the PAGE_ constants.

    Returns:
        PAGE_BUSINESS for Research, PAGE_WAR for the war report, otherwise
        the page itself.
    """
    if current_page == PAGE_RESEARCH:
        return PAGE_BUSINESS
    if current_page == PAGE_WAR_REPORT:
        return PAGE_WAR
    if current_page == PAGE_EMAIL:
        return PAGE_INBOX
    return current_page


assert_equal(nav_section(PAGE_RESEARCH), PAGE_BUSINESS)
assert_equal(nav_section(PAGE_CASINO), PAGE_CASINO)
assert_equal(nav_section(PAGE_EMAIL), PAGE_INBOX)


def nav_label(row: list, war_alert: str, inbox_alert: str) -> str:
    """Build a nav button's text, adding the War or Inbox badge.

    The research count is a chip in #live_numbers instead of a badge
    here, so it can change without redrawing the nav buttons. The unread
    email count is a badge because it rarely changes.

    Args:
        row: One row of NAV_ROWS.
        war_alert: The War badge text from war_badge.
        inbox_alert: The Inbox badge text from inbox_badge.

    Returns:
        The button text, like "War ⚠️" or "Inbox (2)".
    """
    if row[2] == PAGE_WAR:
        return row[0] + war_alert
    if row[2] == PAGE_INBOX:
        return row[0] + inbox_alert
    return row[0]


assert_equal(nav_label(NAV_ROWS[1], "", ""), "Business")
assert_equal(nav_label(NAV_ROWS[0], " ⚠️", " (2)"), "Company")
assert_equal(nav_label(NAV_ROWS[4], " ⚠️", " (2)"), "War ⚠️")
assert_equal(nav_label(NAV_ROWS[5], " ⚠️", " (2)"), "Inbox (2)")


def build_nav(state: State) -> Div:
    """Build the navigation buttons, marking the page being shown.

    Args:
        state: The current game state.

    Returns:
        A Div holding one Button per main page.
    """
    buttons = []
    for row in NAV_ROWS:
        label = nav_label(row, war_badge(state), inbox_badge(state.inbox))
        # The War button only appears once the war has started.
        if row[2] != PAGE_WAR or is_wartime(state.game_phase):
            if row[2] == nav_section(state.current_page):
                buttons.append(Button(label, row[1], classes="current"))
            else:
                buttons.append(Button(label, row[1]))
    if DEBUG_TOOLS:
        if state.current_page == PAGE_DEBUG:
            buttons.append(Button("🐞", "debug_page", classes="current"))
        else:
            buttons.append(Button("🐞", "debug_page"))
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
        classes=top_bar_classes(state.current_page),
    )


def top_bar_classes(current_page: str) -> str:
    """Choose the top bar's CSS classes.

    On the War page the live numbers include the whole battle board, so
    the bar scrolls with the page instead of sticking to the top.

    Args:
        current_page: One of the PAGE_ constants.

    Returns:
        "topbar static" on the War page, otherwise "topbar".
    """
    if current_page == PAGE_WAR:
        return "topbar static"
    return "topbar"


assert_equal(top_bar_classes(PAGE_WAR), "topbar static")
assert_equal(top_bar_classes(PAGE_COMPANY), "topbar")


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
        if is_item_visible(item, state.research):
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
               Div(BulletedList(state.news_feed), classes="news-scroll"),
               classes="card")


def build_email_row(email: Email, email_index: int) -> Div:
    """Build one row of the Inbox list.

    Args:
        email: The email to show.
        email_index: Its position in state.inbox.

    Returns:
        A row with a read/unread icon, the subject, the sender, and an
        Open button.
    """
    icon = "📩"
    if email.is_read:
        icon = "✉️"
    return Div(
        Span(icon, classes="emoji"),
        Div(Div(email.subject, classes="item-name"),
            Div(email.sender + " · tick " + str(email.tick_received),
                classes="muted")),
        Button("Open", "open_email", [Argument("email_index", email_index)]),
        classes="buy-row",
    )


def build_inbox_list(state: State) -> Div:
    """Build the Inbox card: one row per email, newest first.

    Args:
        state: The current game state.

    Returns:
        A card listing every email in the inbox.
    """
    rows = [build_card_head("Inbox", []),
            Div(str(count_unread(state.inbox)) + " unread of "
                + str(len(state.inbox)) + " · 📩 means unread",
                classes="muted")]
    for email_index, email in enumerate(state.inbox):
        rows.append(build_email_row(email, email_index))
    return Div(rows, classes="card narrow")


def build_inbox_content(state: State) -> list:
    """Build the Inbox page's content.

    The list sits inside the live area, so an email that arrives while
    the page is open shows up at once (and every Open button keeps
    pointing at the right email).

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    return [Div(build_live_content(state), id="live_area")]


def build_email_content(state: State, email: Email) -> list:
    """Build the page that shows one opened email.

    Args:
        state: The current game state.
        email: The email to show.

    Returns:
        A list of the page's components.
    """
    return [
        Div(build_live_content(state), id="live_area"),
        Div(Div(build_card_head(email.subject, []),
                Div("From: " + email.sender + " · received on tick "
                    + str(email.tick_received), classes="muted"),
                Div(email.body, classes="email-body"),
                Button("Back to Inbox", "inbox_page"),
                classes="card narrow"),
            classes="page"),
    ]


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
    if state.current_page == PAGE_DEBUG:
        return [build_top_bar(state)]
    if state.current_page == PAGE_WAR:
        return [build_top_bar(state)]
    if state.current_page == PAGE_WAR_REPORT:
        return [build_top_bar(state)]
    if state.current_page == PAGE_EMAIL:
        return [build_top_bar(state)]
    if state.current_page == PAGE_INBOX:
        return [build_top_bar(state),
                Div(build_inbox_list(state), classes="page")]
    if state.current_page == PAGE_ARTIFACTS:
        return [build_top_bar(state),
                Div(build_expedition_controls(state), classes="page")]
    if state.current_page == PAGE_RESEARCH:
        return [build_top_bar(state),
                Div(build_research_list(state),
                    build_completed_research(state),
                    classes="page two-col")]
    return [build_top_bar(state),
            Div(build_news_feed(state), classes="page")]


def build_company_controls(state: State) -> Div:
    """Build the Company page's Buy list and Pricing cards.

    They sit outside #live_area, so no tick ever redraws these buttons.
    They change only when a click route draws the whole page.

    Args:
        state: The current game state.

    Returns:
        The two-column grid holding the Buy list and markup controls.
    """
    return Div(Div(build_buy_list(state)), Div(build_markup_controls(state)),
               classes="page dashboard")


assert_equal(build_company_controls(make_new_state()),
             Div(Div(build_buy_list(make_new_state())),
                 Div(build_markup_controls(make_new_state())),
                 classes="page dashboard"))


def build_company_content(state: State) -> list:
    """Build the company page's content, without any Clock.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    return [Div(build_live_content(state), id="live_area"),
            build_company_controls(state)]


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
            rows.append(build_goods_row(goods, state))
    rows.append(Button("Save Goods", "save_goods"))
    return Div(rows, classes="card")


def goods_detail_text(goods: GoodsType, state: State) -> str:
    """Build the small text beside a goods type's name.

    Args:
        goods: The goods type.
        state: The current game state.

    Returns:
        Its income bonus, and a note if it is a war good.
    """
    text = (percent_text(goods_income_bonus(goods, state.research,
                                            state.game_phase)) + " income")
    if goods.is_war_good:
        return text + " · ⚔️ war good"
    return text


assert_equal(goods_detail_text(make_new_state().goods_types[0],
                               make_new_state()), "+5% income")
assert_equal(goods_detail_text(make_new_state().goods_types[3],
                               make_new_state()),
             "+100% income · ⚔️ war good")


def build_goods_row(goods: GoodsType, state: State) -> Div:
    """Build one goods type's CheckBox row, or a note if it's sanctioned.

    Args:
        goods: The goods type.
        state: The current game state.

    Returns:
        A check row for the goods type.
    """
    name_text = goods.emoji + " " + goods.name
    if is_sanctioned_now(goods, state.game_phase):
        return Div(Span("🚫"), Span(name_text),
                   Span("Sanctioned: can't be sold", classes="muted"),
                   classes="check-row")
    return Div(CheckBox(goods.input_name, goods.is_selling), Span(name_text),
               Span(goods_detail_text(goods, state), classes="muted"),
               classes="check-row")


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
        if is_research_available(project, state.research, state.total_earned,
                                 state.game_phase):
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
    send_email(state, EMAIL_WELCOME)
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
# is locked or sanctioned has no CheckBox on the page, so the browser sends
# no value for it, and Drafter uses the default instead.
@route
def save_goods(state: State, sell_household: bool = False,
               sell_canned_food: bool = False,
               sell_electronics: bool = False,
               sell_war_supplies: bool = False,
               sell_imported_luxuries: bool = False,
               sell_body_armor: bool = False,
               sell_drone_parts: bool = False) -> Page:
    """Save which goods types the company sells.

    Args:
        state: The current game state.
        sell_household: Whether Household Goods is checked.
        sell_canned_food: Whether Canned Food is checked.
        sell_electronics: Whether Electronics is checked.
        sell_war_supplies: Whether War Supplies is checked.
        sell_imported_luxuries: Whether Imported Luxuries is checked.
        sell_body_armor: Whether Body Armor is checked.
        sell_drone_parts: Whether Drone Components is checked.

    Returns:
        The refreshed Business page.
    """
    set_goods_choices(state.goods_types,
                      [sell_household, sell_canned_food, sell_electronics,
                       sell_war_supplies, sell_imported_luxuries,
                       sell_body_armor, sell_drone_parts],
                      state.research, state.game_phase)
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
# During the war, sanctioned Electronics can't be sold.
assert_equal(save_goods(make_war_state(), False, False, True,
                        False).state.goods_types[2].is_selling, False)


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
def war_victory_page(state: State) -> Page:
    """Show the victory page with a summary of the war.

    Args:
        state: The current game state.

    Returns:
        The victory page.
    """
    state.current_page = PAGE_WAR_REPORT
    return Page(state, build_war_report_content(state, True))


assert_equal(war_victory_page(make_finished_war_state(WAR_VICTORY_GOODS)),
             Page(make_report_view_state(WAR_VICTORY_GOODS),
                  build_war_report_content(
                      make_report_view_state(WAR_VICTORY_GOODS), True)))


@route
def war_defeat_page(state: State) -> Page:
    """Show the defeat page with a summary of the war.

    Args:
        state: The current game state.

    Returns:
        The defeat page.
    """
    state.current_page = PAGE_WAR_REPORT
    return Page(state, build_war_report_content(state, False))


assert_equal(war_defeat_page(make_finished_war_state(0)),
             Page(make_report_view_state(0),
                  build_war_report_content(make_report_view_state(0),
                                           False)))


@route
def war_page(state: State) -> Page:
    """Show the War page: the battle board, briefing, and defense shop.

    After the war, it shows the victory or defeat page instead.

    Args:
        state: The current game state.

    Returns:
        The War page.
    """
    if state.game_phase == PHASE_WAR_OVER:
        if is_war_won(state.war_goods_sold):
            return war_victory_page(state)
        return war_defeat_page(state)
    state.current_page = PAGE_WAR
    return Page(state, build_war_content(state))


assert_equal(war_page(make_war_state()),
             make_expected_war_page(make_war_view_state()))
# After the war, the War page shows the right report.
assert_equal(war_page(make_finished_war_state(WAR_VICTORY_GOODS)),
             war_victory_page(make_finished_war_state(WAR_VICTORY_GOODS)))
assert_equal(war_page(make_finished_war_state(0)),
             war_defeat_page(make_finished_war_state(0)))


@route
def inbox_page(state: State) -> Page:
    """Show the Inbox: the list of emails the company has received.

    Args:
        state: The current game state.

    Returns:
        The Inbox page.
    """
    state.current_page = PAGE_INBOX
    return Page(state, build_inbox_content(state))


assert_equal(inbox_page(state_after_emails([EMAIL_WELCOME, EMAIL_RESEARCH])),
             Page(make_inbox_state(),
                  build_inbox_content(make_inbox_state())))


@route
def open_email(state: State, email_index: int) -> Page:
    """Open one email and mark it as read.

    Args:
        state: The current game state.
        email_index: The email's position in state.inbox.

    Returns:
        The page showing that email, or the Inbox if there is no such
        email.
    """
    if not can_open_email(state.inbox, email_index):
        return inbox_page(state)
    email = state.inbox[email_index]
    email.is_read = True
    state.current_page = PAGE_EMAIL
    return Page(state, build_email_content(state, email))


assert_equal(open_email(make_inbox_state(), 1),
             Page(expected_after_opening_welcome(),
                  build_email_content(
                      expected_after_opening_welcome(),
                      expected_after_opening_welcome().inbox[1])))
# No email at that position: the Inbox is shown and nothing is marked read.
assert_equal(open_email(make_inbox_state(), 5),
             Page(make_inbox_state(),
                  build_inbox_content(make_inbox_state())))
# Opening the briefing lets the first wave start.
assert_equal(is_email_unread(open_email(make_unbriefed_war_state(),
                                        0).state.inbox, EMAIL_FIRST_WAVE),
             False)


@route
def buy_defense(state: State, defense_index: int) -> Page:
    """Buy one unit of air defense if the player can afford it.

    Args:
        state: The current game state.
        defense_index: The equipment's position in state.defenses.

    Returns:
        The refreshed War page.
    """
    if can_buy_defense(state, defense_index):
        defense = state.defenses[defense_index]
        state.money = state.money - defense.cost
        defense.owned = defense.owned + 1
    return war_page(state)


assert_equal(buy_defense(make_rich_war_state(), 0),
             make_expected_war_page(expected_after_buying_manpads()))
# Too poor: nothing changes.
assert_equal(buy_defense(make_war_state(), 0),
             make_expected_war_page(make_war_view_state()))


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


# ---------------------------------------------------------------------------
# Debug: shortcuts for demos (hidden when DEBUG_TOOLS is False)
# ---------------------------------------------------------------------------

def debug_ensure_war(state: State) -> None:
    """Start the war if it hasn't started, and skip the briefing.

    Args:
        state: The game state to update.
    """
    state.total_earned = max(state.total_earned, WAR_START_EARNED)
    if state.game_phase == PHASE_PEACE:
        start_war(state)
    skip_briefing(state)


def debug_start_wave(state: State, waves_before: int) -> None:
    """Start the war if needed and start a wave right now.

    Args:
        state: The game state to update.
        waves_before: Skip ahead so this many waves count as started
            (0 = just start the next wave). Never goes backwards.
    """
    debug_ensure_war(state)
    if state.game_phase == PHASE_WAR and not is_wave_active(state):
        if waves_before > state.wave_number:
            state.wave_number = waves_before
        start_wave(state)


def debug_end_war(state: State, is_victory: bool) -> None:
    """End the war right now with the chosen outcome.

    Args:
        state: The game state to update.
        is_victory: Whether the war should be won.
    """
    debug_ensure_war(state)
    if state.game_phase == PHASE_WAR:
        if is_victory:
            state.war_goods_sold = max(state.war_goods_sold,
                                       WAR_VICTORY_GOODS)
            state.waves_defended = WAVE_COUNT
        else:
            state.war_goods_sold = 0
        state.wave_number = WAVE_COUNT
        finish_war(state)


def apply_debug_jump(state: State, target: str) -> State:
    """Move the game forward to a point that is useful for a demo.

    Args:
        state: The game state to update.
        target: One of the DEBUG_JUMP_ constants.

    Returns:
        The updated State (a brand new one for DEBUG_JUMP_PEACE).
    """
    if target == DEBUG_JUMP_PEACE:
        new_state = make_new_state()
        new_state.company_name = state.company_name
        return new_state
    if target == DEBUG_JUMP_RESEARCH:
        state.total_earned = max(state.total_earned, DEBUG_RESEARCH_EARNED)
    elif target == DEBUG_JUMP_WAR:
        state.total_earned = max(state.total_earned, WAR_START_EARNED)
        if state.game_phase == PHASE_PEACE:
            start_war(state)
    elif target == DEBUG_JUMP_THREAT and state.game_phase == PHASE_WAR:
        state.threat = MAX_THREAT - 1
    elif target == DEBUG_JUMP_WAVE:
        debug_start_wave(state, 0)
    elif target == DEBUG_JUMP_DIRE:
        debug_start_wave(state, DIRE_WAVE_EVERY - 1)
    elif target == DEBUG_JUMP_LAST:
        debug_start_wave(state, WAVE_COUNT - 1)
    elif target == DEBUG_JUMP_WIN or target == DEBUG_JUMP_LOSE:
        debug_end_war(state, target == DEBUG_JUMP_WIN)
    elif target == DEBUG_JUMP_CONFISCATION:
        send_email(state, EMAIL_CONFISCATION)
    return state


assert_equal(apply_debug_jump(make_war_state(), DEBUG_JUMP_PEACE),
             make_new_state())
assert_equal(apply_debug_jump(make_new_state(),
                              DEBUG_JUMP_RESEARCH).total_earned,
             DEBUG_RESEARCH_EARNED)
assert_equal(apply_debug_jump(make_new_state(), DEBUG_JUMP_WAR).game_phase,
             PHASE_WAR)
assert_equal(apply_debug_jump(make_war_state(), DEBUG_JUMP_THREAT).threat,
             MAX_THREAT - 1)
assert_equal(apply_debug_jump(make_new_state(), DEBUG_JUMP_WAVE).wave_number,
             1)
assert_equal(apply_debug_jump(make_war_state(), DEBUG_JUMP_DIRE).wave_number,
             DIRE_WAVE_EVERY)
assert_equal(apply_debug_jump(make_war_state(), DEBUG_JUMP_LAST).wave_number,
             WAVE_COUNT)
assert_equal(apply_debug_jump(make_new_state(), DEBUG_JUMP_WIN).news_feed[0],
             WAR_WON_NEWS)
assert_equal(apply_debug_jump(make_war_state(), DEBUG_JUMP_LOSE).game_phase,
             PHASE_WAR_OVER)
assert_equal(apply_debug_jump(make_new_state(),
                              DEBUG_JUMP_CONFISCATION).inbox[0].key,
             EMAIL_CONFISCATION)


def build_debug_card() -> Div:
    """Build the card of debug buttons.

    Returns:
        A card with money buttons and phase jump buttons.
    """
    money_buttons = []
    for amount in DEBUG_MONEY_AMOUNTS:
        money_buttons.append(Button("+" + format_money(amount),
                                    "debug_add_money",
                                    [Argument("amount", amount)]))
    return Div(
        build_card_head("🐞 Debug Tools", []),
        Div("Shortcuts for demos. Set DEBUG_TOOLS = False to hide this page.",
            classes="muted"),
        Header("Add money", 3),
        Div(money_buttons, classes="button-row"),
        Header("Jump ahead", 3),
        Div(Button("Restart in peace", "debug_jump",
                   [Argument("target", DEBUG_JUMP_PEACE)]),
            Button("Unlock peacetime research", "debug_jump",
                   [Argument("target", DEBUG_JUMP_RESEARCH)]),
            Button("Start the war", "debug_jump",
                   [Argument("target", DEBUG_JUMP_WAR)]),
            Button("Fill threat meter", "debug_jump",
                   [Argument("target", DEBUG_JUMP_THREAT)]),
            Button("Start next wave now", "debug_jump",
                   [Argument("target", DEBUG_JUMP_WAVE)]),
            Button("Skip to dire wave " + str(DIRE_WAVE_EVERY), "debug_jump",
                   [Argument("target", DEBUG_JUMP_DIRE)]),
            Button("Skip to the last wave", "debug_jump",
                   [Argument("target", DEBUG_JUMP_LAST)]),
            Button("End the war (win)", "debug_jump",
                   [Argument("target", DEBUG_JUMP_WIN)]),
            Button("End the war (lose)", "debug_jump",
                   [Argument("target", DEBUG_JUMP_LOSE)]),
            Button("Send confiscation email", "debug_jump",
                   [Argument("target", DEBUG_JUMP_CONFISCATION)]),
            classes="button-row"),
        classes="card narrow",
    )


def build_debug_content(state: State) -> list:
    """Build the Debug page's content.

    The buttons sit outside the live area so ticks can't swallow a click.

    Args:
        state: The current game state.

    Returns:
        A list of the page's components.
    """
    return [Div(build_live_content(state), id="live_area"),
            Div(build_debug_card(), classes="page")]


@route
def debug_page(state: State) -> Page:
    """Show the Debug page.

    Args:
        state: The current game state.

    Returns:
        The Debug page.
    """
    state.current_page = PAGE_DEBUG
    return Page(state, build_debug_content(state))


assert_equal(debug_page(make_new_state()),
             make_expected_debug_page(make_debug_state()))


@route
def debug_add_money(state: State, amount: int) -> Page:
    """Add money for demos (it does not count toward lifetime earnings).

    Args:
        state: The current game state.
        amount: The money to add.

    Returns:
        The refreshed Debug page.
    """
    state.money = state.money + amount
    return debug_page(state)


assert_equal(debug_add_money(make_new_state(), 10000).state.money,
             STARTING_MONEY + 10000)


@route
def debug_jump(state: State, target: str) -> Page:
    """Jump the game ahead for demos.

    Args:
        state: The current game state.
        target: One of the DEBUG_JUMP_ constants.

    Returns:
        The Debug page for the updated game.
    """
    return debug_page(apply_debug_jump(state, target))


assert_equal(debug_jump(make_war_state(), DEBUG_JUMP_PEACE),
             make_expected_debug_page(make_debug_state()))
assert_equal(debug_jump(make_new_state(), DEBUG_JUMP_WAR).state.game_phase,
             PHASE_WAR)


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
    run_war_economy(state, tick_interval(state))
    run_loyalty_drift(state)
    run_email_triggers(state)
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
