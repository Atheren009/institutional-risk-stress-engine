"""
Regulatory Stress Testing Engine - Main Entry Point
"""
from .src.engine import StressTestEngine
from .src.market_data import MarketData
from .src.scenarios import Scenario, ScenarioManager
from .src.portfolio import Portfolio, Position

__version__ = "1.0.0"
__author__ = "Quantitative Risk Team"