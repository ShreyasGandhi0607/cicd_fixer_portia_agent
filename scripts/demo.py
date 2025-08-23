#!/usr/bin/env python3
"""Demo script for the CI/CD Fixer Agent with Portia integration."""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cicd_fixer.services.portia_agent import portia_agent
from cicd_fixer.services.github_service import GitHubService
from cicd_fixer.services.gemini_agent import GeminiFixerAgent
from cicd_fixer.analytics.pattern_analyzer import CICDPatternAnalyzer
from cicd_fixer.analytics.intelligent_generator import IntelligentFixGenerator

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)


def print_section(title):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)


async def demo_portia_agent():
    """Demonstrate Portia agent capabilities."""
    print_header("Portia Agent Demo")
    
    print_section("Testing Portia Connection")
    try:
        is_connected = portia_agent.test_portia_connection()
        if is_connected:
            print("✅ Portia agent is connected and ready")
        else:
            print("❌ Portia agent connection failed")
            return False
    except Exception as e:
        print(f"❌ Error testing Portia connection: {e}")
        return False
    
    print_section("Available Tools")
    if hasattr(portia_agent, 'tool_registry') and hasattr(portia_agent.tool_registry, 'tools'):
        tools = portia_agent.tool_registry.tools
        print(f"Found {len(tools)} registered tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.name}")
            print(f"     Description: {tool.description}")
            print(f"     Parameters: {len(tool.parameters)}")
    else:
        print("❌ No tools registry available")
        return False
    
    print_section("Portia Configuration")
    if hasattr(portia_agent, 'config'):
        config = portia_agent.config
        print(f"LLM Provider: {getattr(config, 'llm_provider', 'Unknown')}")
        print(f"Storage Class: {getattr(config, 'storage_class', 'Unknown')}")
        print(f"Argument Clarifications: {getattr(config, 'argument_clarifications_enabled', 'Unknown')}")
    else:
        print("❌ No configuration available")
    
    return True


def demo_github_service():
    """Demonstrate GitHub service capabilities."""
    print_header("GitHub Service Demo")
    
    print_section("Testing GitHub Connection")
    try:
        github_service = GitHubService()
        is_connected = github_service.test_connection()
        if is_connected:
            print("✅ GitHub service is connected")
        else:
            print("❌ GitHub service connection failed")
            return False
    except Exception as e:
        print(f"❌ Error testing GitHub service: {e}")
        return False
    
    print_section("GitHub Service Features")
    print("Available methods:")
    print("  - get_workflow_run(owner, repo, run_id)")
    print("  - get_workflow_run_logs(owner, repo, run_id)")
    print("  - get_workflow_jobs(owner, repo, run_id)")
    print("  - create_issue(owner, repo, title, body, labels)")
    print("  - create_pull_request(owner, repo, title, body, head, base)")
    
    return True


def demo_gemini_agent():
    """Demonstrate Gemini agent capabilities."""
    print_header("Gemini AI Agent Demo")
    
    print_section("Testing Gemini Connection")
    try:
        gemini_agent = GeminiFixerAgent()
        is_connected = gemini_agent.test_connection()
        if is_connected:
            print("✅ Gemini agent is connected")
        else:
            print("❌ Gemini agent connection failed")
            return False
    except Exception as e:
        print(f"❌ Error testing Gemini agent: {e}")
        return False
    
    print_section("Gemini Agent Features")
    print("Available methods:")
    print("  - analyze_failure_and_suggest_fix(error_logs, repo_context)")
    print("  - _build_analysis_prompt(error_logs, repo_context)")
    print("  - _parse_gemini_response(response_text)")
    print("  - _analyze_with_fallback(error_logs, repo_context)")
    
    return True


def demo_analytics():
    """Demonstrate analytics capabilities."""
    print_header("Analytics Demo")
    
    print_section("Pattern Analyzer")
    try:
        pattern_analyzer = CICDPatternAnalyzer()
        print("✅ Pattern analyzer initialized")
        
        # Get pattern summary
        summary = pattern_analyzer.get_pattern_summary()
        print(f"Pattern Summary: {summary}")
        
    except Exception as e:
        print(f"❌ Error initializing pattern analyzer: {e}")
        return False
    
    print_section("Intelligent Fix Generator")
    try:
        fix_generator = IntelligentFixGenerator()
        print("✅ Intelligent fix generator initialized")
        
        # Get fix statistics
        stats = fix_generator.get_fix_statistics()
        print(f"Fix Statistics: {stats}")
        
    except Exception as e:
        print(f"❌ Error initializing fix generator: {e}")
        return False
    
    return True


def demo_mock_analysis():
    """Demonstrate a mock CI/CD failure analysis."""
    print_header("Mock CI/CD Failure Analysis Demo")
    
    print_section("Sample Error Log")
    sample_error = """
    ##[group]Run actions/checkout@v4
    ##[command]git -c http.extraheader="AUTHORIZATION: basic ***" fetch --tags --force --prune --prune-tag --progress --no-recurse-submodules --no-shallow --depth=1 origin +refs/heads/main:refs/remotes/origin/main +refs/pull/123/merge:refs/remotes/pull/123/merge
    ##[error]fatal: unable to access 'https://github.com/owner/repo.git/': The requested URL returned error: 403
    ##[endgroup]
    ##[error]Git checkout failed
    ##[error]Exit code: 128
    ##[group]Run actions/setup-node@v4
    ##[command]node --version
    v18.17.0
    ##[command]npm --version
    9.6.7
    ##[endgroup]
    ##[group]Run npm ci
    ##[command]npm ci
    ##[error]npm ERR! code ENOENT
    ##[error]npm ERR! syscall open
    ##[error]npm ERR! path /home/runner/work/repo/repo/package.json
    ##[error]npm ERR! errno -2
    ##[error]npm ERR! enoent ENOENT: no such file or directory, open 'package.json'
    ##[error]npm ERR! enoent This is related to npm not being able to find a file.
    ##[error]npm ERR! enoent
    ##[error]npm ERR! A complete log of this run can be found at:
    ##[error]npm ERR!     /home/runner/.npm/_logs/2023-08-23T10_00_00_000Z-debug-0.log
    ##[endgroup]
    ##[error]Process completed with exit code 1.
    """
    
    print("Sample CI/CD failure log:")
    print(sample_error[:200] + "...")
    
    print_section("Error Classification")
    try:
        from cicd_fixer.tools.registry import classify_error_type_tool
        tool = classify_error_type_tool()
        error_type = tool.function(sample_error)
        print(f"Classified Error Type: {error_type}")
    except Exception as e:
        print(f"❌ Error classification failed: {e}")
    
    print_section("Fix Generation")
    try:
        from cicd_fixer.tools.registry import generate_fix_suggestion_tool
        tool = generate_fix_suggestion_tool()
        fix_suggestion = tool.function(
            error_type="dependency_error",
            error_logs=sample_error,
            context={"language": "javascript", "framework": "node"}
        )
        print("Generated Fix Suggestion:")
        print(f"  Description: {fix_suggestion['description']}")
        print(f"  Confidence: {fix_suggestion['confidence']}")
        print(f"  Estimated Time: {fix_suggestion['estimated_time']}")
        print(f"  Steps: {len(fix_suggestion['steps'])} steps")
    except Exception as e:
        print(f"❌ Fix generation failed: {e}")
    
    return True


async def main():
    """Main demo function."""
    print("🚀 CI/CD Fixer Agent - Portia Integration Demo")
    print("=" * 60)
    print("This demo showcases the capabilities of the CI/CD Fixer Agent")
    print("with Portia AI framework integration.")
    print("=" * 60)
    
    demos = [
        ("Portia Agent", demo_portia_agent),
        ("GitHub Service", demo_github_service),
        ("Gemini AI Agent", demo_gemini_agent),
        ("Analytics", demo_analytics),
        ("Mock Analysis", demo_mock_analysis)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n🎬 Running {demo_name} demo...")
            if asyncio.iscoroutinefunction(demo_func):
                result = await demo_func()
            else:
                result = demo_func()
            results.append((demo_name, result))
            
            if result:
                print(f"✅ {demo_name} demo completed successfully")
            else:
                print(f"❌ {demo_name} demo failed")
                
        except Exception as e:
            print(f"❌ {demo_name} demo failed with error: {e}")
            results.append((demo_name, False))
    
    # Summary
    print_header("Demo Summary")
    successful_demos = sum(1 for _, result in results if result)
    total_demos = len(results)
    
    print(f"Successful Demos: {successful_demos}/{total_demos}")
    
    for demo_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {demo_name}")
    
    if successful_demos == total_demos:
        print("\n🎉 All demos completed successfully!")
        print("Your CI/CD Fixer Agent with Portia integration is working perfectly!")
    elif successful_demos >= total_demos * 0.8:
        print("\n✅ Most demos completed successfully!")
        print("Your integration is mostly working. Check failed demos for issues.")
    else:
        print("\n⚠️  Several demos failed.")
        print("Please check your configuration and dependencies.")
    
    print("\n🚀 Next Steps:")
    print("1. Start the server: ./start.sh")
    print("2. Access the API: http://localhost:8000")
    print("3. View documentation: http://localhost:8000/docs")
    print("4. Test Portia endpoints: http://localhost:8000/api/v1/portia/test")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed with unexpected error: {e}")
        sys.exit(1)
