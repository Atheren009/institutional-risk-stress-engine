"""
Professional Reporting Module for Stress Testing Engine
"""
import json
import pandas as pd
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


class RiskReportGenerator:
    """Generates professional regulatory-style reports"""
    
    def __init__(self):
        self.report_data = None
    
    def generate_regulatory_report(self, engine_results: Dict) -> str:
        """Generate a comprehensive regulatory-style report"""
        self.report_data = engine_results
        
        report = self._create_executive_summary()
        report += self._create_detailed_analysis()
        report += self._create_capital_assessment()
        report += self._create_risk_metrics_summary()
        
        return report
    
    def _create_executive_summary(self) -> str:
        """Create executive summary section"""
        summary = "REGULATORY STRESS TEST REPORT\n"
        summary += "=" * 50 + "\n"
        summary += f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        metrics = self.report_data.get('portfolio_metrics', {})
        risk_metrics = self.report_data.get('risk_metrics', {})
        
        summary += "EXECUTIVE SUMMARY\n"
        summary += "-" * 25 + "\n"
        summary += f"Initial Portfolio Value: ${metrics.get('initial_value', 0):,.2f}\n"
        summary += f"Maximum Potential Loss: ${abs(metrics.get('max_loss', 0)):,.2f}\n"
        summary += f"Expected Loss (Avg): ${abs(metrics.get('avg_loss', 0)):,.2f}\n"
        summary += f"Value at Risk (99%): ${abs(risk_metrics.get('var_99', 0)):,.2f}\n"
        summary += f"Expected Shortfall (99%): ${abs(risk_metrics.get('expected_shortfall_99', 0)):,.2f}\n\n"
        
        return summary
    
    def _create_detailed_analysis(self) -> str:
        """Create detailed scenario analysis"""
        analysis = "DETAILED SCENARIO ANALYSIS\n"
        analysis += "-" * 30 + "\n"
        
        scenario_analysis = self.report_data.get('scenario_analysis', {})
        analysis += f"Total Scenarios Run: {self.report_data.get('total_scenarios_run', 0)}\n"
        analysis += f"Worst Performing Scenario: {scenario_analysis.get('worst_scenario', 'N/A')}\n"
        analysis += f"Best Performing Scenario: {scenario_analysis.get('best_scenario', 'N/A')}\n"
        analysis += f"Scenarios with Losses: {scenario_analysis.get('scenario_count_negative', 0)}\n"
        analysis += f"Scenarios with Gains: {scenario_analysis.get('scenario_count_positive', 0)}\n\n"
        
        analysis += "SCENARIO-BY-SCENARIO RESULTS:\n"
        analysis += "-" * 35 + "\n"
        
        results_summary = self.report_data.get('results_summary', {})
        for scenario_name, result in results_summary.items():
            analysis += f"{scenario_name}:\n"
            analysis += f"  Base Value: ${result['base_value']:,.2f}\n"
            analysis += f"  Shocked Value: ${result['shocked_value']:,.2f}\n"
            analysis += f"  P&L Impact: ${result['pnl_impact']:,.2f} ({result['pnl_percentage']:.2f}%)\n"
            analysis += f"  Stress Severity: {result['stress_severity']:.2%}\n\n"
        
        return analysis
    
    def _create_capital_assessment(self) -> str:
        """Create capital adequacy assessment"""
        assessment = "CAPITAL ADEQUACY ASSESSMENT\n"
        assessment += "-" * 30 + "\n"
        
        capital_metrics = self.report_data.get('capital_metrics', {})
        
        assessment += f"Required Capital Buffer: ${capital_metrics.get('capital_requirement', 0):,.2f}\n"
        assessment += f"Capital Ratio: {capital_metrics.get('capital_ratio', 0):.2%}\n"
        assessment += f"Capital Coverage Ratio: {capital_metrics.get('capital_coverage_ratio', 0):.2f}x\n"
        assessment += f"Stress Capital Buffer: ${capital_metrics.get('stress_capital_buffer', 0):,.2f}\n\n"
        
        # Capital adequacy determination
        if capital_metrics.get('capital_coverage_ratio', 0) > 1.0:
            assessment += "CAPITAL ADEQUACY: ADEQUATE\n"
            assessment += "The portfolio has sufficient capital to withstand the tested stress scenarios.\n\n"
        else:
            assessment += "CAPITAL ADEQUACY: INSUFFICIENT\n"
            assessment += "The portfolio does not have adequate capital to withstand the tested stress scenarios.\n\n"
        
        return assessment
    
    def _create_risk_metrics_summary(self) -> str:
        """Create risk metrics summary"""
        summary = "RISK METRICS SUMMARY\n"
        summary += "-" * 22 + "\n"
        
        risk_metrics = self.report_data.get('risk_metrics', {})
        portfolio_metrics = self.report_data.get('portfolio_metrics', {})
        
        summary += f"Volatility (P&L): ${portfolio_metrics.get('volatility', 0):,.2f}\n"
        summary += f"Value at Risk (95%): ${abs(risk_metrics.get('var_95', 0)):,.2f}\n"
        summary += f"Value at Risk (99%): ${abs(risk_metrics.get('var_99', 0)):,.2f}\n"
        summary += f"Expected Shortfall (95%): ${abs(risk_metrics.get('expected_shortfall_95', 0)):,.2f}\n"
        summary += f"Expected Shortfall (99%): ${abs(risk_metrics.get('expected_shortfall_99', 0)):,.2f}\n"
        summary += f"Worst Case Loss: ${abs(risk_metrics.get('worst_case_loss', 0)):,.2f}\n"
        summary += f"Stress VaR Equivalent: ${abs(risk_metrics.get('stress_var', 0)):,.2f}\n\n"
        
        return summary
    
    def generate_visualizations(self, output_path: str = "risk_visualizations"):
        """Generate risk visualization charts"""
        try:
            import os
            os.makedirs(output_path, exist_ok=True)
            
            # Create P&L distribution plot
            self._create_pnl_distribution_plot(output_path)
            
            # Create scenario comparison chart
            self._create_scenario_comparison_chart(output_path)
            
            # Create risk metrics waterfall
            self._create_risk_waterfall_chart(output_path)
            
        except ImportError:
            print("Matplotlib/seaborn not available for visualizations")
    
    def _create_pnl_distribution_plot(self, output_path: str):
        """Create P&L distribution plot"""
        try:
            results_summary = self.report_data.get('results_summary', {})
            pnl_values = [result['pnl_impact'] for result in results_summary.values()]
            
            plt.figure(figsize=(10, 6))
            plt.hist(pnl_values, bins=20, edgecolor='black', alpha=0.7)
            plt.title('P&L Distribution Across Stress Scenarios')
            plt.xlabel('P&L Impact ($)')
            plt.ylabel('Frequency')
            plt.axvline(x=0, color='red', linestyle='--', label='Break-even')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{output_path}/pnl_distribution.png")
            plt.close()
        except:
            pass  # Skip if plotting fails
    
    def _create_scenario_comparison_chart(self, output_path: str):
        """Create scenario comparison chart"""
        try:
            results_summary = self.report_data.get('results_summary', {})
            scenarios = list(results_summary.keys())
            pnl_values = [result['pnl_impact'] for result in results_summary.values()]
            
            plt.figure(figsize=(12, 6))
            colors = ['red' if x < 0 else 'green' for x in pnl_values]
            plt.bar(scenarios, pnl_values, color=colors, alpha=0.7)
            plt.title('P&L Impact by Scenario')
            plt.xlabel('Scenario')
            plt.ylabel('P&L Impact ($)')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{output_path}/scenario_comparison.png")
            plt.close()
        except:
            pass  # Skip if plotting fails
    
    def _create_risk_waterfall_chart(self, output_path: str):
        """Create risk metrics waterfall chart"""
        try:
            risk_metrics = self.report_data.get('risk_metrics', {})
            
            metrics = ['VaR 95%', 'VaR 99%', 'ES 95%', 'ES 99%', 'Worst Loss']
            values = [
                abs(risk_metrics.get('var_95', 0)),
                abs(risk_metrics.get('var_99', 0)),
                abs(risk_metrics.get('expected_shortfall_95', 0)),
                abs(risk_metrics.get('expected_shortfall_99', 0)),
                abs(risk_metrics.get('worst_case_loss', 0))
            ]
            
            plt.figure(figsize=(10, 6))
            plt.bar(metrics, values, alpha=0.7)
            plt.title('Risk Metrics Comparison')
            plt.xlabel('Risk Metric')
            plt.ylabel('Value ($)')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{output_path}/risk_metrics.png")
            plt.close()
        except:
            pass  # Skip if plotting fails
    
    def export_to_json(self, output_path: str = "regulatory_report.json"):
        """Export results to JSON format"""
        with open(output_path, 'w') as f:
            json.dump(self.report_data, f, indent=2)
    
    def export_to_csv(self, output_path: str = "regulatory_report.csv"):
        """Export results to CSV format"""
        results_summary = self.report_data.get('results_summary', {})
        
        # Convert to DataFrame
        data = []
        for scenario_name, result in results_summary.items():
            row = {
                'Scenario': scenario_name,
                'Base_Value': result['base_value'],
                'Shocked_Value': result['shocked_value'],
                'PnL_Impact': result['pnl_impact'],
                'PnL_Percentage': result['pnl_percentage'],
                'Stress_Severity': result['stress_severity']
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)