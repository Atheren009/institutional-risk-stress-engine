"""
Data Validation Module for Stress Testing Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import warnings


class DataValidator:
    """Validates market data, portfolio data, and scenario parameters"""
    
    @staticmethod
    def validate_market_data(data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate market data DataFrame"""
        issues = []
        
        if data.empty:
            issues.append("Market data is empty")
            return False, issues
        
        # Check required columns based on data type
        if 'rate' in data.columns and 'tenor' in data.columns:
            # Yield curve data validation
            if not DataValidator._validate_rate_data(data):
                issues.extend(DataValidator._validate_rate_data(data, return_issues=True))
        
        if 'strike' in data.columns and 'maturity' in data.columns and 'volatility' in data.columns:
            # Vol surface data validation
            if not DataValidator._validate_vol_data(data):
                issues.extend(DataValidator._validate_vol_data(data, return_issues=True))
        
        if 'issuer' in data.columns and 'spread' in data.columns:
            # Credit data validation
            if not DataValidator._validate_credit_data(data):
                issues.extend(DataValidator._validate_credit_data(data, return_issues=True))
        
        return len(issues) == 0, issues
    
    @staticmethod
    def _validate_rate_data(data: pd.DataFrame, return_issues=False) -> Any:
        """Validate yield curve data"""
        issues = []
        
        if 'tenor' not in data.columns:
            issues.append("Missing 'tenor' column in rate data")
        if 'rate' not in data.columns:
            issues.append("Missing 'rate' column in rate data")
        
        if 'rate' in data.columns:
            invalid_rates = data[data['rate'].isna() | (data['rate'] < -0.1) | (data['rate'] > 1.0)]
            if not invalid_rates.empty:
                issues.append(f"Found {len(invalid_rates)} invalid rate values (should be between -0.1 and 1.0)")
        
        if 'tenor' in data.columns:
            invalid_tenors = data[data['tenor'].isna()]
            if not invalid_tenors.empty:
                issues.append(f"Found {len(invalid_tenors)} missing tenor values")
        
        if return_issues:
            return issues
        return len(issues) == 0
    
    @staticmethod
    def _validate_vol_data(data: pd.DataFrame, return_issues=False) -> Any:
        """Validate volatility surface data"""
        issues = []
        
        if 'strike' not in data.columns:
            issues.append("Missing 'strike' column in vol data")
        if 'maturity' not in data.columns:
            issues.append("Missing 'maturity' column in vol data")
        if 'volatility' not in data.columns:
            issues.append("Missing 'volatility' column in vol data")
        
        if 'volatility' in data.columns:
            invalid_vols = data[data['volatility'].isna() | (data['volatility'] < 0.001) | (data['volatility'] > 5.0)]
            if not invalid_vols.empty:
                issues.append(f"Found {len(invalid_vols)} invalid volatility values (should be between 0.001 and 5.0)")
        
        if return_issues:
            return issues
        return len(issues) == 0
    
    @staticmethod
    def _validate_credit_data(data: pd.DataFrame, return_issues=False) -> Any:
        """Validate credit spread data"""
        issues = []
        
        if 'issuer' not in data.columns:
            issues.append("Missing 'issuer' column in credit data")
        if 'spread' not in data.columns:
            issues.append("Missing 'spread' column in credit data")
        
        if 'spread' in data.columns:
            invalid_spreads = data[data['spread'].isna() | (data['spread'] < 0) | (data['spread'] > 0.5)]
            if not invalid_spreads.empty:
                issues.append(f"Found {len(invalid_spreads)} invalid spread values (should be between 0 and 0.5)")
        
        if return_issues:
            return issues
        return len(issues) == 0
    
    @staticmethod
    def validate_portfolio_data(data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate portfolio data DataFrame"""
        issues = []
        
        if data.empty:
            issues.append("Portfolio data is empty")
            return False, issues
        
        required_columns = ['id', 'instrument_type', 'quantity', 'underlying']
        for col in required_columns:
            if col not in data.columns:
                issues.append(f"Missing required column: {col}")
        
        if 'quantity' in data.columns:
            invalid_quantities = data[data['quantity'].isna() | (data['quantity'] <= 0)]
            if not invalid_quantities.empty:
                issues.append(f"Found {len(invalid_quantities)} invalid quantity values (should be positive)")
        
        if 'instrument_type' in data.columns:
            valid_types = ['bond', 'swap', 'option', 'equity', 'future', 'forward']
            invalid_types = data[~data['instrument_type'].isin(valid_types)]
            if not invalid_types.empty:
                issues.append(f"Found {len(invalid_types)} invalid instrument types")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_scenario_params(scenario_type: str, params: Dict) -> Tuple[bool, List[str]]:
        """Validate scenario parameters"""
        issues = []
        
        if scenario_type == "parallel":
            if "shift_bp" not in params:
                issues.append("Missing 'shift_bp' parameter for parallel scenario")
            else:
                shift = params["shift_bp"]
                if not isinstance(shift, (int, float)) or abs(shift) > 10000:  # More than 100%
                    issues.append("'shift_bp' should be a reasonable value between -10000 and 10000")
        
        elif scenario_type == "steepener":
            required_params = ["short_shift_bp", "long_shift_bp"]
            for param in required_params:
                if param not in params:
                    issues.append(f"Missing '{param}' parameter for steepener scenario")
                elif not isinstance(params[param], (int, float)):
                    issues.append(f"'{param}' should be numeric")
        
        elif scenario_type == "key_rate":
            if "key_tenors" not in params or "key_shifts_bp" not in params:
                issues.append("Missing 'key_tenors' or 'key_shifts_bp' parameters for key_rate scenario")
            elif len(params["key_tenors"]) != len(params["key_shifts_bp"]):
                issues.append("'key_tenors' and 'key_shifts_bp' should have the same length")
        
        elif scenario_type == "vol_uniform":
            if "vol_shift" not in params:
                issues.append("Missing 'vol_shift' parameter for vol_uniform scenario")
            else:
                vol_shift = params["vol_shift"]
                if not isinstance(vol_shift, (int, float)) or vol_shift < -1 or vol_shift > 5:
                    issues.append("'vol_shift' should be between -1 and 5")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_valuation_results(results: Dict) -> Tuple[bool, List[str]]:
        """Validate valuation results"""
        issues = []
        
        if 'total_npv' not in results:
            issues.append("Missing 'total_npv' in valuation results")
        
        if 'position_values' not in results:
            issues.append("Missing 'position_values' in valuation results")
        
        if 'valuation_date' not in results:
            issues.append("Missing 'valuation_date' in valuation results")
        
        # Check for reasonable NPV values
        total_npv = results.get('total_npv', 0)
        if abs(total_npv) > 1e15:  # Unreasonably large value
            issues.append(f"Total NPV ({total_npv}) seems unreasonably large")
        
        return len(issues) == 0, issues


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass