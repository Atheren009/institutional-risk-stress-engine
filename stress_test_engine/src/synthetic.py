"""
Synthetic Data & Scenario Generator for Stress Testing Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import QuantLib as ql
from datetime import datetime, timedelta


class SyntheticDataGenerator:
    """Generates synthetic market and portfolio data for testing"""
    
    @staticmethod
    def generate_synthetic_yield_curve_data(
        base_date: ql.Date = None,
        tenors: List[str] = None,
        base_rate: float = 0.05,
        volatility: float = 0.005
    ) -> pd.DataFrame:
        """Generate synthetic yield curve data"""
        if base_date is None:
            base_date = ql.Date.todaysDate()
        if tenors is None:
            tenors = ['1D', '1W', '2W', '1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
        
        # Generate rates with realistic term structure
        rates = []
        for i, tenor in enumerate(tenors):
            # Add some realistic term structure behavior
            if tenor.endswith('D') or tenor.endswith('W'):
                rate = base_rate * 0.8  # Short rates typically lower
            elif tenor.endswith('M'):
                rate = base_rate * 0.9
            elif tenor.endswith('Y'):
                years = int(tenor[:-1])
                if years <= 2:
                    rate = base_rate * 0.95
                elif years <= 5:
                    rate = base_rate
                elif years <= 10:
                    rate = base_rate * 1.02
                else:
                    rate = base_rate * 1.05
            else:
                rate = base_rate
            
            # Add some random noise
            rate += np.random.normal(0, volatility)
            rates.append(max(0.001, rate))  # Ensure positive rates
        
        return pd.DataFrame({
            'tenor': tenors,
            'rate': rates
        })
    
    @staticmethod
    def generate_synthetic_vol_surface_data(
        strikes: List[float] = None,
        maturities: List[str] = None,
        atm_vol: float = 0.20
    ) -> pd.DataFrame:
        """Generate synthetic volatility surface data"""
        if strikes is None:
            strikes = [80, 90, 100, 110, 120]  # Percentage of spot
        if maturities is None:
            maturities = ['1M', '3M', '6M', '1Y', '2Y']
        
        data = []
        for maturity in maturities:
            for strike in strikes:
                # Create realistic volatility smile/skew
                atm_adjustment = 0
                if strike < 100:  # OTM puts (low strikes)
                    vol = atm_vol * (1.2 - 0.1 * (100 - strike) / 10)  # Higher vol for low strikes
                elif strike > 100:  # OTM calls (high strikes)
                    vol = atm_vol * (1.1 - 0.05 * (strike - 100) / 10)  # Slightly higher vol for high strikes
                else:  # ATM
                    vol = atm_vol
                
                # Term structure: shorter maturity = higher vol
                if '1M' in maturity:
                    vol *= 1.2
                elif '3M' in maturity:
                    vol *= 1.1
                elif '6M' in maturity:
                    vol *= 1.05
                # 1Y and 2Y have base vol
                
                data.append({
                    'strike': strike,
                    'maturity': maturity,
                    'volatility': max(0.05, min(0.8, vol))  # Keep between 5% and 80%
                })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_synthetic_credit_data(
        issuers: List[str] = None,
        base_spreads: Dict[str, float] = None
    ) -> pd.DataFrame:
        """Generate synthetic credit spread data"""
        if issuers is None:
            issuers = ['AAA Corp', 'AA Corp', 'A Corp', 'BBB Corp', 'High Yield Corp']
        if base_spreads is None:
            base_spreads = {
                'AAA Corp': 0.005,   # 50 bps
                'AA Corp': 0.008,    # 80 bps
                'A Corp': 0.012,     # 120 bps
                'BBB Corp': 0.018,   # 180 bps
                'High Yield Corp': 0.05  # 500 bps
            }
        
        data = []
        for issuer in issuers:
            base_spread = base_spreads.get(issuer, 0.02)  # Default to 200 bps
            
            # Add some variation by tenor
            for tenor in ['1Y', '3Y', '5Y', '7Y', '10Y']:
                spread = base_spread
                # Credit spreads typically increase with tenor
                if '10Y' in tenor:
                    spread *= 1.1
                elif '7Y' in tenor:
                    spread *= 1.05
                elif '5Y' in tenor:
                    spread *= 1.02
                
                data.append({
                    'issuer': issuer,
                    'tenor': tenor,
                    'spread': spread,
                    'rating': issuer.split()[0]  # Extract rating from name
                })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_synthetic_portfolio(
        size: int = 10,
        seed: int = 42
    ) -> pd.DataFrame:
        """Generate synthetic portfolio data"""
        np.random.seed(seed)
        
        instrument_types = ['bond', 'swap', 'option', 'equity']
        data = []
        
        for i in range(size):
            inst_type = np.random.choice(instrument_types, p=[0.4, 0.2, 0.3, 0.1])  # Weight towards bonds
            
            row = {
                'id': f'pos_{i+1:03d}',
                'instrument_type': inst_type,
                'quantity': np.random.uniform(100000, 10000000),  # Between 100K and 10M
                'underlying': f'UNDERLYING_{np.random.randint(1, 20):02d}'
            }
            
            if inst_type == 'bond':
                row['maturity'] = np.random.choice(['1Y', '3Y', '5Y', '7Y', '10Y'])
                row['notional'] = row['quantity']
            elif inst_type == 'swap':
                row['notional'] = row['quantity']
            elif inst_type == 'option':
                row['strike'] = np.random.uniform(90, 110)  # Strike as % of spot
                row['maturity'] = np.random.choice(['1M', '3M', '6M', '1Y'])
                row['notional'] = 100  # Option size
            elif inst_type == 'equity':
                row['notional'] = 100  # Share size
            
            data.append(row)
        
        return pd.DataFrame(data)


class ScenarioGenerator:
    """Generates realistic stress test scenarios"""
    
    @staticmethod
    def generate_interest_rate_scenarios() -> List[Dict]:
        """Generate various interest rate stress scenarios"""
        scenarios = []
        
        # Parallel shift scenarios
        scenarios.append({
            'name': 'parallel_rate_shock_200bp_up',
            'type': 'rate',
            'shock_type': 'parallel',
            'params': {'shift_bp': 200},
            'description': 'Parallel 200bp increase in all rates'
        })
        
        scenarios.append({
            'name': 'parallel_rate_shock_300bp_down',
            'type': 'rate',
            'shock_type': 'parallel',
            'params': {'shift_bp': -300},
            'description': 'Parallel 300bp decrease in all rates'
        })
        
        # Steepener scenarios
        scenarios.append({
            'name': 'steepener_shock',
            'type': 'rate',
            'shock_type': 'steepener',
            'params': {'short_shift_bp': 50, 'long_shift_bp': 200},
            'description': 'Short rates +50bp, Long rates +200bp (steepening)'
        })
        
        scenarios.append({
            'name': 'flatten_shock',
            'type': 'rate',
            'shock_type': 'steepener',
            'params': {'short_shift_bp': 100, 'long_shift_bp': -50},
            'description': 'Short rates +100bp, Long rates -50bp (inversion)'
        })
        
        # Key rate scenarios
        scenarios.append({
            'name': 'key_rate_2s10s',
            'type': 'rate',
            'shock_type': 'key_rate',
            'params': {'key_tenors': [2, 10], 'key_shifts_bp': [150, -100]},
            'description': '2Y +150bp, 10Y -100bp (inversion)'
        })
        
        return scenarios
    
    @staticmethod
    def generate_volatility_scenarios() -> List[Dict]:
        """Generate various volatility stress scenarios"""
        scenarios = []
        
        # Uniform volatility shock
        scenarios.append({
            'name': 'vol_shock_uniform_50percent',
            'type': 'vol',
            'shock_type': 'uniform',
            'params': {'vol_shift': 0.50},
            'description': '50% increase in all volatilities'
        })
        
        # Volatility skew shock
        scenarios.append({
            'name': 'vol_shock_skew',
            'type': 'vol',
            'shock_type': 'skew',
            'params': {'atm_shift': 0.30, 'otm_multiplier': 2.0},
            'description': 'ATM +30%, OTM volatilities double'
        })
        
        # Term structure shock
        scenarios.append({
            'name': 'vol_term_shock',
            'type': 'vol',
            'shock_type': 'term_structure',
            'params': {'short_vol_multiplier': 3.0, 'long_vol_multiplier': 1.5},
            'description': 'Short-dated volatilities triple, long-dated 50% higher'
        })
        
        return scenarios
    
    @staticmethod
    def generate_credit_scenarios() -> List[Dict]:
        """Generate various credit spread stress scenarios"""
        scenarios = []
        
        # Parallel credit spread widening
        scenarios.append({
            'name': 'credit_spread_widening_300bp',
            'type': 'credit',
            'shock_type': 'parallel',
            'params': {'spread_bp': 300},
            'description': 'All credit spreads widen by 300bp'
        })
        
        # Rating migration scenario
        scenarios.append({
            'name': 'rating_migration_downgrade',
            'type': 'credit',
            'shock_type': 'rating_migration',
            'params': {'new_rating': 'BB'},
            'description': 'Simulated downgrade to speculative grade'
        })
        
        # Sector-specific stress
        scenarios.append({
            'name': 'sector_stress_energy',
            'type': 'credit',
            'shock_type': 'sector_specific',
            'params': {'sectors': ['Energy', 'Materials'], 'spread_bp': 500},
            'description': 'Energy and Materials sectors spread +500bp'
        })
        
        return scenarios
    
    @staticmethod
    def generate_historical_crisis_scenarios() -> List[Dict]:
        """Generate historical crisis-like scenarios"""
        scenarios = []
        
        # 2008 Financial Crisis pattern
        scenarios.append({
            'name': 'historical_2008_pattern',
            'type': 'combined',
            'shock_type': 'combined',
            'params': {
                'rate_shock': {'type': 'parallel', 'params': {'shift_bp': -400}},  # Rates cut
                'vol_shock': {'type': 'uniform', 'params': {'vol_shift': 1.00}},   # Vol doubles
                'credit_shock': {'type': 'parallel', 'params': {'spread_bp': 500}}  # Credit spreads widen
            },
            'description': '2008 Crisis: Rate cut + vol shock + credit widening'
        })
        
        # COVID-19 pattern
        scenarios.append({
            'name': 'historical_covid_pattern',
            'type': 'combined',
            'shock_type': 'combined',
            'params': {
                'rate_shock': {'type': 'parallel', 'params': {'shift_bp': -150}},  # Rates cut
                'vol_shock': {'type': 'term_structure', 'params': {'short_vol_multiplier': 2.5, 'long_vol_multiplier': 1.8}},  # Vol explosion
                'credit_shock': {'type': 'sector_specific', 'params': {'sectors': ['Energy', 'Retail'], 'spread_bp': 400}}  # Sector stress
            },
            'description': 'COVID-19: Vol explosion + sector-specific credit stress'
        })
        
        # European debt crisis pattern
        scenarios.append({
            'name': 'historical_euro_debt_pattern',
            'type': 'combined',
            'shock_type': 'combined',
            'params': {
                'rate_shock': {'type': 'steepener', 'params': {'short_shift_bp': 100, 'long_shift_bp': -50}},  # Curve inversion
                'vol_shock': {'type': 'skew', 'params': {'atm_shift': 0.40, 'otm_multiplier': 1.5}},  # Skew shock
                'credit_shock': {'type': 'rating_migration', 'params': {'new_rating': 'BBB'}}  # Sovereign downgrades
            },
            'description': 'Euro debt crisis: Curve inversion + sovereign downgrades'
        })
        
        return scenarios
    
    @staticmethod
    def generate_regulatory_scenarios() -> List[Dict]:
        """Generate regulatory-style stress scenarios"""
        scenarios = []
        
        # Basel III adverse scenario
        scenarios.append({
            'name': 'basel_iii_adverse',
            'type': 'regulatory',
            'shock_type': 'combined',
            'params': {
                'rate_shock': {'type': 'parallel', 'params': {'shift_bp': 200}},  # Rates up
                'vol_shock': {'type': 'uniform', 'params': {'vol_shift': 0.25}},   # Vol up 25%
                'credit_shock': {'type': 'parallel', 'params': {'spread_bp': 300}}  # Credit spreads up
            },
            'description': 'Basel III adverse: Rising rates + vol + credit stress'
        })
        
        # CCAR supervisory scenario
        scenarios.append({
            'name': 'ccar_supervisory',
            'type': 'regulatory',
            'shock_type': 'combined',
            'params': {
                'rate_shock': {'type': 'steepener', 'params': {'short_shift_bp': -100, 'long_shift_bp': 150}},  # Inversion
                'vol_shock': {'type': 'uniform', 'params': {'vol_shift': 0.50}},   # Vol up 50%
                'credit_shock': {'type': 'parallel', 'params': {'spread_bp': 400}}  # Credit spreads up
            },
            'description': 'CCAR supervisory: Inverted curve + vol + credit stress'
        })
        
        return scenarios


# Example usage and testing
if __name__ == "__main__":
    # Generate synthetic data
    print("Generating synthetic yield curve data...")
    yield_curve_data = SyntheticDataGenerator.generate_synthetic_yield_curve_data()
    print(yield_curve_data.head())
    
    print("\nGenerating synthetic volatility surface data...")
    vol_surface_data = SyntheticDataGenerator.generate_synthetic_vol_surface_data()
    print(vol_surface_data.head())
    
    print("\nGenerating synthetic credit data...")
    credit_data = SyntheticDataGenerator.generate_synthetic_credit_data()
    print(credit_data.head())
    
    print("\nGenerating synthetic portfolio...")
    portfolio_data = SyntheticDataGenerator.generate_synthetic_portfolio(size=5)
    print(portfolio_data)
    
    print("\nGenerating interest rate scenarios...")
    ir_scenarios = ScenarioGenerator.generate_interest_rate_scenarios()
    for scenario in ir_scenarios[:2]:  # Show first 2
        print(f"- {scenario['name']}: {scenario['description']}")
    
    print("\nGenerating all scenario types...")
    all_scenarios = (
        ScenarioGenerator.generate_interest_rate_scenarios() +
        ScenarioGenerator.generate_volatility_scenarios() +
        ScenarioGenerator.generate_credit_scenarios() +
        ScenarioGenerator.generate_historical_crisis_scenarios() +
        ScenarioGenerator.generate_regulatory_scenarios()
    )
    print(f"Total scenarios generated: {len(all_scenarios)}")