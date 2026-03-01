#!/usr/bin/env python3
"""
Comprehensive Test Runner for Temporal Graph RAG System
Runs all tests and validates the system is working correctly.
"""

import asyncio
import sys
import os
import traceback
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from test_temporal_graph_rag import run_all_tests as run_core_tests
from test_discord_integration import run_integration_tests


class TestRunner:
    """Comprehensive test runner for the temporal Graph RAG system."""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
    
    async def run_test_suite(self, name: str, test_func):
        """Run a test suite and track results."""
        print(f"\n🧪 Running {name}...")
        print("-" * 40)
        
        try:
            await test_func()
            self.passed_tests += 1
            self.test_results.append((name, "PASSED", None))
            print(f"✅ {name} - PASSED")
        except Exception as e:
            self.failed_tests += 1
            error_msg = str(e)
            self.test_results.append((name, "FAILED", error_msg))
            print(f"❌ {name} - FAILED: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def run_sync_test_suite(self, name: str, test_func):
        """Run a synchronous test suite."""
        print(f"\n🧪 Running {name}...")
        print("-" * 40)
        
        try:
            test_func()
            self.passed_tests += 1
            self.test_results.append((name, "PASSED", None))
            print(f"✅ {name} - PASSED")
        except Exception as e:
            self.failed_tests += 1
            error_msg = str(e)
            self.test_results.append((name, "FAILED", error_msg))
            print(f"❌ {name} - FAILED: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def print_summary(self):
        """Print test summary."""
        total_tests = self.passed_tests + self.failed_tests
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Test Suites: {total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for name, status, error in self.test_results:
                if status == "FAILED":
                    print(f"  - {name}: {error}")
        
        print("\n📋 DETAILED RESULTS:")
        for name, status, _ in self.test_results:
            status_icon = "✅" if status == "PASSED" else "❌"
            print(f"  {status_icon} {name}")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Your temporal Graph RAG system is working perfectly!")
        else:
            print(f"\n⚠️ {self.failed_tests} test suite(s) failed. Please review and fix the issues.")


async def main():
    """Main test runner function."""
    
    print("🚀 Temporal Graph RAG System Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    runner = TestRunner()
    
    # Run core temporal Graph RAG tests
    await runner.run_test_suite("Core Temporal Graph RAG Tests", run_core_tests)
    
    # Run integration tests
    await runner.run_test_suite("Integration & Real-World Tests", run_integration_tests)
    
    # Print final summary
    runner.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if runner.failed_tests == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
