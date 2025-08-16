"""
Audit Trail Implementation - Following Standardized Modules Framework

This module implements comprehensive audit trail functionality for tracking
all optimization decisions and changes in the ecosystem.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .module_interface import IAuditTrail, OptimizationRequest
from .domain_entities import AuditEntry, OptimizationStatus

class DatabaseAuditTrail(IAuditTrail):
    """Database-backed audit trail implementation"""
    
    def __init__(self, config):
        self.config = config
        self.audit_entries: Dict[str, List[AuditEntry]] = {}
        
        # In production, this would connect to a proper database
        # For now, we'll use in-memory storage with file backup
        self.storage_path = Path(config.output_dir) / "audit_trail"
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def log_optimization_start(self, request: OptimizationRequest) -> str:
        """Log start of optimization process"""
        entry_id = str(uuid.uuid4())
        correlation_id = request.request_id
        
        entry = AuditEntry(
            entry_id=entry_id,
            request_id=request.request_id,
            timestamp=datetime.now(),
            action="optimization_started",
            actor="system",
            details={
                "components": request.components,
                "max_iterations": request.max_iterations,
                "priority_level": request.priority_level,
                "requester": request.requester,
                "configuration": request.configuration
            },
            correlation_id=correlation_id
        )
        
        self._store_audit_entry(entry)
        
        return correlation_id
    
    def log_pattern_identification(self, request_id: str, patterns: List[Dict[str, Any]]) -> None:
        """Log identified patterns"""
        entry_id = str(uuid.uuid4())
        
        entry = AuditEntry(
            entry_id=entry_id,
            request_id=request_id,
            timestamp=datetime.now(),
            action="patterns_identified",
            actor="ai_analyzer",
            details={
                "pattern_count": len(patterns),
                "patterns": patterns,
                "analysis_summary": self._generate_pattern_summary(patterns)
            }
        )
        
        self._store_audit_entry(entry)
    
    def log_optimization_attempt(self, request_id: str, attempt: Dict[str, Any]) -> None:
        """Log optimization attempt"""
        entry_id = str(uuid.uuid4())
        
        entry = AuditEntry(
            entry_id=entry_id,
            request_id=request_id,
            timestamp=datetime.now(),
            action="optimization_attempt",
            actor="optimization_engine",
            details=attempt,
            before_state=attempt.get("before_state"),
            after_state=attempt.get("after_state")
        )
        
        self._store_audit_entry(entry)
    
    def log_optimization_result(self, request_id: str, result: Dict[str, Any]) -> None:
        """Log optimization result"""
        entry_id = str(uuid.uuid4())
        
        entry = AuditEntry(
            entry_id=entry_id,
            request_id=request_id,
            timestamp=datetime.now(),
            action="optimization_completed",
            actor="optimization_engine",
            details=result
        )
        
        self._store_audit_entry(entry)
        
        # Persist to file for durability
        self._persist_audit_trail(request_id)
    
    def get_audit_history(self, request_id: str) -> List[Dict[str, Any]]:
        """Get audit history for request"""
        if request_id not in self.audit_entries:
            # Try to load from persistent storage
            self._load_audit_trail(request_id)
        
        entries = self.audit_entries.get(request_id, [])
        
        # Convert to dictionaries for serialization
        return [self._audit_entry_to_dict(entry) for entry in entries]
    
    def _store_audit_entry(self, entry: AuditEntry) -> None:
        """Store audit entry in memory"""
        if entry.request_id not in self.audit_entries:
            self.audit_entries[entry.request_id] = []
        
        self.audit_entries[entry.request_id].append(entry)
    
    def _persist_audit_trail(self, request_id: str) -> None:
        """Persist audit trail to file"""
        if request_id not in self.audit_entries:
            return
        
        file_path = self.storage_path / f"{request_id}.json"
        
        entries_data = [
            self._audit_entry_to_dict(entry) 
            for entry in self.audit_entries[request_id]
        ]
        
        try:
            with open(file_path, 'w') as f:
                json.dump(entries_data, f, indent=2, default=str)
        except Exception as e:
            # Log error but don't fail the optimization
            print(f"Failed to persist audit trail: {e}")
    
    def _load_audit_trail(self, request_id: str) -> None:
        """Load audit trail from file"""
        file_path = self.storage_path / f"{request_id}.json"
        
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r') as f:
                entries_data = json.load(f)
            
            entries = []
            for entry_data in entries_data:
                entry = AuditEntry(
                    entry_id=entry_data["entry_id"],
                    request_id=entry_data["request_id"],
                    timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                    action=entry_data["action"],
                    actor=entry_data["actor"],
                    details=entry_data["details"],
                    before_state=entry_data.get("before_state"),
                    after_state=entry_data.get("after_state"),
                    correlation_id=entry_data.get("correlation_id")
                )
                entries.append(entry)
            
            self.audit_entries[request_id] = entries
            
        except Exception as e:
            print(f"Failed to load audit trail: {e}")
    
    def _audit_entry_to_dict(self, entry: AuditEntry) -> Dict[str, Any]:
        """Convert audit entry to dictionary"""
        return {
            "entry_id": entry.entry_id,
            "request_id": entry.request_id,
            "timestamp": entry.timestamp.isoformat(),
            "action": entry.action,
            "actor": entry.actor,
            "details": entry.details,
            "before_state": entry.before_state,
            "after_state": entry.after_state,
            "correlation_id": entry.correlation_id
        }
    
    def _generate_pattern_summary(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of identified patterns"""
        if not patterns:
            return {"summary": "No patterns identified"}
        
        # Count patterns by component
        component_counts = {}
        issue_type_counts = {}
        total_impact = 0
        high_priority_count = 0
        
        for pattern in patterns:
            # Component analysis
            component = pattern.get("component", "unknown")
            component_counts[component] = component_counts.get(component, 0) + 1
            
            # Issue type analysis
            issue_type = pattern.get("issue_type", "unknown")
            issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1
            
            # Impact analysis
            impact = pattern.get("impact_score", 0)
            total_impact += impact
            
            if impact > 0.8:
                high_priority_count += 1
        
        avg_impact = total_impact / len(patterns) if patterns else 0
        
        return {
            "total_patterns": len(patterns),
            "component_distribution": component_counts,
            "issue_type_distribution": issue_type_counts,
            "average_impact_score": round(avg_impact, 2),
            "high_priority_patterns": high_priority_count,
            "recommendations": self._generate_audit_recommendations(patterns)
        }
    
    def _generate_audit_recommendations(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on pattern analysis for audit"""
        recommendations = []
        
        if not patterns:
            return ["Continue monitoring ecosystem health"]
        
        # Component-based recommendations
        component_counts = {}
        for pattern in patterns:
            component = pattern.get("component", "unknown")
            component_counts[component] = component_counts.get(component, 0) + 1
        
        if component_counts:
            most_affected = max(component_counts, key=component_counts.get)
            recommendations.append(f"Focus optimization efforts on {most_affected} component")
        
        # Priority-based recommendations
        high_impact = [p for p in patterns if p.get("impact_score", 0) > 0.8]
        if high_impact:
            recommendations.append(f"Prioritize {len(high_impact)} high-impact patterns for immediate action")
        
        # Frequency-based recommendations
        frequent_issues = [p for p in patterns if p.get("frequency", 0) > 0.2]
        if frequent_issues:
            recommendations.append(f"Address {len(frequent_issues)} frequently occurring issues")
        
        return recommendations

class FileAuditTrail(IAuditTrail):
    """File-based audit trail for simpler deployments"""
    
    def __init__(self, config):
        self.config = config
        self.audit_file = Path(config.output_dir) / "audit_trail.jsonl"
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_optimization_start(self, request: OptimizationRequest) -> str:
        """Log start of optimization process"""
        correlation_id = request.request_id
        
        entry = {
            "entry_id": str(uuid.uuid4()),
            "request_id": request.request_id,
            "timestamp": datetime.now().isoformat(),
            "action": "optimization_started",
            "actor": "system",
            "details": {
                "components": request.components,
                "max_iterations": request.max_iterations,
                "priority_level": request.priority_level,
                "requester": request.requester
            },
            "correlation_id": correlation_id
        }
        
        self._append_audit_entry(entry)
        return correlation_id
    
    def log_pattern_identification(self, request_id: str, patterns: List[Dict[str, Any]]) -> None:
        """Log identified patterns"""
        entry = {
            "entry_id": str(uuid.uuid4()),
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "action": "patterns_identified",
            "actor": "ai_analyzer",
            "details": {
                "pattern_count": len(patterns),
                "patterns": patterns
            }
        }
        
        self._append_audit_entry(entry)
    
    def log_optimization_attempt(self, request_id: str, attempt: Dict[str, Any]) -> None:
        """Log optimization attempt"""
        entry = {
            "entry_id": str(uuid.uuid4()),
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "action": "optimization_attempt",
            "actor": "optimization_engine",
            "details": attempt
        }
        
        self._append_audit_entry(entry)
    
    def log_optimization_result(self, request_id: str, result: Dict[str, Any]) -> None:
        """Log optimization result"""
        entry = {
            "entry_id": str(uuid.uuid4()),
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "action": "optimization_completed",
            "actor": "optimization_engine",
            "details": result
        }
        
        self._append_audit_entry(entry)
    
    def get_audit_history(self, request_id: str) -> List[Dict[str, Any]]:
        """Get audit history for request"""
        entries = []
        
        if not self.audit_file.exists():
            return entries
        
        try:
            with open(self.audit_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry.get("request_id") == request_id:
                            entries.append(entry)
        except Exception as e:
            print(f"Failed to read audit history: {e}")
        
        return entries
    
    def _append_audit_entry(self, entry: Dict[str, Any]) -> None:
        """Append audit entry to file"""
        try:
            with open(self.audit_file, 'a') as f:
                f.write(json.dumps(entry, default=str) + '\n')
        except Exception as e:
            print(f"Failed to write audit entry: {e}")

class AuditTrailManager:
    """Manager for audit trail operations with business logic"""
    
    def __init__(self, audit_trail: IAuditTrail):
        self.audit_trail = audit_trail
    
    def generate_audit_report(self, request_id: str) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        history = self.audit_trail.get_audit_history(request_id)
        
        if not history:
            return {"error": "No audit history found for request"}
        
        # Analyze audit trail
        timeline = self._build_timeline(history)
        performance_analysis = self._analyze_performance(history)
        decision_analysis = self._analyze_decisions(history)
        compliance_check = self._check_compliance(history)
        
        return {
            "request_id": request_id,
            "audit_report_generated": datetime.now().isoformat(),
            "timeline": timeline,
            "performance_analysis": performance_analysis,
            "decision_analysis": decision_analysis,
            "compliance_check": compliance_check,
            "recommendations": self._generate_audit_recommendations_from_history(history)
        }
    
    def _build_timeline(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build chronological timeline of events"""
        timeline = []
        
        for entry in history:
            timeline.append({
                "timestamp": entry["timestamp"],
                "action": entry["action"],
                "actor": entry["actor"],
                "summary": self._generate_entry_summary(entry)
            })
        
        return sorted(timeline, key=lambda x: x["timestamp"])
    
    def _analyze_performance(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance metrics from audit trail"""
        start_time = None
        end_time = None
        iterations_completed = 0
        successful_iterations = 0
        
        for entry in history:
            if entry["action"] == "optimization_started":
                start_time = entry["timestamp"]
            elif entry["action"] == "optimization_completed":
                end_time = entry["timestamp"]
            elif entry["action"] == "optimization_attempt":
                iterations_completed += 1
                if entry["details"].get("status") == "success":
                    successful_iterations += 1
        
        total_duration = None
        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            total_duration = (end_dt - start_dt).total_seconds()
        
        return {
            "total_duration_seconds": total_duration,
            "iterations_completed": iterations_completed,
            "successful_iterations": successful_iterations,
            "success_rate": successful_iterations / iterations_completed if iterations_completed > 0 else 0
        }
    
    def _analyze_decisions(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze decisions made during optimization"""
        decisions = []
        
        for entry in history:
            if entry["action"] in ["patterns_identified", "optimization_attempt"]:
                decisions.append({
                    "timestamp": entry["timestamp"],
                    "decision_type": entry["action"],
                    "details": entry["details"]
                })
        
        return {
            "total_decisions": len(decisions),
            "decision_timeline": decisions
        }
    
    def _check_compliance(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check compliance with audit requirements"""
        required_actions = [
            "optimization_started",
            "patterns_identified", 
            "optimization_attempt",
            "optimization_completed"
        ]
        
        present_actions = set(entry["action"] for entry in history)
        missing_actions = set(required_actions) - present_actions
        
        return {
            "compliance_score": len(present_actions & set(required_actions)) / len(required_actions),
            "required_actions": required_actions,
            "present_actions": list(present_actions),
            "missing_actions": list(missing_actions),
            "compliant": len(missing_actions) == 0
        }
    
    def _generate_entry_summary(self, entry: Dict[str, Any]) -> str:
        """Generate human-readable summary for audit entry"""
        action = entry["action"]
        actor = entry["actor"]
        details = entry["details"]
        
        if action == "optimization_started":
            components = details.get("components", [])
            return f"Started optimization for {len(components)} components: {', '.join(components)}"
        elif action == "patterns_identified":
            count = details.get("pattern_count", 0)
            return f"AI identified {count} optimization patterns"
        elif action == "optimization_attempt":
            iteration = details.get("iteration", "unknown")
            status = details.get("status", "unknown")
            return f"Iteration {iteration} {status}"
        elif action == "optimization_completed":
            status = details.get("status", "unknown")
            return f"Optimization {status}"
        else:
            return f"Action: {action} by {actor}"
    
    def _generate_audit_recommendations_from_history(self, history: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on audit history"""
        recommendations = []
        
        # Analyze performance
        performance = self._analyze_performance(history)
        
        if performance["success_rate"] < 0.5:
            recommendations.append("Low success rate detected - review optimization criteria")
        
        if performance["total_duration_seconds"] and performance["total_duration_seconds"] > 3600:
            recommendations.append("Optimization took over 1 hour - consider parallel processing")
        
        # Analyze compliance
        compliance = self._check_compliance(history)
        
        if not compliance["compliant"]:
            recommendations.append(f"Missing audit actions: {', '.join(compliance['missing_actions'])}")
        
        if not recommendations:
            recommendations.append("Audit trail appears complete and compliant")
        
        return recommendations
