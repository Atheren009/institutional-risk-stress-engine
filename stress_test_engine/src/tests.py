"""
Automated Testing Framework for Stress Testing Engine
"""
import unittest
import pandas as pd
import numpy as np
from src.engine import StressTestEngine
from src.market_data import MarketData
from src.portfolio import Portfolio, Position
from src.scenarios import Scenario, ScenarioManager
from src.synthetic import SyntheticDataGenerator, ScenarioGenerator


class TestMarketData(unittest.TestCase):
    """Test market data functionality"""
    
    def setUp(self):
        self.market_data = MarketData()
        self.sample_data = SyntheticDataGenerator.generate_synthetic_yield_curve_data()
    
    def test_yield_curve_data_loading(self):
        """Test loading and validating yield curve data"""
        self.market_data.load_yield_curve_data(self.sample_data)
        self.assertIsNotNone(self.market_data.yield_curve_data)
        self.assertEqual(len(self.market_data.yield_curve_data), len(self.sample_data))
    
    def test_yield_curve_construction(self):
        """Test yield curve construction"""
        self.market_data.load_yield_curve_data(self.sample_data)
        curve = self.market_data.build_yield_curve()
        self.assertIsNotNone(curve)
    
    def test_rate_shock_application(self):
        """Test applying rate shocks"""
        self.market_data.load_yield_curve_data(self.sample_data)
        original_curve = self.market_data.build_yield_curve()
        
        # Apply a parallel shift
        shocked_curve = self.market_data.apply_rate_shock("parallel", {"shift_bp": 100})
        self.assertIsNotNone(shocked_curve)


class TestPortfolio(unittest.TestCase):
    """Test portfolio functionality"""
    
    def setUp(self):
        self.portfolio = Portfolio("Test Portfolio")
        self.synthetic_portfolio = SyntheticDataGenerator.generate_synthetic_portfolio(size=5)
    
    def test_portfolio_loading(self):
        """Test loading portfolio from DataFrame"""
        self.portfolio.load_from_dataframe(self.synthetic_portfolio)
        self.assertEqual(len(self.portfolio.positions), len(self.synthetic_portfolio))
    
    def test_position_addition(self):
        """Test adding positions manually"""
        pos = Position(
            id="test_pos",
            instrument_type="bond",
            quantity=1000000,
            underlying="Test Bond",
            notional=1000.0
        )
        self.portfolio.add_position(pos)
        self.assertIn("test_pos", self.portfolio.positions)


class TestScenarios(unittest.TestCase):
    """Test scenario functionality"""
    
    def setUp(self):
        self.scenario_manager = ScenarioManager()
    
    def test_scenario_creation(self):
        """Test creating and managing scenarios"""
        scenario = self.scenario_manager.create_scenario("test_scenario", "Test scenario")
        scenario.add_rate_shock("parallel", {"shift_bp": 100})
        
        retrieved = self.scenario_manager.get_scenario("test_scenario")
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved.rate_shocks), 1)
    
    def test_synthetic_scenarios(self):
        """Test synthetic scenario generation"""
        scenarios = ScenarioGenerator.generate_interest_rate_scenarios()
        self.assertGreater(len(scenarios), 0)
        
        # Check that each scenario has required fields
        for scenario in scenarios:
            self.assertIn('name', scenario)
            self.assertIn('type', scenario)
            self.assertIn('shock_type', scenario)
            self.assertIn('params', scenario)


class TestStressEngine(unittest.TestCase):
    """Test the main stress testing engine"""
    
    def setUp(self):
        self.engine = StressTestEngine()
        
        # Load synthetic data
        market_data = SyntheticDataGenerator.generate_synthetic_yield_curve_data()
        self.engine.load_market_data(market_data)
        
        portfolio_df = SyntheticDataGenerator.generate_synthetic_portfolio(size=3)
        portfolio = Portfolio("Test Portfolio")
        portfolio.load_from_dataframe(portfolio_df)
        self.engine.set_portfolio(portfolio)
        
        # Add a simple scenario
        scenario = self.engine.scenario_manager.create_scenario("test_rate_shock")
        scenario.add_rate_shock("parallel", {"shift_bp": 100})
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine.market_data)
        self.assertIsNotNone(self.engine.portfolio)
        self.assertIsNotNone(self.engine.valuation_engine)
    
    def test_single_scenario_run(self):
        """Test running a single scenario"""
        result = self.engine.run_stress_test("test_rate_shock")
        self.assertIsNotNone(result)
        self.assertIn('pnl_impact', result)
        self.assertIsInstance(result['pnl_impact'], (int, float))
    
    def test_all_scenarios_run(self):
        """Test running all scenarios"""
        results = self.engine.run_all_scenarios()
        self.assertGreater(len(results), 0)
    
    def test_capital_impact_report(self):
        """Test generating capital impact report"""
        # Run a scenario first
        self.engine.run_stress_test("test_rate_shock")
        
        report = self.engine.generate_capital_impact_report()
        self.assertIsNotNone(report)
        self.assertIn('total_scenarios_run', report)
        self.assertIn('risk_metrics', report)
        self.assertIn('capital_metrics', report)


class TestSyntheticData(unittest.TestCase):
    """Test synthetic data generation"""
    
    def test_yield_curve_generation(self):
        """Test yield curve data generation"""
        data = SyntheticDataGenerator.generate_synthetic_yield_curve_data()
        self.assertIsNotNone(data)
        self.assertGreater(len(data), 0)
        self.assertIn('tenor', data.columns)
        self.assertIn('rate', data.columns)
    
    def test_vol_surface_generation(self):
        """Test volatility surface data generation"""
        data = SyntheticDataGenerator.generate_synthetic_vol_surface_data()
        self.assertIsNotNone(data)
        self.assertGreater(len(data), 0)
        self.assertIn('strike', data.columns)
        self.assertIn('maturity', data.columns)
        self.assertIn('volatility', data.columns)
    
    def test_portfolio_generation(self):
        """Test portfolio data generation"""
        data = SyntheticDataGenerator.generate_synthetic_portfolio(size=10)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 10)
        self.assertIn('id', data.columns)
        self.assertIn('instrument_type', data.columns)


class TestIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def test_full_workflow(self):
        """Test the complete workflow from data to results"""
        engine = StressTestEngine()
        
        # Load market data
        market_data_df = SyntheticDataGenerator.generate_synthetic_yield_curve_data()
        engine.load_market_data(market_data_df)
        
        # Load portfolio
        portfolio_df = SyntheticDataGenerator.generate_synthetic_portfolio(size=5)
        portfolio = Portfolio("Integration Test Portfolio")
        portfolio.load_from_dataframe(portfolio_df)
        engine.set_portfolio(portfolio)
        
        # Add scenarios
        scenario = engine.scenario_manager.create_scenario("integration_test")
        scenario.add_rate_shock("parallel", {"shift_bp": 200})
        
        # Run stress test
        result = engine.run_stress_test("integration_test")
        
        # Check results
        self.assertIsNotNone(result)
        self.assertIn('base_value', result)
        self.assertIn('shocked_value', result)
        self.assertIn('pnl_impact', result)
        
        # Generate report
        report = engine.generate_capital_impact_report()
        self.assertIsNotNone(report)
        self.assertGreater(report['total_scenarios_run'], 0)


def run_all_tests():
    """Run all tests in the framework"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMarketData))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolio))
    suite.addTests(loader.loadTestsFromTestCase(TestScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestStressEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestSyntheticData))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("Running automated test suite for Stress Testing Engine...")
    print("=" * 60)
    
    result = run_all_tests()
    
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "0%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[FAILURE] Some tests failed!")