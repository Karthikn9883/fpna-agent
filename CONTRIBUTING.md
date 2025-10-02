# Contributing to CFO Agentic RAG

Thank you for your interest in contributing to the CFO Agentic RAG project! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- OpenAI API key (for testing agentic features)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/cfo-agentic-rag.git
   cd cfo-agentic-rag
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov  # For testing
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # Create from template
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run tests to verify setup**
   ```bash
   python -m pytest tests/ -v
   ```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_financial_analysis.py -v

# Run with coverage
python -m pytest tests/ --cov=agent --cov-report=html
```

### Writing Tests
- Add tests for all new functionality
- Follow the existing test structure in `tests/`
- Use descriptive test names and docstrings
- Ensure tests are independent and can run in any order

### Test Categories
- **Financial Analysis Tests**: Validate calculation accuracy
- **Data Tests**: Check data loading and integrity
- **Tool Tests**: Verify tool routing and responses
- **Integration Tests**: End-to-end functionality

## 📝 Code Style

### Python Style Guide
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where appropriate
- Write descriptive docstrings for functions and classes
- Keep functions focused and modular

### Code Formatting
```bash
# Install formatting tools
pip install black isort flake8

# Format code
black .
isort .

# Check style
flake8 .
```

### Example Code Style
```python
def calculate_gross_margin(revenue: float, cogs: float) -> float:
    """
    Calculate gross margin percentage.
    
    Args:
        revenue: Total revenue amount
        cogs: Cost of goods sold
        
    Returns:
        Gross margin as a percentage (0.0 to 1.0)
        
    Raises:
        ValueError: If revenue is zero or negative
    """
    if revenue <= 0:
        raise ValueError("Revenue must be positive")
    
    return (revenue - cogs) / revenue
```

## 🏗️ Architecture Guidelines

### Adding New Financial Tools
1. Create tool function in `agent/tools.py`
2. Add tool specification to `TOOL_SPECS`
3. Update dispatcher in `dispatch()` function
4. Add routing logic to `agent/agent.py`
5. Create comprehensive tests

### Adding New Chart Types
1. Implement chart function in `agent/charts.py`
2. Add chart rendering logic in `app.py`
3. Update tool to return appropriate chart payload
4. Test chart rendering with sample data

### Data Processing
- All financial data should be normalized to USD
- Use pandas Period objects for date handling
- Validate data integrity in processing functions
- Handle missing or invalid data gracefully

## 🐛 Bug Reports

### Before Submitting
- Check existing issues to avoid duplicates
- Verify the bug with the latest version
- Test with sample data to isolate the issue

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Enter '...'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.9.0]
- Browser: [e.g., Chrome 96.0]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Feature Request Template
```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the business/user scenario this addresses.

**Proposed Solution**
Your ideas for how this could be implemented.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Any other context or screenshots.
```

## 🔄 Pull Request Process

### Before Submitting
1. Create a feature branch from `main`
2. Make your changes with clear, focused commits
3. Add or update tests for your changes
4. Ensure all tests pass
5. Update documentation if needed
6. Test the Streamlit app manually

### Pull Request Template
```markdown
**Description**
Brief description of changes.

**Type of Change**
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

**Checklist**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process
1. Automated tests must pass
2. Code review by maintainers
3. Manual testing of financial calculations
4. Documentation review
5. Merge after approval

## 📊 Financial Accuracy Standards

### Calculation Requirements
- All financial formulas must be mathematically correct
- Use proper rounding for currency (2 decimal places)
- Handle edge cases (zero division, negative values)
- Validate against known financial principles

### Testing Financial Logic
```python
def test_revenue_calculation():
    """Test revenue calculation accuracy"""
    # Test with known values
    actual_revenue = 1000000.00
    budget_revenue = 1100000.00
    
    variance = actual_revenue - budget_revenue
    variance_pct = (variance / budget_revenue) * 100
    
    assert variance == -100000.00
    assert abs(variance_pct - (-9.09)) < 0.01  # Within tolerance
```

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### Getting Help
- Check documentation and existing issues first
- Ask questions in GitHub Discussions
- Provide context and examples when asking for help
- Be patient and respectful when receiving help

## 📚 Resources

### Financial Concepts
- [Financial Statement Analysis](https://www.investopedia.com/terms/f/financial-statement-analysis.asp)
- [EBITDA Calculation](https://www.investopedia.com/terms/e/ebitda.asp)
- [Cash Runway Analysis](https://www.investopedia.com/terms/c/cash-runway.asp)

### Technical Resources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Documentation](https://plotly.com/python/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## 📞 Contact

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Security**: Email security@yourproject.com for security issues

Thank you for contributing to CFO Agentic RAG! 🚀