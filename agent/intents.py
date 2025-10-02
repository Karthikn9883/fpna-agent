from __future__ import annotations
import re

INTENTS = [
    ('revenue_vs_budget', re.compile(r'(revenue).*?(vs|versus).*?(budget)|revenue\s+vs\s+budget', re.I)),
    ('gm_trend',          re.compile(r'(gross\s*margin|gm).*(trend|last|past)', re.I)),
    ('opex_breakdown',    re.compile(r'(opex|operating\s*exp).*?(breakdown|by\s*category)', re.I)),
    ('cash_runway',       re.compile(r'cash.*runway|runway', re.I)),
]

def classify(text: str) -> str:
    t = (text or "").lower()

    # NEW: data coverage / dataset info
    if re.search(r"\bmonths?\s+of\s+data\b", t) or re.search(r"\bhow many months\b", t):
        return "data_coverage"
    if "what months" in t or "which months" in t:
        return "data_coverage"

    # existing rules…
    if "revenue" in t and "budget" in t:
        return "revenue_vs_budget"
    if "gross margin" in t or "gm%" in t or "gm %" in t:
        return "gm_trend"
    if "opex" in t and ("breakdown" in t or "by category" in t):
        return "opex_breakdown"
    if "runway" in t:
        return "cash_runway"

    return "unknown"