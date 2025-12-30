"""
Test script for the stress testing engine
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.engine import StressTestEngine, create_sample_market_data, create_sample_portfolio
from src.scenarios import create_basel_iii_scenarios


def test_basic_functionality():
    print("Testing basic stress testing functionality...")
    
    # Create engine
    engine = StressTestEngine()
    
    # Load sample market data
    market_data = create_sample_market_data()
    engine.load_market_data(market_data)
    
    # Set sample portfolio
    portfolio = create_sample_portfolio()
    engine.set_portfolio(portfolio)
    
    # Add some scenarios
    basel_scenarios = create_basel_iii_scenarios()
    for name, scenario in basel_scenarios.scenarios.items():
        engine.scenario_manager.scenarios[name] = scenario
    
    print("Available scenarios:", engine.scenario_manager.get_all_scenario_names())
    
    # Run a simple scenario
    if engine.scenario_manager.get_all_scenario_names():
        scenario_name = engine.scenario_manager.get_all_scenario_names()[0]
        print(f"\nRunning scenario: {scenario_name}")
        
        try:
            result = engine.run_stress_test(scenario_name)
            print(f"Base value: {result['base_value']:.2f}")
            print(f"Shocked value: {result['shocked_value']:.2f}")
            print(f"PnL impact: {result['pnl_impact']:.2f}")
            
            # Generate report
            report = engine.generate_capital_impact_report()
            print("\nCapital Impact Report:")
            print(f"Total scenarios run: {report['total_scenarios_run']}")
            print(f"Max loss: {report['max_loss']:.2f}")
            print(f"Avg loss: {report['avg_loss']:.2f}")
            print(f"Worst scenario: {report['worst_scenario']}")
            
            return True
        except Exception as e:
            print(f"Error running scenario: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("No scenarios available to run")
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n[SUCCESS] Basic functionality test passed!")
    else:
        print("\n[FAILURE] Basic functionality test failed!")
        sys.exit(1)