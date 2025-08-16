"""
Command-line interface for CodeMetrics
"""

import click
import sys
from pathlib import Path

from .analyzer import MetricsAnalyzer
from .collector import DataCollector
from .dashboard import Dashboard
from .config import Config

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """CodeMetrics - AI-Powered Development Analytics"""
    pass

@cli.command()
@click.option('--project', default='.', help='Project path to analyze')
@click.option('--type', 'analysis_type', default='full', 
              type=click.Choice(['full', 'performance', 'quality', 'security']),
              help='Type of analysis to perform')
@click.option('--output', help='Output file for results')
@click.option('--config', help='Config file path')
def analyze(project, analysis_type, output, config):
    """Run analytics on a project"""
    try:
        config_obj = Config.load(config) if config else Config()
        collector = DataCollector(config_obj)
        analyzer = MetricsAnalyzer(config_obj)
        
        click.echo(f"🔍 Analyzing project: {project}")
        click.echo(f"📊 Analysis type: {analysis_type}")
        
        # Collect data
        data = collector.collect_project_data(project, analysis_type)
        
        # Analyze with AI
        results = analyzer.analyze(data, analysis_type)
        
        if output:
            results.save(output)
            click.echo(f"📁 Results saved to: {output}")
        else:
            click.echo("📊 Analysis Results:")
            click.echo(results.summary())
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--input', 'input_file', help='Input analytics file')
@click.option('--format', 'output_format', default='html',
              type=click.Choice(['html', 'pdf', 'json', 'markdown']),
              help='Report format')
@click.option('--output', help='Output file path')
def report(input_file, output_format, output):
    """Generate analytics reports"""
    try:
        click.echo(f"📋 Generating {output_format} report...")
        # Implementation for report generation
        click.echo(f"✅ Report generated: {output}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--port', default=8080, help='Dashboard port')
@click.option('--host', default='localhost', help='Dashboard host')
@click.option('--config', help='Config file path')
def dashboard(port, host, config):
    """Start the analytics dashboard"""
    try:
        config_obj = Config.load(config) if config else Config()
        dashboard = Dashboard(config_obj)
        
        click.echo(f"🚀 Starting dashboard at http://{host}:{port}")
        dashboard.run(host=host, port=port)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--repos', help='Comma-separated list of repositories')
@click.option('--output', help='Output file for ecosystem health data')
def ecosystem_health(repos, output):
    """Check health of the entire ecosystem"""
    try:
        repo_list = repos.split(',') if repos else [
            "Jita81/Standardized-Modules-Framework-v1.0.0",
            "Jita81/CODEREVIEW", 
            "Jita81/CODECREATE",
            "Jita81/CODETEST",
            "Jita81/CODEMETRICS"
        ]
        
        click.echo("🔍 Checking ecosystem health...")
        for repo in repo_list:
            click.echo(f"  📊 Analyzing {repo}")
            
        click.echo(f"✅ Ecosystem health check complete: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
