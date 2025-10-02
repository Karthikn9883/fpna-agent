from __future__ import annotations
from typing import List, Dict
import plotly.graph_objects as go
import pandas as pd

def fmt_usd(x: float) -> str:
    sign = '-' if x < 0 else ''
    x = abs(x)
    if x >= 1_000_000:
        return f"{sign}${x/1_000_000:.1f}M"
    if x >= 1_000:
        return f"{sign}${x/1_000:.1f}K"
    return f"{sign}${x:,.0f}"

def revenue_vs_budget_fig(actual: float, budget: float, month: pd.Period, for_print: bool = False):
    fig = go.Figure()
    fig.add_bar(
        name='Actual',
        x=[str(month)], y=[actual],
        marker_pattern_shape='/' if for_print else None,
        text=[fmt_usd(actual)] if for_print else None,
        textposition='outside'
    )
    fig.add_bar(
        name='Budget',
        x=[str(month)], y=[budget],
        marker_pattern_shape='\\' if for_print else None,
        text=[fmt_usd(budget)] if for_print else None,
        textposition='outside'
    )
    fig.update_layout(
        barmode='group',
        title=f"Revenue vs Budget — {str(month)}",
        xaxis_title='', yaxis_title='USD',
        uniformtext_minsize=10, uniformtext_mode='hide'
    )
    return fig

def gm_trend_fig(gm_pct: pd.Series, for_print: bool = False):
    fig = go.Figure()
    fig.add_scatter(
        x=[str(m) for m in gm_pct.index],
        y=(gm_pct * 100.0),
        mode='lines+markers',
        name='GM %',
        line=dict(dash='dash' if for_print else None),
        marker=dict(symbol='diamond' if for_print else 'circle', size=8)
    )
    fig.update_layout(title='Gross Margin % Trend', xaxis_title='Month', yaxis_title='GM %')
    return fig

def opex_breakdown_fig(ser: pd.Series, month: pd.Period):
    # Original donut for on-screen color view
    fig = go.Figure(data=[go.Pie(labels=ser.index, values=ser.values, hole=0.35)])
    fig.update_layout(title=f"Opex Breakdown — {str(month)}")
    return fig

def opex_breakdown_bar_fig(ser: pd.Series, month: pd.Period, for_print: bool = False):
    # Print-friendly horizontal bars with labels/patterns
    fig = go.Figure()
    fig.add_bar(
        y=ser.index.tolist(),
        x=ser.values.tolist(),
        orientation='h',
        marker_pattern_shape='/' if for_print else None,
        text=[fmt_usd(v) for v in ser.values] if for_print else None,
        textposition='outside'
    )
    fig.update_layout(
        title=f"Opex Breakdown — {str(month)}",
        xaxis_title='USD', yaxis_title='Category',
        uniformtext_minsize=10, uniformtext_mode='hide'
    )
    fig.update_yaxes(autorange="reversed")  # largest at top
    return fig

def cash_trend_fig(cash_df: pd.DataFrame, for_print: bool = False):
    s = cash_df.sort_values('month').set_index('month')['amount_usd']
    fig = go.Figure()
    fig.add_scatter(
        x=[str(m) for m in s.index],
        y=s.values,
        mode='lines+markers',
        name='Cash (USD)',
        line=dict(dash='dot' if for_print else None),
        marker=dict(symbol='square' if for_print else 'circle', size=7)
    )
    fig.update_layout(title='Cash Balance Trend', xaxis_title='Month', yaxis_title='USD')
    return fig
def dataset_overview_fig(fin_df: pd.DataFrame, cash_df: pd.DataFrame, for_print: bool = False):
    """Comprehensive overview chart showing revenue trends and cash balance"""
    fig = go.Figure()
    
    # Revenue trend (actual vs budget)
    revenue_data = fin_df[fin_df['account_category'] == 'Revenue'].groupby(['month', 'source'])['amount_usd'].sum().unstack(fill_value=0)
    
    if 'actuals' in revenue_data.columns:
        fig.add_scatter(
            x=[str(m) for m in revenue_data.index],
            y=revenue_data['actuals'].values,
            mode='lines+markers',
            name='Revenue (Actual)',
            line=dict(color='#1f77b4', dash='solid' if not for_print else 'dash'),
            marker=dict(symbol='circle', size=6),
            yaxis='y1'
        )
    
    if 'budget' in revenue_data.columns:
        fig.add_scatter(
            x=[str(m) for m in revenue_data.index],
            y=revenue_data['budget'].values,
            mode='lines+markers',
            name='Revenue (Budget)',
            line=dict(color='#ff7f0e', dash='dot'),
            marker=dict(symbol='diamond', size=6),
            yaxis='y1'
        )
    
    # Cash balance trend on secondary y-axis
    cash_sorted = cash_df.sort_values('month')
    fig.add_scatter(
        x=[str(m) for m in cash_sorted['month']],
        y=cash_sorted['amount_usd'].values,
        mode='lines+markers',
        name='Cash Balance',
        line=dict(color='#2ca02c', dash='dashdot'),
        marker=dict(symbol='square', size=6),
        yaxis='y2'
    )
    
    # Update layout with dual y-axes
    fig.update_layout(
        title='Financial Overview: Revenue Trends & Cash Balance',
        xaxis_title='Month',
        yaxis=dict(
            title='Revenue (USD)',
            side='left',
            titlefont=dict(color='#1f77b4'),
            tickfont=dict(color='#1f77b4')
        ),
        yaxis2=dict(
            title='Cash Balance (USD)',
            side='right',
            overlaying='y',
            titlefont=dict(color='#2ca02c'),
            tickfont=dict(color='#2ca02c')
        ),
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified'
    )
    
    return fig

def category_trend_fig(category: str, data_points: List[Dict], for_print: bool = False):
    """Chart showing spend trend for a specific expense category"""
    if not data_points:
        return go.Figure()
    
    months = [p["month"] for p in data_points]
    amounts = [p["amount"] for p in data_points]
    
    fig = go.Figure()
    fig.add_scatter(
        x=months,
        y=amounts,
        mode='lines+markers',
        name=f'{category} Spend',
        line=dict(dash='solid' if not for_print else 'dash'),
        marker=dict(symbol='circle', size=8),
        fill='tonexty' if not for_print else None
    )
    
    fig.update_layout(
        title=f'{category} Spend Trend Over Time',
        xaxis_title='Month',
        yaxis_title='USD',
        hovermode='x'
    )
    
    return fig

def revenue_trend_fig(data_points: List[Dict], for_print: bool = False):
    """Chart showing revenue trends (actual vs budget) over time"""
    if not data_points:
        return go.Figure()
    
    months = [p["month"] for p in data_points]
    actuals = [p.get("actual", 0) for p in data_points]
    budgets = [p.get("budget", 0) for p in data_points if "budget" in p]
    
    fig = go.Figure()
    
    # Actual revenue line
    fig.add_scatter(
        x=months,
        y=actuals,
        mode='lines+markers',
        name='Revenue (Actual)',
        line=dict(color='#1f77b4', width=3),
        marker=dict(symbol='circle', size=8)
    )
    
    # Budget revenue line (if available)
    if budgets and len(budgets) == len(months):
        fig.add_scatter(
            x=months,
            y=budgets,
            mode='lines+markers',
            name='Revenue (Budget)',
            line=dict(color='#ff7f0e', dash='dash', width=2),
            marker=dict(symbol='diamond', size=6)
        )
    
    fig.update_layout(
        title='Revenue Trend Analysis',
        xaxis_title='Month',
        yaxis_title='Revenue (USD)',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig