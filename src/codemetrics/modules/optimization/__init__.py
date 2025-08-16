"""
Optimization Module - Following Standardized Modules Framework

This module implements the Intelligent Ecosystem Optimization Engine using proper
modular architecture with separated concerns, dependency injection, and comprehensive
business logic encapsulation.

Architecture Components:
- module_interface.py: Interface contracts and protocols
- module_implementation.py: Main implementation with dependency injection
- business_logic.py: Core business rules and logic
- domain_entities.py: Business objects and data structures
- audit_trail.py: Comprehensive audit and compliance tracking
- error_handling.py: Robust error handling and recovery
"""

from .module_interface import (
    IOptimizationEngine,
    IFeedbackCollector,
    IPatternAnalyzer,
    IOptimizationGenerator,
    IOptimizationTester,
    IAuditTrail,
    OptimizationRequest,
    OptimizationResponse,
    FeedbackAnalysisRequest,
    FeedbackAnalysisResponse
)

from .module_implementation import (
    OptimizationEngine,
    OptimizationEngineFactory
)

from .business_logic import OptimizationBusinessLogic

from .domain_entities import (
    OptimizationPattern,
    OptimizationStrategy,
    OptimizationIteration,
    OptimizationResult,
    BusinessRule,
    OptimizationThreshold,
    EcosystemHealth,
    OptimizationMetrics,
    AuditEntry,
    OptimizationConfiguration,
    ComponentFeedback,
    OptimizationReport,
    OptimizationStatus,
    ComponentType,
    IssueType
)

from .audit_trail import (
    DatabaseAuditTrail,
    FileAuditTrail,
    AuditTrailManager
)

from .error_handling import (
    ErrorHandler,
    OptimizationException,
    ConfigurationError,
    AuthenticationError,
    NetworkError,
    AIAnalysisError,
    GitOperationError,
    TestingError,
    BusinessLogicError,
    TimeoutError,
    ErrorSeverity,
    ErrorCategory,
    handle_optimization_errors
)

# Version and metadata
__version__ = "1.0.0"
__author__ = "Automated Agile Framework Team"
__description__ = "Intelligent Ecosystem Optimization Engine with Modular Architecture"

# Public API
__all__ = [
    # Core interfaces
    "IOptimizationEngine",
    "IFeedbackCollector", 
    "IPatternAnalyzer",
    "IOptimizationGenerator",
    "IOptimizationTester",
    "IAuditTrail",
    
    # Request/Response objects
    "OptimizationRequest",
    "OptimizationResponse",
    "FeedbackAnalysisRequest",
    "FeedbackAnalysisResponse",
    
    # Main implementation
    "OptimizationEngine",
    "OptimizationEngineFactory",
    
    # Business logic
    "OptimizationBusinessLogic",
    
    # Domain entities
    "OptimizationPattern",
    "OptimizationStrategy", 
    "OptimizationIteration",
    "OptimizationResult",
    "BusinessRule",
    "OptimizationThreshold",
    "EcosystemHealth",
    "OptimizationMetrics",
    "AuditEntry",
    "OptimizationConfiguration",
    "ComponentFeedback",
    "OptimizationReport",
    "OptimizationStatus",
    "ComponentType",
    "IssueType",
    
    # Audit trail
    "DatabaseAuditTrail",
    "FileAuditTrail", 
    "AuditTrailManager",
    
    # Error handling
    "ErrorHandler",
    "OptimizationException",
    "ConfigurationError",
    "AuthenticationError",
    "NetworkError",
    "AIAnalysisError",
    "GitOperationError",
    "TestingError",
    "BusinessLogicError",
    "TimeoutError",
    "ErrorSeverity",
    "ErrorCategory",
    "handle_optimization_errors"
]

# Module configuration
OPTIMIZATION_MODULE_CONFIG = {
    "name": "optimization",
    "version": __version__,
    "description": __description__,
    "architecture": "standardized_modules_framework_v1.0.0",
    "components": {
        "interface": "module_interface.py",
        "implementation": "module_implementation.py", 
        "business_logic": "business_logic.py",
        "domain_entities": "domain_entities.py",
        "audit_trail": "audit_trail.py",
        "error_handling": "error_handling.py"
    },
    "patterns": [
        "dependency_injection",
        "factory_pattern",
        "strategy_pattern",
        "observer_pattern",
        "command_pattern"
    ],
    "compliance": {
        "business_rules": True,
        "audit_trail": True,
        "error_handling": True,
        "testing": True,
        "documentation": True
    }
}
