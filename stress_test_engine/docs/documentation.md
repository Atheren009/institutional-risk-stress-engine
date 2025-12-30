# Regulatory Stress Testing Engine - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Installation](#installation)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Risk Factor Models](#risk-factor-models)
8. [Scenario Framework](#scenario-framework)
9. [Validation & Testing](#validation--testing)
10. [Performance](#performance)
11. [Regulatory Compliance](#regulatory-compliance)

## Overview

The Regulatory Stress Testing Engine is a comprehensive framework designed to evaluate portfolio resilience under adverse market conditions. It addresses the core regulatory question: "If the market breaks tomorrow, how much money do we lose — and do we survive?"

### Key Features
- **Multi-factor stress testing**: Interest rates, volatility, credit spreads
- **Regulatory compliance**: Basel III, CCAR, and internal model-ready
- **Advanced metrics**: VaR, Expected Shortfall, stress capital requirements
- **Professional reporting**: Regulatory-style reports with visualizations
- **Modular architecture**: Easy to extend and customize

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

### Technology Stack
- **Core Engine**: QuantLib C++ for performance-critical calculations
- **Orchestration**: Python for scenario management and reporting
- **Data**: Pandas for data manipulation
- **Visualization**: Matplotlib/Seaborn for risk visualizations

## Core Components

### 1. MarketData Class
Handles all market risk factor data including:
- Yield curve construction and manipulation
- Volatility surface management
- Credit spread modeling
- Equity and commodity price handling

### 2. Portfolio Class
Manages portfolio positions and risk:
- Position tracking and aggregation
- Instrument-specific valuation
- Greeks calculation
- Exposure analysis

### 3. ScenarioManager Class
Manages stress test scenarios:
- Scenario creation and storage
- Shock parameter validation
- Multi-factor scenario support

### 4. StressTestEngine Class
Main orchestration engine:
- Scenario execution
- Portfolio revaluation
- Risk metric calculation
- Report generation

### 5. RiskReportGenerator Class
Professional reporting:
- Regulatory-style reports
- Visualizations
- Export functionality (JSON, CSV)

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

## Usage Guide

### Quick Start
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

### Advanced Usage

#### Custom Scenarios
```python
# Create custom scenario
scenario = engine.scenario_manager.create_scenario("custom_shock")
scenario.add_rate_shock("steepener", {
    "short_shift_bp": 50,
    "long_shift_bp": 200
})
scenario.add_vol_shock("uniform", {"vol_shift": 0.30})
```

#### Data Validation
```python
from src.validation import DataValidator

# Validate market data
is_valid, issues = DataValidator.validate_market_data(market_df)
if not is_valid:
    print(f"Validation failed: {', '.join(issues)}")
```

#### Professional Reporting
```python
from src.reports import RiskReportGenerator

report_gen = RiskReportGenerator()
regulatory_report = report_gen.generate_regulatory_report(engine_results)
report_gen.generate_visualizations("output/charts")
```

## API Reference

### StressTestEngine
```python
class StressTestEngine:
    def __init__(self)
    def load_market_data(self, curve_data: pd.DataFrame)
    def set_portfolio(self, portfolio: Portfolio)
    def run_stress_test(self, scenario_name: str) -> Dict
    def run_all_scenarios(self) -> Dict[str, Dict]
    def generate_capital_impact_report(self) -> Dict
```

### MarketData
```python
class MarketData:
    def load_yield_curve_data(self, curve_data: pd.DataFrame)
    def build_yield_curve(self) -> ql.YieldTermStructure
    def apply_rate_shock(self, shock_type: str, shock_params: Dict) -> ql.YieldTermStructure
    def load_vol_surface_data(self, vol_data: pd.DataFrame)
    def load_credit_data(self, credit_data: pd.DataFrame)
```

### Portfolio
```python
class Portfolio:
    def add_position(self, position: Position)
    def load_from_dataframe(self, df: pd.DataFrame)
    def get_exposure_by_underlying(self) -> Dict[str, float]
```

### Scenario Management
```python
class Scenario:
    def add_rate_shock(self, shock_type: str, shock_params: Dict)
    def add_vol_shock(self, shock_type: str, shock_params: Dict)
    def add_credit_shock(self, shock_type: str, shock_params: Dict)

class ScenarioManager:
    def create_scenario(self, name: str, description: str = "") -> Scenario
    def get_scenario(self, name: str) -> Scenario
    def load_scenarios_from_json(self, file_path: str)
```

## Risk Factor Models

### Interest Rate Modeling
- **Curve Construction**: Piecewise linear forward curves
- **Shock Types**: Parallel, steepener/flattener, key-rate, non-linear
- **Validation**: Arbitrage-free curve construction

### Volatility Modeling
- **Surface Construction**: Strike and maturity dimensions
- **Shock Types**: Uniform, skew, term structure
- **Greeks**: Delta, gamma, vega, theta, rho

### Credit Modeling
- **Spread Curves**: Rating and sector-specific
- **Migration**: Rating migration simulation
- **Correlation**: Multi-name credit modeling

## Scenario Framework

### Supported Scenario Types

#### Rate Scenarios
- `parallel`: Uniform shift across all tenors
- `steepener`: Differential short/long end movement
- `key_rate`: Specific maturity node adjustments

#### Volatility Scenarios
- `uniform`: Proportional increase across surface
- `skew`: OTM options more affected than ATM
- `term_structure`: Maturity-dependent shocks

#### Credit Scenarios
- `parallel`: Uniform spread widening/narrowing
- `rating_migration`: Simulated rating changes
- `sector_specific`: Sector-focused stress

### Regulatory Scenarios
- Basel III adverse conditions
- CCAR supervisory scenarios
- Historical crisis patterns
- Internal model validation

## Validation & Testing

### Data Validation
- Market data integrity checks
- Portfolio data validation
- Scenario parameter validation
- Valuation result validation

### Automated Testing
- Unit tests for all components
- Integration tests for full workflow
- Synthetic data validation
- Scenario execution verification

### Quality Assurance
- 15+ comprehensive test cases
- Data validation at each layer
- Error handling and recovery
- Performance benchmarking

## Performance

### Benchmarks
- Curve construction: <100ms for 15-point curve
- Portfolio valuation: <10ms per position
- Scenario execution: <1s for 100-scenario run
- Report generation: <500ms

### Optimization Features
- QuantLib C++ core for performance
- Vectorized operations where possible
- Efficient memory usage
- Parallel scenario execution (future)

## Regulatory Compliance

### Basel III Alignment
- Standardized scenarios
- Capital adequacy metrics
- Stress testing requirements
- Documentation standards

### CCAR Support
- Supervisory scenarios
- Comprehensive reporting
- Validation requirements
- Model risk management

### Internal Model Ready
- Custom scenario support
- Advanced metrics calculation
- Validation framework
- Audit trail maintenance

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

## Troubleshooting

### Common Issues
- **Data Format Errors**: Ensure required columns exist
- **QuantLib Issues**: Verify QuantLib installation
- **Memory Problems**: Process large portfolios in batches
- **Performance**: Use synthetic data for testing

### Error Handling
- Comprehensive validation at each step
- Descriptive error messages
- Graceful degradation
- Recovery mechanisms

## Best Practices

### Data Management
- Validate all inputs before processing
- Use consistent date conventions
- Maintain data lineage
- Implement data quality checks

### Scenario Design
- Base scenarios on historical events
- Include forward-looking risks
- Consider correlation between factors
- Document scenario rationale

### Risk Management
- Calculate multiple risk metrics
- Include sensitivity analysis
- Maintain audit trails
- Regular model validation

## Roadmap

### Planned Features
- Real-time risk monitoring
- Advanced correlation modeling
- Multi-asset class support
- Regulatory reporting automation

### Future Enhancements
- Machine learning integration
- Cloud deployment options
- Advanced visualization
- API-first architecture

---

*This documentation covers version 1.0 of the Regulatory Stress Testing Engine. For the latest updates, please check the project repository.*