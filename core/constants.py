from enum import Enum

# ---------------------------------------------------------------------------
# Timeouts
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT_MS = 5000

class ElementState(str, Enum):
    VISIBLE  = "visible"
    ATTACHED = "attached"


class LoadState(str, Enum):
    DOM_CONTENT  = "domcontentloaded"
    NETWORK_IDLE = "networkidle"


class HtmlAttr(str, Enum):
    HREF          = "href"
    VALUE         = "value"
    ARIA_CONTROLS = "aria-controls"


class HtmlTag(str, Enum):
    OPTION = "option"


# Sentinel for a disabled / placeholder <select> option
INVALID_SELECT_VALUE = "-1"

# ---------------------------------------------------------------------------
# Parametrize param names
# ---------------------------------------------------------------------------
PARAM_SITE = "site"

# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------
TRACE_OUTPUT_PATH = "test_trace.zip"
