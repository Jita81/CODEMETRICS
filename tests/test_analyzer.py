"""
Tests for the MetricsAnalyzer class
"""

import pytest
from unittest.mock import Mock, patch
from src.codemetrics.analyzer import MetricsAnalyzer, AnalysisResult
from src.codemetrics.config import Config

class TestMetricsAnalyzer:
    
    @pytest.fixture
    def config(self):
        """Create a test configuration"""
        return Config(
            anthropic_api_key="test-key",
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.3
        )
    
    @pytest.fixture
    def analyzer(self, config):
        """Create a test analyzer"""
        with patch('src.codemetrics.analyzer.anthropic.Anthropic'):
            return MetricsAnalyzer(config)
    
    def test_analyzer_initialization(self, config):
        """Test analyzer initialization"""
        with patch('src.codemetrics.analyzer.anthropic.Anthropic') as mock_anthropic:
            analyzer = MetricsAnalyzer(config)
            assert analyzer.config == config
            mock_anthropic.assert_called_once_with(api_key="test-key")
    
    def test_fallback_analysis(self, analyzer):
        """Test fallback analysis when AI fails"""
        test_data = {"test": "data"}
        error_msg = "API Error"
        
        result = analyzer._fallback_analysis(test_data, error_msg)
        
        assert isinstance(result, AnalysisResult)
        assert result.performance_score == 70
        assert result.quality_score == 75
        assert result.security_score == 80
        assert "fallback method" in result.key_findings[0]
        assert error_msg in str(result.metrics["error"])
    
    def test_parse_analysis_response_with_json(self, analyzer):
        """Test parsing valid JSON response"""
        json_response = '''
        {
            "performance_score": 85,
            "quality_score": 90,
            "security_score": 88,
            "key_findings": ["Good performance", "High quality"],
            "recommendations": ["Continue monitoring", "Add tests"],
            "detailed_metrics": {"complexity": 10}
        }
        '''
        
        result = analyzer._parse_analysis_response(json_response, {})
        
        assert result.performance_score == 85
        assert result.quality_score == 90
        assert result.security_score == 88
        assert "Good performance" in result.key_findings
        assert "Continue monitoring" in result.recommendations
        assert result.metrics["complexity"] == 10
    
    def test_analysis_result_summary(self):
        """Test AnalysisResult summary generation"""
        result = AnalysisResult(
            performance_score=85,
            quality_score=90,
            security_score=88,
            key_findings=["Test finding"],
            recommendations=["Test recommendation"],
            metrics={"test": "data"},
            timestamp=1234567890
        )
        
        summary = result.summary()
        
        assert "Performance Score: 85/100" in summary
        assert "Quality Score: 90/100" in summary
        assert "Security Score: 88/100" in summary
        assert "Test finding" in summary
        assert "Test recommendation" in summary
