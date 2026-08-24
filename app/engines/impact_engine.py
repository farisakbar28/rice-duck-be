"""Archived research module.

Model C never imports or executes this module. Quantitative weed, pesticide,
fertilizer, and infrastructure claims require independent research inputs.
"""


def research_only_notice() -> dict:
    """Return the sole archive marker; this is not a Model C calculation."""
    return {
        "status": "research/archive only",
        "note": "Not a DSS Core output and not an economic calculation.",
    }
