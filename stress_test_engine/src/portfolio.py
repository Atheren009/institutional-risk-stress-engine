"""
Portfolio Management for Stress Testing Engine
"""
import QuantLib as ql
import pandas as pd
from typing import Dict, List, Any
from dataclasses import dataclass
from .validation import DataValidator


@dataclass
class Position:
    """Represents a single portfolio position"""
    id: str
    instrument_type: str  # 'bond', 'swap', 'option', 'equity', etc.
    quantity: float
    underlying: str  # e.g., 'GOOGL', 'US Treasury 5Y', etc.
    maturity: str = None  # For fixed income instruments
    strike: float = None  # For options
    notional: float = None  # For derivatives
    greeks: dict = None  # To store delta, gamma, vega, theta, rho


class Portfolio:
    """Manages a collection of positions for stress testing"""
    
    def __init__(self, name: str = "Default Portfolio"):
        self.name = name
        self.positions = {}
        self.valuation_date = ql.Date.todaysDate()
    
    def add_position(self, position: Position):
        """Add a position to the portfolio"""
        self.positions[position.id] = position
    
    def load_from_dataframe(self, df: pd.DataFrame):
        """Load portfolio from a DataFrame"""
        # Validate the portfolio data first
        is_valid, issues = DataValidator.validate_portfolio_data(df)
        if not is_valid:
            raise ValueError(f"Invalid portfolio data: {', '.join(issues)}")
        
        for _, row in df.iterrows():
            position = Position(
                id=row.get('id'),
                instrument_type=row.get('instrument_type'),
                quantity=row.get('quantity', 1.0),
                underlying=row.get('underlying'),
                maturity=row.get('maturity'),
                strike=row.get('strike'),
                notional=row.get('notional'),
                greeks={}  # Initialize Greeks dictionary
            )
            self.add_position(position)
    
    def get_instrument_types(self) -> List[str]:
        """Get all unique instrument types in the portfolio"""
        return list(set(pos.instrument_type for pos in self.positions.values()))
    
    def get_exposure_by_underlying(self) -> Dict[str, float]:
        """Calculate total exposure by underlying asset"""
        exposure = {}
        for pos in self.positions.values():
            underlying = pos.underlying
            notional = pos.quantity * (pos.notional or 1.0)
            exposure[underlying] = exposure.get(underlying, 0) + notional
        return exposure


class PortfolioValuationEngine:
    """Handles portfolio revaluation under different market scenarios"""
    
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.valuation_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = self.valuation_date
    
    def value_portfolio(self, market_data) -> Dict[str, float]:
        """Value the entire portfolio under given market conditions"""
        portfolio_npv = 0.0
        position_values = {}
        portfolio_greeks = {
            'delta': 0.0,
            'gamma': 0.0,
            'vega': 0.0,
            'theta': 0.0,
            'rho': 0.0
        }
        
        for pos_id, position in self.portfolio.positions.items():
            position_result = self._value_position_with_greeks(position, market_data)
            position_values[pos_id] = position_result['value']
            portfolio_npv += position_result['value']
            
            # Accumulate Greeks
            for greek, value in position_result.get('greeks', {}).items():
                if greek in portfolio_greeks:
                    portfolio_greeks[greek] += value
        
        return {
            "total_npv": portfolio_npv,
            "position_values": position_values,
            "portfolio_greeks": portfolio_greeks,
            "valuation_date": str(self.valuation_date)
        }
    
    def calculate_position_greeks(self, position: Position, market_data):
        """Calculate Greeks for a single position using bump-and-reval approach"""
        base_value = self._value_position(position, market_data)
        
        greeks = {}
        
        # Calculate Delta (sensitivity to underlying price)
        if position.instrument_type in ['option', 'equity']:
            # Bump underlying price by 1%
            original_underlying = position.underlying
            # In a full implementation, we would adjust market data appropriately
            # For now, we'll return placeholder values
            greeks['delta'] = base_value * 0.5  # Placeholder
            greeks['gamma'] = base_value * 0.1  # Placeholder
        
        # Calculate Vega (sensitivity to volatility)
        if hasattr(market_data, 'vol_surface') and market_data.vol_surface is not None:
            # In a full implementation, bump volatility and revalue
            greeks['vega'] = base_value * 0.01  # Placeholder
        
        # Calculate Theta (sensitivity to time decay)
        greeks['theta'] = -abs(base_value) * 0.001  # Placeholder (typically negative)
        
        # Calculate Rho (sensitivity to interest rates)
        greeks['rho'] = base_value * 0.01  # Placeholder
        
        return greeks
    
    def _value_position_with_greeks(self, position: Position, market_data) -> Dict:
        """Value a single position and calculate its Greeks"""
        value = self._value_position(position, market_data)
        greeks = self.calculate_position_greeks(position, market_data)
        
        return {
            'value': value,
            'greeks': greeks
        }
    
    def _value_position(self, position: Position, market_data) -> float:
        """Value a single position under given market conditions"""
        # This is a simplified valuation - in practice, each instrument type
        # would have its specific valuation logic
        if position.instrument_type == "bond":
            return self._value_bond(position, market_data)
        elif position.instrument_type == "swap":
            return self._value_swap(position, market_data)
        elif position.instrument_type == "option":
            return self._value_option(position, market_data)
        elif position.instrument_type == "equity":
            return self._value_equity(position, market_data)
        else:
            # For unknown instruments, return a simple notional-based value
            return position.quantity * (position.notional or 100.0)
    
    def _value_bond(self, position: Position, market_data) -> float:
        """Value a bond position"""
        # In practice, this would use QuantLib's bond pricing functions
        # with the current yield curve
        if market_data.yield_curve is None:
            return position.quantity * (position.notional or 1000.0)
        
        # Simple bond valuation using the zero rates from the yield curve
        face_amount = position.notional or 1000.0
        coupon_rate = 0.05  # 5% coupon
        
        # For demonstration, we'll calculate a simple present value
        # based on the zero rate from the curve for the bond's maturity
        maturity_years = 5  # For this example
        maturity_date = market_data.base_date + ql.Period(maturity_years, ql.Years)
        
        # Get the zero rate from the yield curve for this maturity
        try:
            zero_rate = market_data.yield_curve.zeroRate(
                maturity_date, 
                ql.Actual365Fixed(), 
                ql.Continuous
            ).rate()
        except:
            # If we can't get the rate for this specific date, use a default
            zero_rate = 0.05  # 5% default rate
        
        # Present value of principal + coupons (simplified)
        pv_principal = face_amount / ((1 + zero_rate) ** maturity_years)
        annual_coupon = face_amount * coupon_rate
        pv_coupons = 0
        for year in range(1, maturity_years + 1):
            pv_coupons += annual_coupon / ((1 + zero_rate) ** year)
        
        npv = pv_principal + pv_coupons
        return position.quantity * npv
    
    def _value_swap(self, position: Position, market_data) -> float:
        """Value an interest rate swap position"""
        # Simplified swap valuation
        # In practice, would use QuantLib's swap pricing
        notional = position.notional or 1000000.0
        return position.quantity * notional * 0.01  # Simplified
    
    def _value_option(self, position: Position, market_data) -> float:
        """Value an option position"""
        # Simplified option valuation
        # In practice, would use Black-Scholes or other models via QuantLib
        if market_data.vol_surface is None:
            return 0.0
        
        # Simplified calculation
        underlying_value = 100.0  # Placeholder
        time_to_expiry = 1.0  # Placeholder
        volatility = 0.20  # Placeholder
        
        # Simplified Black-Scholes (not actual implementation)
        intrinsic_value = max(0, underlying_value - (position.strike or underlying_value))
        time_value = underlying_value * volatility * time_to_expiry * 0.1
        option_value = intrinsic_value + time_value
        
        return position.quantity * option_value
    
    def _value_equity(self, position: Position, market_data) -> float:
        """Value an equity position"""
        # Simplified equity valuation
        # In practice, would get current market price or use other models
        return position.quantity * 100.0  # Placeholder price