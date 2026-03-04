import os
import pytest
from dataclasses import dataclass
from playwright.sync_api import Playwright, Browser, BrowserContext, Page
from typing import Generator

from config.settings import logger, GRID_URL
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage
from core.constants import PARAM_SITE, TRACE_OUTPUT_PATH
from data.data_loader import _TEST_DATA_ENV_KEY


def pytest_addoption(parser):
    parser.addoption(
        "--test-data",
        default=None,
        help="Test data filename inside data/ directory (default: test_data.json)",
    )


def pytest_configure(config):
    try:
        test_data = config.getoption("--test-data")
        if test_data:
            os.environ[_TEST_DATA_ENV_KEY] = test_data
    except ValueError:
        pass

IS_CI = os.getenv("CI", "false").lower() == "true"

CHROMIUM_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-blink-features=AutomationControlled',
    '--start-maximized',
]

REAL_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


@dataclass
class EcommerceSitePages:
    home:   HomePage
    login:  LoginPage
    search: SearchResultsPage
    item:   ItemPage
    cart:   CartPage


# ---------------------------------------------------------------------------
# Browser / context / page
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Generator[Browser, None, None]:
    if GRID_URL:
        logger.info(f"Connecting to remote Playwright grid at {GRID_URL}")
        browser_instance = playwright.chromium.connect(ws_endpoint=GRID_URL)
    else:
        logger.info(f"Launching local Playwright Chromium instance (headless={IS_CI})")
        browser_instance = playwright.chromium.launch(
            headless=IS_CI,
            args=CHROMIUM_ARGS,
        )
    yield browser_instance
    browser_instance.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    browser_context = browser.new_context(
        no_viewport=True,
        user_agent=REAL_USER_AGENT,
    )
    browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield browser_context
    try:
        browser_context.tracing.stop(path=TRACE_OUTPUT_PATH)
    except Exception:
        pass
    browser_context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page_instance = context.new_page()
    yield page_instance
    page_instance.close()


@pytest.fixture(scope="function")
def site_pages(page: Page, request) -> EcommerceSitePages:
    site = request.node.callspec.params[PARAM_SITE]
    return EcommerceSitePages(
        home=HomePage(page, site),
        login=LoginPage(page, site),
        search=SearchResultsPage(page, site),
        item=ItemPage(page, site),
        cart=CartPage(page, site),
    )
