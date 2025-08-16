"""
Domain Entities - Following Standardized Modules Framework

This module defines the core domain entities for the optimization system,
representing the business objects and their relationships.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

class OptimizationStatus(Enum):
    """Status enumeration for optimizations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ComponentType(Enum):
    """Types of ecosystem components"""
    FRAMEWORK = "framework"
    CODECREATE = "codecreate"
    CODEREVIEW = "codereview"
    CODETEST = "codetest"
    CODEMETRICS = "codemetrics"

class IssueType(Enum):
    """Types of issues that can be optimized"""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    RELIABILITY = "reliability"
    USABILITY = "usability"
    INTEGRATION = "integration"
    SECURITY = "security"

@dataclass
class OptimizationPattern:
    """Represents an identified optimization pattern"""
    pattern_id: str
    component: ComponentType
    issue_type: IssueType
    frequency: float
    impact_score: float
    confidence: float
    description: str
    suggested_optimization: str
    root_cause_analysis: Dict[str, Any]
    business_impact: str
    estimated_effort: str
    prerequisites: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizationPattern':
        """Create OptimizationPattern from dictionary"""
        return cls(
            pattern_id=data.get("pattern_id", ""),
            component=ComponentType(data.get("component", "unknown")),
            issue_type=IssueType(data.get("issue_type", "performance")),
            frequency=data.get("frequency", 0.0),
            impact_score=data.get("impact_score", 0.0),
            confidence=data.get("confidence", 0.0),
            description=data.get("description", ""),
            suggested_optimization=data.get("suggested_optimization", ""),
            root_cause_analysis=data.get("root_cause_analysis", {}),
            business_impact=data.get("business_impact", ""),
            estimated_effort=data.get("estimated_effort", "unknown"),
            prerequisites=data.get("prerequisites", []),
            risks=data.get("risks", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert OptimizationPattern to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "component": self.component.value,
            "issue_type": self.issue_type.value,
            "frequency": self.frequency,
            "impact_score": self.impact_score,
            "confidence": self.confidence,
            "description": self.description,
            "suggested_optimization": self.suggested_optimization,
            "root_cause_analysis": self.root_cause_analysis,
            "business_impact": self.business_impact,
            "estimated_effort": self.estimated_effort,
            "prerequisites": self.prerequisites,
            "risks": self.risks,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class OptimizationStrategy:
    """Represents a strategy for implementing an optimization"""
    strategy_id: str
    pattern_id: str
    approach: str
    implementation_steps: List[str]
    files_to_modify: List[Dict[str, str]]
    configuration_changes: List[Dict[str, Any]]
    workflow_changes: List[Dict[str, str]]
    testing_strategy: Dict[str, Any]
    rollback_plan: str
    estimated_duration: int  # in minutes
    resource_requirements: List[str]
    success_criteria: List[str]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class OptimizationIteration:
    """Represents a single optimization iteration"""
    iteration_id: str
    request_id: str
    iteration_number: int
    pattern: OptimizationPattern
    strategy: OptimizationStrategy
    branch_name: str
    status: OptimizationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    test_results: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    success_score: float = 0.0

@dataclass
class OptimizationResult:
    """Represents the final result of an optimization"""
    result_id: str
    request_id: str
    iteration: int
    pattern: OptimizationPattern
    strategy: Dict[str, Any]
    test_results: Dict[str, Any]
    success_score: float
    branch_name: str
    timestamp: datetime
    recommendations: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert OptimizationResult to dictionary"""
        return {
            "result_id": getattr(self, 'result_id', f"result_{self.iteration}"),
            "request_id": getattr(self, 'request_id', ''),
            "iteration": self.iteration,
            "pattern": self.pattern.to_dict() if hasattr(self.pattern, 'to_dict') else self.pattern,
            "strategy": self.strategy,
            "test_results": self.test_results,
            "success_score": self.success_score,
            "branch_name": self.branch_name,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "recommendations": getattr(self, 'recommendations', []),
            "lessons_learned": getattr(self, 'lessons_learned', [])
        }

@dataclass
class BusinessRule:
    """Represents a business rule for optimization validation"""
    name: str
    description: str
    validator: Callable[[Dict[str, Any]], bool]
    priority: int = 1  # 1 = highest priority
    category: str = "general"
    error_message: str = ""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data against this business rule"""
        try:
            return self.validator(data)
        except Exception:
            return False

@dataclass
class OptimizationThreshold:
    """Represents thresholds for optimization success criteria"""
    name: str
    minimum_value: float
    target_value: float
    maximum_value: float
    unit: str = ""
    description: str = ""

@dataclass
class EcosystemHealth:
    """Represents the overall health of the ecosystem"""
    timestamp: datetime
    overall_score: float
    component_scores: Dict[ComponentType, float]
    active_patterns: List[OptimizationPattern]
    recent_optimizations: List[OptimizationResult]
    performance_trends: Dict[str, List[float]]
    recommendations: List[str]
    alerts: List[str]

@dataclass
class OptimizationMetrics:
    """Represents metrics for optimization tracking"""
    total_optimizations: int = 0
    successful_optimizations: int = 0
    average_success_score: float = 0.0
    average_performance_improvement: float = 0.0
    component_performance: Dict[str, float] = field(default_factory=dict)
    optimization_frequency: Dict[str, int] = field(default_factory=dict)
    time_to_optimization: Dict[str, float] = field(default_factory=dict)
    business_impact_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuditEntry:
    """Represents an audit trail entry"""
    entry_id: str
    request_id: str
    timestamp: datetime
    action: str
    actor: str  # system, user, ai
    details: Dict[str, Any]
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None

@dataclass
class OptimizationConfiguration:
    """Configuration for optimization engine"""
    max_iterations: int = 10
    timeout_minutes: int = 60
    parallel_optimizations: int = 3
    success_threshold: float = 0.7
    performance_threshold: float = 0.05
    quality_threshold: float = 0.70
    test_coverage_requirement: float = 0.70
    enabled_components: List[ComponentType] = field(default_factory=lambda: list(ComponentType))
    business_rules_enabled: bool = True
    audit_trail_enabled: bool = True
    notifications_enabled: bool = True
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        if self.max_iterations <= 0:
            errors.append("max_iterations must be positive")
        
        if self.timeout_minutes <= 0:
            errors.append("timeout_minutes must be positive")
        
        if not 0 <= self.success_threshold <= 1:
            errors.append("success_threshold must be between 0 and 1")
        
        if not 0 <= self.performance_threshold <= 1:
            errors.append("performance_threshold must be between 0 and 1")
        
        if not 0 <= self.quality_threshold <= 1:
            errors.append("quality_threshold must be between 0 and 1")
        
        return errors

@dataclass 
class ComponentFeedback:
    """Represents feedback data from an ecosystem component"""
    component: ComponentType
    timestamp: datetime
    performance_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    error_logs: List[str]
    usage_statistics: Dict[str, Any]
    user_feedback: List[str]
    health_score: float
    issues_identified: List[str]
    suggestions: List[str]

@dataclass
class OptimizationReport:
    """Comprehensive report for optimization results"""
    report_id: str
    request_id: str
    generation_time: datetime
    summary: Dict[str, Any]
    detailed_results: List[OptimizationResult]
    business_impact_analysis: Dict[str, Any]
    recommendations: List[str]
    lessons_learned: List[str]
    next_steps: List[str]
    appendices: Dict[str, Any] = field(default_factory=dict)
