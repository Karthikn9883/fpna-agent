import pandas as pd
from agent.metrics import revenue_month, gross_margin_pct_series, ebitda_series, cash_runway

def _toy_fin():
    # 2 months, simple totals
    data = [
        ['2025-05','Co','Revenue',1000.0,'actuals'],
        ['2025-05','Co','COGS',   400.0,'actuals'],
        ['2025-05','Co','Opex:Ops',300.0,'actuals'],
        ['2025-05','Co','Revenue',900.0,'budget'],
        ['2025-06','Co','Revenue',1200.0,'actuals'],
        ['2025-06','Co','COGS',   500.0,'actuals'],
        ['2025-06','Co','Opex:Ops',350.0,'actuals'],
        ['2025-06','Co','Revenue',1100.0,'budget'],
    ]
    df = pd.DataFrame(data, columns=['month','entity','account_category','amount_usd','source'])
    df['month'] = pd.PeriodIndex(df['month'], freq='M')
    return df

def _toy_cash():
    df = pd.DataFrame({'month':['2025-05','2025-06'],'entity':['Consolidated','Consolidated'],'amount_usd':[10000.0, 9800.0]})
    df['month'] = pd.PeriodIndex(df['month'], freq='M')
    return df

def test_revenue_month():
    fin = _toy_fin()
    a,b,delta,dp = revenue_month(fin, pd.Period('2025-06',freq='M'))
    assert a == 1200.0 and b == 1100.0
    assert round(dp,4) == round((1200-1100)/1100,4)

def test_gm_pct():
    fin = _toy_fin()
    months = pd.PeriodIndex(['2025-05','2025-06'], freq='M')
    gm = gross_margin_pct_series(fin, months)
    assert round(gm.iloc[0],3) == round((1000-400)/1000,3)

def test_runway():
    fin = _toy_fin(); cash = _toy_cash()
    months = pd.PeriodIndex(['2025-05','2025-06'], freq='M')
    e = ebitda_series(fin, months)
    r = cash_runway(cash, e.tail(2))
    assert r > 0
