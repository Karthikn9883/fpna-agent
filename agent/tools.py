# agent/tools.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import pandas as pd

from agent.metrics import (
    revenue_month,
    gross_margin_pct_series,
    opex_breakdown_month,
    ebitda_series,
    cash_runway,
)
from agent.charts import (
    revenue_vs_budget_fig,
    gm_trend_fig,
    opex_breakdown_fig,
    opex_breakdown_bar_fig,
    cash_trend_fig,
    fmt_usd,
)
from agent.parser import parse_months
from agent.data import get_available_months

# ---------- Tool signatures ----------
# Each tool returns:
# {
#   "answer": "board-ready sentence",
#   "chart": {"kind": "...", "payload": {...}}  # optional, tells app to render chart
# }

def tool_revenue_vs_budget(fin: pd.DataFrame, cash: pd.DataFrame, question: str, entity: Optional[str]) -> Dict[str, Any]:
    months = get_available_months(fin)
    sel = parse_months(question, months)
    if sel is None or sel.empty:
        sel = pd.Series([months.max()], dtype="period[M]")
    m = sel.iloc[-1]
    actual, budget, delta, dp = revenue_month(fin, m, entity)
    pct = f"{dp*100:.1f}%" if pd.notna(dp) else "n/a"
    answer = f"{m}: Revenue {fmt_usd(actual)} vs Budget {fmt_usd(budget)} ({('+' if delta >= 0 else '')}{pct} vs plan)."
    # chart hint
    return {
        "answer": answer,
        "chart": {"kind": "rev_vs_budget", "payload": {"actual": float(actual), "budget": float(budget), "month": str(m)}}
    }

def tool_gm_trend(fin: pd.DataFrame, cash: pd.DataFrame, question: str, entity: Optional[str]) -> Dict[str, Any]:
    months = get_available_months(fin)
    sel = parse_months(question, months)
    if sel is None or sel.empty:
        sel = months.sort_values().tail(3)
    gm = gross_margin_pct_series(fin, sel, entity).dropna().sort_index()
    if gm.empty:
        return {"answer": "No data to compute Gross Margin % for the selected range."}
    start_m, end_m = gm.index[0], gm.index[-1]
    start_v, end_v = float(gm.iloc[0]), float(gm.iloc[-1])
    delta_pp = (end_v - start_v) * 100.0
    answer = (
        f"Gross Margin % from {start_m} → {end_m}: "
        f"{start_v*100:.2f}% → {end_v*100:.2f}% "
        f"({('+' if delta_pp >= 0 else '')}{delta_pp:.2f} pp)."
    )
    # chart hint carries the series values
    payload = {"points": [{"month": str(m), "gm_pct": float(v)} for m, v in gm.items()]}
    return {"answer": answer, "chart": {"kind": "gm_trend", "payload": payload}}

def tool_opex_breakdown(fin: pd.DataFrame, cash: pd.DataFrame, question: str, entity: Optional[str]) -> Dict[str, Any]:
    months = get_available_months(fin)
    q = (question or "").lower()
    
    # Check if asking about a specific category
    specific_category = None
    if "marketing" in q:
        specific_category = "Marketing"
    elif "sales" in q:
        specific_category = "Sales"
    elif "r&d" in q:
        specific_category = "R&D"
    elif "admin" in q:
        specific_category = "Admin"
    
    # Enhanced date parsing for year and month-specific filtering
    import re
    from dateutil.parser import parse as dtparse
    
    target_year = None
    target_month = None
    target_period = None
    
    # Try to parse specific month-year combinations first
    # Pattern 1: "January 2025", "March 2024", etc.
    month_year_pattern = r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s+(20\d{2})\b'
    month_year_match = re.search(month_year_pattern, question or "", re.IGNORECASE)
    
    if month_year_match:
        month_str = month_year_match.group(1)
        year_str = month_year_match.group(2)
        try:
            parsed_date = dtparse(f"{month_str} {year_str}")
            target_period = pd.Period(f"{parsed_date.year}-{parsed_date.month:02d}", freq="M")
            target_year = parsed_date.year
            target_month = parsed_date.month
        except:
            pass
    
    # Pattern 2: "2025-01", "2024-03", etc.
    if not target_period:
        iso_pattern = r'\b(20\d{2})[-/](\d{1,2})\b'
        iso_match = re.search(iso_pattern, question or "")
        if iso_match:
            year = int(iso_match.group(1))
            month = int(iso_match.group(2))
            if 1 <= month <= 12:
                target_period = pd.Period(f"{year}-{month:02d}", freq="M")
                target_year = year
                target_month = month
    
    # Pattern 3: Year only (fallback)
    if not target_period:
        year_match = re.search(r'\b(20\d{2})\b', question or "")
        if year_match:
            target_year = int(year_match.group(1))
    
    # Filter to actuals only for spend questions
    actuals_fin = fin[fin['source'] == 'actuals'].copy()
    
    if specific_category:
        # Calculate total spend for specific category
        category_pattern = f"Opex:{specific_category}"
        category_data = actuals_fin[actuals_fin['account_category'] == category_pattern]
        
        if category_data.empty:
            return {"answer": f"No {specific_category} expenses found in the dataset."}
        
        # Apply date filters if specified
        if target_period:
            # Specific month filtering
            category_data = category_data[category_data['month'] == target_period]
            if category_data.empty:
                return {"answer": f"No {specific_category} expenses found for {target_period}."}
        elif target_year:
            # Year filtering
            category_data = category_data[category_data['month'].dt.year == target_year]
            if category_data.empty:
                return {"answer": f"No {specific_category} expenses found for {target_year}."}
        
        total_spend = float(category_data['amount_usd'].sum())
        months_with_data = category_data['month'].nunique()
        
        # Get monthly breakdown for chart
        monthly_spend = category_data.groupby('month')['amount_usd'].sum().sort_index()
        
        # Build answer based on the specificity of the date filter
        if target_period:
            # Specific month
            answer = f"Based on the actuals, {specific_category} spend in {target_period} was {fmt_usd(total_spend)}."
        elif target_year:
            # Specific year
            date_range = f"{category_data['month'].min()} → {category_data['month'].max()}"
            answer = f"Based on the actuals, {specific_category} spend in {target_year} totals {fmt_usd(total_spend)} across {months_with_data} months ({date_range})."
        else:
            # All time
            date_range = f"{category_data['month'].min()} → {category_data['month'].max()}"
            answer = f"Based on the actuals, {specific_category} spend totals {fmt_usd(total_spend)} across {months_with_data} months ({date_range})."
        
        # Create trend chart for the specific category
        data_points = [{"month": str(m), "amount": float(v)} for m, v in monthly_spend.items()]
        return {"answer": answer, "chart": {"kind": "category_trend", "payload": {"category": specific_category, "data": data_points}}}
    
    else:
        # General opex breakdown for latest month or specified period
        sel = parse_months(question, months)
        if sel is None or sel.empty:
            sel = pd.Series([months.max()], dtype="period[M]")
        m = sel.iloc[-1]
        ser = opex_breakdown_month(actuals_fin, m, entity)
        if ser.empty:
            return {"answer": f"No Opex categories found for {m}."}
        total = float(ser.sum())
        answer = f"Opex breakdown for {m}; total {fmt_usd(total)}."
        payload = {"month": str(m), "bars": [{"category": str(k), "amount": float(v)} for k, v in ser.items()]}
        return {"answer": answer, "chart": {"kind": "opex_breakdown", "payload": payload}}

def tool_cash_runway(fin: pd.DataFrame, cash: pd.DataFrame, question: str, entity: Optional[str]) -> Dict[str, Any]:
    months = get_available_months(fin)
    last6 = months.sort_values().tail(6)
    e = ebitda_series(fin, last6, entity)
    r = cash_runway(cash, e.tail(3))
    if r == float("inf"):
        last3 = e.tail(3)
        answer = (
            "Runway is ∞ because average net burn over the last 3 months is $0 "
            f"(EBITDA: {', '.join(f'{m}: {v:,.0f}' for m, v in last3.items())})."
        )
    else:
        answer = f"Runway is {r:.1f} months based on latest cash and average net burn (last 3 months)."
    # chart hint: always show cash trend
    return {"answer": answer, "chart": {"kind": "cash_trend", "payload": {}}}

def tool_revenue_analysis(fin: pd.DataFrame, cash: pd.DataFrame, question: str, entity: Optional[str]) -> Dict[str, Any]:
    """Comprehensive revenue analysis for CFO-level questions"""
    months = get_available_months(fin)
    q = (question or "").lower()
    
    # Enhanced date parsing for year and month-specific filtering
    import re
    from dateutil.parser import parse as dtparse
    
    target_year = None
    target_month = None
    target_period = None
    
    # Try to parse specific month-year combinations first
    # Pattern 1: "January 2025", "March 2024", etc.
    month_year_pattern = r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s+(20\d{2})\b'
    month_year_match = re.search(month_year_pattern, question or "", re.IGNORECASE)
    
    if month_year_match:
        month_str = month_year_match.group(1)
        year_str = month_year_match.group(2)
        try:
            parsed_date = dtparse(f"{month_str} {year_str}")
            target_period = pd.Period(f"{parsed_date.year}-{parsed_date.month:02d}", freq="M")
            target_year = parsed_date.year
            target_month = parsed_date.month
        except:
            pass
    
    # Pattern 2: "2025-01", "2024-03", etc.
    if not target_period:
        iso_pattern = r'\b(20\d{2})[-/](\d{1,2})\b'
        iso_match = re.search(iso_pattern, question or "")
        if iso_match:
            year = int(iso_match.group(1))
            month = int(iso_match.group(2))
            if 1 <= month <= 12:
                target_period = pd.Period(f"{year}-{month:02d}", freq="M")
                target_year = year
                target_month = month
    
    # Pattern 3: Year only (fallback)
    if not target_period:
        year_match = re.search(r'\b(20\d{2})\b', question or "")
        if year_match:
            target_year = int(year_match.group(1))
    
    # Filter revenue data
    revenue_data = fin[fin['account_category'] == 'Revenue'].copy()
    
    if revenue_data.empty:
        return {"answer": "No revenue data found in the dataset."}
    
    # Apply date filters if specified
    if target_period:
        # Specific month filtering
        revenue_data = revenue_data[revenue_data['month'] == target_period]
        if revenue_data.empty:
            return {"answer": f"No revenue data found for {target_period}."}
        months = months[months == target_period]
    elif target_year:
        # Year filtering
        revenue_data = revenue_data[revenue_data['month'].dt.year == target_year]
        if revenue_data.empty:
            return {"answer": f"No revenue data found for {target_year}."}
        months = months[months.dt.year == target_year]
    
    # Calculate totals by source
    actuals_total = float(revenue_data[revenue_data['source'] == 'actuals']['amount_usd'].sum())
    budget_total = float(revenue_data[revenue_data['source'] == 'budget']['amount_usd'].sum())
    
    # Monthly revenue trends
    monthly_actuals = revenue_data[revenue_data['source'] == 'actuals'].groupby('month')['amount_usd'].sum().sort_index()
    monthly_budget = revenue_data[revenue_data['source'] == 'budget'].groupby('month')['amount_usd'].sum().sort_index()
    
    # Performance metrics
    variance = actuals_total - budget_total
    variance_pct = (variance / budget_total * 100) if budget_total > 0 else 0
    
    # Growth analysis (if sufficient data)
    growth_info = ""
    if len(monthly_actuals) >= 6:
        if len(monthly_actuals) >= 12:
            recent_6m = monthly_actuals.tail(6).mean()
            prior_6m = monthly_actuals.head(6).mean()
        else:
            # For shorter periods, compare first half vs second half
            mid_point = len(monthly_actuals) // 2
            recent_6m = monthly_actuals.tail(mid_point).mean()
            prior_6m = monthly_actuals.head(mid_point).mean()
        
        growth_rate = ((recent_6m - prior_6m) / prior_6m * 100) if prior_6m > 0 else 0
        growth_info = f"\n• Growth: Recent avg {fmt_usd(recent_6m)} vs Prior avg {fmt_usd(prior_6m)} ({growth_rate:+.1f}%)"
    
    # Entity breakdown
    entity_breakdown = ""
    if revenue_data['entity'].nunique() > 1:
        entity_actuals = revenue_data[revenue_data['source'] == 'actuals'].groupby('entity')['amount_usd'].sum().sort_values(ascending=False)
        entity_breakdown = f"\n• By Entity: " + ", ".join([f"{entity} {fmt_usd(amount)}" for entity, amount in entity_actuals.items()])
    
    # Build title based on the specificity of the date filter
    if target_period:
        title = f"Revenue Analysis for {target_period}"
    elif target_year:
        title = f"Revenue Analysis for {target_year}"
    else:
        date_range = f"{months.min()} → {months.max()}" if not months.empty else "No data"
        title = f"Revenue Analysis ({date_range})"
    
    answer = (f"{title}:\n"
             f"• Total Revenue (Actual): {fmt_usd(actuals_total)}\n"
             f"• Total Revenue (Budget): {fmt_usd(budget_total)}\n"
             f"• Variance: {fmt_usd(variance)} ({variance_pct:+.1f}% vs budget)"
             f"{growth_info}"
             f"{entity_breakdown}")
    
    # Create revenue trend chart
    chart_data = []
    for month in monthly_actuals.index:
        point = {"month": str(month), "actual": float(monthly_actuals.get(month, 0))}
        if month in monthly_budget.index:
            point["budget"] = float(monthly_budget[month])
        chart_data.append(point)
    
    return {"answer": answer, "chart": {"kind": "revenue_trend", "payload": {"data": chart_data}}}

def tool_financial_performance(fin: pd.DataFrame, cash: pd.DataFrame, question: str, entity: Optional[str]) -> Dict[str, Any]:
    """Comprehensive financial performance analysis for CFO dashboard"""
    months = get_available_months(fin)
    
    if months.empty:
        return {"answer": "No financial data available for analysis."}
    
    # Get actuals data
    actuals = fin[fin['source'] == 'actuals'].copy()
    
    # Revenue analysis
    revenue = actuals[actuals['account_category'] == 'Revenue']['amount_usd'].sum()
    
    # Cost analysis
    cogs = actuals[actuals['account_category'] == 'COGS']['amount_usd'].sum()
    gross_profit = revenue - cogs
    gross_margin_pct = (gross_profit / revenue * 100) if revenue > 0 else 0
    
    # OpEx analysis
    opex_categories = actuals[actuals['account_category'].str.startswith('Opex:')]
    total_opex = opex_categories['amount_usd'].sum()
    
    # EBITDA calculation
    ebitda = gross_profit - total_opex
    ebitda_margin_pct = (ebitda / revenue * 100) if revenue > 0 else 0
    
    # Cash analysis
    cash_start = cash['amount_usd'].iloc[0] if not cash.empty else 0
    cash_end = cash['amount_usd'].iloc[-1] if not cash.empty else 0
    cash_burn = cash_start - cash_end
    
    # Monthly burn rate (last 6 months)
    if len(months) >= 6:
        recent_months = months.tail(6)
        recent_ebitda = []
        for m in recent_months:
            month_data = actuals[actuals['month'] == m]
            month_rev = month_data[month_data['account_category'] == 'Revenue']['amount_usd'].sum()
            month_cogs = month_data[month_data['account_category'] == 'COGS']['amount_usd'].sum()
            month_opex = month_data[month_data['account_category'].str.startswith('Opex:')]['amount_usd'].sum()
            month_ebitda = month_rev - month_cogs - month_opex
            recent_ebitda.append(month_ebitda)
        avg_monthly_burn = -sum(recent_ebitda) / len(recent_ebitda) if recent_ebitda else 0
        runway_months = cash_end / avg_monthly_burn if avg_monthly_burn > 0 else float('inf')
    else:
        avg_monthly_burn = 0
        runway_months = float('inf')
    
    runway_text = f"{runway_months:.1f} months" if runway_months != float('inf') else "∞ (profitable)"
    
    answer = (f"Financial Performance Summary ({months.min()} → {months.max()}):\n"
             f"• Revenue: {fmt_usd(revenue)}\n"
             f"• Gross Profit: {fmt_usd(gross_profit)} ({gross_margin_pct:.1f}% margin)\n"
             f"• Total OpEx: {fmt_usd(total_opex)}\n"
             f"• EBITDA: {fmt_usd(ebitda)} ({ebitda_margin_pct:.1f}% margin)\n"
             f"• Cash: {fmt_usd(cash_start)} → {fmt_usd(cash_end)} ({fmt_usd(-cash_burn)} burn)\n"
             f"• Runway: {runway_text}")
    
    return {"answer": answer, "chart": {"kind": "cash_trend", "payload": {}}}

def tool_data_coverage(fin: pd.DataFrame, cash: pd.DataFrame, question: str, entity: Optional[str]) -> Dict[str, Any]:
    months = get_available_months(fin)
    n = len(months)
    if n == 0:
        return {"answer": "I don’t see any monthly rows in the dataset."}
    # Get current date context to distinguish historical vs projected data
    from datetime import datetime
    current_period = pd.Period(datetime.now(), freq='M')
    historical = months[months <= current_period]
    projected = months[months > current_period]
    
    entities = fin['entity'].nunique()
    entity_names = sorted(fin['entity'].dropna().unique().tolist())
    
    # Calculate key financial metrics across the dataset
    revenue_data = fin[fin['account_category'] == 'Revenue'].groupby(['month', 'source'])['amount_usd'].sum().unstack(fill_value=0)
    total_revenue_actual = revenue_data.get('actuals', pd.Series()).sum() if 'actuals' in revenue_data.columns else 0
    total_revenue_budget = revenue_data.get('budget', pd.Series()).sum() if 'budget' in revenue_data.columns else 0
    
    # Cash analysis
    cash_start = cash['amount_usd'].iloc[0] if not cash.empty else 0
    cash_end = cash['amount_usd'].iloc[-1] if not cash.empty else 0
    cash_change = cash_end - cash_start
    
    # Build comprehensive answer with numerical insights
    coverage_text = f"{len(historical)} historical + {len(projected)} projected" if len(projected) > 0 else f"{n} historical"
    
    answer = (f"Dataset Analysis ({coverage_text} months from {months.min()} → {months.max()}):\n"
             f"• Entities: {', '.join(entity_names)} ({entities} total)\n"
             f"• Total Revenue (Actual): {fmt_usd(total_revenue_actual)}\n"
             f"• Total Revenue (Budget): {fmt_usd(total_revenue_budget)}\n"
             f"• Cash Movement: {fmt_usd(cash_start)} → {fmt_usd(cash_end)} ({fmt_usd(cash_change)} change)")
    
    # Generate a comprehensive overview chart showing revenue and cash trends
    return {"answer": answer, "chart": {"kind": "dataset_overview", "payload": {}}}

# Tool catalog passed to the LLM
# Tool catalog passed to the LLM (Responses API format: name + input_schema)
TOOL_SPECS = [
    {
        "type": "function",
        "name": "revenue_analysis",
        "description": "Comprehensive revenue analysis including totals, variance, growth trends, and entity breakdown with trend charts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity": {"type": "string", "description": "Entity name if specified."}
            },
            "required": []
        },
    },
    {
        "type": "function",
        "name": "revenue_vs_budget",
        "description": "Compare revenue actual vs budget for a requested month or period; answer with a grouped bar chart if possible.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month_hint": {
                    "type": "string",
                    "description": "Natural text describing the month(s), e.g., 'June 2025', 'last 3 months'."
                },
                "entity": {
                    "type": "string",
                    "description": "Entity name if specified."
                }
            },
            "required": []
        },
    },
    {
        "type": "function",
        "name": "gm_trend",
        "description": "Gross Margin % trend over a requested window; return a line chart where appropriate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month_hint": {"type": "string"},
                "entity": {"type": "string"}
            },
            "required": []
        },
    },
    {
        "type": "function",
        "name": "opex_breakdown",
        "description": "Analyze operating expenses - either breakdown by category for a specific month, or calculate total spend for specific categories (Marketing, Sales, R&D, Admin) across all periods with trend charts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month_hint": {"type": "string"},
                "entity": {"type": "string"}
            },
            "required": []
        },
    },
    {
        "type": "function",
        "name": "cash_runway",
        "description": "Compute cash runway from latest cash and average monthly net burn (last 3 months); include a cash trend chart.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity": {"type": "string"}
            },
            "required": []
        },
    },
    {
        "type": "function",
        "name": "financial_performance",
        "description": "Comprehensive financial performance analysis including revenue, margins, EBITDA, cash burn, and runway calculations for CFO dashboard.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity": {"type": "string", "description": "Entity name if specified."}
            },
            "required": []
        },
    },
    {
        "type": "function",
        "name": "data_coverage",
        "description": "Provide comprehensive dataset analysis including financial metrics, cash flow trends, and visual charts for data coverage questions.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        },
    },
]


# Dispatcher used by the agent after tool call
def dispatch(tool_name: str, args: Dict[str, Any], fin: pd.DataFrame, cash: pd.DataFrame, question_text: str, entity: Optional[str]) -> Dict[str, Any]:
    hint = (args or {}).get("month_hint") or question_text
    ent = (args or {}).get("entity") or entity
    if tool_name == "revenue_analysis":
        return tool_revenue_analysis(fin, cash, hint, ent)
    if tool_name == "revenue_vs_budget":
        return tool_revenue_vs_budget(fin, cash, hint, ent)
    if tool_name == "gm_trend":
        return tool_gm_trend(fin, cash, hint, ent)
    if tool_name == "opex_breakdown":
        return tool_opex_breakdown(fin, cash, hint, ent)
    if tool_name == "cash_runway":
        return tool_cash_runway(fin, cash, hint, ent)
    if tool_name == "financial_performance":
        return tool_financial_performance(fin, cash, hint, ent)
    if tool_name == "data_coverage":
        return tool_data_coverage(fin, cash, hint, ent)
    return {"answer": "Unknown tool requested."}
