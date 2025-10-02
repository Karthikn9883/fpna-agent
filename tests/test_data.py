"""
Tests for data loading and processing functions
"""

import pytest
import pandas as pd
from agent.data import load_from_csv_dir, normalize, get_available_months


class TestDataLoading:
    """Test data loading and normalization"""
    
    def test_load_from_csv_dir(self):
        """Test loading CSV files from fixtures directory"""
        dfs = load_from_csv_dir('fixtures')
        
        # Check that all expected files are loaded
        expected_files = ['actuals', 'budget', 'fx', 'cash']
        for file in expected_files:
            assert file in dfs
            assert isinstance(dfs[file], pd.DataFrame)
            assert not dfs[file].empty
    
    def test_normalize_function(self):
        """Test data normalization process"""
        dfs = load_from_csv_dir('fixtures')
        norm = normalize(dfs)
        
        # Check normalized structure
        assert 'financials' in norm
        assert 'cash' in norm
        
        fin = norm['financials']
        cash = norm['cash']
        
        # Check financial data structure
        required_fin_columns = ['month', 'entity', 'account_category', 'amount_usd', 'source']
        for col in required_fin_columns:
            assert col in fin.columns
        
        # Check cash data structure
        required_cash_columns = ['month', 'entity', 'amount_usd']
        for col in required_cash_columns:
            assert col in cash.columns
        
        # Check data types
        assert fin['month'].dtype == 'period[M]'
        assert cash['month'].dtype == 'period[M]'
        assert pd.api.types.is_numeric_dtype(fin['amount_usd'])
        assert pd.api.types.is_numeric_dtype(cash['amount_usd'])
    
    def test_get_available_months(self, financial_data):
        """Test getting available months from financial data"""
        months = get_available_months(financial_data)
        
        assert isinstance(months, pd.Series)
        assert not months.empty
        assert months.dtype == 'period[M]'
        assert months.is_monotonic_increasing  # Should be sorted
        
        # Check expected date range
        assert months.min() == pd.Period('2023-01', freq='M')
        assert months.max() == pd.Period('2025-12', freq='M')


class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_financial_data_completeness(self, financial_data):
        """Test that financial data has all required categories"""
        categories = financial_data['account_category'].unique()
        
        # Check for required account categories
        assert 'Revenue' in categories
        assert 'COGS' in categories
        
        # Check for OpEx categories
        opex_categories = [cat for cat in categories if cat.startswith('Opex:')]
        expected_opex = ['Opex:Marketing', 'Opex:Sales', 'Opex:R&D', 'Opex:Admin']
        for opex in expected_opex:
            assert opex in opex_categories
        
        # Check for both actuals and budget data
        sources = financial_data['source'].unique()
        assert 'actuals' in sources
        assert 'budget' in sources
    
    def test_cash_data_completeness(self, cash_data):
        """Test that cash data is complete and consistent"""
        assert not cash_data.empty
        
        # Check for expected entities
        entities = cash_data['entity'].unique()
        assert 'Consolidated' in entities
        
        # Check that cash amounts are reasonable (positive)
        assert (cash_data['amount_usd'] > 0).all()
        
        # Check date continuity (should have consecutive months)
        months = cash_data['month'].sort_values().unique()
        assert len(months) == 36  # Expected 36 months of data
    
    def test_currency_conversion(self, financial_data):
        """Test that currency conversion to USD worked correctly"""
        # All amounts should be in USD after normalization
        assert 'amount_usd' in financial_data.columns
        assert pd.api.types.is_numeric_dtype(financial_data['amount_usd'])
        
        # Check that USD amounts are reasonable (positive for revenue/expenses)
        revenue_data = financial_data[financial_data['account_category'] == 'Revenue']
        assert (revenue_data['amount_usd'] > 0).all()
        
        cogs_data = financial_data[financial_data['account_category'] == 'COGS']
        assert (cogs_data['amount_usd'] > 0).all()
    
    def test_entity_consistency(self, sample_data):
        """Test that entities are consistent across datasets"""
        fin, cash = sample_data
        
        # Check that financial data has expected entities
        fin_entities = set(fin['entity'].unique())
        expected_entities = {'ParentCo', 'EMEA'}
        assert expected_entities.issubset(fin_entities)
        
        # Cash data should have consolidated entity
        cash_entities = set(cash['entity'].unique())
        assert 'Consolidated' in cash_entities