"""
Web dashboard for CodeMetrics analytics
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
except ImportError:
    Flask = None
    print("Flask not installed. Dashboard functionality requires: pip install flask")

from .config import Config
from .collector import DataCollector
from .analyzer import MetricsAnalyzer

class Dashboard:
    """Web-based analytics dashboard"""
    
    def __init__(self, config: Config):
        self.config = config
        self.app = None
        self.collector = DataCollector(config)
        self.analyzer = MetricsAnalyzer(config)
        
        if Flask:
            self._setup_flask_app()
    
    def _setup_flask_app(self):
        """Initialize Flask application"""
        
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        
        # Main dashboard route
        @self.app.route('/')
        def dashboard():
            return self._render_dashboard()
        
        # API routes
        @self.app.route('/api/analyze', methods=['POST'])
        def api_analyze():
            return self._api_analyze()
        
        @self.app.route('/api/metrics/<project_name>')
        def api_metrics(project_name):
            return self._api_get_metrics(project_name)
        
        @self.app.route('/api/ecosystem-health')
        def api_ecosystem_health():
            return self._api_ecosystem_health()
        
        # Static file serving
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            return send_from_directory('static', filename)
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """Start the dashboard server"""
        
        if not self.app:
            raise RuntimeError("Flask not available. Install with: pip install flask")
        
        host = host or self.config.dashboard_host
        port = port or self.config.dashboard_port
        debug = debug or self.config.dashboard_debug
        
        print(f"🚀 CodeMetrics Dashboard starting at http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    def _render_dashboard(self) -> str:
        """Render the main dashboard page"""
        
        # For now, return a simple HTML page
        # In a full implementation, this would use proper templates
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeMetrics Dashboard</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: #f5f5f5;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
        }}
        .metrics-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px; margin-bottom: 20px;
        }}
        .metric-card {{ 
            background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .score {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .ecosystem-status {{ 
            background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .status-item {{ 
            display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee;
        }}
        .status-active {{ color: #4CAF50; }}
        .status-pending {{ color: #FF9800; }}
        button {{
            background: #667eea; color: white; border: none; padding: 10px 20px;
            border-radius: 5px; cursor: pointer; margin: 5px;
        }}
        button:hover {{ background: #5a6fd8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 CodeMetrics Dashboard</h1>
        <p>AI-Powered Development Analytics for the Automated Agile Framework</p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <h3>🚀 Performance Score</h3>
            <div class="score" id="performance-score">Loading...</div>
            <p>Current system performance metrics</p>
        </div>
        
        <div class="metric-card">
            <h3>🔍 Quality Score</h3>
            <div class="score" id="quality-score">Loading...</div>
            <p>Code quality and maintainability</p>
        </div>
        
        <div class="metric-card">
            <h3>🛡️ Security Score</h3>
            <div class="score" id="security-score">Loading...</div>
            <p>Security compliance and best practices</p>
        </div>
        
        <div class="metric-card">
            <h3>📈 Ecosystem Health</h3>
            <div class="score" id="ecosystem-health">Loading...</div>
            <p>Overall framework integration status</p>
        </div>
    </div>
    
    <div class="ecosystem-status">
        <h3>🏗️ Automated Agile Framework Status</h3>
        
        <div class="status-item">
            <span>🏗️ Standardized Modules Framework</span>
            <span class="status-active">✅ Active</span>
        </div>
        
        <div class="status-item">
            <span>🤖 CodeCreate (Claude 4 Generation)</span>
            <span class="status-active">✅ Active</span>
        </div>
        
        <div class="status-item">
            <span>🔍 CodeReview (AI Quality Analysis)</span>
            <span class="status-active">✅ Active</span>
        </div>
        
        <div class="status-item">
            <span>🧪 CodeTest (Framework Testing)</span>
            <span class="status-active">✅ Active</span>
        </div>
        
        <div class="status-item">
            <span>📊 CodeMetrics (This Dashboard)</span>
            <span class="status-active">✅ Active</span>
        </div>
    </div>
    
    <div style="margin-top: 20px; text-align: center;">
        <button onclick="runAnalysis()">🔍 Run New Analysis</button>
        <button onclick="generateReport()">📋 Generate Report</button>
        <button onclick="refreshMetrics()">🔄 Refresh Metrics</button>
    </div>
    
    <script>
        // Load initial metrics
        refreshMetrics();
        
        function refreshMetrics() {{
            // Simulate loading metrics - in real implementation, this would call the API
            setTimeout(() => {{
                document.getElementById('performance-score').textContent = '87';
                document.getElementById('quality-score').textContent = '92';
                document.getElementById('security-score').textContent = '89';
                document.getElementById('ecosystem-health').textContent = '94';
            }}, 1000);
        }}
        
        function runAnalysis() {{
            alert('🔍 Starting analysis... This feature will trigger the analytics engine.');
        }}
        
        function generateReport() {{
            alert('📋 Generating report... This will create a comprehensive analytics report.');
        }}
        
        // Auto-refresh every 30 seconds
        setInterval(refreshMetrics, 30000);
    </script>
</body>
</html>
        """
    
    def _api_analyze(self) -> Dict[str, Any]:
        """API endpoint for running analysis"""
        
        try:
            data = request.get_json()
            project_path = data.get('project_path', '.')
            analysis_type = data.get('analysis_type', 'full')
            
            # Collect data and analyze
            project_data = self.collector.collect_project_data(project_path, analysis_type)
            results = self.analyzer.analyze(project_data, analysis_type)
            
            return jsonify({
                'success': True,
                'results': {
                    'performance_score': results.performance_score,
                    'quality_score': results.quality_score,
                    'security_score': results.security_score,
                    'key_findings': results.key_findings,
                    'recommendations': results.recommendations,
                    'timestamp': results.timestamp
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def _api_get_metrics(self, project_name: str) -> Dict[str, Any]:
        """API endpoint for getting project metrics"""
        
        # In a real implementation, this would load from cache/database
        return jsonify({
            'project_name': project_name,
            'metrics': {
                'performance_score': 87,
                'quality_score': 92,
                'security_score': 89,
                'last_updated': time.time()
            }
        })
    
    def _api_ecosystem_health(self) -> Dict[str, Any]:
        """API endpoint for ecosystem health check"""
        
        # Simulate ecosystem health check
        health_data = {
            'overall_health': 94,
            'components': {
                'standardized_framework': {
                    'status': 'active',
                    'health_score': 95,
                    'last_activity': time.time() - 3600  # 1 hour ago
                },
                'codecreate': {
                    'status': 'active',
                    'health_score': 92,
                    'last_activity': time.time() - 1800  # 30 minutes ago
                },
                'codereview': {
                    'status': 'active', 
                    'health_score': 97,
                    'last_activity': time.time() - 900   # 15 minutes ago
                },
                'codetest': {
                    'status': 'active',
                    'health_score': 90,
                    'last_activity': time.time() - 1200  # 20 minutes ago
                },
                'codemetrics': {
                    'status': 'active',
                    'health_score': 93,
                    'last_activity': time.time()         # Now
                }
            },
            'integration_score': 91,
            'performance_trends': 'improving',
            'last_check': time.time()
        }
        
        return jsonify(health_data)
    
    def generate_static_report(self, analysis_results: Dict[str, Any], output_path: str) -> None:
        """Generate a static HTML report"""
        
        report_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeMetrics Analysis Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .scores {{ display: flex; justify-content: space-around; margin: 40px 0; }}
        .score-card {{ text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
        .score {{ font-size: 3em; font-weight: bold; color: #667eea; }}
        .findings, .recommendations {{ margin: 30px 0; }}
        .findings h3, .recommendations h3 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 CodeMetrics Analysis Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="scores">
        <div class="score-card">
            <div class="score">{analysis_results.get('performance_score', 0)}</div>
            <h4>Performance Score</h4>
        </div>
        <div class="score-card">
            <div class="score">{analysis_results.get('quality_score', 0)}</div>
            <h4>Quality Score</h4>
        </div>
        <div class="score-card">
            <div class="score">{analysis_results.get('security_score', 0)}</div>
            <h4>Security Score</h4>
        </div>
    </div>
    
    <div class="findings">
        <h3>🔍 Key Findings</h3>
        <ul>
            {''.join(f'<li>{finding}</li>' for finding in analysis_results.get('key_findings', []))}
        </ul>
    </div>
    
    <div class="recommendations">
        <h3>💡 Recommendations</h3>
        <ul>
            {''.join(f'<li>{rec}</li>' for rec in analysis_results.get('recommendations', []))}
        </ul>
    </div>
</body>
</html>
        """
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report_html)
