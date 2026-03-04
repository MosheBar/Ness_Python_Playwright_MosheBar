# E-Commerce Playwright Automation Framework

A robust, Data-Driven E2E testing framework built with **Python**, **Playwright**, and **Pytest**.  
Designed to run resiliently across diverse e-commerce sites (e.g. eBay) using a clean POM architecture with smart locator fallback.

---

## Architecture

### 1. Page Object Model (POM)
All page logic lives in stateless page classes (`home_page.py`, `search_results_page.py`, `item_page.py`, `cart_page.py`, `login_page.py`).  
**No locators are hardcoded** in Python — they are loaded from site-specific JSON files via `data/data_loader.py` and eagerly extracted into named attributes in each page's `__init__`.

### 2. Smart Locators & Resilience
`BasePage` (`core/base_page.py`) implements fallback-driven interaction methods:
- `smart_click(selectors[])` — tries each selector in order; logs which succeeded/failed
- `smart_fill(selectors[])` — same for inputs
- `smart_get_text(selectors[])` — same for reading text
- `smart_get_number(selectors[])` — extracts a float via JS `parseFloat`, no regex needed

Each element defines **alternative selectors** in the JSON. If the primary fails (A/B test, DOM change), the next is tried automatically. A screenshot is captured on final failure.

### 3. Data-Driven Configuration
- **Test inputs**: `data/test_data.json` — site, query, maxPrice, limit
- **Locators**: `data/locators/{site}_locators.json` — fully external, per-site
- **Locator keys**: `data/locator_keys.py` — `str`-inheriting Enums per page section
- **Shared constants**: `core/constants.py` — Playwright states/load strategies, HTML attrs, timeouts (all as Enums or named constants — no hardcoded strings anywhere)
- Adding a new site requires only a new locators JSON — no Python changes

### 4. Fixtures (conftest.py)
Fixtures form a dependency chain:
```
playwright (built-in)
    └── browser     (session scope — one Chromium instance per run)
            └── context  (function scope — fresh cookies + tracing per test)
                    └── page      (function scope — one tab per test)
                            └── site_pages  (function scope — all 5 page objects)
```
`site_pages` returns an `EcommerceSitePages` dataclass, so tests access pages via `site_pages.home`, `site_pages.cart`, etc.

### 5. Remote Grid / Moon Support
The `browser` fixture checks `GRID_URL` in `.env`.  
When set, it connects via WebSocket (`playwright.chromium.connect(ws_endpoint=...)`), enabling execution on Selenium Grid / Moon with full session isolation per test.

---

## 4 Core Functions

| Function | Location | Description |
|---|---|---|
| `login(email, password)` | `LoginPage` | Fills credentials and submits. Skipped gracefully when no creds provided (Guest mode). |
| `search_items_by_name_under_price(query, maxPrice, limit)` | `SearchResultsPage` | Applies price filter, collects up to `limit` item URLs, paginates if needed. |
| `add_items_to_cart(urls)` | `ItemPage` | Navigates each URL, selects random variants (custom listbox / native select / button), clicks Add to Cart, takes screenshot. |
| `get_cart_total()` | `CartPage` | Navigates to cart, reads subtotal as float via JS evaluation. Assertion (`total ≤ budget`) lives in the test. |

---

## Prerequisites

```bash
python -m venv venv

# Windows (PowerShell)
.\\venv\\Scripts\\Activate.ps1

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
playwright install --with-deps chromium
```

---

## Environment Setup

Edit `.env` before running:

```dotenv
# Optional: Remote Grid WebSocket endpoint (Moon / Selenium Grid)
# e.g. ws://moon.example.local:4444/playwright
GRID_URL=

# Optional: Login credentials — leave empty to run as Guest
USER_EMAIL=
USER_PASSWORD=
```

---

## CI/CD — GitHub Actions

The workflow in `.github/workflows/playwright.yml` runs automatically on:
- **Every push** to `main` / `master`
- **Every pull request** to `main` / `master`
- **Nightly** at 00:00 UTC (scheduled cron)

After each run it generates and publishes an Allure report to **GitHub Pages** (the `gh-pages` branch), making results accessible via a public URL without any manual steps.

Credentials and `GRID_URL` are stored as **GitHub Secrets** (Settings → Secrets → Actions) and injected at runtime — never stored in the repo.

---

## Running Tests

```bash
# Run all tests with default test data (data/test_data.json)
pytest tests

# Run with a custom test data file (must be in the data/ directory)
pytest tests --test-data=smoke_tests.json
pytest tests --test-data=load_tests.json

# Open the Allure report
allure serve allure-results
```

> `pytest.ini` configures `--alluredir=allure-results` and `-v` automatically via `addopts`, so no extra flags needed.

---

## Constraints & Assumptions

| Topic | Decision |
|---|---|
| **Authentication** | Login is **optional**. If `USER_EMAIL` / `USER_PASSWORD` are empty in `.env`, the test runs as a Guest (no login step). This is intentional to support environments without valid credentials and to handle eBay's anti-bot flows. |
| **Currency** | Currency symbol validation is **not enforced**. The framework extracts the first numeric value from the cart subtotal text and compares it against the budget threshold. This avoids locale/currency failures (eBay may display currency differently by region). |
| **Variants** | Variants (size, colour, etc.) are selected **randomly** from available options. Three strategies are tried in order: custom ARIA listbox → native `<select>` → button group. Items with no variants proceed directly to Add to Cart. |
| **Pagination** | If fewer than `limit` items are found on the first results page, the framework automatically paginates until `limit` is reached or no more pages exist. |
| **Parallelism** | Parallel browser execution is supported via Selenium Grid / Moon through `GRID_URL` in `.env`. Locally, tests run sequentially unless `pytest-xdist` is added. |

---

## Project Structure

```
├── config/
│   └── settings.py              # Loads .env, logger, env variables
├── core/
│   ├── base_page.py             # Smart locator methods, screenshots, go_to
│   └── constants.py             # Playwright states, load strategies, HTML attrs (Enums + constants)
├── pages/
│   ├── home_page.py
│   ├── login_page.py
│   ├── search_results_page.py
│   ├── item_page.py
│   └── cart_page.py
├── data/
│   ├── locator_keys.py          # str-Enum key classes per page section
│   ├── data_loader.py           # load_locators() (lru_cache) + load_test_params()
│   ├── test_data.json           # Data-driven test inputs
│   └── locators/
│       └── ebay_locators.json   # Per-site locator definitions
├── tests/
│   └── test_ecommerce.py        # Parametrized E2E test
├── conftest.py                  # browser/context/page/site_pages fixtures
├── pytest.ini                   # Allure, markers configuration
└── .env                         # Credentials & Grid URL (not committed)
```