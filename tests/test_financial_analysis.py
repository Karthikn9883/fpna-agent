"""
Comprehensive pytest tests for CFO Agentic RAG Financial Analysis System
Tests all key financial calculations and formulas
"""

import pytest
import pandas as pd
import sys
import os

# Add the parent directory to the path so we can import from agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.data import load_from_csv_dir, normalize, get_available_months
from agent.tools import (
    tool_revenue_analysis, 
    tool_opex_breakdown, 
    tool_financial_performance,
    tool_gm_trend,
    tool_cash_runway
)
from agent.metrics import (
    revenue_month,
    gross_margin_pct_series,
    opex_breakdown_month,
    ebitda_series,
    cash_runway
)


@pytest.fixture
def sample_data():
    """Load and normalize test data"""
    dfs = load_from_csv_dir('fixtures')
    norm = normalize(dfs)
    return norm['financials'], norm['cash']


class TestRevenueAnalysis:
    """Test Revenue (USD): actual vs budget calculations"""
    
    def test_total_revenue_calculation(self, sample_data):
        fin, cash = sample_data
        result = tool_revenue_analysis(fin, cash, 'total revenue analysis', None)
        
        # Verify revenue totals are calculated correctly
        assert "Total Revenue (Actual)" in result['answer']
        assert "Total Revenue (Budget)" in result['answer']
        assert "Variance:" in result['answer']
        
        # Extract actual revenue from answer
        lines = result['answer'].split('\n')
        actual_line = [line for line in lines if "Total Revenue (Actual)" in line][0]
        assert "$29.1M" in actual_line  # Expected total from our data
    
    def test_revenue_variance_calculation(self, sample_data):
        fin, cash = sample_data
        result = tool_revenue_analysis(fin, cash, 'revenue variance analysis', None)
        
        # Verify variance calculation: actual - budget
        assert "Variance:" in result['answer']
        assert "vs budget" in result['answer']
        
        # Should show negative variance (under budget)
        assert "-$1.7M" in result['answer']
        assert "-5.4%" in result['answer']
    
    def test_monthly_revenue_specific(self, sample_data):
        fin, cash = sample_data
        result = tool_revenue_analysis(fin, cash, 'revenue in January 2025', None)
        
        # Test month-specific revenue calculation
        assert "Revenue Analysis for 2025-01" in result['answer']
        assert "Total Revenue (Actual)" in result['answer']
        
        # Verify chart data is provided
        assert result['chart']['kind'] == 'revenue_trend'
        assert len(result['chart']['payload']['data']) >= 1


class TestGrossMarginCalculation:
    """Test Gross Margin %: (Revenue – COGS) / Revenue"""
    
    def test_gross_margin_formula(self, sample_data):
        fin, cash = sample_data
        months = get_available_months(fin)
        
        # Test gross margin calculation for a specific month
        test_month = months.iloc[0]  # First available month
        
        # Get revenue and COGS for the month
        month_data = fin[(fin['month'] == test_month) & (fin['source'] == 'actuals')]
        revenue = month_data[month_data['account_category'] == 'Revenue']['amount_usd'].sum()
        cogs = month_data[month_data['account_category'] == 'COGS']['amount_usd'].sum()
        
        # Calculate expected gross margin
        expected_gm = (revenue - cogs) / revenue if revenue > 0 else 0
        
        # Test using the gross margin function
        gm_series = gross_margin_pct_series(fin, pd.Series([test_month]), None)
        actual_gm = gm_series.iloc[0] if not gm_series.empty else 0
        
        # Verify calculation is correct (within small tolerance for floating point)
        assert abs(actual_gm - expected_gm) < 0.001
    
    def test_gm_trend_tool(self, sample_data):
        fin, cash = sample_data
        result = tool_gm_trend(fin, cash, 'gross margin trend last 3 months', None)
        
        # Verify GM trend analysis
        assert "Gross Margin %" in result['answer']
        assert "%" in result['answer']  # Should show percentage values
        assert result['chart']['kind'] == 'gm_trend'


class TestOpexAnalysis:
    """Test Opex total (USD): grouped by Opex:* categories"""
    
    def test_opex_category_grouping(self, sample_data):
        fin, cash = sample_data
        months = get_available_months(fin)
        test_month = months.iloc[-1]  # Latest month
        
        # Test opex breakdown calculation
        opex_breakdown = opex_breakdown_month(fin, test_month, None)
        
        # Verify all opex categories are included
        expected_categories = ['Marketing', 'Sales', 'R&D', 'Admin']
        for category in expected_categories:
            assert any(category in str(cat) for cat in opex_breakdown.index)
    
    def test_marketing_spend_calculation(self, sample_data):
        fin, cash = sample_data
        result = tool_opex_breakdown(fin, cash, 'how much money is spent on marketing?', None)
        
        # Verify marketing spend calculation
        assert "Marketing spend totals" in result['answer']
        assert "$5.5M" in result['answer']  # Expected total from our data
        
        # Verify chart is provided
        assert result['chart']['kind'] == 'category_trend'
    
    def test_monthly_opex_specific(self, sample_data):
        fin, cash = sample_data
        result = tool_opex_breakdown(fin, cash, 'marketing spend in January 2025', None)
        
        # Test month-specific opex calculation
        assert "Marketing spend in 2025-01 was" in result['answer']
        assert "$" in result['answer']  # Should show dollar amount


class TestEBITDACalculation:
    """Test EBITDA (proxy): Revenue – COGS – Opex"""
    
    def test_ebitda_formula(self, sample_data):
        fin, cash = sample_data
        months = get_available_months(fin)
        test_months = months.tail(3)  # Last 3 months
        
        # Calculate EBITDA using the function
        ebitda_data = ebitda_series(fin, test_months, None)
        
        # Verify EBITDA calculation for each month
        for month in test_months:
            if month in ebitda_data.index:
                month_data = fin[(fin['month'] == month) & (fin['source'] == 'actuals')]
                
                revenue = month_data[month_data['account_category'] == 'Revenue']['amount_usd'].sum()
                cogs = month_data[month_data['account_category'] == 'COGS']['amount_usd'].sum()
                opex = month_data[month_data['account_category'].str.startswith('Opex:')]['amount_usd'].sum()
                
                expected_ebitda = revenue - cogs - opex
                actual_ebitda = ebitda_data[month]
                
                # Verify calculation (within tolerance)
                assert abs(actual_ebitda - expected_ebitda) < 1.0  # Within $1
    
    def test_financial_performance_ebitda(self, sample_data):
        fin, cash = sample_data
        result = tool_financial_performance(fin, cash, 'financial performance summary', None)
        
        # Verify EBITDA is included in financial performance
        assert "EBITDA:" in result['answer']
        assert "margin" in result['answer']
        assert "$12.4M" in result['answer']  # Expected EBITDA from our data


class TestCashRunwayCalculation:
    """Test Cash runway: cash ÷ avg monthly net burn (last 3 months)"""
    
    def test_cash_runway_formula(self, sample_data):
        fin, cash = sample_data
        months = get_available_months(fin)
        last_3_months = months.tail(3)
        
        # Calculate EBITDA for last 3 months (proxy for net burn)
        ebitda_data = ebitda_series(fin, last_3_months, None)
        
        # Calculate runway using the function
        runway = cash_runway(cash, ebitda_data)
        
        # Verify runway calculation
        if not ebitda_data.empty:
            avg_monthly_burn = -ebitda_data.mean()  # Negative EBITDA = burn
            current_cash = cash['amount_usd'].iloc[-1] if not cash.empty else 0
            
            if avg_monthly_burn > 0:
                expected_runway = current_cash / avg_monthly_burn
                assert abs(runway - expected_runway) < 0.1  # Within 0.1 months
            else:
                assert runway == float('inf')  # Profitable = infinite runway
    
    def test_cash_runway_tool(self, sample_data):
        fin, cash = sample_data
        result = tool_cash_runway(fin, cash, 'cash runway analysis', None)
        
        # Verify cash runway analysis
        assert "Runway is" in result['answer']
        assert "months" in result['answer'] or "∞" in result['answer']
        assert result['chart']['kind'] == 'cash_trend'


class TestDateSpecificAnalysis:
    """Test month and year specific filtering"""
    
    def test_year_specific_filtering(self, sample_data):
        fin, cash = sample_data
        
        # Test year-specific revenue
        result_2025 = tool_revenue_analysis(fin, cash, 'revenue in 2025', None)
        assert "Revenue Analysis for 2025" in result_2025['answer']
        
        # Test year-specific expenses
        result_marketing = tool_opex_breakdown(fin, cash, 'marketing spend in 2025', None)
        assert "Marketing spend in 2025 totals" in result_marketing['answer']
    
    def test_month_specific_filtering(self, sample_data):
        fin, cash = sample_data
        
        # Test month-specific revenue
        result_jan = tool_revenue_analysis(fin, cash, 'revenue in January 2025', None)
        assert "Revenue Analysis for 2025-01" in result_jan['answer']
        
        # Test month-specific expenses
        result_marketing = tool_opex_breakdown(fin, cash, 'marketing spend in January 2025', None)
        assert "Marketing spend in 2025-01 was" in result_marketing['answer']


class TestDataIntegrity:
    """Test data loading and integrity"""
    
    def test_data_loading(self, sample_data):
        fin, cash = sample_data
        
        # Verify data is loaded correctly
        assert not fin.empty
        assert not cash.empty
        assert 'month' in fin.columns
        assert 'amount_usd' in fin.columns
        assert 'source' in fin.columns
    
    def test_financial_data_completeness(self, sample_data):
        fin, cash = sample_data
        
        # Verify key account categories exist
        categories = fin['account_category'].unique()
        assert 'Revenue' in categories
        assert 'COGS' in categories
        assert any('Opex:' in cat for cat in categories)
        
        # Verify both actuals and budget data exist
        sources = fin['source'].unique()
        assert 'actuals' in sources
        assert 'budget' in sources


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])