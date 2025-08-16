"""
Optimization Business Logic - Following Standardized Modules Framework

This module contains the core business rules and logic for ecosystem optimization,
separated from implementation details according to the modular architecture.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

from .domain_entities import OptimizationPattern, BusinessRule, OptimizationThreshold

class OptimizationBusinessLogic:
    """Core business logic for ecosystem optimization"""
    
    def __init__(self, config):
        self.config = config
        self.business_rules = self._initialize_business_rules()
        self.optimization_thresholds = self._initialize_optimization_thresholds()
    
    def _initialize_business_rules(self) -> List[BusinessRule]:
        """Initialize business rules for optimization"""
        return [
            BusinessRule(
                name="minimum_confidence_threshold",
                description="Patterns must have confidence > 0.7",
                validator=lambda pattern: pattern.get("confidence", 0) > 0.7
            ),
            BusinessRule(
                name="minimum_impact_score",
                description="Patterns must have impact score > 0.5", 
                validator=lambda pattern: pattern.get("impact_score", 0) > 0.5
            ),
            BusinessRule(
                name="frequency_threshold",
                description="Issues must occur > 5% of the time",
                validator=lambda pattern: pattern.get("frequency", 0) > 0.05
            ),
            BusinessRule(
                name="no_critical_component_risk",
                description="Must not risk critical production components",
                validator=lambda pattern: not self._is_critical_component_risk(pattern)
            ),
            BusinessRule(
                name="test_coverage_requirement",
                description="Component must have adequate test coverage",
                validator=lambda pattern: self._has_adequate_test_coverage(pattern)
            )
        ]
    
    def _initialize_optimization_thresholds(self) -> Dict[str, OptimizationThreshold]:
        """Initialize optimization success thresholds"""
        return {
            "performance": OptimizationThreshold(
                name="performance_improvement",
                minimum_value=0.05,  # 5% minimum improvement
                target_value=0.20,   # 20% target improvement
                maximum_value=1.0    # 100% maximum improvement
            ),
            "quality": OptimizationThreshold(
                name="quality_score",
                minimum_value=0.70,  # 70% minimum quality
                target_value=0.85,   # 85% target quality
                maximum_value=1.0    # 100% maximum quality
            ),
            "reliability": OptimizationThreshold(
                name="test_success_rate",
                minimum_value=0.80,  # 80% minimum success rate
                target_value=0.95,   # 95% target success rate
                maximum_value=1.0    # 100% maximum success rate
            )
        }
    
    def filter_patterns_by_business_rules(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter patterns based on business rules"""
        filtered_patterns = []
        
        for pattern in patterns:
            if self._pattern_meets_business_rules(pattern):
                filtered_patterns.append(pattern)
        
        return filtered_patterns
    
    def _pattern_meets_business_rules(self, pattern: Dict[str, Any]) -> bool:
        """Check if pattern meets all business rules"""
        for rule in self.business_rules:
            if not rule.validator(pattern):
                return False
        return True
    
    def _is_critical_component_risk(self, pattern: Dict[str, Any]) -> bool:
        """Check if optimization poses risk to critical components"""
        critical_components = ["authentication", "payment", "security", "data_storage"]
        component = pattern.get("component", "").lower()
        optimization_type = pattern.get("suggested_optimization", "").lower()
        
        # High-risk optimizations on critical components
        high_risk_operations = ["delete", "remove", "disable", "bypass"]
        
        if any(critical in component for critical in critical_components):
            if any(risk_op in optimization_type for risk_op in high_risk_operations):
                return True
        
        return False
    
    def _has_adequate_test_coverage(self, pattern: Dict[str, Any]) -> bool:
        """Check if component has adequate test coverage"""
        component = pattern.get("component", "")
        
        # Business rule: Components must have > 70% test coverage for optimization
        min_coverage = 0.70
        
        # In real implementation, this would query actual test coverage
        # For now, simulate based on component type
        coverage_simulation = {
            "codecreate": 0.85,
            "codereview": 0.92,
            "codetest": 0.89,
            "framework": 0.78
        }
        
        current_coverage = coverage_simulation.get(component.lower(), 0.60)
        return current_coverage >= min_coverage
    
    def generate_pattern_insights(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Generate business insights from patterns"""
        insights = []
        
        if not patterns:
            return ["No significant patterns identified for optimization"]
        
        # Analyze pattern distribution by component
        component_counts = {}
        total_impact = 0
        
        for pattern in patterns:
            component = pattern.get("component", "unknown")
            component_counts[component] = component_counts.get(component, 0) + 1
            total_impact += pattern.get("impact_score", 0)
        
        # Generate insights
        most_affected_component = max(component_counts, key=component_counts.get)
        insights.append(f"Most optimization opportunities in {most_affected_component} ({component_counts[most_affected_component]} patterns)")
        
        avg_impact = total_impact / len(patterns) if patterns else 0
        insights.append(f"Average impact score: {avg_impact:.2f} - {'High' if avg_impact > 0.7 else 'Medium' if avg_impact > 0.5 else 'Low'} priority")
        
        # Analyze issue types
        issue_types = {}
        for pattern in patterns:
            issue_type = pattern.get("issue_type", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        if issue_types:
            top_issue = max(issue_types, key=issue_types.get)
            insights.append(f"Primary issue type: {top_issue} ({issue_types[top_issue]} occurrences)")
        
        # Business impact assessment
        high_impact_patterns = [p for p in patterns if p.get("impact_score", 0) > 0.8]
        if high_impact_patterns:
            insights.append(f"Critical: {len(high_impact_patterns)} high-impact patterns require immediate attention")
        
        return insights
    
    def generate_pattern_recommendations(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Generate business recommendations from patterns"""
        recommendations = []
        
        if not patterns:
            return ["Continue monitoring ecosystem health"]
        
        # Priority-based recommendations
        high_priority = [p for p in patterns if p.get("impact_score", 0) > 0.8 and p.get("frequency", 0) > 0.2]
        medium_priority = [p for p in patterns if p.get("impact_score", 0) > 0.6 and p.get("frequency", 0) > 0.1]
        
        if high_priority:
            recommendations.append(f"URGENT: Address {len(high_priority)} critical optimization opportunities immediately")
            for pattern in high_priority[:3]:  # Top 3 critical
                recommendations.append(f"• {pattern.get('component', 'Unknown')}: {pattern.get('suggested_optimization', 'Optimize')}")
        
        if medium_priority:
            recommendations.append(f"Schedule {len(medium_priority)} medium-priority optimizations for next sprint")
        
        # Component-specific recommendations
        component_recommendations = self._generate_component_recommendations(patterns)
        recommendations.extend(component_recommendations)
        
        # Business process recommendations
        if len(patterns) > 10:
            recommendations.append("Consider increasing optimization frequency due to high pattern volume")
        
        return recommendations
    
    def _generate_component_recommendations(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Generate component-specific recommendations"""
        recommendations = []
        
        # Group patterns by component
        component_patterns = {}
        for pattern in patterns:
            component = pattern.get("component", "unknown")
            if component not in component_patterns:
                component_patterns[component] = []
            component_patterns[component].append(pattern)
        
        # Generate recommendations per component
        for component, comp_patterns in component_patterns.items():
            if len(comp_patterns) >= 3:
                avg_impact = statistics.mean([p.get("impact_score", 0) for p in comp_patterns])
                recommendations.append(f"{component.title()}: {len(comp_patterns)} patterns, avg impact {avg_impact:.2f} - needs architectural review")
        
        return recommendations
    
    def calculate_pattern_confidence(self, patterns: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate confidence scores for pattern analysis"""
        if not patterns:
            return {"overall": 0.0}
        
        confidence_scores = {}
        
        # Overall confidence
        individual_confidences = [p.get("confidence", 0) for p in patterns]
        confidence_scores["overall"] = statistics.mean(individual_confidences)
        
        # Component-specific confidence
        component_confidences = {}
        for pattern in patterns:
            component = pattern.get("component", "unknown")
            if component not in component_confidences:
                component_confidences[component] = []
            component_confidences[component].append(pattern.get("confidence", 0))
        
        for component, confidences in component_confidences.items():
            confidence_scores[f"{component}_confidence"] = statistics.mean(confidences)
        
        # Pattern type confidence
        type_confidences = {}
        for pattern in patterns:
            issue_type = pattern.get("issue_type", "unknown")
            if issue_type not in type_confidences:
                type_confidences[issue_type] = []
            type_confidences[issue_type].append(pattern.get("confidence", 0))
        
        for issue_type, confidences in type_confidences.items():
            confidence_scores[f"{issue_type}_confidence"] = statistics.mean(confidences)
        
        return confidence_scores
    
    def validate_optimization_result(self, pattern: Dict[str, Any], strategy: Dict[str, Any], test_results: Dict[str, Any]) -> bool:
        """Validate optimization result against business rules"""
        
        # Check if tests passed
        if not test_results.get("tests_passed", False):
            return False
        
        # Check performance improvement threshold
        performance_improvement = test_results.get("performance_improvement", 0)
        if performance_improvement < self.optimization_thresholds["performance"].minimum_value:
            return False
        
        # Check quality threshold
        quality_score = test_results.get("quality_score", 0)
        if quality_score < self.optimization_thresholds["quality"].minimum_value:
            return False
        
        # Check reliability threshold
        test_success_rate = test_results.get("test_success_rate", test_results.get("tests_passed", 0))
        if isinstance(test_success_rate, bool):
            test_success_rate = 1.0 if test_success_rate else 0.0
        
        if test_success_rate < self.optimization_thresholds["reliability"].minimum_value:
            return False
        
        # Check for regressions
        if self._has_performance_regression(test_results):
            return False
        
        return True
    
    def _has_performance_regression(self, test_results: Dict[str, Any]) -> bool:
        """Check for performance regressions"""
        # Business rule: No performance metric should degrade by more than 5%
        max_acceptable_regression = -0.05
        
        performance_metrics = ["response_time", "memory_usage", "cpu_utilization", "error_rate"]
        
        for metric in performance_metrics:
            if metric in test_results:
                change = test_results[metric]
                if isinstance(change, (int, float)) and change < max_acceptable_regression:
                    return True
        
        return False
    
    def calculate_success_score(self, pattern: Dict[str, Any], test_results: Dict[str, Any]) -> float:
        """Calculate weighted success score for optimization"""
        
        # Weight factors based on business priorities
        weights = {
            "performance": 0.40,  # Performance improvements are highest priority
            "quality": 0.30,      # Code quality is important for maintainability
            "reliability": 0.20,  # Test reliability ensures stability
            "confidence": 0.10    # Pattern confidence provides assurance
        }
        
        # Calculate component scores
        performance_score = self._calculate_performance_score(test_results)
        quality_score = test_results.get("quality_score", 0)
        reliability_score = self._calculate_reliability_score(test_results)
        confidence_score = pattern.get("confidence", 0)
        
        # Calculate weighted score
        success_score = (
            performance_score * weights["performance"] +
            quality_score * weights["quality"] +
            reliability_score * weights["reliability"] +
            confidence_score * weights["confidence"]
        )
        
        return min(success_score, 1.0)  # Cap at 1.0
    
    def _calculate_performance_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate performance score from test results"""
        performance_improvement = test_results.get("performance_improvement", 0)
        
        # Normalize performance improvement to 0-1 scale
        # 20% improvement = 1.0, 5% improvement = 0.25
        performance_threshold = self.optimization_thresholds["performance"]
        
        if performance_improvement >= performance_threshold.target_value:
            return 1.0
        elif performance_improvement >= performance_threshold.minimum_value:
            # Linear scaling between minimum and target
            return (performance_improvement - performance_threshold.minimum_value) / \
                   (performance_threshold.target_value - performance_threshold.minimum_value) * 0.8
        else:
            return 0.0
    
    def _calculate_reliability_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate reliability score from test results"""
        tests_passed = test_results.get("tests_passed", False)
        if isinstance(tests_passed, bool):
            return 1.0 if tests_passed else 0.0
        
        # If it's a numeric score, normalize it
        test_success_rate = float(tests_passed)
        reliability_threshold = self.optimization_thresholds["reliability"]
        
        if test_success_rate >= reliability_threshold.target_value:
            return 1.0
        elif test_success_rate >= reliability_threshold.minimum_value:
            return (test_success_rate - reliability_threshold.minimum_value) / \
                   (reliability_threshold.target_value - reliability_threshold.minimum_value)
        else:
            return 0.0
    
    def generate_final_recommendations(self, optimization_results: List[Dict[str, Any]]) -> List[str]:
        """Generate final business recommendations from optimization results"""
        recommendations = []
        
        if not optimization_results:
            return ["No successful optimizations identified. Consider adjusting optimization criteria."]
        
        # Sort results by success score
        sorted_results = sorted(optimization_results, key=lambda r: r.get("success_score", 0), reverse=True)
        
        # Identify top performers
        top_optimizations = [r for r in sorted_results if r.get("success_score", 0) > 0.8]
        moderate_optimizations = [r for r in sorted_results if 0.6 <= r.get("success_score", 0) <= 0.8]
        
        if top_optimizations:
            recommendations.append(f"IMPLEMENT IMMEDIATELY: {len(top_optimizations)} high-success optimizations (score > 0.8)")
            for opt in top_optimizations[:3]:  # Top 3
                component = opt.get("pattern", {}).get("component", "Unknown")
                score = opt.get("success_score", 0)
                recommendations.append(f"• {component}: Success score {score:.2f} - Deploy to production")
        
        if moderate_optimizations:
            recommendations.append(f"REVIEW FOR IMPLEMENTATION: {len(moderate_optimizations)} moderate-success optimizations")
        
        # Performance analysis
        performance_improvements = [r.get("test_results", {}).get("performance_improvement", 0) for r in optimization_results]
        if performance_improvements:
            avg_improvement = statistics.mean(performance_improvements)
            recommendations.append(f"Average performance improvement: {avg_improvement:.1%}")
        
        # Component-specific recommendations
        component_performance = {}
        for result in optimization_results:
            component = result.get("pattern", {}).get("component", "unknown")
            score = result.get("success_score", 0)
            
            if component not in component_performance:
                component_performance[component] = []
            component_performance[component].append(score)
        
        for component, scores in component_performance.items():
            avg_score = statistics.mean(scores)
            if avg_score > 0.7:
                recommendations.append(f"{component.title()}: Excellent optimization potential (avg score: {avg_score:.2f})")
            elif avg_score < 0.5:
                recommendations.append(f"{component.title()}: Requires architecture review (low optimization success)")
        
        return recommendations
