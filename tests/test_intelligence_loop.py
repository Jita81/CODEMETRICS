"""
Tests for the Ecosystem Intelligence Loop
"""

import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codemetrics.config import Config
from codemetrics.intelligence_loop import (
    EcosystemIntelligenceLoop, 
    FeedbackItem, 
    ImprovementCandidate, 
    IterationResult,
    ProcessType, 
    FeedbackSeverity
)

class TestEcosystemIntelligenceLoop:
    """Test the Ecosystem Intelligence Loop"""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration"""
        return Config(
            anthropic_api_key="test-key",
            github_token="test-token",
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.3
        )
    
    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock the Anthropic client"""
        with patch('codemetrics.intelligence_loop.anthropic.Anthropic') as mock_client:
            mock_response = Mock()
            mock_response.content = [Mock(text='{"test": "response"}')]
            mock_client.return_value.messages.create.return_value = mock_response
            yield mock_client
    
    @pytest.fixture
    def intelligence_loop(self, config, mock_anthropic_client):
        """Create an intelligence loop instance"""
        with patch('codemetrics.intelligence_loop.CodeCreateIntegration'), \
             patch('codemetrics.intelligence_loop.CodeReviewIntegration'), \
             patch('codemetrics.intelligence_loop.CodeTestIntegration'):
            return EcosystemIntelligenceLoop(config)
    
    def test_initialization(self, intelligence_loop):
        """Test intelligence loop initialization"""
        assert intelligence_loop.max_iterations == 10
        assert intelligence_loop.analysis_window_days == 30
        assert intelligence_loop.min_feedback_frequency == 3
        assert len(intelligence_loop.feedback_history) == 0
        assert len(intelligence_loop.active_iterations) == 0
    
    def test_feedback_item_creation(self):
        """Test creating feedback items"""
        feedback = FeedbackItem(
            id="test-feedback",
            process_type=ProcessType.GENERATE,
            severity=FeedbackSeverity.MEDIUM,
            description="Test feedback",
            error_details="Test error details",
            frequency=5,
            first_seen=datetime.now() - timedelta(days=7),
            last_seen=datetime.now(),
            affected_modules=["test_module"]
        )
        
        assert feedback.id == "test-feedback"
        assert feedback.process_type == ProcessType.GENERATE
        assert feedback.severity == FeedbackSeverity.MEDIUM
        assert feedback.frequency == 5
        assert len(feedback.affected_modules) == 1
    
    def test_improvement_candidate_creation(self):
        """Test creating improvement candidates"""
        candidate = ImprovementCandidate(
            process_type=ProcessType.REVIEW,
            improvement_type="bug_fix",
            description="Fix security detection",
            target_files=["security.py"],
            code_changes=[{"file": "security.py", "change": "fix"}],
            confidence_score=0.85,
            expected_impact="high",
            risk_level="medium"
        )
        
        assert candidate.process_type == ProcessType.REVIEW
        assert candidate.improvement_type == "bug_fix"
        assert candidate.confidence_score == 0.85
        assert len(candidate.target_files) == 1
        assert len(candidate.code_changes) == 1
    
    def test_extract_codecreate_feedback(self, intelligence_loop):
        """Test extracting feedback from CodeCreate metrics"""
        metrics = {
            "total_generations": 100,
            "successful_generations": 70  # 70% success rate
        }
        quality = {
            "common_issues": [
                {"issue": "Missing tests", "frequency": 0.15}
            ]
        }
        
        feedback_items = intelligence_loop._extract_codecreate_feedback(metrics, quality)
        
        assert len(feedback_items) == 2  # Low success rate + quality issue
        
        # Check low success rate feedback
        success_feedback = next(f for f in feedback_items if "success_rate" in f.description)
        assert success_feedback.process_type == ProcessType.GENERATE
        assert success_feedback.severity == FeedbackSeverity.MEDIUM
        assert success_feedback.frequency == 30  # Failed generations
        
        # Check quality issue feedback
        quality_feedback = next(f for f in feedback_items if "Missing tests" in f.description)
        assert quality_feedback.process_type == ProcessType.GENERATE
        assert quality_feedback.severity == FeedbackSeverity.MEDIUM
    
    def test_extract_codereview_feedback(self, intelligence_loop):
        """Test extracting feedback from CodeReview metrics"""
        metrics = {
            "detection_rates": {
                "sql_injection": 0.95,
                "xss_vulnerabilities": 0.75  # Below 85% threshold
            }
        }
        trends = {
            "vulnerability_trends": {
                "last_30_days": {
                    "critical": 2,
                    "high": 5,
                    "total": 10
                }
            }
        }
        
        feedback_items = intelligence_loop._extract_codereview_feedback(metrics, trends)
        
        assert len(feedback_items) == 2  # Low detection + critical vulnerabilities
        
        # Check detection rate feedback
        detection_feedback = next(f for f in feedback_items if "detection_rate" in f.description)
        assert detection_feedback.process_type == ProcessType.REVIEW
        assert "xss_vulnerabilities" in detection_feedback.description
        
        # Check critical vulnerabilities feedback
        vuln_feedback = next(f for f in feedback_items if "Critical vulnerabilities" in f.description)
        assert vuln_feedback.severity == FeedbackSeverity.CRITICAL
        assert vuln_feedback.frequency == 2
    
    def test_extract_codetest_feedback(self, intelligence_loop):
        """Test extracting feedback from CodeTest metrics"""
        metrics = {
            "framework_compliance_rate": 0.85,  # Below 90% threshold
            "module_type_coverage": {
                "CORE_modules": {
                    "success_rate": 0.80,  # Below 85% threshold
                    "tests_run": 50
                },
                "INTEGRATION_modules": {
                    "success_rate": 0.90,  # Above threshold
                    "tests_run": 30
                }
            }
        }
        compliance = {}
        
        feedback_items = intelligence_loop._extract_codetest_feedback(metrics, compliance)
        
        assert len(feedback_items) == 2  # Low compliance + CORE module issues
        
        # Check compliance feedback
        compliance_feedback = next(f for f in feedback_items if "compliance_rate" in f.description)
        assert compliance_feedback.process_type == ProcessType.TEST
        assert compliance_feedback.severity == FeedbackSeverity.MEDIUM
        
        # Check module-specific feedback
        module_feedback = next(f for f in feedback_items if "CORE_modules" in f.description)
        assert module_feedback.frequency == 50
    
    @pytest.mark.asyncio
    async def test_analyze_feedback_patterns(self, intelligence_loop):
        """Test AI analysis of feedback patterns"""
        feedback_data = {
            "processes": {
                "codecreate": {"metrics": {"total_generations": 100}},
                "codereview": {"metrics": {"total_reviews": 50}},
                "codetest": {"metrics": {"total_test_runs": 75}}
            }
        }
        
        # Mock successful AI response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "root_cause_analysis": [
                {
                    "root_cause": "Insufficient test coverage",
                    "affected_processes": ["generate", "test"],
                    "severity": "medium",
                    "confidence": 0.8,
                    "evidence": ["Low test generation", "Test failures"]
                }
            ],
            "pattern_insights": {
                "recurring_issues": ["Missing tests"],
                "cross_process_correlations": [],
                "trend_analysis": {
                    "improving_areas": ["Security"],
                    "degrading_areas": ["Testing"],
                    "stable_areas": ["Generation"]
                }
            },
            "improvement_priorities": [
                {
                    "priority": 1,
                    "focus_area": "Test coverage improvement",
                    "expected_impact": "high",
                    "effort_required": "medium"
                }
            ]
        }''')]
        
        with patch.object(intelligence_loop.client.messages, 'create', return_value=mock_response):
            result = await intelligence_loop._analyze_feedback_patterns(feedback_data)
        
        assert "root_cause_analysis" in result
        assert "pattern_insights" in result
        assert "improvement_priorities" in result
        assert len(result["root_cause_analysis"]) == 1
        assert result["root_cause_analysis"][0]["root_cause"] == "Insufficient test coverage"
    
    @pytest.mark.asyncio
    async def test_generate_improvement_candidates(self, intelligence_loop):
        """Test generating improvement candidates"""
        priority = {
            "priority": 1,
            "focus_area": "Test coverage improvement",
            "expected_impact": "high",
            "effort_required": "medium"
        }
        feedback_analysis = {"test": "data"}
        
        # Mock successful AI response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "improvements": [
                {
                    "process_type": "test",
                    "improvement_type": "feature",
                    "description": "Add automated test generation",
                    "target_files": ["test_generator.py"],
                    "code_changes": [
                        {
                            "file": "test_generator.py",
                            "change_type": "add",
                            "description": "Add test generation logic",
                            "code": "def generate_tests(): pass"
                        }
                    ],
                    "confidence_score": 0.85,
                    "expected_impact": "high",
                    "risk_level": "low"
                }
            ]
        }''')]
        
        with patch.object(intelligence_loop.client.messages, 'create', return_value=mock_response):
            candidates = await intelligence_loop._generate_improvement_candidates(priority, feedback_analysis)
        
        assert len(candidates) == 1
        candidate = candidates[0]
        assert candidate.process_type == ProcessType.TEST
        assert candidate.improvement_type == "feature"
        assert candidate.confidence_score == 0.85
        assert len(candidate.code_changes) == 1
    
    def test_calculate_success_score(self, intelligence_loop):
        """Test success score calculation"""
        # Test successful case
        test_results = {
            "tests_passed": 8,
            "tests_failed": 2,
            "errors_fixed": 3,
            "new_errors": 1
        }
        score = intelligence_loop._calculate_success_score(test_results)
        expected = 0.8 + 0.3 - 0.2  # 80% pass rate + 30% fix bonus - 20% error penalty
        assert score == expected
        
        # Test error case
        test_results_error = {"error": "Test failed"}
        score_error = intelligence_loop._calculate_success_score(test_results_error)
        assert score_error == 0.0
        
        # Test no tests case
        test_results_empty = {"tests_passed": 0, "tests_failed": 0}
        score_empty = intelligence_loop._calculate_success_score(test_results_empty)
        assert score_empty == 0.5
    
    def test_evaluate_iterations(self, intelligence_loop):
        """Test iteration evaluation and ranking"""
        # Create mock iteration results
        candidate1 = ImprovementCandidate(
            process_type=ProcessType.GENERATE,
            improvement_type="bug_fix",
            description="Fix 1",
            target_files=[],
            code_changes=[],
            confidence_score=0.8,
            expected_impact="high",
            risk_level="low"
        )
        
        candidate2 = ImprovementCandidate(
            process_type=ProcessType.REVIEW,
            improvement_type="performance",
            description="Fix 2",
            target_files=[],
            code_changes=[],
            confidence_score=0.9,
            expected_impact="medium",
            risk_level="low"
        )
        
        iterations = [
            IterationResult(
                iteration_id="iter_1",
                improvement_candidate=candidate1,
                branch_name="branch_1",
                test_results={},
                performance_metrics={},
                success_score=0.7,
                errors_fixed=2,
                new_errors_introduced=0,
                timestamp=datetime.now()
            ),
            IterationResult(
                iteration_id="iter_2",
                improvement_candidate=candidate2,
                branch_name="branch_2",
                test_results={},
                performance_metrics={},
                success_score=0.9,
                errors_fixed=3,
                new_errors_introduced=0,
                timestamp=datetime.now()
            ),
            IterationResult(
                iteration_id="iter_3",
                improvement_candidate=candidate1,
                branch_name="branch_3",
                test_results={"error": "failed"},
                performance_metrics={},
                success_score=0.0,  # Failed iteration
                errors_fixed=0,
                new_errors_introduced=1,
                timestamp=datetime.now()
            )
        ]
        
        best_improvements = intelligence_loop.evaluate_iterations(iterations)
        
        # Should return 2 successful iterations, sorted by score
        assert len(best_improvements) == 2
        assert best_improvements[0].success_score == 0.9  # Highest score first
        assert best_improvements[1].success_score == 0.7
        assert best_improvements[0].improvement_candidate.description == "Fix 2"
    
    def test_generate_intelligence_report(self, intelligence_loop):
        """Test intelligence report generation"""
        feedback_analysis = {"test": "feedback"}
        candidates = []
        iteration_results = []
        best_improvements = []
        
        report = intelligence_loop.generate_intelligence_report(
            feedback_analysis, candidates, iteration_results, best_improvements
        )
        
        assert "intelligence_loop_report" in report
        intelligence_report = report["intelligence_loop_report"]
        
        assert "timestamp" in intelligence_report
        assert "execution_summary" in intelligence_report
        assert "feedback_analysis" in intelligence_report
        assert "improvement_candidates" in intelligence_report
        assert "iteration_results" in intelligence_report
        assert "best_improvements" in intelligence_report
        assert "next_steps" in intelligence_report
        
        # Check execution summary
        summary = intelligence_report["execution_summary"]
        assert "feedback_sources_analyzed" in summary
        assert "improvement_candidates_generated" in summary
        assert "iterations_tested" in summary
        assert "successful_improvements_found" in summary
    
    @pytest.mark.asyncio
    async def test_collect_ecosystem_feedback(self, intelligence_loop):
        """Test collecting feedback from ecosystem"""
        # Mock the integration responses
        intelligence_loop.codecreate.collect_generation_metrics = Mock(return_value={
            "total_generations": 100,
            "successful_generations": 85
        })
        intelligence_loop.codecreate.analyze_generation_quality = Mock(return_value={
            "common_issues": []
        })
        
        intelligence_loop.codereview.collect_review_metrics = Mock(return_value={
            "total_reviews": 50,
            "detection_rates": {"sql_injection": 0.95}
        })
        intelligence_loop.codereview.analyze_security_trends = Mock(return_value={
            "vulnerability_trends": {"last_30_days": {"critical": 0}}
        })
        
        intelligence_loop.codetest.collect_testing_metrics = Mock(return_value={
            "total_test_runs": 75,
            "framework_compliance_rate": 0.92
        })
        intelligence_loop.codetest.analyze_framework_compliance = Mock(return_value={
            "overall_compliance_score": 90
        })
        
        # Mock the AI analysis
        with patch.object(intelligence_loop, '_analyze_feedback_patterns', return_value={"analysis": "test"}):
            feedback_data = await intelligence_loop.collect_ecosystem_feedback()
        
        assert "collection_timestamp" in feedback_data
        assert "processes" in feedback_data
        assert "codecreate" in feedback_data["processes"]
        assert "codereview" in feedback_data["processes"]
        assert "codetest" in feedback_data["processes"]
        assert "ai_analysis" in feedback_data
    
    @pytest.mark.asyncio 
    async def test_full_intelligence_loop_mock(self, intelligence_loop):
        """Test the full intelligence loop with mocks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock all the components
            with patch.object(intelligence_loop, 'collect_ecosystem_feedback', return_value={
                "processes": {"codecreate": {}, "codereview": {}, "codetest": {}},
                "ai_analysis": {"improvement_priorities": []}
            }), \
            patch.object(intelligence_loop, 'identify_improvements', return_value=[]), \
            patch.object(intelligence_loop, 'run_iterative_improvements', return_value=[]), \
            patch.object(intelligence_loop, 'evaluate_iterations', return_value=[]):
                
                result = await intelligence_loop.run_intelligence_loop(temp_dir)
                
                assert "intelligence_loop_report" in result
                assert "execution_summary" in result["intelligence_loop_report"]

if __name__ == "__main__":
    pytest.main([__file__])
