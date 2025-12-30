# Instituional Stress Testing Engine

A comprehensive framework for conducting regulatory-style stress tests to evaluate portfolio resilience under adverse market conditions. This system answers the core regulatory question: "If the market breaks tomorrow, how much money do we lose — and do we survive?"

## Features

### Core Functionality
- **Multi-factor stress testing**: Interest rates, volatility, credit spreads
- **Regulatory compliance**: Basel III, CCAR, and internal model-ready
- **Advanced risk metrics**: VaR, Expected Shortfall, stress capital requirements
- **Professional reporting**: Regulatory-style reports with visualizations
- **Modular architecture**: Easy to extend and customize

### Risk Factor Models
- **Interest Rates**: Parallel shifts, steepener/flattener, key-rate shocks
- **Volatility**: Uniform, skew, term structure shocks
- **Credit**: Spread widening, rating migration, sector-specific stress

### Technical Capabilities
- QuantLib C++ integration for performance
- Comprehensive data validation
- Automated testing framework
- Professional reporting system
- Synthetic data generation

## Architecture

The system follows a layered institutional architecture:

```
┌─────────────────────────────────────┐
│           User Interface            │
├─────────────────────────────────────┤
│        Business Logic Layer         │
│   - Scenario Management             │
│   - Portfolio Valuation            │
│   - Risk Metrics Calculation       │
├─────────────────────────────────────┤
│        Data & Validation Layer      │
│   - Market Data Handler            │
│   - Data Validation               │
│   - Synthetic Data Generator       │
├─────────────────────────────────────┤
│         Core Engine Layer           │
│   - QuantLib Integration          │
│   - Curve Construction            │
│   - Greeks Calculation            │
└─────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.8+
- QuantLib-Python
- Pandas, NumPy
- Matplotlib (for visualizations)

### Setup
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Run Stress Tests
```bash
# Run with synthetic data
python -m src.cli run --use-synthetic

# Run with specific scenario
python -m src.cli run --scenario-name parallel_rate_shock_200bp_up

# Generate regulatory report
python -m src.cli report --format text

# List available scenarios
python -m src.cli list-scenarios

# Generate synthetic data
python -m src.cli generate-data --type all --output generated/
```

### Python API

```python
from src.engine import StressTestEngine
from src.synthetic import SyntheticDataGenerator

# Initialize engine
engine = StressTestEngine()

# Load market data
market_data = SyntheticDataGenerator.generate_synthetic_yield_curve_data()
engine.load_market_data(market_data)

# Load portfolio
portfolio = create_sample_portfolio()  # or load from CSV
engine.set_portfolio(portfolio)

# Run stress test
result = engine.run_stress_test("basel_iii_adverse_rate")
print(f"P&L Impact: ${result['pnl_impact']:,.2f}")

# Generate report
report = engine.generate_capital_impact_report()
print(report)
```

## Components

### Market Data Module (`src/market_data.py`)
- Yield curve construction and manipulation
- Volatility surface management
- Credit spread modeling
- Risk factor shock application

### Portfolio Module (`src/portfolio.py`)
- Position tracking and management
- Instrument-specific valuation
- Greeks calculation
- Exposure analysis

### Scenario Module (`src/scenarios.py`)
- Scenario definition and management
- Multi-factor shock support
- Regulatory scenario templates
- Historical crisis patterns

### Engine Module (`src/engine.py`)
- Main orchestration engine
- Scenario execution
- Risk metric calculation
- Report generation

### Validation Module (`src/validation.py`)
- Market data validation
- Portfolio data validation
- Scenario parameter validation
- Result validation

### Reporting Module (`src/reports.py`)
- Regulatory-style reports
- Risk visualizations
- Export functionality (JSON, CSV)

### Synthetic Data Module (`src/synthetic.py`)
- Market data generation
- Portfolio generation
- Scenario templates
- Testing data

### Testing Framework (`src/tests.py`)
- Unit tests for all components
- Integration tests
- Synthetic data validation
- Performance benchmarks

## Risk Metrics

The engine calculates comprehensive risk metrics:

- **Value at Risk (VaR)** at 95% and 99% confidence levels
- **Expected Shortfall (ES)** at 95% and 99% confidence levels
- **Stress VaR** equivalent for regulatory compliance
- **Capital adequacy ratios** and buffers
- **Sensitivity analysis** for different risk factors
- **Greeks** for options and derivatives

## Regulatory Compliance

### Basel III Support
- Standardized stress scenarios
- Capital adequacy calculations
- Documentation requirements
- Validation standards

### CCAR Alignment
- Supervisory scenario support
- Comprehensive reporting
- Model validation framework
- Governance requirements

## Validation & Testing

### Data Validation
- Market data integrity checks
- Portfolio data validation
- Scenario parameter validation
- Valuation result validation

### Automated Testing
- 15+ comprehensive test cases
- Unit tests for all components
- Integration tests for full workflow
- Performance benchmarks

## Performance

### Benchmarks
- Curve construction: <100ms for 15-point curve
- Portfolio valuation: <10ms per position
- Scenario execution: <1s for 100-scenario run
- Report generation: <500ms

### Optimization Features
- QuantLib C++ core for performance
- Efficient memory usage
- Vectorized operations where possible

## Extensions & Customization

### Adding New Instruments
1. Extend `PortfolioValuationEngine._value_*` methods
2. Implement specific valuation logic
3. Add Greeks calculation if applicable

### New Risk Factors
1. Extend `MarketData` with new factor methods
2. Add shock application logic
3. Update validation rules

### Custom Reports
1. Extend `RiskReportGenerator`
2. Add new visualization types
3. Implement custom metrics

## Documentation

Complete documentation is available in `docs/documentation.md`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*The Regulatory Stress Testing Engine provides a professional-grade framework for regulatory compliance and risk management. It is designed to meet institutional requirements while remaining flexible for custom implementations.*
