from __future__ import annotations
import pandas as pd
from dateutil.parser import parse as dtparse

def _to_period(s: pd.Series) -> pd.Series:
    # Robust month coercion: accepts 'YYYY-MM', 'YYYY-MM-DD', 'Jun 2025', etc.
    def coerce(x):
        if pd.isna(x):
            return pd.NaT
        x = str(x)
        try:
            # Fast path: YYYY-MM
            if len(x) == 7 and x[4] == '-':
                return pd.Period(x, freq='M')
            # Fallback general parser
            return pd.Period(dtparse(x).strftime('%Y-%m'), freq='M')
        except Exception:
            return pd.NaT
    return s.map(coerce)

def load_from_xlsx(path_or_url: str) -> dict[str, pd.DataFrame]:
    xls = pd.ExcelFile(path_or_url)
    dfs = {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}
    return dfs

def load_from_csv_dir(csv_dir: str) -> dict[str, pd.DataFrame]:
    import pathlib
    p = pathlib.Path(csv_dir)
    dfs = {}
    for name in ['actuals','budget','fx','cash']:
        f = p / f"{name}.csv"
        dfs[name] = pd.read_csv(f)
    return dfs

def normalize(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    actuals = dfs['actuals'].copy()
    budget = dfs['budget'].copy()
    fx = dfs['fx'].copy()
    cash = dfs['cash'].copy()

    # Coerce months
    for d in (actuals, budget, fx, cash):
        d['month'] = _to_period(d['month'])

    # FX normalization
    for d in (actuals, budget):
        if 'currency' not in d.columns:
            d['currency'] = 'USD'
        merged = d.merge(fx, on=['month','currency'], how='left', validate='m:1')
        if merged['rate_to_usd'].isna().any():
            missing = merged[merged['rate_to_usd'].isna()][['month','currency']].drop_duplicates()
            raise ValueError(f"Missing FX rate_to_usd for rows:\n{missing}" )
        d['amount_usd'] = (merged['amount'] * merged['rate_to_usd']).astype(float)

    # Canonical long table
    actuals_long = actuals.assign(source='actuals')[[ 'month','entity','account_category','amount_usd','source' ]]
    budget_long  = budget.assign(source='budget')[[  'month','entity','account_category','amount_usd','source' ]]
    combined = pd.concat([actuals_long, budget_long], ignore_index=True)

    # Cash already in USD
    cash = cash.rename(columns={'cash_usd':'amount_usd'})

    return {'financials': combined, 'cash': cash}

def get_available_months(fin_combined: pd.DataFrame) -> pd.Series:
    return fin_combined['month'].dropna().drop_duplicates().sort_values()
