"""
Tests for individual tool functions in the CFO Agentic RAG system
"""

import pytest
from agent.tools import (
    tool_revenue_analysis,
    tool_opex_breakdown, 
    tool_financial_performance,
    tool_gm_trend,
    tool_cash_runway,
    tool_data_coverage
)


class TestToolRouting:
    """Test that tools handle different question types correctly"""
    
    def test_revenue_analysis_tool(self, sample_data):
        fin, cash = sample_data
        
        questions = [
            'how much revenue did we get overall?',
            'total revenue analysis',
            'revenue performance',
            'what was our revenue in 2025?'
        ]
        
        for question in questions:
            result = tool_revenue_analysis(fin, cash, question, None)
            assert 'answer' in result
            assert 'chart' in result
            assert 'Total Revenue (Actual)' in result['answer']
    
    def test_opex_breakdown_tool(self, sample_data):
        fin, cash = sample_data
        
        questions = [
            'how much money is spent on marketing?',
            'marketing spend in 2025',
            'marketing costs for January 2025'
        ]
        
        for question in questions:
            result = tool_opex_breakdown(fin, cash, question, None)
            assert 'answer' in result
            assert 'chart' in result
            assert 'Marketing spend' in result['answer']
    
    def test_financial_performance_tool(self, sample_data):
        fin, cash = sample_data
        
        result = tool_financial_performance(fin, cash, 'financial performance summary', None)
        
        # Check all key metrics are included
        required_metrics = ['Revenue:', 'Gross Profit:', 'Total OpEx:', 'EBITDA:', 'Cash:', 'Runway:']
        for metric in required_metrics:
            assert metric in result['answer']
    
    def test_cash_runway_tool(self, sample_data):
        fin, cash = sample_data
        
        result = tool_cash_runway(fin, cash, 'cash runway analysis', None)
        
        assert 'Runway is' in result['answer']
        assert result['chart']['kind'] == 'cash_trend'
    
    def test_data_coverage_tool(self, sample_data):
        fin, cash = sample_data
        
        result = tool_data_coverage(fin, cash, 'dataset analysis', None)
        
        assert 'Dataset contains' in result['answer'] or 'Dataset Analysis' in result['answer']
        assert 'entities' in result['answer'].lower()


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_question(self, sample_data):
        fin, cash = sample_data
        
        # Test with empty/None questions
        result = tool_revenue_analysis(fin, cash, '', None)
        assert 'answer' in result
        
        result = tool_opex_breakdown(fin, cash, None, None)
        assert 'answer' in result
    
    def test_invalid_date_filtering(self, sample_data):
        fin, cash = sample_data
        
        # Test with invalid years
        result = tool_revenue_analysis(fin, cash, 'revenue in 2030', None)
        assert 'No revenue data found for 2030' in result['answer']
        
        result = tool_opex_breakdown(fin, cash, 'marketing spend in 2030', None)
        assert 'No Marketing expenses found for 2030' in result['answer']
    
    def test_invalid_category(self, sample_data):
        fin, cash = sample_data
        
        # Test with non-existent expense category
        result = tool_opex_breakdown(fin, cash, 'how much is spent on invalid_category?', None)
        # Should fall back to general opex breakdown
        assert 'answer' in result