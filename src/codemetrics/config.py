"""
Configuration management for CodeMetrics
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Config:
    """Configuration class for CodeMetrics"""
    
    # API Configuration
    anthropic_api_key: str = field(default_factory=lambda: os.getenv('ANTHROPIC_API_KEY', ''))
    github_token: str = field(default_factory=lambda: os.getenv('GITHUB_TOKEN', ''))
    
    # AI Model Configuration
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 8192
    temperature: float = 0.3
    
    # Analysis Configuration
    max_file_size_kb: int = 2000
    max_workers: int = 4
    chunk_size_lines: int = 200
    
    # Caching Configuration
    cache_enabled: bool = True
    cache_dir: str = ".codemetrics_cache"
    cache_ttl_hours: int = 24
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay: float = 2.0
    
    # Dashboard Configuration
    dashboard_host: str = "localhost"
    dashboard_port: int = 8080
    dashboard_debug: bool = False
    
    # Ecosystem Configuration
    ecosystem_repos: list = field(default_factory=lambda: [
        "Jita81/Standardized-Modules-Framework-v1.0.0",
        "Jita81/CODEREVIEW",
        "Jita81/CODECREATE", 
        "Jita81/CODEMETRICS"
    ])
    
    # Output Configuration
    output_dir: str = "reports"
    output_format: str = "json"
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from file or environment"""
        config_data = {}
        
        # Try to load from file
        if config_path:
            config_file = Path(config_path)
        else:
            # Look for config in standard locations
            possible_paths = [
                Path("config/config.yml"),
                Path("config.yml"),
                Path(".codemetrics.yml"),
                Path(os.path.expanduser("~/.codemetrics/config.yml"))
            ]
            config_file = None
            for path in possible_paths:
                if path.exists():
                    config_file = path
                    break
        
        if config_file and config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        
        # Override with environment variables
        env_overrides = {
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
            'github_token': os.getenv('GITHUB_TOKEN'),
            'model': os.getenv('CODEMETRICS_MODEL'),
            'max_tokens': os.getenv('CODEMETRICS_MAX_TOKENS'),
            'temperature': os.getenv('CODEMETRICS_TEMPERATURE'),
            'cache_enabled': os.getenv('CODEMETRICS_CACHE_ENABLED'),
            'output_dir': os.getenv('CODEMETRICS_OUTPUT_DIR'),
        }
        
        # Apply non-None environment overrides
        for key, value in env_overrides.items():
            if value is not None:
                if key in ['max_tokens']:
                    config_data[key] = int(value)
                elif key in ['temperature']:
                    config_data[key] = float(value)
                elif key in ['cache_enabled']:
                    config_data[key] = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    config_data[key] = value
        
        return cls(**config_data)
    
    def save(self, config_path: str) -> None:
        """Save configuration to file"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict, excluding sensitive data
        config_dict = {
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'max_file_size_kb': self.max_file_size_kb,
            'max_workers': self.max_workers,
            'chunk_size_lines': self.chunk_size_lines,
            'cache_enabled': self.cache_enabled,
            'cache_dir': self.cache_dir,
            'cache_ttl_hours': self.cache_ttl_hours,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'dashboard_host': self.dashboard_host,
            'dashboard_port': self.dashboard_port,
            'dashboard_debug': self.dashboard_debug,
            'ecosystem_repos': self.ecosystem_repos,
            'output_dir': self.output_dir,
            'output_format': self.output_format,
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
            
        if not 0 <= self.temperature <= 1:
            raise ValueError("temperature must be between 0 and 1")
            
        return True
