from enum import Enum


class HomeKeys(str, Enum):
    URL          = "url"
    SEARCH_INPUT = "search_input"
    SEARCH_BTN   = "search_btn"
    LOGIN_LINK   = "login_link"
    LOGIN_URL    = "login_url"


class LoginKeys(str, Enum):
    USERNAME_INPUT = "username_input"
    CONTINUE_BTN   = "continue_btn"
    PASSWORD_INPUT = "password_input"
    SUBMIT_BTN     = "submit_btn"


class SearchKeys(str, Enum):
    PRICE_FILTER_MAX    = "price_filter_input_max"
    PRICE_FILTER_SUBMIT = "price_filter_submit"
    ITEM_LINKS          = "item_links"
    NEXT_PAGE_BTN       = "next_page_btn"


class ItemKeys(str, Enum):
    VARIANT_CUSTOM_LISTBOXES = "variant_custom_listboxes"
    VARIANT_NATIVE_SELECTS   = "variant_native_selects"
    VARIANT_OPTIONS          = "variant_options"
    VARIANT_BUTTONS          = "variant_buttons"
    ADD_TO_CART_BTN          = "add_to_cart_btn"


class CartKeys(str, Enum):
    URL      = "url"
    SUBTOTAL = "cart_subtotal_text"
