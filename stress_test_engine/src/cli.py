"""
API and CLI Interface for Stress Testing Engine
"""
import argparse
import sys
import json
import os
from typing import Dict, Any
import pandas as pd

from src.engine import StressTestEngine
from src.synthetic import SyntheticDataGenerator, ScenarioGenerator
from src.reports import RiskReportGenerator
from src.validation import DataValidator


class StressTestAPI:
    """API interface for the stress testing engine"""
    
    def __init__(self):
        self.engine = StressTestEngine()
        self.report_generator = RiskReportGenerator()
    
    def initialize_from_files(self, market_data_path: str, portfolio_path: str, scenarios_path: str = None):
        """Initialize engine from data files"""
        # Load market data
        market_df = pd.read_csv(market_data_path)
        self.engine.load_market_data(market_df)
        
        # Load portfolio
        portfolio_df = pd.read_csv(portfolio_path)
        from src.portfolio import Portfolio
        portfolio = Portfolio("API Portfolio")
        portfolio.load_from_dataframe(portfolio_df)
        self.engine.set_portfolio(portfolio)
        
        # Load scenarios if provided
        if scenarios_path and os.path.exists(scenarios_path):
            self.engine.scenario_manager.load_scenarios_from_json(scenarios_path)
    
    def run_single_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Run a single stress test scenario"""
        return self.engine.run_stress_test(scenario_name)
    
    def run_multiple_scenarios(self, scenario_names: list = None) -> Dict[str, Dict]:
        """Run multiple scenarios"""
        if scenario_names:
            results = {}
            for name in scenario_names:
                results[name] = self.engine.run_stress_test(name)
            return results
        else:
            return self.engine.run_all_scenarios()
    
    def get_capital_report(self) -> Dict[str, Any]:
        """Get capital impact report"""
        return self.engine.generate_capital_impact_report()
    
    def generate_regulatory_report(self, output_format: str = 'text') -> str:
        """Generate regulatory-style report"""
        results = self.engine.generate_capital_impact_report()
        if output_format == 'text':
            return self.report_generator.generate_regulatory_report(results)
        elif output_format == 'json':
            return json.dumps(results, indent=2)
        else:
            return str(results)
    
    def generate_visualizations(self, output_dir: str = "visualizations"):
        """Generate risk visualizations"""
        results = self.engine.generate_capital_impact_report()
        self.report_generator.report_data = results
        self.report_generator.generate_visualizations(output_dir)
    
    def export_results(self, output_path: str, format: str = 'json'):
        """Export results to file"""
        results = self.engine.generate_capital_impact_report()
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
        elif format == 'csv':
            self.report_generator.report_data = results
            self.report_generator.export_to_csv(output_path)


def create_cli_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Regulatory Stress Testing Engine - Professional Risk Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with sample data
  python -m src.cli run --market-data data/sample_market_data.csv --portfolio data/sample_portfolio.csv

  # Run specific scenario
  python -m src.cli run --scenario-name basel_iii_adverse_rate

  # Generate regulatory report
  python -m src.cli report --format pdf

  # List available scenarios
  python -m src.cli list-scenarios

  # Generate synthetic data
  python -m src.cli generate-data --type all --output generated/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run stress test scenarios')
    run_parser.add_argument('--market-data', type=str, help='Market data CSV file path')
    run_parser.add_argument('--portfolio', type=str, help='Portfolio CSV file path')
    run_parser.add_argument('--scenarios', type=str, help='Scenarios JSON file path')
    run_parser.add_argument('--scenario-name', type=str, help='Specific scenario to run')
    run_parser.add_argument('--output', type=str, default='results.json', help='Output file for results')
    run_parser.add_argument('--use-synthetic', action='store_true', help='Use synthetic data instead of files')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate regulatory reports')
    report_parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text', help='Report format')
    report_parser.add_argument('--visualizations', action='store_true', help='Generate visualizations')
    report_parser.add_argument('--output', type=str, default='report', help='Output path')
    
    # List scenarios command
    list_parser = subparsers.add_parser('list-scenarios', help='List available scenarios')
    
    # Generate data command
    data_parser = subparsers.add_parser('generate-data', help='Generate synthetic data')
    data_parser.add_argument('--type', choices=['market', 'portfolio', 'scenarios', 'all'], 
                           default='all', help='Type of data to generate')
    data_parser.add_argument('--output', type=str, default='generated/', help='Output directory')
    data_parser.add_argument('--size', type=int, default=10, help='Portfolio size for synthetic portfolio')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate input data')
    validate_parser.add_argument('--market-data', type=str, help='Market data CSV file path')
    validate_parser.add_argument('--portfolio', type=str, help='Portfolio CSV file path')
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    api = StressTestAPI()
    
    if args.command == 'run':
        # Initialize engine
        if args.use_synthetic:
            # Use synthetic data
            market_data = SyntheticDataGenerator.generate_synthetic_yield_curve_data()
            api.engine.load_market_data(market_data)
            
            portfolio_df = SyntheticDataGenerator.generate_synthetic_portfolio(size=5)
            from src.portfolio import Portfolio
            portfolio = Portfolio("Synthetic Portfolio")
            portfolio.load_from_dataframe(portfolio_df)
            api.engine.set_portfolio(portfolio)
            
            # Add synthetic scenarios
            ir_scenarios = ScenarioGenerator.generate_interest_rate_scenarios()
            for scenario_def in ir_scenarios[:3]:  # Add first 3 scenarios
                scenario = api.engine.scenario_manager.create_scenario(
                    scenario_def['name'], 
                    scenario_def['description']
                )
                if scenario_def['shock_type'] == 'parallel':
                    scenario.add_rate_shock('parallel', scenario_def['params'])
        else:
            # Load from files
            if not args.market_data or not args.portfolio:
                print("Error: Both --market-data and --portfolio are required when not using synthetic data")
                return
            
            try:
                api.initialize_from_files(args.market_data, args.portfolio, args.scenarios)
            except FileNotFoundError as e:
                print(f"Error: File not found - {e}")
                return
            except Exception as e:
                print(f"Error loading data: {e}")
                return
        
        # Run scenarios
        try:
            if args.scenario_name:
                result = api.run_single_scenario(args.scenario_name)
                print(f"Results for scenario '{args.scenario_name}':")
                print(json.dumps(result, indent=2))
            else:
                results = api.run_multiple_scenarios()
                print("Running all scenarios...")
                print(json.dumps(results, indent=2))
                
                # Save results
                api.export_results(args.output, format='json')
                print(f"Results saved to {args.output}")
        except Exception as e:
            print(f"Error running scenarios: {e}")
            return
    
    elif args.command == 'report':
        try:
            report = api.generate_regulatory_report(output_format=args.format)
            print(report)
            
            if args.visualizations:
                api.generate_visualizations(args.output)
                print(f"Visualizations saved to {args.output}/")
        except Exception as e:
            print(f"Error generating report: {e}")
            return
    
    elif args.command == 'list-scenarios':
        # Add some default scenarios if none exist
        if not api.engine.scenario_manager.get_all_scenario_names():
            # Add synthetic scenarios
            ir_scenarios = ScenarioGenerator.generate_interest_rate_scenarios()
            for scenario_def in ir_scenarios[:3]:
                scenario = api.engine.scenario_manager.create_scenario(
                    scenario_def['name'], 
                    scenario_def['description']
                )
                if scenario_def['shock_type'] == 'parallel':
                    scenario.add_rate_shock('parallel', scenario_def['params'])
        
        scenarios = api.engine.scenario_manager.get_all_scenario_names()
        print("Available scenarios:")
        for name in scenarios:
            print(f"  - {name}")
    
    elif args.command == 'generate-data':
        os.makedirs(args.output, exist_ok=True)
        
        if args.type in ['market', 'all']:
            market_data = SyntheticDataGenerator.generate_synthetic_yield_curve_data()
            market_data.to_csv(os.path.join(args.output, 'market_data.csv'), index=False)
            print(f"Generated market data: {os.path.join(args.output, 'market_data.csv')}")
        
        if args.type in ['portfolio', 'all']:
            portfolio_data = SyntheticDataGenerator.generate_synthetic_portfolio(size=args.size)
            portfolio_data.to_csv(os.path.join(args.output, 'portfolio.csv'), index=False)
            print(f"Generated portfolio data: {os.path.join(args.output, 'portfolio.csv')}")
        
        if args.type in ['scenarios', 'all']:
            # Generate scenario JSON
            all_scenarios = (
                ScenarioGenerator.generate_interest_rate_scenarios() +
                ScenarioGenerator.generate_volatility_scenarios() +
                ScenarioGenerator.generate_credit_scenarios()
            )
            
            # Convert to the expected JSON format
            scenario_json = []
            for scenario in all_scenarios[:5]:  # Limit to first 5
                scenario_json.append({
                    "name": scenario["name"],
                    "description": scenario["description"],
                    "rate_shocks": [{"type": scenario["shock_type"], "params": scenario["params"]}] if scenario["type"] == "rate" else [],
                    "vol_shocks": [{"type": scenario["shock_type"], "params": scenario["params"]}] if scenario["type"] == "vol" else [],
                    "credit_shocks": [{"type": scenario["shock_type"], "params": scenario["params"]}] if scenario["type"] == "credit" else []
                })
            
            with open(os.path.join(args.output, 'scenarios.json'), 'w') as f:
                json.dump(scenario_json, f, indent=2)
            print(f"Generated scenarios: {os.path.join(args.output, 'scenarios.json')}")
    
    elif args.command == 'validate':
        if args.market_data:
            try:
                market_df = pd.read_csv(args.market_data)
                is_valid, issues = DataValidator.validate_market_data(market_df)
                print(f"Market data validation: {'PASS' if is_valid else 'FAIL'}")
                if issues:
                    print("Issues found:")
                    for issue in issues:
                        print(f"  - {issue}")
            except Exception as e:
                print(f"Error validating market data: {e}")
        
        if args.portfolio:
            try:
                portfolio_df = pd.read_csv(args.portfolio)
                is_valid, issues = DataValidator.validate_portfolio_data(portfolio_df)
                print(f"Portfolio data validation: {'PASS' if is_valid else 'FAIL'}")
                if issues:
                    print("Issues found:")
                    for issue in issues:
                        print(f"  - {issue}")
            except Exception as e:
                print(f"Error validating portfolio data: {e}")


if __name__ == "__main__":
    main()