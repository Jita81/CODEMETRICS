"""
Error Handling - Following Standardized Modules Framework

This module implements comprehensive error handling patterns for the optimization system,
ensuring robustness and proper error reporting throughout the optimization process.
"""

import logging
import traceback
from typing import Dict, List, Any, Optional, Type, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categories of errors"""
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    AI_ANALYSIS = "ai_analysis"
    GIT_OPERATIONS = "git_operations"
    TESTING = "testing"
    BUSINESS_LOGIC = "business_logic"
    DATA_VALIDATION = "data_validation"
    SYSTEM_RESOURCE = "system_resource"
    TIMEOUT = "timeout"

@dataclass
class OptimizationError:
    """Structured error information"""
    error_id: str
    timestamp: datetime
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any]
    component: str
    request_id: Optional[str] = None
    iteration: Optional[int] = None
    traceback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    resolution_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.resolution_suggestions is None:
            self.resolution_suggestions = []

class OptimizationException(Exception):
    """Base exception for optimization errors"""
    
    def __init__(self, message: str, category: ErrorCategory, severity: ErrorSeverity, 
                 details: Dict[str, Any] = None, component: str = "unknown",
                 resolution_suggestions: List[str] = None):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.component = component
        self.resolution_suggestions = resolution_suggestions or []

class ConfigurationError(OptimizationException):
    """Configuration-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message, 
            ErrorCategory.CONFIGURATION, 
            ErrorSeverity.HIGH,
            details,
            "configuration",
            ["Check configuration file", "Validate environment variables", "Review documentation"]
        )

class AuthenticationError(OptimizationException):
    """Authentication-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            ErrorCategory.AUTHENTICATION,
            ErrorSeverity.HIGH,
            details,
            "authentication",
            ["Check API keys", "Verify token permissions", "Review authentication configuration"]
        )

class NetworkError(OptimizationException):
    """Network-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            ErrorCategory.NETWORK,
            ErrorSeverity.MEDIUM,
            details,
            "network",
            ["Check internet connectivity", "Verify API endpoints", "Review firewall settings"]
        )

class AIAnalysisError(OptimizationException):
    """AI analysis-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            ErrorCategory.AI_ANALYSIS,
            ErrorSeverity.HIGH,
            details,
            "ai_analyzer",
            ["Retry with different parameters", "Check Claude API status", "Reduce input complexity"]
        )

class GitOperationError(OptimizationException):
    """Git operation-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            ErrorCategory.GIT_OPERATIONS,
            ErrorSeverity.MEDIUM,
            details,
            "git_operations",
            ["Check repository permissions", "Verify git configuration", "Review branch status"]
        )

class TestingError(OptimizationException):
    """Testing-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            ErrorCategory.TESTING,
            ErrorSeverity.MEDIUM,
            details,
            "testing",
            ["Review test configuration", "Check test dependencies", "Verify test environment"]
        )

class BusinessLogicError(OptimizationException):
    """Business logic-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            ErrorCategory.BUSINESS_LOGIC,
            ErrorSeverity.HIGH,
            details,
            "business_logic",
            ["Review business rules", "Check input validation", "Verify logic constraints"]
        )

class TimeoutError(OptimizationException):
    """Timeout-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message,
            ErrorCategory.TIMEOUT,
            ErrorSeverity.MEDIUM,
            details,
            "timeout",
            ["Increase timeout value", "Optimize operation", "Use asynchronous processing"]
        )

class ErrorHandler:
    """Centralized error handling for optimization operations"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or self._setup_logger()
        self.error_history: List[OptimizationError] = []
        self.error_handlers: Dict[ErrorCategory, Callable] = {}
        self.recovery_strategies: Dict[ErrorCategory, Callable] = {}
        
        self._setup_default_handlers()
        self._setup_recovery_strategies()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger for error handling"""
        logger = logging.getLogger("optimization_error_handler")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_default_handlers(self):
        """Setup default error handlers"""
        self.error_handlers = {
            ErrorCategory.CONFIGURATION: self._handle_configuration_error,
            ErrorCategory.AUTHENTICATION: self._handle_authentication_error,
            ErrorCategory.NETWORK: self._handle_network_error,
            ErrorCategory.AI_ANALYSIS: self._handle_ai_analysis_error,
            ErrorCategory.GIT_OPERATIONS: self._handle_git_error,
            ErrorCategory.TESTING: self._handle_testing_error,
            ErrorCategory.BUSINESS_LOGIC: self._handle_business_logic_error,
            ErrorCategory.TIMEOUT: self._handle_timeout_error
        }
    
    def _setup_recovery_strategies(self):
        """Setup automatic recovery strategies"""
        self.recovery_strategies = {
            ErrorCategory.NETWORK: self._recover_network_error,
            ErrorCategory.AI_ANALYSIS: self._recover_ai_analysis_error,
            ErrorCategory.TESTING: self._recover_testing_error,
            ErrorCategory.TIMEOUT: self._recover_timeout_error
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> OptimizationError:
        """Handle any error and convert to structured format"""
        
        # Determine error details
        if isinstance(error, OptimizationException):
            category = error.category
            severity = error.severity
            component = error.component
            resolution_suggestions = error.resolution_suggestions
            details = error.details
        else:
            category = self._categorize_error(error)
            severity = self._determine_severity(error, category)
            component = context.get("component", "unknown") if context else "unknown"
            resolution_suggestions = self._generate_resolution_suggestions(error, category)
            details = {"error_type": type(error).__name__}
        
        # Create structured error
        optimization_error = OptimizationError(
            error_id=self._generate_error_id(),
            timestamp=datetime.now(),
            category=category,
            severity=severity,
            message=str(error),
            details=details,
            component=component,
            request_id=context.get("request_id") if context else None,
            iteration=context.get("iteration") if context else None,
            traceback=traceback.format_exc(),
            context=context,
            resolution_suggestions=resolution_suggestions
        )
        
        # Store error
        self.error_history.append(optimization_error)
        
        # Log error
        self._log_error(optimization_error)
        
        # Handle specific error category
        if category in self.error_handlers:
            self.error_handlers[category](optimization_error)
        
        return optimization_error
    
    def attempt_recovery(self, error: OptimizationError, context: Dict[str, Any] = None) -> bool:
        """Attempt automatic recovery from error"""
        
        if error.category in self.recovery_strategies:
            try:
                return self.recovery_strategies[error.category](error, context)
            except Exception as recovery_error:
                self.logger.error(f"Recovery attempt failed: {recovery_error}")
                return False
        
        return False
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on exception type and message"""
        
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Authentication errors
        if any(keyword in error_message for keyword in ["unauthorized", "authentication", "api key", "token"]):
            return ErrorCategory.AUTHENTICATION
        
        # Network errors
        if any(keyword in error_message for keyword in ["connection", "network", "timeout", "unreachable"]):
            return ErrorCategory.NETWORK
        
        # Configuration errors
        if any(keyword in error_message for keyword in ["config", "missing", "invalid", "not found"]):
            return ErrorCategory.CONFIGURATION
        
        # Git errors
        if any(keyword in error_message for keyword in ["git", "repository", "branch", "commit"]):
            return ErrorCategory.GIT_OPERATIONS
        
        # AI Analysis errors
        if any(keyword in error_message for keyword in ["claude", "anthropic", "model", "tokens"]):
            return ErrorCategory.AI_ANALYSIS
        
        # Testing errors
        if any(keyword in error_message for keyword in ["test", "pytest", "coverage"]):
            return ErrorCategory.TESTING
        
        # Timeout errors
        if "timeout" in error_type or "timeout" in error_message:
            return ErrorCategory.TIMEOUT
        
        # Default to system resource
        return ErrorCategory.SYSTEM_RESOURCE
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        
        # Critical errors that stop optimization completely
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.CRITICAL
        
        # High severity errors that significantly impact optimization
        if category in [ErrorCategory.AI_ANALYSIS, ErrorCategory.BUSINESS_LOGIC]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors that may be recoverable
        if category in [ErrorCategory.NETWORK, ErrorCategory.GIT_OPERATIONS, ErrorCategory.TESTING]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        return ErrorSeverity.LOW
    
    def _generate_resolution_suggestions(self, error: Exception, category: ErrorCategory) -> List[str]:
        """Generate resolution suggestions based on error category"""
        
        suggestions_map = {
            ErrorCategory.AUTHENTICATION: [
                "Verify API key is valid and not expired",
                "Check authentication token permissions",
                "Review service account configuration"
            ],
            ErrorCategory.NETWORK: [
                "Check internet connectivity",
                "Verify firewall and proxy settings",
                "Retry operation after brief delay"
            ],
            ErrorCategory.CONFIGURATION: [
                "Review configuration file syntax",
                "Check all required parameters are set",
                "Validate environment variables"
            ],
            ErrorCategory.AI_ANALYSIS: [
                "Retry with reduced input size",
                "Check Claude API service status",
                "Adjust temperature and token limits"
            ],
            ErrorCategory.GIT_OPERATIONS: [
                "Verify repository permissions",
                "Check git configuration",
                "Ensure clean working directory"
            ],
            ErrorCategory.TESTING: [
                "Review test dependencies",
                "Check test environment setup",
                "Verify test data availability"
            ],
            ErrorCategory.TIMEOUT: [
                "Increase timeout duration",
                "Use asynchronous processing",
                "Break down operation into smaller steps"
            ]
        }
        
        return suggestions_map.get(category, ["Review error details and documentation"])
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return f"OPT_ERR_{uuid.uuid4().hex[:8].upper()}"
    
    def _log_error(self, error: OptimizationError):
        """Log error with appropriate level"""
        
        log_message = f"[{error.error_id}] {error.component}: {error.message}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Log context if available
        if error.context:
            self.logger.debug(f"[{error.error_id}] Context: {error.context}")
    
    # Specific error handlers
    def _handle_configuration_error(self, error: OptimizationError):
        """Handle configuration errors"""
        self.logger.critical("Configuration error detected - optimization cannot proceed")
        
    def _handle_authentication_error(self, error: OptimizationError):
        """Handle authentication errors"""
        self.logger.critical("Authentication error - check API keys and permissions")
    
    def _handle_network_error(self, error: OptimizationError):
        """Handle network errors"""
        self.logger.warning("Network error - attempting retry with backoff")
    
    def _handle_ai_analysis_error(self, error: OptimizationError):
        """Handle AI analysis errors"""
        self.logger.error("AI analysis failed - may retry with different parameters")
    
    def _handle_git_error(self, error: OptimizationError):
        """Handle git operation errors"""
        self.logger.warning("Git operation failed - check repository state")
    
    def _handle_testing_error(self, error: OptimizationError):
        """Handle testing errors"""
        self.logger.warning("Testing failed - may affect optimization validation")
    
    def _handle_business_logic_error(self, error: OptimizationError):
        """Handle business logic errors"""
        self.logger.error("Business logic violation - optimization cannot proceed")
    
    def _handle_timeout_error(self, error: OptimizationError):
        """Handle timeout errors"""
        self.logger.warning("Operation timed out - may retry with increased timeout")
    
    # Recovery strategies
    def _recover_network_error(self, error: OptimizationError, context: Dict[str, Any] = None) -> bool:
        """Attempt recovery from network errors"""
        import time
        
        # Simple retry with exponential backoff
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            delay = base_delay * (2 ** attempt)
            self.logger.info(f"Retrying network operation in {delay} seconds (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
            
            # In real implementation, would retry the original operation
            # For now, simulate success after retries
            if attempt == max_retries - 1:
                return True
        
        return False
    
    def _recover_ai_analysis_error(self, error: OptimizationError, context: Dict[str, Any] = None) -> bool:
        """Attempt recovery from AI analysis errors"""
        
        # Try with reduced parameters
        if "token" in error.message.lower():
            self.logger.info("Reducing token limit and retrying AI analysis")
            # In real implementation, would retry with reduced tokens
            return True
        
        return False
    
    def _recover_testing_error(self, error: OptimizationError, context: Dict[str, Any] = None) -> bool:
        """Attempt recovery from testing errors"""
        
        # Skip non-critical tests and continue
        if error.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]:
            self.logger.info("Skipping failed test and continuing optimization")
            return True
        
        return False
    
    def _recover_timeout_error(self, error: OptimizationError, context: Dict[str, Any] = None) -> bool:
        """Attempt recovery from timeout errors"""
        
        # Increase timeout and retry
        self.logger.info("Increasing timeout duration and retrying")
        # In real implementation, would retry with increased timeout
        return True
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors encountered"""
        
        if not self.error_history:
            return {"total_errors": 0, "message": "No errors recorded"}
        
        # Count errors by category and severity
        category_counts = {}
        severity_counts = {}
        
        for error in self.error_history:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        recent_errors = sorted(self.error_history, key=lambda e: e.timestamp, reverse=True)[:5]
        
        return {
            "total_errors": len(self.error_history),
            "category_distribution": category_counts,
            "severity_distribution": severity_counts,
            "recent_errors": [
                {
                    "error_id": error.error_id,
                    "timestamp": error.timestamp.isoformat(),
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "message": error.message,
                    "component": error.component
                }
                for error in recent_errors
            ]
        }

# Decorator for automatic error handling
def handle_optimization_errors(error_handler: ErrorHandler = None):
    """Decorator to automatically handle optimization errors"""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            handler = error_handler or ErrorHandler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                optimization_error = handler.handle_error(e, context)
                
                # Attempt recovery
                if handler.attempt_recovery(optimization_error, context):
                    # If recovery successful, retry once
                    try:
                        return func(*args, **kwargs)
                    except Exception as retry_error:
                        handler.handle_error(retry_error, context)
                        raise
                else:
                    raise
        
        return wrapper
    return decorator
