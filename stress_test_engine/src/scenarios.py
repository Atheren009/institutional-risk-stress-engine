"""
Scenario Management for Stress Testing Engine
"""
import QuantLib as ql
from typing import Dict, List, Any
import json


class Scenario:
    """Represents a single stress scenario"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.rate_shocks = []  # List of rate shock definitions
        self.vol_shocks = []   # List of volatility shock definitions
        self.credit_shocks = [] # List of credit shock definitions
    
    def add_rate_shock(self, shock_type: str, shock_params: Dict[str, Any]):
        """Add an interest rate shock to this scenario"""
        self.rate_shocks.append({
            "type": shock_type,
            "params": shock_params
        })
    
    def add_vol_shock(self, shock_type: str, shock_params: Dict[str, Any]):
        """Add a volatility shock to this scenario"""
        self.vol_shocks.append({
            "type": shock_type,
            "params": shock_params
        })
    
    def add_credit_shock(self, shock_type: str, shock_params: Dict[str, Any]):
        """Add a credit spread shock to this scenario"""
        self.credit_shocks.append({
            "type": shock_type,
            "params": shock_params
        })


class ScenarioManager:
    """Manages multiple stress scenarios"""
    
    def __init__(self):
        self.scenarios = {}
    
    def create_scenario(self, name: str, description: str = "") -> Scenario:
        """Create and register a new scenario"""
        scenario = Scenario(name, description)
        self.scenarios[name] = scenario
        return scenario
    
    def get_scenario(self, name: str) -> Scenario:
        """Get a scenario by name"""
        return self.scenarios.get(name)
    
    def load_scenarios_from_json(self, file_path: str):
        """Load scenarios from a JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for scenario_data in data:
            name = scenario_data['name']
            description = scenario_data.get('description', '')
            scenario = self.create_scenario(name, description)
            
            # Add rate shocks
            for rate_shock in scenario_data.get('rate_shocks', []):
                scenario.add_rate_shock(rate_shock['type'], rate_shock['params'])
            
            # Add vol shocks
            for vol_shock in scenario_data.get('vol_shocks', []):
                scenario.add_vol_shock(vol_shock['type'], vol_shock['params'])
            
            # Add credit shocks
            for credit_shock in scenario_data.get('credit_shocks', []):
                scenario.add_credit_shock(credit_shock['type'], credit_shock['params'])
    
    def get_all_scenario_names(self) -> List[str]:
        """Get names of all scenarios"""
        return list(self.scenarios.keys())


# Predefined regulatory scenarios
def create_basel_iii_scenarios() -> ScenarioManager:
    """Create standard Basel III stress scenarios"""
    sm = ScenarioManager()
    
    # Basel III adverse scenario: Parallel rate increase
    adverse_rate = sm.create_scenario(
        "basel_iii_adverse_rate", 
        "Basel III adverse interest rate scenario: +300bp parallel shift"
    )
    adverse_rate.add_rate_shock("parallel", {"shift_bp": 300})
    
    # Basel III adverse scenario: Credit spread widening
    adverse_credit = sm.create_scenario(
        "basel_iii_adverse_credit",
        "Basel III adverse credit scenario: +300bp credit spread widening"
    )
    adverse_credit.add_credit_shock("parallel", {"spread_bp": 300})
    
    # Combined scenario
    combined = sm.create_scenario(
        "basel_iii_combined",
        "Basel III combined adverse scenario"
    )
    combined.add_rate_shock("parallel", {"shift_bp": 200})
    combined.add_vol_shock("uniform", {"vol_shift": 0.20})
    combined.add_credit_shock("parallel", {"spread_bp": 300})
    
    return sm


def create_historical_scenarios() -> ScenarioManager:
    """Create historical crisis scenarios"""
    sm = ScenarioManager()
    
    # 2008 Financial Crisis scenario
    crisis_2008 = sm.create_scenario(
        "historical_2008_crisis",
        "2008 Financial Crisis: Rate cut + vol shock + credit widening"
    )
    crisis_2008.add_rate_shock("parallel", {"shift_bp": -400})  # Rates cut
    crisis_2008.add_vol_shock("skew", {"atm_shift": 0.50, "otm_multiplier": 2.0})
    crisis_2008.add_credit_shock("parallel", {"spread_bp": 500})
    
    # COVID-19 scenario
    covid = sm.create_scenario(
        "historical_covid",
        "COVID-19 market shock: Vol explosion + credit stress"
    )
    covid.add_vol_shock("term_structure", {"short_vol_multiplier": 3.0, "long_vol_multiplier": 1.5})
    covid.add_credit_shock("sector_specific", {"sectors": ["financials", "energy"], "spread_bp": 400})
    
    return sm