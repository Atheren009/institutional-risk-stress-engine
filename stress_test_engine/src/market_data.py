"""
Market Data Handler for Stress Testing Engine
"""
import pandas as pd
import QuantLib as ql
from typing import Dict, List, Tuple, Optional
import numpy as np
from .validation import DataValidator


class MarketData:
    """Handles market data for stress testing"""
    
    def __init__(self):
        self.yield_curve = None
        self.vol_surface = None
        self.credit_curves = {}
        self.base_date = ql.Date.todaysDate()
        self.instruments = []
        self.spot_rates = {}  # For equity spot rates
        self.fx_rates = {}    # For FX rates
        self.commodity_prices = {}  # For commodities
        
    def load_yield_curve_data(self, curve_data: pd.DataFrame) -> None:
        """Load yield curve instruments data"""
        # Validate the data first
        is_valid, issues = DataValidator.validate_market_data(curve_data)
        if not is_valid:
            raise ValueError(f"Invalid yield curve data: {', '.join(issues)}")
        
        # Expected columns: tenor, rate, instrument_type
        self.yield_curve_data = curve_data
        
    def build_yield_curve(self) -> ql.YieldTermStructure:
        """Build base yield curve from market data"""
        dates = []
        rates = []
        
        for _, row in self.yield_curve_data.iterrows():
            tenor = row['tenor']
            rate = row['rate']
            
            # Convert tenor to date
            if tenor.endswith('D'):
                days = int(tenor[:-1])
                date = self.base_date + ql.Period(days, ql.Days)
            elif tenor.endswith('W'):
                weeks = int(tenor[:-1])
                date = self.base_date + ql.Period(weeks, ql.Weeks)
            elif tenor.endswith('M'):
                months = int(tenor[:-1])
                date = self.base_date + ql.Period(months, ql.Months)
            elif tenor.endswith('Y'):
                years = int(tenor[:-1])
                date = self.base_date + ql.Period(years, ql.Years)
            else:
                # Try to parse as a simple number (assume years)
                try:
                    years = int(tenor)
                    date = self.base_date + ql.Period(years, ql.Years)
                except ValueError:
                    raise ValueError(f"Unknown tenor format: {tenor}")
                
            dates.append(date)
            rates.append(rate)
        
        # Create deposit rate helpers
        helpers = []
        for i in range(len(dates)):
            # Calculate tenor period based on the difference between dates
            tenor_in_days = (dates[i] - self.base_date)
            if tenor_in_days <= 31:  # Less than 1 month - use days
                tenor_period = ql.Period(int(tenor_in_days), ql.Days)
            elif tenor_in_days <= 365:  # Less than 1 year - use months
                tenor_period = ql.Period(int(tenor_in_days / 30), ql.Months)
            else:  # More than 1 year - use years
                tenor_period = ql.Period(int(tenor_in_days / 365), ql.Years)
            
            helpers.append(ql.DepositRateHelper(
                ql.QuoteHandle(ql.SimpleQuote(rates[i])),
                tenor_period,
                2,  # settlement days
                ql.TARGET(),
                ql.ModifiedFollowing,
                True,
                ql.Actual365Fixed()
            ))
        
        # Create yield curve using the helpers
        self.yield_curve = ql.PiecewiseLinearForward(
            self.base_date,
            helpers,
            ql.Actual365Fixed()
        )
        
        return self.yield_curve
    
    def load_vol_surface_data(self, vol_data: pd.DataFrame) -> None:
        """Load volatility surface data"""
        # Validate the data first
        is_valid, issues = DataValidator.validate_market_data(vol_data)
        if not is_valid:
            raise ValueError(f"Invalid volatility surface data: {', '.join(issues)}")
        
        # Expected columns: strike, maturity, volatility
        self.vol_surface_data = vol_data
    
    def build_vol_surface(self) -> ql.BlackVarianceSurface:
        """Build volatility surface from market data"""
        if hasattr(self, 'vol_surface_data'):
            # Extract data
            strikes = self.vol_surface_data['strike'].values
            maturities = self.vol_surface_data['maturity'].values
            vols = self.vol_surface_data['volatility'].values
            
            # Convert maturities to dates
            maturity_dates = []
            for maturity in maturities:
                if maturity.endswith('Y'):
                    years = int(maturity[:-1])
                    maturity_dates.append(self.base_date + ql.Period(years, ql.Years))
                elif maturity.endswith('M'):
                    months = int(maturity[:-1])
                    maturity_dates.append(self.base_date + ql.Period(months, ql.Months))
                else:
                    years = float(maturity)
                    maturity_dates.append(self.base_date + ql.Period(int(years*12), ql.Months))
            
            # Create volatility surface
            # Note: This is a simplified approach - a full implementation would require proper surface construction
            self.vol_surface = None  # Placeholder for actual surface
            return self.vol_surface
        return None
    
    def apply_vol_shock(self, shock_type: str, shock_params: Dict) -> ql.BlackVarianceSurface:
        """Apply volatility shock to the surface"""
        # Placeholder for volatility shock implementation
        original_surface = self.build_vol_surface() if hasattr(self, 'vol_surface_data') else None
        
        if shock_type == "uniform":
            shift = shock_params.get("vol_shift", 0.0)
            # In a full implementation, this would modify the surface
            pass
        elif shock_type == "skew":
            atm_shift = shock_params.get("atm_shift", 0.0)
            otm_multiplier = shock_params.get("otm_multiplier", 1.0)
            # In a full implementation, this would adjust the skew
            pass
        elif shock_type == "term_structure":
            short_vol_multiplier = shock_params.get("short_vol_multiplier", 1.0)
            long_vol_multiplier = shock_params.get("long_vol_multiplier", 1.0)
            # In a full implementation, this would adjust the term structure
            pass
        
        return original_surface  # Placeholder
    
    def load_credit_data(self, credit_data: pd.DataFrame) -> None:
        """Load credit spread data"""
        # Validate the data first
        is_valid, issues = DataValidator.validate_market_data(credit_data)
        if not is_valid:
            raise ValueError(f"Invalid credit data: {', '.join(issues)}")
        
        # Expected columns: issuer, tenor, spread, rating
        self.credit_data = credit_data
    
    def build_credit_curve(self, issuer: str) -> ql.RelinkableYieldTermStructureHandle:
        """Build credit curve for a specific issuer"""
        if hasattr(self, 'credit_data'):
            issuer_data = self.credit_data[self.credit_data['issuer'] == issuer]
            if not issuer_data.empty:
                # Create credit curve based on spreads over risk-free curve
                # This is a simplified approach - full implementation would use CDS or bond data
                pass
        return None
    
    def apply_credit_shock(self, issuer: str, shock_type: str, shock_params: Dict) -> ql.RelinkableYieldTermStructureHandle:
        """Apply credit spread shock"""
        original_curve = self.build_credit_curve(issuer)
        
        if shock_type == "parallel":
            spread_bp = shock_params.get("spread_bp", 0) / 10000.0
            # In a full implementation, this would adjust the credit curve
            pass
        elif shock_type == "rating_migration":
            new_rating = shock_params.get("new_rating", "BBB")
            # In a full implementation, this would simulate rating migration
            pass
        
        return original_curve  # Placeholder
    
    def apply_rate_shock(self, shock_type: str, shock_params: Dict) -> ql.YieldTermStructure:
        """Apply interest rate shock to the curve"""
        # Rebuild the original curve from the original data
        original_curve = self.build_yield_curve()
        
        # Get original curve data
        original_dates = self.yield_curve_data['tenor'].tolist()  # Use original data instead
        original_rates = self.yield_curve_data['rate'].tolist()
        
        # Apply shock based on type
        shocked_rates = []
        if shock_type == "parallel":
            shift = shock_params.get("shift_bp", 0) / 10000.0
            shocked_rates = [rate + shift for rate in original_rates]
        elif shock_type == "steepener":
            short_shift = shock_params.get("short_shift_bp", 0) / 10000.0
            long_shift = shock_params.get("long_shift_bp", 0) / 10000.0
            # Apply different shifts based on tenor
            for i, tenor in enumerate(original_dates):
                # Convert tenor string to years for comparison
                if tenor.endswith('D'):
                    tenor_years = int(tenor[:-1]) / 365.0
                elif tenor.endswith('W'):
                    tenor_years = int(tenor[:-1]) / 52.0
                elif tenor.endswith('M'):
                    tenor_years = int(tenor[:-1]) / 12.0
                elif tenor.endswith('Y'):
                    tenor_years = int(tenor[:-1])
                else:
                    tenor_years = int(tenor)  # Assume years if no suffix
                
                if tenor_years <= 2:  # Short end
                    shocked_rates.append(original_rates[i] + short_shift)
                else:  # Long end
                    shocked_rates.append(original_rates[i] + long_shift)
        elif shock_type == "key_rate":
            key_tenors = shock_params.get("key_tenors", [])
            key_shifts = shock_params.get("key_shifts_bp", [])
            # Apply shifts to specific tenors with interpolation
            for i, tenor in enumerate(original_dates):
                # Convert tenor string to years
                if tenor.endswith('D'):
                    tenor_years = int(tenor[:-1]) / 365.0
                elif tenor.endswith('W'):
                    tenor_years = int(tenor[:-1]) / 52.0
                elif tenor.endswith('M'):
                    tenor_years = int(tenor[:-1]) / 12.0
                elif tenor.endswith('Y'):
                    tenor_years = int(tenor[:-1])
                else:
                    tenor_years = int(tenor)  # Assume years if no suffix
                
                shift = 0
                for j, key_tenor in enumerate(key_tenors):
                    if abs(tenor_years - key_tenor) < 0.5:  # Close to key tenor
                        shift += key_shifts[j] / 10000.0
                shocked_rates.append(original_rates[i] + shift)
        else:
            raise ValueError(f"Unknown shock type: {shock_type}")
        
        # Create new yield curve data with shocked rates
        shocked_curve_data = self.yield_curve_data.copy()
        shocked_curve_data['rate'] = shocked_rates
        
        # Create a temporary MarketData object to build the shocked curve
        temp_market_data = MarketData()
        temp_market_data.base_date = self.base_date
        temp_market_data.yield_curve_data = shocked_curve_data
        
        # Build and return the shocked curve
        return temp_market_data.build_yield_curve()