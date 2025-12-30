"""
Complete example of the regulatory stress testing engine
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.engine import StressTestEngine, create_sample_market_data, create_sample_portfolio
from src.scenarios import create_basel_iii_scenarios, create_historical_scenarios


def run_complete_example():
    print("=== Regulatory Stress Testing Engine Example ===\n")
    
    # Create the stress testing engine
    engine = StressTestEngine()
    print("[OK] Engine initialized")
    
    # Load market data
    market_data = create_sample_market_data()
    engine.load_market_data(market_data)
    print("[OK] Market data loaded")
    
    # Create and set portfolio
    portfolio = create_sample_portfolio()
    engine.set_portfolio(portfolio)
    print("[OK] Portfolio created with sample positions")
    
    # Add Basel III scenarios
    basel_scenarios = create_basel_iii_scenarios()
    for name, scenario in basel_scenarios.scenarios.items():
        engine.scenario_manager.scenarios[name] = scenario
    print("[OK] Basel III scenarios loaded")
    
    # Add historical scenarios
    historical_scenarios = create_historical_scenarios()
    for name, scenario in historical_scenarios.scenarios.items():
        engine.scenario_manager.scenarios[name] = scenario
    print("[OK] Historical scenarios loaded")
    
    print(f"\nAvailable scenarios: {engine.scenario_manager.get_all_scenario_names()}")
    
    # Run all scenarios
    print("\n--- Running Stress Tests ---")
    results = engine.run_all_scenarios()
    
    # Display results
    print("\n--- Stress Test Results ---")
    for scenario_name, result in results.items():
        print(f"Scenario: {scenario_name}")
        print(f"  Base Value: ${result['base_value']:,.2f}")
        print(f"  Shocked Value: ${result['shocked_value']:,.2f}")
        print(f"  PnL Impact: ${result['pnl_impact']:,.2f}")
        print(f"  PnL %: {((result['pnl_impact'] / result['base_value']) * 100):.2f}%")
        print()
    
    # Generate capital impact report
    print("--- Capital Impact Report ---")
    report = engine.generate_capital_impact_report()
    print(f"Total scenarios run: {report['total_scenarios_run']}")
    print(f"Maximum loss: ${report['max_loss']:,.2f}")
    print(f"Average loss: ${report['avg_loss']:,.2f}")
    print(f"Worst scenario: {report['worst_scenario']}")
    
    print(f"\nDetailed Results Summary:")
    for name, summary in report['results_summary'].items():
        print(f"  {name}: PnL ${summary['pnl_impact']:,.2f} ({summary['pnl_percentage']:.2f}%)")
    
    return True


if __name__ == "__main__":
    success = run_complete_example()
    if success:
        print("\n[SUCCESS] Complete example executed successfully!")
    else:
        print("\n[FAILURE] Example execution failed!")
        sys.exit(1)