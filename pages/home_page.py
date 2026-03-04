from core.base_page import BasePage
from data.data_loader import load_locators
from data.locator_keys import HomeKeys


class HomePage(BasePage):
    _SECTION = "home"

    def __init__(self, page, site: str):
        super().__init__(page)
        locators         = load_locators(site).get(self._SECTION, {})
        self.home_url    = locators[HomeKeys.URL]
        self.search_input = locators[HomeKeys.SEARCH_INPUT]
        self.search_btn  = locators[HomeKeys.SEARCH_BTN]
        self.login_url   = locators.get(HomeKeys.LOGIN_URL)
        self.login_link  = locators.get(HomeKeys.LOGIN_LINK)

    def navigate(self):
        self.go_to(self.home_url)

    def search(self, query: str):
        self.smart_fill(self.search_input, query)
        self.smart_click(self.search_btn)
        self.wait_for_page_load()

    def go_to_login(self):
        if self.login_url:
            self.go_to(self.login_url)
        else:
            self.smart_click(self.login_link)
        self.wait_for_page_load()
