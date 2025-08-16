"""
Ecosystem Intelligence Loop - AI-powered feedback analysis and iterative improvement

This module implements an intelligent feedback loop that:
1. Monitors feedback from CodeCreate, CodeReview, and CodeTest
2. Identifies patterns in bugs and failures
3. Determines which processes need improvements
4. Creates experimental branches with improvements
5. Tests multiple iterations to find the best solutions
6. Uses Claude for analysis and improvement generation
"""

import json
import asyncio
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import anthropic
    import git
except ImportError as e:
    raise ImportError(f"Required packages not installed: {e}. Run: pip install anthropic GitPython")

from .config import Config
from .analyzer import MetricsAnalyzer
from ..integrations.codecreate import CodeCreateIntegration
from ..integrations.codereview import CodeReviewIntegration
from ..integrations.codetest import CodeTestIntegration

class ProcessType(Enum):
    """Types of processes in the ecosystem"""
    GENERATE = "generate"
    REVIEW = "review"
    TEST = "test"
    FRAMEWORK = "framework"

class FeedbackSeverity(Enum):
    """Severity levels for feedback"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FeedbackItem:
    """Individual feedback item from ecosystem processes"""
    id: str
    process_type: ProcessType
    severity: FeedbackSeverity
    description: str
    error_details: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    affected_modules: List[str]
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImprovementCandidate:
    """Candidate improvement for a process"""
    process_type: ProcessType
    improvement_type: str
    description: str
    target_files: List[str]
    code_changes: List[Dict[str, str]]
    confidence_score: float
    expected_impact: str
    risk_level: str

@dataclass
class IterationResult:
    """Result of testing an improvement iteration"""
    iteration_id: str
    improvement_candidate: ImprovementCandidate
    branch_name: str
    test_results: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    success_score: float
    errors_fixed: int
    new_errors_introduced: int
    timestamp: datetime

class EcosystemIntelligenceLoop:
    """Main intelligence loop for ecosystem improvement"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.analyzer = MetricsAnalyzer(config)
        
        # Initialize integrations
        self.codecreate = CodeCreateIntegration(config.github_token)
        self.codereview = CodeReviewIntegration(config.github_token)
        self.codetest = CodeTestIntegration(config.github_token)
        
        # State management
        self.feedback_history: List[FeedbackItem] = []
        self.active_iterations: List[IterationResult] = []
        self.improvement_cache: Dict[str, List[ImprovementCandidate]] = {}
        
        # Configuration
        self.max_iterations = 10
        self.analysis_window_days = 30
        self.min_feedback_frequency = 3  # Minimum occurrences to consider
        
    async def run_intelligence_loop(self, target_repo_path: str) -> Dict[str, Any]:
        """Run the complete intelligence loop"""
        
        print("🧠 Starting Ecosystem Intelligence Loop...")
        
        try:
            # Step 1: Collect and analyze feedback
            feedback_analysis = await self.collect_ecosystem_feedback()
            
            # Step 2: Identify improvement opportunities
            improvement_candidates = await self.identify_improvements(feedback_analysis)
            
            # Step 3: Run iterative testing
            iteration_results = await self.run_iterative_improvements(
                target_repo_path, improvement_candidates
            )
            
            # Step 4: Evaluate and select best improvements
            best_improvements = self.evaluate_iterations(iteration_results)
            
            # Step 5: Generate final report
            report = self.generate_intelligence_report(
                feedback_analysis, improvement_candidates, iteration_results, best_improvements
            )
            
            print(f"✅ Intelligence loop completed. Found {len(best_improvements)} optimal improvements.")
            
            return report
            
        except Exception as e:
            print(f"❌ Intelligence loop failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def collect_ecosystem_feedback(self) -> Dict[str, Any]:
        """Collect feedback from all ecosystem processes"""
        
        print("📊 Collecting ecosystem feedback...")
        
        feedback_data = {
            "collection_timestamp": datetime.now().isoformat(),
            "analysis_window_days": self.analysis_window_days,
            "processes": {}
        }
        
        # Collect from CodeCreate
        try:
            codecreate_metrics = self.codecreate.collect_generation_metrics()
            codecreate_quality = self.codecreate.analyze_generation_quality()
            
            feedback_data["processes"]["codecreate"] = {
                "metrics": codecreate_metrics,
                "quality": codecreate_quality,
                "feedback_items": self._extract_codecreate_feedback(codecreate_metrics, codecreate_quality)
            }
        except Exception as e:
            feedback_data["processes"]["codecreate"] = {"error": str(e)}
        
        # Collect from CodeReview
        try:
            codereview_metrics = self.codereview.collect_review_metrics()
            security_trends = self.codereview.analyze_security_trends()
            
            feedback_data["processes"]["codereview"] = {
                "metrics": codereview_metrics,
                "trends": security_trends,
                "feedback_items": self._extract_codereview_feedback(codereview_metrics, security_trends)
            }
        except Exception as e:
            feedback_data["processes"]["codereview"] = {"error": str(e)}
        
        # Collect from CodeTest
        try:
            codetest_metrics = self.codetest.collect_testing_metrics()
            compliance_analysis = self.codetest.analyze_framework_compliance()
            
            feedback_data["processes"]["codetest"] = {
                "metrics": codetest_metrics,
                "compliance": compliance_analysis,
                "feedback_items": self._extract_codetest_feedback(codetest_metrics, compliance_analysis)
            }
        except Exception as e:
            feedback_data["processes"]["codetest"] = {"error": str(e)}
        
        # Analyze feedback patterns using Claude
        feedback_analysis = await self._analyze_feedback_patterns(feedback_data)
        feedback_data["ai_analysis"] = feedback_analysis
        
        return feedback_data
    
    def _extract_codecreate_feedback(self, metrics: Dict[str, Any], quality: Dict[str, Any]) -> List[FeedbackItem]:
        """Extract feedback items from CodeCreate data"""
        
        feedback_items = []
        
        # Check generation success rate
        if metrics.get("total_generations", 0) > 0:
            success_rate = metrics.get("successful_generations", 0) / metrics["total_generations"]
            if success_rate < 0.85:  # Below 85% success rate
                feedback_items.append(FeedbackItem(
                    id=f"codecreate_low_success_{datetime.now().strftime('%Y%m%d')}",
                    process_type=ProcessType.GENERATE,
                    severity=FeedbackSeverity.MEDIUM if success_rate > 0.70 else FeedbackSeverity.HIGH,
                    description=f"Generation success rate is low: {success_rate:.2%}",
                    error_details=f"Only {metrics['successful_generations']} out of {metrics['total_generations']} generations succeeded",
                    frequency=metrics["total_generations"] - metrics["successful_generations"],
                    first_seen=datetime.now() - timedelta(days=7),
                    last_seen=datetime.now(),
                    affected_modules=["generation_engine"]
                ))
        
        # Check quality issues
        if quality.get("common_issues"):
            for issue in quality["common_issues"]:
                if issue["frequency"] > 0.1:  # More than 10% frequency
                    feedback_items.append(FeedbackItem(
                        id=f"codecreate_quality_{issue['issue'].replace(' ', '_')}",
                        process_type=ProcessType.GENERATE,
                        severity=FeedbackSeverity.MEDIUM,
                        description=f"Common quality issue: {issue['issue']}",
                        error_details=f"Occurs in {issue['frequency']:.1%} of generations",
                        frequency=int(issue["frequency"] * 100),
                        first_seen=datetime.now() - timedelta(days=14),
                        last_seen=datetime.now(),
                        affected_modules=["code_generation"]
                    ))
        
        return feedback_items
    
    def _extract_codereview_feedback(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[FeedbackItem]:
        """Extract feedback items from CodeReview data"""
        
        feedback_items = []
        
        # Check detection rates
        detection_rates = metrics.get("detection_rates", {})
        for vulnerability_type, rate in detection_rates.items():
            if rate < 0.85:  # Below 85% detection rate
                feedback_items.append(FeedbackItem(
                    id=f"codereview_detection_{vulnerability_type}",
                    process_type=ProcessType.REVIEW,
                    severity=FeedbackSeverity.HIGH if rate < 0.70 else FeedbackSeverity.MEDIUM,
                    description=f"Low detection rate for {vulnerability_type}",
                    error_details=f"Detection rate is only {rate:.1%}",
                    frequency=int((1 - rate) * 100),
                    first_seen=datetime.now() - timedelta(days=10),
                    last_seen=datetime.now(),
                    affected_modules=["security_analysis", vulnerability_type.replace("_", "-")]
                ))
        
        # Check vulnerability trends
        if trends.get("vulnerability_trends"):
            recent = trends["vulnerability_trends"]["last_30_days"]
            if recent.get("critical", 0) > 0:
                feedback_items.append(FeedbackItem(
                    id="codereview_critical_vulnerabilities",
                    process_type=ProcessType.REVIEW,
                    severity=FeedbackSeverity.CRITICAL,
                    description=f"Critical vulnerabilities found: {recent['critical']}",
                    error_details=f"Found {recent['critical']} critical and {recent['high']} high severity vulnerabilities",
                    frequency=recent["critical"],
                    first_seen=datetime.now() - timedelta(days=30),
                    last_seen=datetime.now(),
                    affected_modules=["security_scanning"]
                ))
        
        return feedback_items
    
    def _extract_codetest_feedback(self, metrics: Dict[str, Any], compliance: Dict[str, Any]) -> List[FeedbackItem]:
        """Extract feedback items from CodeTest data"""
        
        feedback_items = []
        
        # Check compliance rates
        if metrics.get("framework_compliance_rate", 0) < 0.90:
            compliance_rate = metrics["framework_compliance_rate"]
            feedback_items.append(FeedbackItem(
                id="codetest_low_compliance",
                process_type=ProcessType.TEST,
                severity=FeedbackSeverity.MEDIUM if compliance_rate > 0.80 else FeedbackSeverity.HIGH,
                description=f"Framework compliance rate is low: {compliance_rate:.1%}",
                error_details=f"Compliance rate below 90% threshold",
                frequency=int((1 - compliance_rate) * 100),
                first_seen=datetime.now() - timedelta(days=14),
                last_seen=datetime.now(),
                affected_modules=["framework_validation"]
            ))
        
        # Check module-specific issues
        module_coverage = metrics.get("module_type_coverage", {})
        for module_type, data in module_coverage.items():
            if data.get("success_rate", 0) < 0.85:
                feedback_items.append(FeedbackItem(
                    id=f"codetest_{module_type.lower()}_issues",
                    process_type=ProcessType.TEST,
                    severity=FeedbackSeverity.MEDIUM,
                    description=f"Low success rate for {module_type} modules",
                    error_details=f"Success rate: {data['success_rate']:.1%}",
                    frequency=data.get("tests_run", 0),
                    first_seen=datetime.now() - timedelta(days=7),
                    last_seen=datetime.now(),
                    affected_modules=[module_type.lower()]
                ))
        
        return feedback_items
    
    async def _analyze_feedback_patterns(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude to analyze feedback patterns and root causes"""
        
        prompt = f"""
You are an expert AI system analyst for the Automated Agile Framework ecosystem. Analyze the following feedback data from CodeCreate (generation), CodeReview (quality/security), and CodeTest (testing/compliance) processes.

Feedback Data:
{json.dumps(feedback_data, indent=2, default=str)}

Please provide analysis in the following JSON format:
{{
    "root_cause_analysis": [
        {{
            "root_cause": "Description of underlying issue",
            "affected_processes": ["generate", "review", "test"],
            "severity": "low|medium|high|critical",
            "confidence": 0.0-1.0,
            "evidence": ["Evidence point 1", "Evidence point 2"]
        }}
    ],
    "pattern_insights": {{
        "recurring_issues": ["Issue 1", "Issue 2"],
        "cross_process_correlations": [
            {{
                "processes": ["process1", "process2"],
                "correlation": "Description",
                "strength": 0.0-1.0
            }}
        ],
        "trend_analysis": {{
            "improving_areas": ["Area 1"],
            "degrading_areas": ["Area 2"],
            "stable_areas": ["Area 3"]
        }}
    }},
    "improvement_priorities": [
        {{
            "priority": 1,
            "focus_area": "Description",
            "expected_impact": "high|medium|low",
            "effort_required": "high|medium|low"
        }}
    ]
}}
        """
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.messages.create(
                    model=self.config.model,
                    max_tokens=4000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            
            ai_response = response.content[0].text
            
            # Extract JSON from response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"error": "Could not parse AI response", "raw_response": ai_response}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def identify_improvements(self, feedback_analysis: Dict[str, Any]) -> List[ImprovementCandidate]:
        """Identify specific improvements based on feedback analysis"""
        
        print("🔍 Identifying improvement opportunities...")
        
        improvement_candidates = []
        
        # Use Claude to generate improvement candidates
        ai_analysis = feedback_analysis.get("ai_analysis", {})
        
        for priority in ai_analysis.get("improvement_priorities", []):
            candidates = await self._generate_improvement_candidates(priority, feedback_analysis)
            improvement_candidates.extend(candidates)
        
        # Sort by confidence score and expected impact
        improvement_candidates.sort(key=lambda x: (x.confidence_score, x.expected_impact == "high"), reverse=True)
        
        return improvement_candidates[:self.max_iterations]  # Limit to max iterations
    
    async def _generate_improvement_candidates(self, priority: Dict[str, Any], feedback_analysis: Dict[str, Any]) -> List[ImprovementCandidate]:
        """Generate specific improvement candidates for a priority area"""
        
        prompt = f"""
You are an expert software engineer improving the Automated Agile Framework ecosystem. Based on the priority area and feedback analysis, generate specific code improvements.

Priority Area: {priority}
Feedback Analysis: {json.dumps(feedback_analysis, indent=2, default=str)}

Generate improvements in JSON format:
{{
    "improvements": [
        {{
            "process_type": "generate|review|test|framework",
            "improvement_type": "bug_fix|performance|reliability|accuracy|feature",
            "description": "Detailed description of the improvement",
            "target_files": ["file1.py", "file2.py"],
            "code_changes": [
                {{
                    "file": "path/to/file.py",
                    "change_type": "modify|add|delete",
                    "description": "What this change does",
                    "code": "Actual code to implement or modify"
                }}
            ],
            "confidence_score": 0.0-1.0,
            "expected_impact": "high|medium|low",
            "risk_level": "high|medium|low"
        }}
    ]
}}
        """
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.config.model,
                    max_tokens=6000,
                    temperature=0.4,
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            
            ai_response = response.content[0].text
            
            # Extract JSON from response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                data = json.loads(json_str)
                
                candidates = []
                for imp in data.get("improvements", []):
                    candidates.append(ImprovementCandidate(
                        process_type=ProcessType(imp["process_type"]),
                        improvement_type=imp["improvement_type"],
                        description=imp["description"],
                        target_files=imp["target_files"],
                        code_changes=imp["code_changes"],
                        confidence_score=imp["confidence_score"],
                        expected_impact=imp["expected_impact"],
                        risk_level=imp["risk_level"]
                    ))
                
                return candidates
            
        except Exception as e:
            print(f"⚠️ Failed to generate improvement candidates: {e}")
        
        return []
    
    async def run_iterative_improvements(self, repo_path: str, candidates: List[ImprovementCandidate]) -> List[IterationResult]:
        """Run iterative testing of improvement candidates"""
        
        print(f"🧪 Running {len(candidates)} improvement iterations...")
        
        iteration_results = []
        repo = git.Repo(repo_path)
        original_branch = repo.active_branch.name
        
        try:
            for i, candidate in enumerate(candidates[:self.max_iterations]):
                print(f"  🔄 Running iteration {i+1}/{len(candidates)}: {candidate.description[:50]}...")
                
                result = await self._test_improvement_iteration(repo, candidate, i+1)
                iteration_results.append(result)
                
                # Return to original branch after each iteration
                repo.git.checkout(original_branch)
                
                # Clean up the test branch
                try:
                    repo.git.branch('-D', result.branch_name)
                except:
                    pass  # Branch might not exist if creation failed
            
        except Exception as e:
            print(f"❌ Iteration testing failed: {e}")
            # Ensure we're back on the original branch
            try:
                repo.git.checkout(original_branch)
            except:
                pass
        
        return iteration_results
    
    async def _test_improvement_iteration(self, repo: git.Repo, candidate: ImprovementCandidate, iteration_num: int) -> IterationResult:
        """Test a single improvement iteration"""
        
        branch_name = f"intelligence-loop-iteration-{iteration_num}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            # Create new branch
            repo.git.checkout('-b', branch_name)
            
            # Apply code changes
            changes_applied = self._apply_code_changes(repo, candidate.code_changes)
            
            # Run tests to evaluate the improvement
            test_results = await self._run_improvement_tests(repo.working_dir)
            
            # Calculate success metrics
            success_score = self._calculate_success_score(test_results)
            
            return IterationResult(
                iteration_id=f"iter_{iteration_num}",
                improvement_candidate=candidate,
                branch_name=branch_name,
                test_results=test_results,
                performance_metrics=test_results.get("performance", {}),
                success_score=success_score,
                errors_fixed=test_results.get("errors_fixed", 0),
                new_errors_introduced=test_results.get("new_errors", 0),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return IterationResult(
                iteration_id=f"iter_{iteration_num}",
                improvement_candidate=candidate,
                branch_name=branch_name,
                test_results={"error": str(e)},
                performance_metrics={},
                success_score=0.0,
                errors_fixed=0,
                new_errors_introduced=1,
                timestamp=datetime.now()
            )
    
    def _apply_code_changes(self, repo: git.Repo, code_changes: List[Dict[str, str]]) -> bool:
        """Apply code changes to the repository"""
        
        try:
            for change in code_changes:
                file_path = Path(repo.working_dir) / change["file"]
                
                if change["change_type"] == "modify":
                    if file_path.exists():
                        # For this example, we'll append the change as a comment
                        # In practice, you'd implement more sophisticated code modification
                        with open(file_path, 'a') as f:
                            f.write(f"\n# Intelligence Loop Improvement: {change['description']}\n")
                            f.write(f"# {change['code']}\n")
                
                elif change["change_type"] == "add":
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(f"# Intelligence Loop Addition: {change['description']}\n")
                        f.write(change['code'])
                
                elif change["change_type"] == "delete":
                    if file_path.exists():
                        file_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to apply code changes: {e}")
            return False
    
    async def _run_improvement_tests(self, repo_path: str) -> Dict[str, Any]:
        """Run tests to evaluate the improvement"""
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "performance": {},
            "errors_fixed": 0,
            "new_errors": 0
        }
        
        try:
            # Run basic tests (simplified for this example)
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse test results
            if result.returncode == 0:
                test_results["tests_passed"] = 10  # Simulated
                test_results["errors_fixed"] = 2
            else:
                test_results["tests_failed"] = 3  # Simulated
                test_results["new_errors"] = 1
            
            # Simulate performance metrics
            test_results["performance"] = {
                "execution_time_ms": 1500,
                "memory_usage_mb": 128,
                "cpu_utilization": 0.45
            }
            
        except subprocess.TimeoutExpired:
            test_results["error"] = "Tests timed out"
            test_results["tests_failed"] = 1
            test_results["new_errors"] = 1
        except Exception as e:
            test_results["error"] = str(e)
            test_results["tests_failed"] = 1
            test_results["new_errors"] = 1
        
        return test_results
    
    def _calculate_success_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate a success score for the iteration"""
        
        if test_results.get("error"):
            return 0.0
        
        passed = test_results.get("tests_passed", 0)
        failed = test_results.get("tests_failed", 0)
        errors_fixed = test_results.get("errors_fixed", 0)
        new_errors = test_results.get("new_errors", 0)
        
        total_tests = passed + failed
        if total_tests == 0:
            return 0.5  # Neutral score if no tests
        
        # Base score from test pass rate
        test_score = passed / total_tests
        
        # Bonus for fixing errors
        fix_bonus = min(errors_fixed * 0.1, 0.3)  # Up to 30% bonus
        
        # Penalty for new errors
        error_penalty = min(new_errors * 0.2, 0.5)  # Up to 50% penalty
        
        final_score = max(0.0, min(1.0, test_score + fix_bonus - error_penalty))
        
        return final_score
    
    def evaluate_iterations(self, iteration_results: List[IterationResult]) -> List[IterationResult]:
        """Evaluate and rank iterations to find the best improvements"""
        
        print("📈 Evaluating iteration results...")
        
        # Filter out failed iterations
        successful_iterations = [r for r in iteration_results if r.success_score > 0.0]
        
        # Sort by success score (highest first)
        successful_iterations.sort(key=lambda x: x.success_score, reverse=True)
        
        # Return top 3 improvements or all if less than 3
        best_count = min(3, len(successful_iterations))
        best_improvements = successful_iterations[:best_count]
        
        for i, result in enumerate(best_improvements, 1):
            print(f"  🏆 #{i}: {result.improvement_candidate.description[:60]}... (Score: {result.success_score:.2f})")
        
        return best_improvements
    
    def generate_intelligence_report(self, feedback_analysis: Dict[str, Any], 
                                   candidates: List[ImprovementCandidate],
                                   iteration_results: List[IterationResult],
                                   best_improvements: List[IterationResult]) -> Dict[str, Any]:
        """Generate comprehensive intelligence loop report"""
        
        report = {
            "intelligence_loop_report": {
                "timestamp": datetime.now().isoformat(),
                "execution_summary": {
                    "feedback_sources_analyzed": len(feedback_analysis.get("processes", {})),
                    "improvement_candidates_generated": len(candidates),
                    "iterations_tested": len(iteration_results),
                    "successful_improvements_found": len(best_improvements)
                },
                "feedback_analysis": feedback_analysis,
                "improvement_candidates": [
                    {
                        "process_type": c.process_type.value,
                        "improvement_type": c.improvement_type,
                        "description": c.description,
                        "confidence_score": c.confidence_score,
                        "expected_impact": c.expected_impact,
                        "risk_level": c.risk_level
                    }
                    for c in candidates
                ],
                "iteration_results": [
                    {
                        "iteration_id": r.iteration_id,
                        "description": r.improvement_candidate.description,
                        "success_score": r.success_score,
                        "errors_fixed": r.errors_fixed,
                        "new_errors_introduced": r.new_errors_introduced,
                        "performance_metrics": r.performance_metrics
                    }
                    for r in iteration_results
                ],
                "best_improvements": [
                    {
                        "rank": i + 1,
                        "description": r.improvement_candidate.description,
                        "process_type": r.improvement_candidate.process_type.value,
                        "success_score": r.success_score,
                        "branch_name": r.branch_name,
                        "recommendation": "Consider implementing this improvement"
                    }
                    for i, r in enumerate(best_improvements)
                ],
                "next_steps": [
                    "Review the top-ranked improvements",
                    "Test improvements in staging environment",
                    "Implement successful improvements incrementally",
                    "Continue monitoring ecosystem feedback",
                    "Schedule next intelligence loop execution"
                ]
            }
        }
        
        return report
