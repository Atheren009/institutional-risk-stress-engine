"""
Main Stress Testing Engine
"""
import QuantLib as ql
import pandas as pd
from typing import Dict, List
from .market_data import MarketData
from .scenarios import Scenario, ScenarioManager
from .portfolio import Portfolio, PortfolioValuationEngine
from .reports import RiskReportGenerator


class StressTestEngine:
    """Main engine for regulatory stress testing"""
    
    def __init__(self):
        self.market_data = MarketData()
        self.scenario_manager = ScenarioManager()
        self.portfolio = None
        self.valuation_engine = None
        self.results = {}
        self.report_generator = RiskReportGenerator()
    
    def load_market_data(self, curve_data: pd.DataFrame):
        """Load market data for stress testing"""
        self.market_data.load_yield_curve_data(curve_data)
    
    def set_portfolio(self, portfolio: Portfolio):
        """Set the portfolio to stress test"""
        self.portfolio = portfolio
        self.valuation_engine = PortfolioValuationEngine(portfolio)
    
    def run_stress_test(self, scenario_name: str) -> Dict:
        """Run a single stress test scenario"""
        scenario = self.scenario_manager.get_scenario(scenario_name)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        # Get base case valuation
        base_valuation = self.valuation_engine.value_portfolio(self.market_data)
        
        # Apply scenario shocks and revalue
        shocked_market_data = self._apply_scenario_shocks(scenario)
        shocked_valuation = self.valuation_engine.value_portfolio(shocked_market_data)
        
        # Calculate PnL impact
        pnl_impact = shocked_valuation["total_npv"] - base_valuation["total_npv"]
        
        result = {
            "scenario_name": scenario_name,
            "base_value": base_valuation["total_npv"],
            "shocked_value": shocked_valuation["total_npv"],
            "pnl_impact": pnl_impact,
            "base_valuation": base_valuation,
            "shocked_valuation": shocked_valuation
        }
        
        self.results[scenario_name] = result
        return result
    
    def run_all_scenarios(self) -> Dict[str, Dict]:
        """Run all registered scenarios"""
        results = {}
        for scenario_name in self.scenario_manager.get_all_scenario_names():
            results[scenario_name] = self.run_stress_test(scenario_name)
        return results
    
    def _apply_scenario_shocks(self, scenario: Scenario) -> MarketData:
        """Apply scenario shocks to market data"""
        # Create a copy of market data to avoid modifying the original
        shocked_data = MarketData()
        shocked_data.base_date = self.market_data.base_date
        shocked_data.yield_curve_data = self.market_data.yield_curve_data.copy()
        
        # First, build the base yield curve
        shocked_data.yield_curve = shocked_data.build_yield_curve()
        
        # Apply rate shocks to the already-built curve
        for rate_shock in scenario.rate_shocks:
            shocked_data.yield_curve = shocked_data.apply_rate_shock(
                rate_shock["type"], 
                rate_shock["params"]
            )
        
        # In a full implementation, we would also apply vol and credit shocks
        # For now, we'll return the shocked data with rate adjustments
        return shocked_data
    
    def generate_capital_impact_report(self) -> Dict:
        """Generate capital impact metrics report"""
        if not self.results:
            return {"error": "No stress test results available"}
        
        # Calculate key metrics
        pnl_impacts = [result["pnl_impact"] for result in self.results.values()]
        absolute_pnl_impacts = [abs(pnl) for pnl in pnl_impacts]
        
        # Calculate advanced risk metrics
        var_95 = self._calculate_var(pnl_impacts, 0.95)  # 95% VaR
        var_99 = self._calculate_var(pnl_impacts, 0.99)  # 99% VaR
        expected_shortfall_95 = self._calculate_expected_shortfall(pnl_impacts, 0.95)  # ES at 95%
        expected_shortfall_99 = self._calculate_expected_shortfall(pnl_impacts, 0.99)  # ES at 99%
        
        # Calculate capital adequacy metrics
        worst_loss = min(pnl_impacts) if pnl_impacts else 0
        total_portfolio_value = self._get_base_portfolio_value()
        
        # Capital requirement proxy (simplified)
        capital_requirement = abs(worst_loss) * 1.4  # 40% buffer over worst loss
        
        # Capital ratio
        capital_ratio = (capital_requirement / total_portfolio_value) if total_portfolio_value != 0 else 0
        
        report = {
            "total_scenarios_run": len(self.results),
            "portfolio_metrics": {
                "initial_value": total_portfolio_value,
                "max_loss": worst_loss,
                "avg_loss": sum(pnl_impacts) / len(pnl_impacts) if pnl_impacts else 0,
                "volatility": self._calculate_volatility(pnl_impacts) if pnl_impacts else 0,
            },
            "risk_metrics": {
                "var_95": var_95,
                "var_99": var_99,
                "expected_shortfall_95": expected_shortfall_95,
                "expected_shortfall_99": expected_shortfall_99,
                "worst_case_loss": worst_loss,
                "stress_var": abs(worst_loss),  # Stress testing VaR equivalent
            },
            "capital_metrics": {
                "capital_requirement": capital_requirement,
                "capital_ratio": capital_ratio,
                "capital_coverage_ratio": 1.0 if worst_loss == 0 else abs(total_portfolio_value / worst_loss) if worst_loss < 0 else 0,
                "stress_capital_buffer": capital_requirement - abs(worst_loss) if worst_loss < 0 else 0,
            },
            "scenario_analysis": {
                "worst_scenario": min(self.results.items(), key=lambda x: x[1]["pnl_impact"])[0] if self.results else None,
                "best_scenario": max(self.results.items(), key=lambda x: x[1]["pnl_impact"])[0] if self.results else None,
                "scenario_count_positive": len([pnl for pnl in pnl_impacts if pnl > 0]),
                "scenario_count_negative": len([pnl for pnl in pnl_impacts if pnl < 0]),
            },
            "sensitivity_analysis": self._calculate_sensitivity_metrics(),
            "results_summary": {
                name: {
                    "base_value": result["base_value"],
                    "shocked_value": result["shocked_value"], 
                    "pnl_impact": result["pnl_impact"],
                    "pnl_percentage": (result["pnl_impact"] / result["base_value"]) * 100 if result["base_value"] != 0 else 0,
                    "stress_severity": self._calculate_stress_severity(result)
                }
                for name, result in self.results.items()
            }
        }
        
        return report
    
    def _calculate_var(self, pnl_values, confidence_level):
        """Calculate Value at Risk at given confidence level"""
        if not pnl_values:
            return 0
        sorted_pnl = sorted(pnl_values)
        index = int((1 - confidence_level) * len(sorted_pnl))
        return sorted_pnl[max(0, index)]
    
    def _calculate_expected_shortfall(self, pnl_values, confidence_level):
        """Calculate Expected Shortfall (Conditional VaR)"""
        if not pnl_values:
            return 0
        sorted_pnl = sorted(pnl_values)
        var_index = int((1 - confidence_level) * len(sorted_pnl))
        var_index = max(1, var_index)  # Ensure at least 1 value
        return sum(sorted_pnl[:var_index]) / var_index
    
    def _calculate_volatility(self, pnl_values):
        """Calculate volatility of PnL values"""
        if not pnl_values or len(pnl_values) < 2:
            return 0
        mean = sum(pnl_values) / len(pnl_values)
        variance = sum((x - mean) ** 2 for x in pnl_values) / (len(pnl_values) - 1)
        return variance ** 0.5
    
    def _get_base_portfolio_value(self):
        """Get the base portfolio value from the first result"""
        if not self.results:
            return 0
        # Use the base value from the first scenario result
        first_result = next(iter(self.results.values()))
        return first_result["base_value"]
    
    def _calculate_sensitivity_metrics(self):
        """Calculate sensitivity metrics across scenarios"""
        if not self.results:
            return {}
        
        # This would analyze how sensitive the portfolio is to different risk factors
        # For now, return placeholder metrics
        return {
            "rate_sensitivity": self._analyze_rate_sensitivity(),
            "vol_sensitivity": self._analyze_vol_sensitivity(),
            "credit_sensitivity": self._analyze_credit_sensitivity(),
        }
    
    def _analyze_rate_sensitivity(self):
        """Analyze sensitivity to interest rate changes"""
        # Placeholder for rate sensitivity analysis
        return {"avg_impact_per_rate_bp": 0.0, "convexity_measure": 0.0}
    
    def _analyze_vol_sensitivity(self):
        """Analyze sensitivity to volatility changes"""
        # Placeholder for vol sensitivity analysis
        return {"vega_exposure": 0.0, "vol_convexity": 0.0}
    
    def _analyze_credit_sensitivity(self):
        """Analyze sensitivity to credit spread changes"""
        # Placeholder for credit sensitivity analysis
        return {"credit_exposure": 0.0, "spread_duration": 0.0}
    
    def _calculate_stress_severity(self, result):
        """Calculate stress severity for a scenario"""
        base_value = result["base_value"]
        pnl_impact = result["pnl_impact"]
        if base_value == 0:
            return 0
        return abs(pnl_impact / base_value)


def create_sample_market_data() -> pd.DataFrame:
    """Create sample market data for testing"""
    data = {
        'tenor': ['1D', '1W', '2W', '1M', '2M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y'],
        'rate': [0.045, 0.046, 0.047, 0.048, 0.049, 0.050, 0.052, 0.055, 0.058, 0.060, 0.062, 0.063, 0.065, 0.067, 0.068]
    }
    return pd.DataFrame(data)


def create_sample_portfolio() -> Portfolio:
    """Create a sample portfolio for testing"""
    portfolio = Portfolio("Test Portfolio")
    
    # Add some sample positions
    from .portfolio import Position
    
    portfolio.add_position(Position(
        id="bond_1",
        instrument_type="bond",
        quantity=1000000,
        underlying="US Treasury 5Y",
        notional=1000.0
    ))
    
    portfolio.add_position(Position(
        id="swap_1", 
        instrument_type="swap",
        quantity=1,
        underlying="5Y IRS",
        notional=10000000.0
    ))
    
    portfolio.add_position(Position(
        id="option_1",
        instrument_type="option",
        quantity=100,
        underlying="SPY",
        strike=400.0,
        notional=100.0
    ))
    
    return portfolio