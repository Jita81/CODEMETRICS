"""
CodeMetrics - AI-Powered Development Analytics

Part of the Automated Agile Framework Ecosystem
"""

__version__ = "1.0.0"
__author__ = "Automated Agile Framework Team"
__email__ = "support@automatedagile.dev"

from .analyzer import MetricsAnalyzer
from .collector import DataCollector
from .dashboard import Dashboard
from .config import Config
from .optimizer import IntelligentOptimizer

__all__ = [
    "MetricsAnalyzer",
    "DataCollector", 
    "Dashboard",
    "Config",
    "IntelligentOptimizer"
]
