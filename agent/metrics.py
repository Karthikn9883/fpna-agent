from __future__ import annotations
import pandas as pd
import numpy as np

REV_KEYS = ('Revenue', 'Revenue:')
COGS_KEYS = ('COGS', 'COGS:')
OPEX_PREFIX = 'Opex:'

def _is_rev(s: pd.Series) -> pd.Series:
    return s.eq('Revenue') | s.str.startswith('Revenue:')

def _is_cogs(s: pd.Series) -> pd.Series:
    return s.eq('COGS') | s.str.startswith('COGS:')

def _is_opex(s: pd.Series) -> pd.Series:
    return s.str.startswith('Opex:')

def revenue_month(fin: pd.DataFrame, month, entity: str | None=None):
    f = fin[fin['month'] == month]
    if entity:
        f = f[f['entity'] == entity]
    actual = f[(f['source']=='actuals') & _is_rev(f['account_category'])]['amount_usd'].sum()
    budget = f[(f['source']=='budget')  & _is_rev(f['account_category'])]['amount_usd'].sum()
    delta = actual - budget
    delta_pct = (delta / budget) if budget != 0 else np.nan
    return float(actual), float(budget), float(delta), (float(delta_pct) if pd.notna(delta_pct) else np.nan)

def gross_margin_pct_series(fin: pd.DataFrame, months: pd.Series, entity: str | None=None) -> pd.Series:
    # Uses actuals only
    f = fin[(fin['source']=='actuals') & (fin['month'].isin(months))]
    if entity:
        f = f[f['entity'] == entity]
    grp = f.groupby('month')
    rev = grp.apply(lambda df: df[_is_rev(df['account_category'])]['amount_usd'].sum())
    cogs = grp.apply(lambda df: df[_is_cogs(df['account_category'])]['amount_usd'].sum())
    gm = (rev - cogs)
    with np.errstate(divide='ignore', invalid='ignore'):
        gm_pct = gm / rev.replace(0, np.nan)
    return gm_pct.sort_index()

def opex_breakdown_month(fin: pd.DataFrame, month, entity: str | None=None) -> pd.Series:
    f = fin[(fin['source']=='actuals') & (fin['month']==month)]
    if entity:
        f = f[f['entity']==entity]
    opex = f[f['account_category'].str.startswith('Opex:')]
    ser = opex.groupby('account_category')['amount_usd'].sum().sort_values(ascending=False)
    return ser

def ebitda_series(fin: pd.DataFrame, months: pd.Series, entity: str | None=None) -> pd.Series:
    f = fin[(fin['source']=='actuals') & (fin['month'].isin(months))]
    if entity:
        f = f[f['entity']==entity]
    grp = f.groupby('month')
    rev = grp.apply(lambda df: df[_is_rev(df['account_category'])]['amount_usd'].sum())
    cogs = grp.apply(lambda df: df[_is_cogs(df['account_category'])]['amount_usd'].sum())
    opex = grp.apply(lambda df: df[df['account_category'].str.startswith('Opex:')]['amount_usd'].sum())
    e = (rev - cogs - opex).sort_index()
    return e

def cash_runway(cash_df: pd.DataFrame, ebitda_recent3: pd.Series) -> float | float('inf'):
    if ebitda_recent3.empty:
        return float('inf')
    burns = ebitda_recent3.apply(lambda x: max(0.0, -float(x)))
    avg_burn = burns.tail(3).mean()
    latest_cash = cash_df.sort_values('month')['amount_usd'].iloc[-1]
    if avg_burn == 0 or pd.isna(avg_burn):
        return float('inf')
    return float(latest_cash / avg_burn)
