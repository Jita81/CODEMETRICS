#!/usr/bin/env python3
"""
Example: Running the Ecosystem Intelligence Loop

This example demonstrates how to use the EcosystemIntelligenceLoop to:
1. Monitor feedback from CodeCreate, CodeReview, and CodeTest
2. Identify improvement opportunities using Claude
3. Test multiple improvement iterations
4. Select and recommend the best improvements

Prerequisites:
- Set ANTHROPIC_API_KEY environment variable
- Set GITHUB_TOKEN environment variable (optional)
- Have a git repository to test improvements on
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import codemetrics
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codemetrics.config import Config
from codemetrics.intelligence_loop import EcosystemIntelligenceLoop

async def run_intelligence_loop_example():
    """Run the intelligence loop example"""
    
    print("🧠 Ecosystem Intelligence Loop Example")
    print("=" * 50)
    
    # Check for required environment variables
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY environment variable is required")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    # Load configuration
    try:
        config = Config.load()
        print(f"✅ Configuration loaded")
        print(f"   Model: {config.model}")
        print(f"   Max tokens: {config.max_tokens}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Initialize intelligence loop
    try:
        intelligence_loop = EcosystemIntelligenceLoop(config)
        print(f"✅ Intelligence loop initialized")
    except Exception as e:
        print(f"❌ Failed to initialize intelligence loop: {e}")
        return
    
    # Set the target repository (current directory by default)
    repo_path = os.getcwd()
    print(f"🎯 Target repository: {repo_path}")
    
    # Configure the loop
    intelligence_loop.max_iterations = 5  # Reduced for example
    intelligence_loop.analysis_window_days = 7  # Shorter window for example
    
    print("\n🚀 Running Intelligence Loop...")
    print("-" * 30)
    
    try:
        # Run the intelligence loop
        results = await intelligence_loop.run_intelligence_loop(repo_path)
        
        # Display results
        print("\n📊 Intelligence Loop Results")
        print("=" * 30)
        
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        report = results.get("intelligence_loop_report", {})
        
        # Execution summary
        summary = report.get("execution_summary", {})
        print(f"🔍 Feedback sources analyzed: {summary.get('feedback_sources_analyzed', 0)}")
        print(f"💡 Improvement candidates: {summary.get('improvement_candidates_generated', 0)}")
        print(f"🧪 Iterations tested: {summary.get('iterations_tested', 0)}")
        print(f"🏆 Successful improvements: {summary.get('successful_improvements_found', 0)}")
        
        # Best improvements
        best_improvements = report.get("best_improvements", [])
        if best_improvements:
            print(f"\n🏆 Top {len(best_improvements)} Improvements:")
            for improvement in best_improvements:
                print(f"  #{improvement['rank']}: {improvement['description'][:80]}...")
                print(f"    Process: {improvement['process_type']}")
                print(f"    Success Score: {improvement['success_score']:.2f}")
                print(f"    Branch: {improvement['branch_name']}")
                print()
        
        # Next steps
        next_steps = report.get("next_steps", [])
        if next_steps:
            print("📋 Recommended Next Steps:")
            for i, step in enumerate(next_steps, 1):
                print(f"  {i}. {step}")
        
        print("\n✅ Intelligence loop completed successfully!")
        
        # Optionally save results
        output_file = "intelligence_loop_results.json"
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Intelligence loop failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    # Run the async example
    try:
        asyncio.run(run_intelligence_loop_example())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
