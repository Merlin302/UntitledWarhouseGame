from dataclasses import dataclass
from bakery import assert_equal
from drafter import *


hide_debug_information()
set_website_title("Untitled Warehouse Inc.")
set_website_framed(False)
set_site_information(
    author="TODO: your name",
    description="An incremental warehouse management game.",
    sources=["Drafter documentation"],
    planning=["docs/"],
    links=[],
)


@dataclass
class State:
    """Holds everything the website remembers between pages.

    Attributes:
        company_name: The name of the player's company.
    """
    company_name: str


def make_new_state() -> State:
    """Build the State that a brand new game starts with."""
    return State("Untitled Warehouse Inc.")


@route
def index(state: State) -> Page:
    """Show a welcome message on the home page."""
    return Page(state, ["Hello from " + state.company_name + "!"])


assert_equal(
    index(make_new_state()),
    Page(make_new_state(), ["Hello from Untitled Warehouse Inc.!"]),
)

start_server(make_new_state())
