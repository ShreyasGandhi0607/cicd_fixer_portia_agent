#!/usr/bin/env python3
"""Test script for Portia integration in the CI/CD Fixer Agent."""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cicd_fixer.core.config import get_settings
from cicd_fixer.core.logging import get_logger
from cicd_fixer.services.portia_agent import portia_agent
from cicd_fixer.services.github_service import GitHubService
from cicd_fixer.services.gemini_agent import GeminiFixerAgent

logger = get_logger(__name__)


async def test_portia_agent():
    """Test the Portia agent functionality."""
    print("🧪 Testing Portia Agent Integration")
    print("=" * 50)
    
    try:
        # Test 1: Portia connection
        print("\n1️⃣ Testing Portia connection...")
        is_connected = portia_agent.test_portia_connection()
        if is_connected:
            print("✅ Portia connection successful")
        else:
            print("❌ Portia connection failed")
        
        # Test 2: Tool registry
        print("\n2️⃣ Testing tool registry...")
        if hasattr(portia_agent, 'tool_registry') and hasattr(portia_agent.tool_registry, 'tools'):
            tool_count = len(portia_agent.tool_registry.tools)
            print(f"✅ Tool registry available with {tool_count} tools")
            
            # List available tools
            print("Available tools:")
            for i, tool in enumerate(portia_agent.tool_registry.tools, 1):
                print(f"  {i}. {tool.name}: {tool.description}")
        else:
            print("❌ Tool registry not available")
        
        # Test 3: GitHub service
        print("\n3️⃣ Testing GitHub service...")
        github_service = GitHubService()
        github_connected = github_service.test_connection()
        if github_connected:
            print("✅ GitHub service connection successful")
        else:
            print("❌ GitHub service connection failed")
        
        # Test 4: Gemini agent
        print("\n4️⃣ Testing Gemini agent...")
        gemini_agent = GeminiFixerAgent()
        gemini_connected = gemini_agent.test_connection()
        if gemini_connected:
            print("✅ Gemini agent connection successful")
        else:
            print("❌ Gemini agent connection failed")
        
        # Test 5: Portia configuration
        print("\n5️⃣ Testing Portia configuration...")
        settings = get_settings()
        if settings.google_api_key:
            print("✅ Google API key configured")
        else:
            print("⚠️  Google API key not configured")
        
        if hasattr(portia_agent, 'config'):
            print(f"✅ Portia configuration available")
            print(f"   LLM Provider: {getattr(portia_agent.config, 'llm_provider', 'Unknown')}")
            print(f"   Storage Class: {getattr(portia_agent.config, 'storage_class', 'Unknown')}")
        else:
            print("❌ Portia configuration not available")
        
        # Test 6: Mock analysis (without actual API calls)
        print("\n6️⃣ Testing mock analysis...")
        try:
            # This would normally make API calls, so we'll just test the method exists
            if hasattr(portia_agent, 'analyze_ci_failure'):
                print("✅ analyze_ci_failure method available")
            else:
                print("❌ analyze_ci_failure method not available")
        except Exception as e:
            print(f"⚠️  Mock analysis test failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 Portia Integration Test Summary")
        print("=" * 50)
        
        # Summary
        tests_passed = 0
        total_tests = 6
        
        if is_connected:
            tests_passed += 1
        if hasattr(portia_agent, 'tool_registry'):
            tests_passed += 1
        if github_connected:
            tests_passed += 1
        if gemini_connected:
            tests_passed += 1
        if settings.google_api_key:
            tests_passed += 1
        if hasattr(portia_agent, 'config'):
            tests_passed += 1
        
        print(f"Tests Passed: {tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Portia integration is working correctly.")
        elif tests_passed >= total_tests * 0.8:
            print("✅ Most tests passed. Portia integration is mostly working.")
        else:
            print("⚠️  Several tests failed. Check your configuration.")
        
        return tests_passed == total_tests
        
    except Exception as e:
        logger.error(f"Portia integration test failed: {e}")
        print(f"❌ Test failed with error: {e}")
        return False


def test_environment():
    """Test environment configuration."""
    print("\n🔧 Environment Configuration Test")
    print("=" * 50)
    
    required_vars = [
        "GITHUB_TOKEN",
        "GOOGLE_API_KEY", 
        "GITHUB_WEBHOOK_SECRET",
        "SECRET_KEY"
    ]
    
    optional_vars = [
        "PORTIA_API_KEY",
        "PORTIA_ENVIRONMENT"
    ]
    
    print("Required Environment Variables:")
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"  ❌ {var}: Not set")
            missing_required.append(var)
    
    print("\nOptional Environment Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"  ⚠️  {var}: Not set (optional)")
    
    if missing_required:
        print(f"\n⚠️  Missing required environment variables: {', '.join(missing_required)}")
        print("   Please set these variables in your .env file")
        return False
    else:
        print("\n✅ All required environment variables are set")
        return True


def main():
    """Main test function."""
    print("🚀 CI/CD Fixer Agent - Portia Integration Test")
    print("=" * 60)
    
    # Test environment first
    env_ok = test_environment()
    
    if not env_ok:
        print("\n❌ Environment test failed. Please fix configuration issues first.")
        sys.exit(1)
    
    # Run Portia integration tests
    try:
        success = asyncio.run(test_portia_agent())
        
        if success:
            print("\n🎉 All tests completed successfully!")
            print("Your Portia integration is ready to use.")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
