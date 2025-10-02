# 🤖📊 CFO Agentic RAG - Financial Analysis Copilot

An intelligent financial analysis system that combines **Agentic RAG (Retrieval-Augmented Generation)** with **deterministic Python calculations** to provide CFO-level insights from financial data. Ask natural language questions and get precise numerical analysis with interactive visualizations.

## ✨ Features

### 🎯 **Intelligent Question Routing**
- **Revenue Analysis**: "How much revenue did we get overall?" → Comprehensive revenue breakdown with variance analysis
- **Expense Tracking**: "How much was spent on marketing in January 2025?" → Category-specific spend analysis
- **Financial Performance**: "Give me a financial performance summary" → Complete P&L with margins and runway
- **Date-Specific Queries**: Supports year ("2025") and month-specific ("January 2025") filtering

### 📊 **Accurate Financial Calculations**
- **Revenue**: Actual vs Budget tracking with variance analysis
- **Gross Margin**: `(Revenue - COGS) / Revenue` with trend analysis
- **OpEx Analysis**: Grouped by categories (Marketing, Sales, R&D, Admin)
- **EBITDA**: `Revenue - COGS - OpEx` with margin calculations
- **Cash Runway**: `Cash ÷ Average Monthly Burn` (last 3 months)

### 📈 **Interactive Visualizations**
- Revenue trend charts (actual vs budget)
- Expense category breakdowns and trends
- Cash flow analysis with runway projections
- Gross margin trend analysis

### 🤖 **Agentic RAG Architecture**
- **Smart Tool Selection**: Automatically routes questions to appropriate analysis tools
- **Context Retrieval**: Uses RAG to understand financial data structure and relationships
- **Deterministic Calculations**: Python ensures mathematical accuracy
- **Multi-format Support**: Handles various date formats and question styles

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for the agentic routing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cfo-agentic-rag.git
   cd cfo-agentic-rag
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up OpenAI API key**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   # Or create a .env file with: OPENAI_API_KEY=your-api-key-here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## 💡 Usage Examples

### Revenue Analysis
```
Q: "How much revenue did we get overall?"
A: Revenue Analysis (2023-01 → 2025-12):
   • Total Revenue (Actual): $29.1M
   • Total Revenue (Budget): $30.8M
   • Variance: -$1.7M (-5.4% vs budget)
   • Growth: Recent 6M avg $1.0M vs Prior 6M avg $557.9K (+87.8%)
   • By Entity: ParentCo $22.5M, EMEA $6.6M
```

### Expense Analysis
```
Q: "How much was spent on marketing in January 2025?"
A: Based on the actuals, Marketing spend in 2025-01 was $169.9K.
```

### Financial Performance
```
Q: "Give me a financial performance summary"
A: Financial Performance Summary (2023-01 → 2025-12):
   • Revenue: $29.1M
   • Gross Profit: $24.7M (84.8% margin)
   • Total OpEx: $12.3M
   • EBITDA: $12.4M (42.4% margin)
   • Cash: $6.0M → $4.0M (-$2.0M burn)
   • Runway: ∞ (profitable)
```

## 📁 Project Structure

```
cfo-agentic-rag/
├── README.md              # This file
├── app.py                 # Streamlit web application
├── requirements.txt       # Python dependencies
├── pytest.ini           # Test configuration
├── .gitignore            # Git ignore rules
├── agent/                # Core agentic system
│   ├── __init__.py
│   ├── agent.py          # Main agent with tool routing
│   ├── tools.py          # Financial analysis tools
│   ├── rag.py            # RAG knowledge base
│   ├── charts.py         # Visualization functions
│   ├── data.py           # Data loading and normalization
│   ├── metrics.py        # Financial calculation functions
│   ├── parser.py         # Date and query parsing
│   ├── intents.py        # Intent classification
│   └── nlu.py            # Natural language understanding
├── fixtures/             # Sample financial data
│   ├── actuals.csv       # Actual financial results
│   ├── budget.csv        # Budget/forecast data
│   ├── cash.csv          # Cash flow data
│   └── fx.csv            # Foreign exchange rates
└── tests/                # Comprehensive test suite
    ├── __init__.py
    ├── conftest.py       # Shared test fixtures
    ├── test_financial_analysis.py  # Financial calculation tests
    ├── test_data.py      # Data loading tests
    └── test_tools.py     # Tool routing tests
```

## 🧪 Testing

The system includes comprehensive tests validating all financial calculations and formulas:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_financial_analysis.py -v  # Financial formulas
python -m pytest tests/test_data.py -v               # Data integrity
python -m pytest tests/test_tools.py -v              # Tool routing

# Run with coverage
python -m pytest tests/ --cov=agent --cov-report=html
```

**Test Results**: ✅ 35/35 tests passing

### Validated Financial Formulas
- **Revenue Analysis**: Actual vs budget with variance calculations
- **Gross Margin**: `(Revenue - COGS) / Revenue = 84.8%`
- **EBITDA**: `Revenue - COGS - OpEx = $12.4M (42.4% margin)`
- **Cash Runway**: `Cash ÷ Avg Monthly Burn = ∞ (profitable)`
- **Date Filtering**: Month and year-specific analysis

## 🏗️ Architecture

### Agentic RAG Flow
1. **Question Input**: User asks natural language financial question
2. **Intent Classification**: System determines question type and required analysis
3. **Tool Selection**: Routes to appropriate financial analysis tool
4. **Data Retrieval**: Loads and filters relevant financial data
5. **Calculation**: Performs deterministic mathematical analysis
6. **Visualization**: Generates appropriate charts and graphs
7. **Response**: Returns structured answer with numerical insights

### Key Components
- **Agent**: Orchestrates the entire analysis pipeline
- **RAG System**: Provides context about data structure and relationships
- **Financial Tools**: Specialized analyzers for revenue, expenses, margins, etc.
- **Chart Engine**: Creates interactive visualizations
- **Data Layer**: Handles CSV loading, normalization, and currency conversion

## 📊 Sample Data

The system includes sample financial data covering:
- **36 months** of data (2023-01 → 2025-12)
- **2 entities**: ParentCo (USD) and EMEA (EUR)
- **Account categories**: Revenue, COGS, OpEx (Marketing, Sales, R&D, Admin)
- **Data types**: Actuals and Budget/Forecast
- **Currency conversion**: Automatic USD normalization

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for agentic routing (set in `.env` file)
- `OPENAI_MODEL`: Model to use (default: "gpt-4o-mini")

### Data Format
The system expects CSV files with the following structure:

**Financials** (`actuals.csv`, `budget.csv`):
```csv
month,entity,account_category,amount,currency
2023-01,ParentCo,Revenue,380000,USD
2023-01,ParentCo,COGS,57000,USD
2023-01,ParentCo,Opex:Marketing,76000,USD
```

**Cash Flow** (`cash.csv`):
```csv
month,entity,cash_usd
2023-01,Consolidated,6000000
```
