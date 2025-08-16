"""
Data collection from ecosystem components and project analysis
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import time

from .config import Config

class DataCollector:
    """Collects metrics data from various sources"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def collect_project_data(self, project_path: str, analysis_type: str = "full") -> Dict[str, Any]:
        """Collect comprehensive project data for analysis"""
        
        project_path = Path(project_path).resolve()
        
        data = {
            "project_info": self._get_project_info(project_path),
            "file_metrics": self._analyze_files(project_path),
            "dependency_analysis": self._analyze_dependencies(project_path),
            "git_metrics": self._get_git_metrics(project_path),
            "ecosystem_integration": self._check_ecosystem_integration(project_path),
            "timestamp": time.time(),
            "analysis_type": analysis_type
        }
        
        if analysis_type in ["full", "performance"]:
            data["performance_metrics"] = self._collect_performance_metrics(project_path)
        
        if analysis_type in ["full", "quality"]:
            data["quality_metrics"] = self._collect_quality_metrics(project_path)
            
        if analysis_type in ["full", "security"]:
            data["security_metrics"] = self._collect_security_metrics(project_path)
        
        return data
    
    def _get_project_info(self, project_path: Path) -> Dict[str, Any]:
        """Collect basic project information"""
        
        info = {
            "path": str(project_path),
            "name": project_path.name,
            "size_bytes": self._get_directory_size(project_path),
            "file_count": len(list(project_path.rglob("*"))),
            "programming_languages": self._detect_languages(project_path)
        }
        
        # Check for common files
        common_files = ["README.md", "requirements.txt", "package.json", "Dockerfile", ".gitignore"]
        info["has_files"] = {
            file: (project_path / file).exists() 
            for file in common_files
        }
        
        return info
    
    def _analyze_files(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project files for metrics"""
        
        metrics = {
            "total_files": 0,
            "code_files": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "empty_lines": 0,
            "file_types": {},
            "largest_files": [],
            "complexity_scores": []
        }
        
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'}
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                metrics["total_files"] += 1
                
                # Track file types
                ext = file_path.suffix.lower()
                metrics["file_types"][ext] = metrics["file_types"].get(ext, 0) + 1
                
                # Analyze code files
                if ext in code_extensions:
                    metrics["code_files"] += 1
                    file_metrics = self._analyze_file(file_path)
                    
                    metrics["total_lines"] += file_metrics["total_lines"]
                    metrics["code_lines"] += file_metrics["code_lines"]
                    metrics["comment_lines"] += file_metrics["comment_lines"]
                    metrics["empty_lines"] += file_metrics["empty_lines"]
                    
                    if file_metrics["complexity"] > 0:
                        metrics["complexity_scores"].append({
                            "file": str(file_path.relative_to(project_path)),
                            "complexity": file_metrics["complexity"]
                        })
                    
                    # Track largest files
                    metrics["largest_files"].append({
                        "file": str(file_path.relative_to(project_path)),
                        "lines": file_metrics["total_lines"],
                        "size_bytes": file_path.stat().st_size
                    })
        
        # Sort and limit largest files
        metrics["largest_files"] = sorted(
            metrics["largest_files"], 
            key=lambda x: x["lines"], 
            reverse=True
        )[:10]
        
        return metrics
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual file metrics"""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            return {"total_lines": 0, "code_lines": 0, "comment_lines": 0, "empty_lines": 0, "complexity": 0}
        
        total_lines = len(lines)
        code_lines = 0
        comment_lines = 0
        empty_lines = 0
        complexity = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                empty_lines += 1
            elif stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                comment_lines += 1
            else:
                code_lines += 1
                
                # Simple complexity calculation (control structures)
                complexity_keywords = ['if', 'for', 'while', 'try', 'except', 'catch', 'switch', 'case']
                for keyword in complexity_keywords:
                    if keyword in stripped.lower():
                        complexity += 1
        
        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "empty_lines": empty_lines,
            "complexity": complexity
        }
    
    def _analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies"""
        
        deps = {
            "python": self._get_python_dependencies(project_path),
            "node": self._get_node_dependencies(project_path),
            "docker": self._check_docker_config(project_path)
        }
        
        return deps
    
    def _get_python_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Get Python dependency information"""
        
        requirements_file = project_path / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                return {
                    "has_requirements": True,
                    "dependency_count": len(requirements),
                    "dependencies": requirements[:20]  # Limit for analysis
                }
            except Exception:
                pass
        
        return {"has_requirements": False, "dependency_count": 0, "dependencies": []}
    
    def _get_node_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Get Node.js dependency information"""
        
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                deps = package_data.get('dependencies', {})
                dev_deps = package_data.get('devDependencies', {})
                
                return {
                    "has_package_json": True,
                    "dependency_count": len(deps),
                    "dev_dependency_count": len(dev_deps),
                    "total_dependencies": len(deps) + len(dev_deps)
                }
            except Exception:
                pass
        
        return {"has_package_json": False, "dependency_count": 0}
    
    def _check_docker_config(self, project_path: Path) -> Dict[str, Any]:
        """Check Docker configuration"""
        
        dockerfile = project_path / "Dockerfile"
        docker_compose = project_path / "docker-compose.yml"
        
        return {
            "has_dockerfile": dockerfile.exists(),
            "has_docker_compose": docker_compose.exists(),
            "containerized": dockerfile.exists() or docker_compose.exists()
        }
    
    def _get_git_metrics(self, project_path: Path) -> Dict[str, Any]:
        """Collect Git repository metrics"""
        
        try:
            # Check if it's a git repository
            git_dir = project_path / ".git"
            if not git_dir.exists():
                return {"is_git_repo": False}
            
            # Get basic git info
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            commit_count = int(result.stdout.strip()) if result.returncode == 0 else 0
            
            # Get recent activity
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "10"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            recent_commits = len(result.stdout.strip().split('\n')) if result.returncode == 0 else 0
            
            return {
                "is_git_repo": True,
                "commit_count": commit_count,
                "recent_commits": recent_commits
            }
            
        except Exception:
            return {"is_git_repo": False}
    
    def _check_ecosystem_integration(self, project_path: Path) -> Dict[str, Any]:
        """Check integration with Automated Agile Framework components"""
        
        integration = {
            "standardized_framework": False,
            "codecreate_compatible": False,
            "codereview_configured": False,
            "github_actions": False
        }
        
        # Check for framework patterns
        if (project_path / "module.json").exists():
            integration["standardized_framework"] = True
        
        # Check for CodeCreate patterns
        codecreate_indicators = [
            ".github/workflows/codecreate.yml",
            "codecreate_config.json",
            "generated_by_codecreate.md"
        ]
        for indicator in codecreate_indicators:
            if (project_path / indicator).exists():
                integration["codecreate_compatible"] = True
                break
        
        # Check for CodeReview setup
        codereview_indicators = [
            ".github/workflows/codereview.yml",
            ".ai_review_cache"
        ]
        for indicator in codereview_indicators:
            if (project_path / indicator).exists():
                integration["codereview_configured"] = True
                break
        
        # Check for GitHub Actions
        github_actions_dir = project_path / ".github" / "workflows"
        if github_actions_dir.exists() and any(github_actions_dir.iterdir()):
            integration["github_actions"] = True
        
        return integration
    
    def _collect_performance_metrics(self, project_path: Path) -> Dict[str, Any]:
        """Collect performance-related metrics"""
        
        return {
            "estimated_startup_time": "unknown",
            "memory_footprint": "unknown",
            "api_endpoints": self._count_api_endpoints(project_path),
            "database_queries": "unknown"
        }
    
    def _collect_quality_metrics(self, project_path: Path) -> Dict[str, Any]:
        """Collect code quality metrics"""
        
        return {
            "test_coverage": self._estimate_test_coverage(project_path),
            "documentation_score": self._assess_documentation(project_path),
            "code_duplication": "unknown"
        }
    
    def _collect_security_metrics(self, project_path: Path) -> Dict[str, Any]:
        """Collect security-related metrics"""
        
        return {
            "security_files": self._count_security_files(project_path),
            "sensitive_patterns": self._scan_sensitive_patterns(project_path),
            "dependency_vulnerabilities": "unknown"
        }
    
    def _count_api_endpoints(self, project_path: Path) -> int:
        """Count potential API endpoints"""
        endpoint_count = 0
        
        for py_file in project_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Simple pattern matching for FastAPI/Flask routes
                    endpoint_count += content.count('@app.') + content.count('@router.')
            except Exception:
                continue
        
        return endpoint_count
    
    def _estimate_test_coverage(self, project_path: Path) -> str:
        """Estimate test coverage based on file structure"""
        
        test_files = list(project_path.rglob("test_*.py")) + list(project_path.rglob("*_test.py"))
        code_files = list(project_path.rglob("*.py"))
        
        if not code_files:
            return "no_code_files"
        
        coverage_ratio = len(test_files) / len(code_files)
        
        if coverage_ratio >= 0.8:
            return "high"
        elif coverage_ratio >= 0.5:
            return "medium"
        elif coverage_ratio >= 0.2:
            return "low"
        else:
            return "very_low"
    
    def _assess_documentation(self, project_path: Path) -> str:
        """Assess documentation quality"""
        
        doc_files = list(project_path.rglob("*.md")) + list(project_path.rglob("*.rst"))
        
        has_readme = (project_path / "README.md").exists()
        has_docs_dir = (project_path / "docs").exists()
        
        if has_readme and has_docs_dir and len(doc_files) >= 5:
            return "excellent"
        elif has_readme and len(doc_files) >= 3:
            return "good"
        elif has_readme:
            return "basic"
        else:
            return "poor"
    
    def _count_security_files(self, project_path: Path) -> int:
        """Count security-related files"""
        
        security_patterns = [
            "security.py", "auth.py", "authentication.py",
            "authorization.py", "permissions.py", "middleware.py"
        ]
        
        count = 0
        for pattern in security_patterns:
            count += len(list(project_path.rglob(pattern)))
        
        return count
    
    def _scan_sensitive_patterns(self, project_path: Path) -> List[str]:
        """Scan for potentially sensitive patterns"""
        
        sensitive_patterns = [
            "password", "secret", "token", "api_key", "private_key"
        ]
        
        findings = []
        
        for py_file in project_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    for pattern in sensitive_patterns:
                        if pattern in content and len(findings) < 10:  # Limit findings
                            findings.append(f"Found '{pattern}' pattern in {py_file.name}")
            except Exception:
                continue
        
        return findings
    
    def _get_directory_size(self, path: Path) -> int:
        """Calculate total directory size"""
        
        total_size = 0
        try:
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        
        return total_size
    
    def _detect_languages(self, project_path: Path) -> List[str]:
        """Detect programming languages in the project"""
        
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.html': 'HTML',
            '.css': 'CSS',
            '.sql': 'SQL'
        }
        
        found_languages = set()
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in language_extensions:
                    found_languages.add(language_extensions[ext])
        
        return sorted(list(found_languages))
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored in analysis"""
        
        ignore_patterns = [
            '.git', '__pycache__', 'node_modules', '.pytest_cache',
            '.venv', 'venv', '.env', 'build', 'dist'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)
