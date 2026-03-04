import allure
from core.base_page import BasePage
from data.data_loader import load_locators
from data.locator_keys import CartKeys


class CartPage(BasePage):
    _SECTION = "cart"

    def __init__(self, page, site: str):
        super().__init__(page)
        locators                = load_locators(site).get(self._SECTION, {})
        self.cart_url           = locators.get(CartKeys.URL)
        self.subtotal_selectors = locators[CartKeys.SUBTOTAL]

    def get_cart_total(self) -> float:
        if self.cart_url and not self.page.url.startswith(self.cart_url):
            self.go_to(self.cart_url)

        self.wait_for_network_idle()

        with allure.step("Reading cart subtotal"):
            total = self.smart_get_number(self.subtotal_selectors)
            allure.attach(str(total), name="Cart Total")
            self.take_screenshot("Cart_Page_Final")
            return total
