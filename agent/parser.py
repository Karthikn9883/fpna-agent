from __future__ import annotations
import re
import calendar
import pandas as pd
from dateutil.parser import parse as dtparse

# e.g., "June 2025"
MONTH_RX = re.compile(r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*)\s+(\d{4})\b", re.I)

def parse_months(text: str, available_months: pd.Series) -> pd.Series | None:
    t = (text or "").lower()
    am = available_months.sort_values()

    # last N months
    m = re.search(r"last\s+(\d+)\s+months?", t)
    if m:
        n = int(m.group(1))
        return am.tail(n)

    # quarter like Q2 2025
    mq = re.search(r"q([1-4])\s*(\d{4})", t)
    if mq:
        q = int(mq.group(1)); y = int(mq.group(2))
        start = (q - 1) * 3 + 1
        months = [pd.Period(f"{y}-{m:02d}", freq="M") for m in range(start, start + 3)]
        return pd.Series(months)

    # named month + year
    mm = MONTH_RX.search(text or "")
    if mm:
        p = pd.Period(dtparse(mm.group(0)).strftime("%Y-%m"), freq="M")
        return pd.Series([p])

    # ISO like 2025-06 or 2025/06
    mi = re.search(r"(20\d{2})[-/](0[1-9]|1[0-2])", t)
    if mi:
        y = int(mi.group(1)); m2 = mi.group(2)
        p = pd.Period(f"{y}-{m2}", freq="M")
        return pd.Series([p])

    # Lone month name (e.g., "June") → latest occurrence of that month number in data
    for i, name in enumerate(calendar.month_name[1:], start=1):
        if name.lower() in t or name[:3].lower() in t:
            candidates = am[am.dt.month == i]
            if not candidates.empty:
                return pd.Series([candidates.max()])

    # this month / current month / right now → latest available month
    if "this month" in t or "current month" in t or "right now" in t:
        return pd.Series([am.max()])

    return None
