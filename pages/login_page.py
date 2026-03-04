import allure
from core.base_page import BasePage
from data.data_loader import load_locators
from data.locator_keys import LoginKeys


class LoginPage(BasePage):
    _SECTION = "login"

    def __init__(self, page, site: str):
        super().__init__(page)
        locators            = load_locators(site).get(self._SECTION, {})
        self.username_input = locators[LoginKeys.USERNAME_INPUT]
        self.continue_btn   = locators[LoginKeys.CONTINUE_BTN]
        self.password_input = locators[LoginKeys.PASSWORD_INPUT]
        self.submit_btn     = locators[LoginKeys.SUBMIT_BTN]

    def login(self, email: str, password: str):
        with allure.step(f"Login with {email}"):
            self.smart_fill(self.username_input, email)
            self.smart_click(self.continue_btn)
            self.smart_fill(self.password_input, password)
            self.smart_click(self.submit_btn)
            self.wait_for_network_idle()
