"""
Pytest configuration and shared fixtures for CFO Agentic RAG tests
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import from agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.data import load_from_csv_dir, normalize


@pytest.fixture(scope="session")
def sample_data():
    """Load and normalize test data once per test session"""
    dfs = load_from_csv_dir('fixtures')
    norm = normalize(dfs)
    return norm['financials'], norm['cash']


@pytest.fixture(scope="session") 
def financial_data(sample_data):
    """Get just the financial data"""
    fin, _ = sample_data
    return fin


@pytest.fixture(scope="session")
def cash_data(sample_data):
    """Get just the cash data"""
    _, cash = sample_data
    return cash