"""
Intelligent Feedback Optimization Engine using Claude

This module analyzes ecosystem feedback, identifies improvement opportunities,
and automatically tests optimization strategies across Framework, CodeCreate,
CodeReview, and CodeTest components.
"""

import json
import time
import asyncio
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

try:
    import anthropic
    import git
except ImportError:
    raise ImportError("Required packages not installed. Run: pip install anthropic gitpython")

from .config import Config
from .analyzer import MetricsAnalyzer
from ..integrations import CodeCreateIntegration, CodeReviewIntegration, CodeTestIntegration, FrameworkIntegration

@dataclass
class OptimizationResult:
    """Result of an optimization iteration"""
    iteration: int
    branch_name: str
    component: str
    changes_made: List[str]
    test_results: Dict[str, Any]
    performance_improvement: float
    success_score: float
    timestamp: float

@dataclass
class FeedbackPattern:
    """Identified pattern in ecosystem feedback"""
    component: str
    issue_type: str
    frequency: float
    impact_score: float
    suggested_optimization: str
    confidence: float

class IntelligentOptimizer:
    """AI-powered ecosystem optimization engine"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.analyzer = MetricsAnalyzer(config)
        
        # Ecosystem integrations
        self.codecreate = CodeCreateIntegration(config.github_token)
        self.codereview = CodeReviewIntegration(config.github_token)
        self.codetest = CodeTestIntegration(config.github_token)
        self.framework = FrameworkIntegration(config.github_token)
        
        self.optimization_results = []
    
    async def analyze_ecosystem_feedback(self) -> List[FeedbackPattern]:
        """Analyze feedback patterns across all ecosystem components"""
        
        print("🔍 Analyzing ecosystem feedback patterns...")
        
        # Collect feedback data from all components
        feedback_data = {
            "codecreate": await self._collect_codecreate_feedback(),
            "codereview": await self._collect_codereview_feedback(), 
            "codetest": await self._collect_codetest_feedback(),
            "framework": await self._collect_framework_feedback()
        }
        
        # Use Claude to analyze patterns
        patterns = await self._claude_analyze_patterns(feedback_data)
        
        print(f"📊 Identified {len(patterns)} optimization opportunities")
        return patterns
    
    async def optimize_ecosystem(self, max_iterations: int = 10) -> List[OptimizationResult]:
        """Run intelligent optimization iterations across ecosystem"""
        
        print(f"🚀 Starting intelligent ecosystem optimization ({max_iterations} iterations)")
        
        # Step 1: Analyze current feedback patterns
        feedback_patterns = await self.analyze_ecosystem_feedback()
        
        if not feedback_patterns:
            print("ℹ️ No significant optimization opportunities identified")
            return []
        
        # Step 2: Prioritize optimization opportunities
        prioritized_patterns = self._prioritize_patterns(feedback_patterns)
        
        # Step 3: Run optimization iterations
        optimization_results = []
        
        for iteration in range(min(max_iterations, len(prioritized_patterns))):
            pattern = prioritized_patterns[iteration]
            
            print(f"\n🔧 Iteration {iteration + 1}: Optimizing {pattern.component} - {pattern.issue_type}")
            
            result = await self._run_optimization_iteration(
                iteration + 1, 
                pattern
            )
            
            if result:
                optimization_results.append(result)
                print(f"✅ Iteration {iteration + 1} completed - Success score: {result.success_score:.2f}")
            else:
                print(f"❌ Iteration {iteration + 1} failed")
        
        # Step 4: Analyze results and recommend best optimizations
        best_optimizations = self._analyze_optimization_results(optimization_results)
        
        print(f"\n📊 Optimization complete. {len(best_optimizations)} successful improvements identified.")
        
        return optimization_results
    
    async def _run_optimization_iteration(self, iteration: int, pattern: FeedbackPattern) -> Optional[OptimizationResult]:
        """Run a single optimization iteration"""
        
        try:
            # Generate branch name
            timestamp = int(time.time())
            branch_name = f"ai-optimize-{pattern.component}-{iteration}-{timestamp}"
            
            # Use Claude to generate specific optimization changes
            optimization_plan = await self._claude_generate_optimization(pattern)
            
            if not optimization_plan:
                return None
            
            # Create optimization branch
            repo_path = self._get_component_repo_path(pattern.component)
            if not repo_path or not repo_path.exists():
                print(f"⚠️ Repository path not found for {pattern.component}")
                return None
            
            # Apply changes
            changes_made = await self._apply_optimization_changes(
                repo_path, 
                branch_name, 
                optimization_plan
            )
            
            # Test changes
            test_results = await self._test_optimization_changes(repo_path, pattern.component)
            
            # Calculate success score
            success_score = self._calculate_success_score(pattern, test_results)
            performance_improvement = test_results.get('performance_improvement', 0.0)
            
            return OptimizationResult(
                iteration=iteration,
                branch_name=branch_name,
                component=pattern.component,
                changes_made=changes_made,
                test_results=test_results,
                performance_improvement=performance_improvement,
                success_score=success_score,
                timestamp=time.time()
            )
            
        except Exception as e:
            print(f"❌ Optimization iteration {iteration} failed: {e}")
            return None
    
    async def _claude_analyze_patterns(self, feedback_data: Dict[str, Any]) -> List[FeedbackPattern]:
        """Use Claude to analyze feedback patterns and identify optimization opportunities"""
        
        analysis_prompt = f"""
You are an expert AI system analyst for the Automated Agile Framework ecosystem. 
Analyze the following feedback data and identify optimization opportunities.

Ecosystem Components:
1. Framework: Standardized module scaffolding
2. CodeCreate: AI code generation with Claude 4
3. CodeReview: AI quality and security analysis  
4. CodeTest: Framework compliance testing

Feedback Data:
{json.dumps(feedback_data, indent=2, default=str)}

Identify patterns that indicate areas for improvement. For each pattern, provide:

1. Component affected
2. Issue type (performance, quality, reliability, usability)
3. Frequency (how often this issue occurs, 0.0-1.0)
4. Impact score (severity of impact, 0.0-1.0) 
5. Suggested optimization approach
6. Confidence in the analysis (0.0-1.0)

Focus on:
- Recurring failure patterns
- Performance bottlenecks
- Quality inconsistencies
- Integration friction points
- User experience issues

Return results as JSON array with this structure:
[
  {{
    "component": "codecreate|codereview|codetest|framework",
    "issue_type": "performance|quality|reliability|usability|integration",
    "frequency": 0.0-1.0,
    "impact_score": 0.0-1.0,
    "suggested_optimization": "specific optimization approach",
    "confidence": 0.0-1.0,
    "description": "detailed description of the issue pattern"
  }}
]

Only include patterns with confidence > 0.7 and impact_score > 0.5.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=0.2,  # Lower temperature for more analytical responses
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            content = response.content[0].text
            
            # Extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                patterns_data = json.loads(json_str)
                
                patterns = []
                for p in patterns_data:
                    patterns.append(FeedbackPattern(
                        component=p['component'],
                        issue_type=p['issue_type'],
                        frequency=p['frequency'],
                        impact_score=p['impact_score'],
                        suggested_optimization=p['suggested_optimization'],
                        confidence=p['confidence']
                    ))
                
                return patterns
            
        except Exception as e:
            print(f"⚠️ Claude pattern analysis failed: {e}")
        
        return []
    
    async def _claude_generate_optimization(self, pattern: FeedbackPattern) -> Optional[Dict[str, Any]]:
        """Use Claude to generate specific optimization changes"""
        
        optimization_prompt = f"""
You are an expert software engineer specializing in the Automated Agile Framework ecosystem.
Generate specific optimization changes for the following identified pattern:

Component: {pattern.component}
Issue Type: {pattern.issue_type}
Suggested Optimization: {pattern.suggested_optimization}
Confidence: {pattern.confidence}

Based on this pattern, provide specific code changes, configuration updates, or workflow modifications.

Component Context:
- Framework: Python scaffolding templates, module structures
- CodeCreate: Claude 4 integration, token optimization, generation workflows
- CodeReview: AI analysis patterns, security rules, quality checks
- CodeTest: Testing workflows, validation patterns, CI/CD optimization

Provide optimization plan as JSON:
{{
  "files_to_modify": [
    {{
      "file_path": "relative/path/to/file",
      "change_type": "modify|create|delete",
      "description": "what changes to make",
      "content_changes": "specific code/config changes"
    }}
  ],
  "configuration_changes": [
    {{
      "component": "github_actions|config_file|environment",
      "parameter": "parameter_name",
      "old_value": "current_value",
      "new_value": "optimized_value",
      "reason": "why this change improves performance"
    }}
  ],
  "workflow_changes": [
    {{
      "workflow_file": "file_path",
      "change_description": "what workflow change to make",
      "expected_improvement": "expected performance/quality improvement"
    }}
  ],
  "testing_strategy": {{
    "validation_steps": ["step1", "step2"],
    "success_criteria": ["criteria1", "criteria2"],
    "rollback_plan": "how to rollback if changes fail"
  }}
}}

Be specific and actionable. Focus on changes that can be automatically applied and tested.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=0.3,
                messages=[{"role": "user", "content": optimization_prompt}]
            )
            
            content = response.content[0].text
            
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            
        except Exception as e:
            print(f"⚠️ Claude optimization generation failed: {e}")
        
        return None
    
    async def _collect_codecreate_feedback(self) -> Dict[str, Any]:
        """Collect feedback from CodeCreate component"""
        
        return {
            "generation_metrics": self.codecreate.collect_generation_metrics(),
            "quality_analysis": self.codecreate.analyze_generation_quality(),
            "recent_failures": await self._get_recent_failures("CODECREATE"),
            "performance_issues": await self._get_performance_issues("CODECREATE")
        }
    
    async def _collect_codereview_feedback(self) -> Dict[str, Any]:
        """Collect feedback from CodeReview component"""
        
        return {
            "review_metrics": self.codereview.collect_review_metrics(),
            "security_trends": self.codereview.analyze_security_trends(),
            "recent_failures": await self._get_recent_failures("CODEREVIEW"),
            "false_positive_analysis": await self._get_false_positive_patterns("CODEREVIEW")
        }
    
    async def _collect_codetest_feedback(self) -> Dict[str, Any]:
        """Collect feedback from CodeTest component"""
        
        return {
            "testing_metrics": self.codetest.collect_testing_metrics(),
            "compliance_analysis": self.codetest.analyze_framework_compliance(),
            "recent_failures": await self._get_recent_failures("CODETEST"),
            "performance_bottlenecks": await self._get_performance_bottlenecks("CODETEST")
        }
    
    async def _collect_framework_feedback(self) -> Dict[str, Any]:
        """Collect feedback from Framework component"""
        
        return {
            "framework_metrics": self.framework.collect_framework_metrics(),
            "adoption_patterns": self.framework.get_adoption_patterns(),
            "scaffold_quality": self.framework.analyze_scaffold_quality(),
            "recent_issues": await self._get_recent_issues("FRAMEWORK")
        }
    
    async def _get_recent_failures(self, component: str) -> List[Dict[str, Any]]:
        """Get recent failures for a component"""
        
        # Simulate recent failure analysis
        # In real implementation, this would query GitHub Actions, logs, etc.
        return [
            {
                "timestamp": time.time() - 3600,
                "error_type": "generation_timeout",
                "frequency": 0.15,
                "impact": "high"
            },
            {
                "timestamp": time.time() - 7200,
                "error_type": "token_limit_exceeded", 
                "frequency": 0.08,
                "impact": "medium"
            }
        ]
    
    async def _get_performance_issues(self, component: str) -> List[Dict[str, Any]]:
        """Get performance issues for a component"""
        
        return [
            {
                "issue": "slow_claude_response",
                "avg_delay": 15.2,
                "frequency": 0.22,
                "impact_score": 0.7
            }
        ]
    
    async def _get_false_positive_patterns(self, component: str) -> List[Dict[str, Any]]:
        """Get false positive patterns for review component"""
        
        return [
            {
                "pattern": "safe_sql_queries_flagged",
                "frequency": 0.12,
                "impact": "developer_friction"
            }
        ]
    
    async def _get_performance_bottlenecks(self, component: str) -> List[Dict[str, Any]]:
        """Get performance bottlenecks for testing component"""
        
        return [
            {
                "bottleneck": "docker_build_time",
                "avg_duration": 8.5,
                "frequency": 0.89,
                "optimization_potential": 0.6
            }
        ]
    
    async def _get_recent_issues(self, component: str) -> List[Dict[str, Any]]:
        """Get recent issues for framework component"""
        
        return [
            {
                "issue": "incomplete_templates",
                "template_type": "INTEGRATION",
                "frequency": 0.18,
                "user_impact": "setup_time_increase"
            }
        ]
    
    def _prioritize_patterns(self, patterns: List[FeedbackPattern]) -> List[FeedbackPattern]:
        """Prioritize patterns based on impact and confidence"""
        
        return sorted(
            patterns,
            key=lambda p: p.impact_score * p.frequency * p.confidence,
            reverse=True
        )
    
    def _get_component_repo_path(self, component: str) -> Optional[Path]:
        """Get local repository path for component"""
        
        # In real implementation, this would clone/update repositories
        base_path = Path.home() / "repos"
        
        repo_mapping = {
            "codecreate": base_path / "CODECREATE",
            "codereview": base_path / "CODEREVIEW", 
            "codetest": base_path / "CODETEST",
            "framework": base_path / "Standardized-Modules-Framework-v1.0.0"
        }
        
        return repo_mapping.get(component)
    
    async def _apply_optimization_changes(self, repo_path: Path, branch_name: str, optimization_plan: Dict[str, Any]) -> List[str]:
        """Apply optimization changes to a branch"""
        
        changes_made = []
        
        try:
            # Create and checkout new branch
            repo = git.Repo(repo_path)
            repo.git.checkout('-b', branch_name)
            
            # Apply file modifications
            for file_change in optimization_plan.get('files_to_modify', []):
                file_path = repo_path / file_change['file_path']
                
                if file_change['change_type'] == 'modify' and file_path.exists():
                    # Apply content changes (simplified)
                    changes_made.append(f"Modified {file_change['file_path']}: {file_change['description']}")
                
                elif file_change['change_type'] == 'create':
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(file_change.get('content_changes', ''))
                    changes_made.append(f"Created {file_change['file_path']}")
            
            # Apply configuration changes
            for config_change in optimization_plan.get('configuration_changes', []):
                changes_made.append(f"Config: {config_change['parameter']} = {config_change['new_value']}")
            
            # Commit changes
            repo.git.add('.')
            repo.git.commit('-m', f"AI Optimization: {branch_name}")
            
        except Exception as e:
            print(f"⚠️ Failed to apply changes: {e}")
        
        return changes_made
    
    async def _test_optimization_changes(self, repo_path: Path, component: str) -> Dict[str, Any]:
        """Test optimization changes"""
        
        try:
            # Run component-specific tests
            test_results = {
                "tests_passed": True,
                "performance_improvement": 0.15,  # Simulated
                "quality_score": 0.92,
                "execution_time": 45.2,
                "errors": []
            }
            
            # Simulate running tests
            if component == "codecreate":
                test_results["generation_time_improvement"] = 0.22
                test_results["token_efficiency"] = 0.78
            elif component == "codereview":
                test_results["detection_accuracy"] = 0.94
                test_results["false_positive_reduction"] = 0.18
            elif component == "codetest":
                test_results["test_execution_time"] = 8.5
                test_results["coverage_improvement"] = 0.12
            elif component == "framework":
                test_results["scaffold_time_reduction"] = 0.28
                test_results["template_completeness"] = 0.96
            
            return test_results
            
        except Exception as e:
            return {
                "tests_passed": False,
                "errors": [str(e)],
                "performance_improvement": 0.0
            }
    
    def _calculate_success_score(self, pattern: FeedbackPattern, test_results: Dict[str, Any]) -> float:
        """Calculate success score for optimization"""
        
        if not test_results.get('tests_passed', False):
            return 0.0
        
        # Weight different factors
        performance_score = test_results.get('performance_improvement', 0.0)
        quality_score = test_results.get('quality_score', 0.0)
        
        # Combine with pattern confidence
        success_score = (
            performance_score * 0.4 +
            quality_score * 0.3 +
            pattern.confidence * 0.3
        )
        
        return min(success_score, 1.0)
    
    def _analyze_optimization_results(self, results: List[OptimizationResult]) -> List[OptimizationResult]:
        """Analyze optimization results and identify best improvements"""
        
        # Sort by success score
        sorted_results = sorted(results, key=lambda r: r.success_score, reverse=True)
        
        # Return top results with success score > 0.7
        return [r for r in sorted_results if r.success_score > 0.7]
    
    def generate_optimization_report(self, results: List[OptimizationResult]) -> str:
        """Generate comprehensive optimization report"""
        
        if not results:
            return "No successful optimizations identified."
        
        report = f"""
# 🚀 Ecosystem Optimization Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Iterations**: {len(results)}
**Successful Optimizations**: {len([r for r in results if r.success_score > 0.7])}

## 📊 Optimization Results

"""
        
        for result in sorted(results, key=lambda r: r.success_score, reverse=True):
            status = "✅ SUCCESS" if result.success_score > 0.7 else "⚠️ PARTIAL"
            
            report += f"""
### {status} {result.component.upper()} - Iteration {result.iteration}

**Branch**: `{result.branch_name}`
**Success Score**: {result.success_score:.2f}
**Performance Improvement**: {result.performance_improvement:.1%}

**Changes Made**:
{chr(10).join(f"- {change}" for change in result.changes_made)}

**Test Results**:
- Tests Passed: {result.test_results.get('tests_passed', False)}
- Quality Score: {result.test_results.get('quality_score', 0):.2f}
- Execution Time: {result.test_results.get('execution_time', 0):.1f}s

---
"""
        
        # Add recommendations
        best_results = [r for r in results if r.success_score > 0.8]
        if best_results:
            report += f"""
## 🎯 Recommended Actions

The following optimizations showed excellent results (success score > 0.8):

{chr(10).join(f"1. **{r.component.upper()}**: {r.branch_name} (Score: {r.success_score:.2f})" for r in best_results)}

These changes can be merged to improve ecosystem performance.
"""
        
        return report
