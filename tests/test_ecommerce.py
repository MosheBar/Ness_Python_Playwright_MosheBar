import pytest
import allure

from config.settings import logger, USER_EMAIL, USER_PASSWORD
from data.data_loader import load_test_params, FIELD_QUERY, FIELD_MAX_PRICE, FIELD_LIMIT
from core.constants import PARAM_SITE

_PARAM_NAMES = f"{PARAM_SITE}, {FIELD_QUERY}, {FIELD_MAX_PRICE}, {FIELD_LIMIT}"


@allure.feature("E-Commerce Checkout Flow")
@pytest.mark.parametrize(_PARAM_NAMES, load_test_params())
def test_ecommerce_end_to_end(page, site_pages, site, query, maxPrice, limit):

    allure.dynamic.title(f"Test checkout flow for {site} with query '{query}'")

    site_pages.home.navigate()

    if USER_EMAIL and USER_PASSWORD:
        site_pages.home.go_to_login()
        site_pages.login.login(USER_EMAIL, USER_PASSWORD)
    else:
        logger.info("No credentials provided. Proceeding as Guest checkout.")

    site_pages.home.search(query)

    item_urls = site_pages.search.search_items_by_name_under_price(query, maxPrice, limit)

    if not item_urls:
        logger.warning("No items found for criteria. Skipping add-to-cart.")
    else:
        site_pages.item.add_items_to_cart(item_urls)

    cart_total = site_pages.cart.get_cart_total()
    budget_threshold = maxPrice * len(item_urls)

    with allure.step(f"Assert cart total {cart_total} <= budget threshold {budget_threshold}"):
        assert cart_total <= budget_threshold, (
            f"Cart total {cart_total} exceeds budget limit {budget_threshold}"
        )
