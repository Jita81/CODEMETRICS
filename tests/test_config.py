"""
Tests for the Config class
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from src.codemetrics.config import Config

class TestConfig:
    
    def test_default_config(self):
        """Test default configuration values"""
        config = Config()
        
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.max_tokens == 8192
        assert config.temperature == 0.3
        assert config.cache_enabled == True
        assert config.max_retries == 3
    
    def test_config_validation_success(self):
        """Test successful config validation"""
        config = Config(anthropic_api_key="test-key")
        
        assert config.validate() == True
    
    def test_config_validation_missing_api_key(self):
        """Test config validation with missing API key"""
        config = Config(anthropic_api_key="")
        
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            config.validate()
    
    def test_config_validation_invalid_temperature(self):
        """Test config validation with invalid temperature"""
        config = Config(anthropic_api_key="test-key", temperature=1.5)
        
        with pytest.raises(ValueError, match="temperature must be between 0 and 1"):
            config.validate()
    
    def test_config_validation_invalid_max_tokens(self):
        """Test config validation with invalid max_tokens"""
        config = Config(anthropic_api_key="test-key", max_tokens=-100)
        
        with pytest.raises(ValueError, match="max_tokens must be positive"):
            config.validate()
    
    def test_config_load_from_file(self):
        """Test loading configuration from YAML file"""
        config_data = {
            'model': 'test-model',
            'max_tokens': 4000,
            'temperature': 0.5,
            'cache_enabled': False
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            config = Config.load(config_path)
            
            assert config.model == 'test-model'
            assert config.max_tokens == 4000
            assert config.temperature == 0.5
            assert config.cache_enabled == False
        finally:
            Path(config_path).unlink()
    
    def test_config_save_to_file(self):
        """Test saving configuration to YAML file"""
        config = Config(
            model="test-model",
            max_tokens=4000,
            temperature=0.5
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            config_path = f.name
        
        try:
            config.save(config_path)
            
            with open(config_path, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert saved_data['model'] == 'test-model'
            assert saved_data['max_tokens'] == 4000
            assert saved_data['temperature'] == 0.5
            # Sensitive data should not be saved
            assert 'anthropic_api_key' not in saved_data
        finally:
            Path(config_path).unlink()
