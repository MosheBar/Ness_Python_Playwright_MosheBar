import allure
import random
from core.base_page import BasePage
from config.settings import logger
from data.data_loader import load_locators
from data.locator_keys import ItemKeys
from core.constants import HtmlAttr, HtmlTag, INVALID_SELECT_VALUE


class ItemPage(BasePage):
    _SECTION = "item"

    def __init__(self, page, site: str):
        super().__init__(page)
        locators                     = load_locators(site).get(self._SECTION, {})
        self.add_to_cart_btn         = locators[ItemKeys.ADD_TO_CART_BTN]
        self.custom_listbox_selectors = locators.get(ItemKeys.VARIANT_CUSTOM_LISTBOXES, [])
        self.native_select_selectors  = locators.get(ItemKeys.VARIANT_NATIVE_SELECTS, [])
        variant_options               = locators.get(ItemKeys.VARIANT_OPTIONS)
        self.variant_option_selector  = variant_options[0] if variant_options else None
        self.variant_buttons          = locators.get(ItemKeys.VARIANT_BUTTONS, [])

    def add_items_to_cart(self, urls: list[str]):
        for item_index, url in enumerate(urls):
            with allure.step(f"Adding item {item_index + 1} to cart - URL: {url}"):
                self.go_to(url)
                self.wait_for_page_load()
                self._select_variants_if_exist()
                self.smart_click(self.add_to_cart_btn)
                self.take_screenshot(f"item_added_{item_index + 1}")

    def _select_variants_if_exist(self):
        if self._try_custom_listboxes():
            return
        if self._try_native_selects():
            return
        if self._try_variant_buttons():
            return
        logger.info("No variants found — proceeding without selection")

    def _try_custom_listboxes(self) -> bool:
        for selector in self.custom_listbox_selectors:
            try:
                listbox_buttons = self.page.locator(selector).all()
                if not listbox_buttons:
                    continue
                logger.info(f"Found {len(listbox_buttons)} custom listbox variant(s) via '{selector}'")
                for listbox_btn in listbox_buttons:
                    try:
                        listbox_btn.click()
                        if not self.variant_option_selector:
                            continue
                        listbox_id = listbox_btn.get_attribute(HtmlAttr.ARIA_CONTROLS)
                        if listbox_id:
                            scoped_selector = f"#{listbox_id} {self.variant_option_selector}"
                            available_options = self.page.locator(scoped_selector).all()
                        else:
                            available_options = [
                                opt for opt in self.page.locator(self.variant_option_selector).all()
                                if opt.is_visible()
                            ]
                        if available_options:
                            chosen = random.choice(available_options)
                            chosen.scroll_into_view_if_needed()
                            chosen.click()
                    except Exception as e:
                        logger.warning(f"Custom listbox variant selection failed: {e}")
                return True
            except Exception:
                continue
        return False

    def _try_native_selects(self) -> bool:
        for selector in self.native_select_selectors:
            try:
                native_selects = self.page.locator(selector).all()
                if not native_selects:
                    continue
                logger.info(f"Found {len(native_selects)} native select variant(s) via '{selector}'")
                for native_select in native_selects:
                    all_options = native_select.locator(HtmlTag.OPTION).all()
                    selectable_values = [
                        opt.get_attribute(HtmlAttr.VALUE) for opt in all_options
                        if opt.get_attribute(HtmlAttr.VALUE) and opt.get_attribute(HtmlAttr.VALUE) != INVALID_SELECT_VALUE
                    ]
                    if selectable_values:
                        native_select.select_option(value=random.choice(selectable_values))
                return True
            except Exception:
                continue
        return False

    def _try_variant_buttons(self) -> bool:
        for selector in self.variant_buttons:
            try:
                buttons = self.page.locator(selector).all()
                if not buttons:
                    continue
                random.choice(buttons).click()
                return True
            except Exception:
                continue
        return False
