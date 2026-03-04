import allure
from core.base_page import BasePage
from config.settings import logger
from data.data_loader import load_locators
from data.locator_keys import SearchKeys
from core.constants import ElementState, LoadState, DEFAULT_TIMEOUT_MS


class SearchResultsPage(BasePage):
    _SECTION = "search"

    def __init__(self, page, site: str):
        super().__init__(page)
        locators                  = load_locators(site).get(self._SECTION, {})
        self.price_filter_max     = locators.get(SearchKeys.PRICE_FILTER_MAX)
        self.price_filter_submit  = locators.get(SearchKeys.PRICE_FILTER_SUBMIT)
        self.item_links           = locators[SearchKeys.ITEM_LINKS]
        self.next_page_btn        = locators.get(SearchKeys.NEXT_PAGE_BTN)

    def search_items_by_name_under_price(self, query: str, max_price: float, limit: int = 5) -> list[str]:
        self.wait_for_page_load()
        if self.price_filter_max and self.price_filter_submit:
            self._apply_price_filter(max_price)
        else:
            logger.warning("Price filter locators not configured — skipping price filter")
        return self._collect_item_urls(limit)

    def _apply_price_filter(self, max_price: float) -> None:
        with allure.step(f"Apply max price filter ({int(max_price)})"):
            price_input = self._find_price_input()
            if price_input is None:
                logger.error("Price filter input NOT found — skipping price filter")
                return
            try:
                price_input.scroll_into_view_if_needed()
                self._fill_price(price_input, str(int(max_price)))
                self._submit_price_filter()
            except Exception as e:
                logger.error(f"Price filter interaction failed: {e}")
                allure.attach(str(e), name="Price Filter Error")

    def _find_price_input(self):
        for selector in self.price_filter_max:
            try:
                price_input_element = self.page.locator(selector).first
                price_input_element.wait_for(state=ElementState.VISIBLE, timeout=DEFAULT_TIMEOUT_MS)
                logger.info(f"Price filter input found: {selector}")
                return price_input_element
            except Exception:
                logger.warning(f"Price filter selector not visible: {selector}")
        return None

    def _fill_price(self, price_input, expected_value: str) -> None:
        price_input.click()
        price_input.fill(expected_value)
        self.wait_for_network_idle()
        price_input.blur()
        self.wait_for_network_idle()

    def _submit_price_filter(self) -> None:
        self.wait_for_page_load()
        for submit_selector in self.price_filter_submit:
            try:
                submit_btn = self.page.locator(submit_selector).first
                submit_btn.wait_for(state=ElementState.VISIBLE, timeout=DEFAULT_TIMEOUT_MS)
                with self.page.expect_navigation(wait_until=LoadState.DOM_CONTENT, timeout=DEFAULT_TIMEOUT_MS):
                    submit_btn.click()
                logger.info(f"Price filter submitted via: {submit_selector}")
                return
            except Exception:
                continue
        raise RuntimeError("Price filter submit button not found — all selectors exhausted")

    def _collect_item_urls(self, limit: int) -> list[str]:
        collected_urls = []
        self.wait_for_page_load()
        with allure.step(f"Extracting up to {limit} item URLs"):
            while len(collected_urls) < limit:
                self.page.wait_for_selector(
                    self.item_links[0],
                    state=ElementState.ATTACHED,
                    timeout=DEFAULT_TIMEOUT_MS,
                )
                for item_link in self.page.locator(self.item_links[0]).all():
                    if len(collected_urls) >= limit:
                        break
                    href = item_link.get_attribute("href")
                    if href and href not in collected_urls:
                        collected_urls.append(href)

                if len(collected_urls) >= limit:
                    break

                try:
                    with self.page.expect_navigation(wait_until=LoadState.DOM_CONTENT, timeout=DEFAULT_TIMEOUT_MS):
                        self.smart_click(self.next_page_btn, timeout_ms=DEFAULT_TIMEOUT_MS)
                except Exception:
                    break

        return collected_urls[:limit]
