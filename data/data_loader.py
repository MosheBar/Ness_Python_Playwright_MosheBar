import json
import os
from functools import lru_cache

_DATA_DIR             = os.path.dirname(__file__)
_LOCATORS_DIR         = "locators"
_LOCATORS_FILE_SUFFIX = "_locators.json"
_TEST_DATA_FILE_DEFAULT = "test_data.json"
_TEST_DATA_ENV_KEY       = "PYTEST_TEST_DATA_FILE"

FIELD_QUERY     = "query"
FIELD_MAX_PRICE = "maxPrice"
FIELD_LIMIT     = "limit"


@lru_cache(maxsize=None)
def load_locators(site: str) -> dict:
    # NOTE: the returned dict is cached and shared across all callers.
    # Pages must treat self.locators as read-only — never mutate it.
    locator_path = os.path.join(_DATA_DIR, _LOCATORS_DIR, f"{site}{_LOCATORS_FILE_SUFFIX}")
    with open(locator_path, "r") as f:
        return json.load(f)


def load_test_params() -> list[tuple]:
    test_data_file = os.environ.get(_TEST_DATA_ENV_KEY, _TEST_DATA_FILE_DEFAULT)
    data_path = os.path.join(_DATA_DIR, test_data_file)
    with open(data_path, "r") as f:
        data = json.load(f)
    params = []
    for site, queries in data.items():
        for q in queries:
            params.append((site, q[FIELD_QUERY], q[FIELD_MAX_PRICE], q[FIELD_LIMIT]))
    return params
