# CFO Agentic RAG System Tests

This directory contains comprehensive tests for the CFO Agentic RAG Financial Analysis System.

## Test Structure

### Core Test Files

- **`test_financial_analysis.py`** - Main financial calculation tests
  - Revenue analysis (actual vs budget)
  - Gross margin calculations ((Revenue - COGS) / Revenue)
  - OpEx analysis (grouped by categories)
  - EBITDA calculations (Revenue - COGS - OpEx)
  - Cash runway calculations (cash ÷ avg monthly burn)
  - Date-specific filtering (month/year)

- **`test_data.py`** - Data loading and integrity tests
  - CSV file loading from fixtures
  - Data normalization and currency conversion
  - Data completeness and consistency checks

- **`test_tools.py`** - Tool function tests
  - Individual tool routing and responses
  - Error handling and edge cases
  - Question type classification

### Configuration Files

- **`conftest.py`** - Shared pytest fixtures and configuration
- **`__init__.py`** - Makes tests a proper Python package

## Running Tests

### Run All Tests
```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/test_financial_analysis.py -v
```

### Run Specific Test Class
```bash
python -m pytest tests/test_financial_analysis.py::TestRevenueAnalysis -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=agent --cov-report=html
```

## Test Results Summary

✅ **35/35 Tests Passing**

### Financial Formula Validation
- **Revenue Analysis**: $29.1M actual vs $30.8M budget (-5.4% variance)
- **Gross Margin**: 84.8% = ($29.1M - $4.4M) / $29.1M  
- **OpEx Categories**: Marketing ($5.5M), Sales ($3.4M), R&D ($1.8M), Admin ($1.7M)
- **EBITDA**: $12.4M = $29.1M - $4.4M - $12.3M (42.4% margin)
- **Cash Runway**: ∞ (profitable company with positive EBITDA)

### Date-Specific Analysis
- **Year Filtering**: "Revenue in 2025" → $12.0M
- **Month Filtering**: "Marketing spend in January 2025" → $169.9K
- **Multi-format Support**: "Jan 2025", "2025-01", "January 2025"

### Data Integrity
- **36 months** of financial data (2023-01 → 2025-12)
- **2 entities**: ParentCo, EMEA
- **Currency normalization** to USD
- **Complete account categories**: Revenue, COGS, OpEx:Marketing/Sales/R&D/Admin

## Key Test Categories

1. **Revenue Analysis** (3 tests)
2. **Gross Margin Calculation** (2 tests) 
3. **OpEx Analysis** (3 tests)
4. **EBITDA Calculation** (2 tests)
5. **Cash Runway Calculation** (2 tests)
6. **Date-Specific Analysis** (2 tests)
7. **Data Integrity** (7 tests)
8. **Tool Routing** (5 tests)
9. **Error Handling** (3 tests)

All tests validate that the CFO Agentic RAG system provides accurate financial analysis with proper mathematical formulas and robust date filtering capabilities.