"""Archived research module.

Model A DSS Core never imports or executes this module. Quantitative weed,
pesticide, and fertilizer claims require independent research inputs.
"""

def research_only_notice() -> dict:
    return {"status":"research/archive only","note":"Not a DSS Core output and not an economic calculation."}
