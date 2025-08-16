"""
Optimization Module Interface - Following Standardized Modules Framework

This module defines the interface contract for the Intelligent Ecosystem Optimization Engine,
adhering to the modular architecture principles of the Standardized Modules Framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OptimizationRequest:
    """Request object for optimization operations"""
    request_id: str
    components: List[str]
    max_iterations: int
    priority_level: str
    requester: str
    timestamp: datetime
    configuration: Dict[str, Any]

@dataclass
class OptimizationResponse:
    """Response object for optimization operations"""
    request_id: str
    status: str
    results: List[Dict[str, Any]]
    success_count: int
    failure_count: int
    total_duration: float
    recommendations: List[str]
    audit_trail: List[Dict[str, Any]]

@dataclass
class FeedbackAnalysisRequest:
    """Request object for feedback analysis"""
    request_id: str
    components: List[str]
    time_range: Dict[str, datetime]
    analysis_depth: str
    filters: Dict[str, Any]

@dataclass
class FeedbackAnalysisResponse:
    """Response object for feedback analysis"""
    request_id: str
    patterns: List[Dict[str, Any]]
    insights: List[str]
    confidence_scores: Dict[str, float]
    recommendations: List[str]

class IOptimizationEngine(ABC):
    """Interface for optimization engine implementations"""
    
    @abstractmethod
    async def analyze_feedback_patterns(self, request: FeedbackAnalysisRequest) -> FeedbackAnalysisResponse:
        """Analyze ecosystem feedback patterns"""
        pass
    
    @abstractmethod
    async def optimize_ecosystem(self, request: OptimizationRequest) -> OptimizationResponse:
        """Run ecosystem optimization with multiple iterations"""
        pass
    
    @abstractmethod
    async def validate_optimization(self, optimization_id: str) -> Dict[str, Any]:
        """Validate optimization results"""
        pass
    
    @abstractmethod
    def get_optimization_status(self, request_id: str) -> Dict[str, Any]:
        """Get status of ongoing optimization"""
        pass

class IFeedbackCollector(ABC):
    """Interface for feedback collection from ecosystem components"""
    
    @abstractmethod
    async def collect_component_feedback(self, component: str, time_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Collect feedback from a specific component"""
        pass
    
    @abstractmethod
    async def aggregate_ecosystem_feedback(self, components: List[str]) -> Dict[str, Any]:
        """Aggregate feedback across multiple components"""
        pass

class IPatternAnalyzer(ABC):
    """Interface for AI-powered pattern analysis"""
    
    @abstractmethod
    async def identify_patterns(self, feedback_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization patterns using Claude"""
        pass
    
    @abstractmethod
    async def prioritize_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize patterns by impact and feasibility"""
        pass

class IOptimizationGenerator(ABC):
    """Interface for generating optimization strategies"""
    
    @abstractmethod
    async def generate_optimization_strategy(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization strategy for a pattern"""
        pass
    
    @abstractmethod
    async def create_optimization_branch(self, strategy: Dict[str, Any]) -> str:
        """Create git branch with optimization changes"""
        pass

class IOptimizationTester(ABC):
    """Interface for testing optimization strategies"""
    
    @abstractmethod
    async def test_optimization(self, branch_name: str, component: str) -> Dict[str, Any]:
        """Test optimization in isolated environment"""
        pass
    
    @abstractmethod
    async def measure_performance_impact(self, baseline: Dict[str, Any], optimized: Dict[str, Any]) -> Dict[str, Any]:
        """Measure performance impact of optimization"""
        pass

class IAuditTrail(ABC):
    """Interface for optimization audit trail"""
    
    @abstractmethod
    def log_optimization_start(self, request: OptimizationRequest) -> str:
        """Log start of optimization process"""
        pass
    
    @abstractmethod
    def log_pattern_identification(self, request_id: str, patterns: List[Dict[str, Any]]) -> None:
        """Log identified patterns"""
        pass
    
    @abstractmethod
    def log_optimization_attempt(self, request_id: str, attempt: Dict[str, Any]) -> None:
        """Log optimization attempt"""
        pass
    
    @abstractmethod
    def log_optimization_result(self, request_id: str, result: Dict[str, Any]) -> None:
        """Log optimization result"""
        pass
    
    @abstractmethod
    def get_audit_history(self, request_id: str) -> List[Dict[str, Any]]:
        """Get audit history for request"""
        pass

# Type protocols for dependency injection
class OptimizationConfig(Protocol):
    """Configuration protocol for optimization module"""
    anthropic_api_key: str
    github_token: str
    model: str
    max_tokens: int
    temperature: float
    max_iterations: int
    optimization_timeout: int
    test_timeout: int

class OptimizationMetrics(Protocol):
    """Metrics protocol for optimization tracking"""
    def record_optimization_start(self, request_id: str) -> None: ...
    def record_optimization_complete(self, request_id: str, duration: float, success: bool) -> None: ...
    def record_pattern_found(self, pattern_type: str, confidence: float) -> None: ...
    def record_test_result(self, component: str, success: bool, duration: float) -> None: ...

class OptimizationNotifications(Protocol):
    """Notifications protocol for optimization events"""
    def notify_optimization_start(self, request: OptimizationRequest) -> None: ...
    def notify_optimization_complete(self, response: OptimizationResponse) -> None: ...
    def notify_critical_pattern(self, pattern: Dict[str, Any]) -> None: ...
    def notify_optimization_failure(self, request_id: str, error: str) -> None: ...
