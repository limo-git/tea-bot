#!/usr/bin/env python3
"""
Simple Test Runner for Temporal Graph RAG System (No pytest required)
"""

import asyncio
import sys
import os
import traceback
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from retrieval.query_engine import understand_query, run_query_pipeline
from retrieval.context_assembler import assemble_context
from generation.answer_generator import generate_answer


class SimpleTestRunner:
    """Simple test runner without external dependencies."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    def assert_equal(self, actual, expected, message=""):
        """Simple assertion helper."""
        if actual != expected:
            raise AssertionError(f"{message}: Expected {expected}, got {actual}")
    
    def assert_true(self, condition, message=""):
        """Simple boolean assertion."""
        if not condition:
            raise AssertionError(f"{message}: Expected True, got False")
    
    def assert_in(self, item, container, message=""):
        """Simple 'in' assertion."""
        if item not in container:
            raise AssertionError(f"{message}: {item} not found in {container}")
    
    async def run_test(self, test_name, test_func):
        """Run a single test function."""
        print(f"  🧪 {test_name}...")
        try:
            await test_func()
            print(f"    ✅ PASSED")
            self.passed += 1
            self.test_results.append((test_name, "PASSED", None))
        except Exception as e:
            print(f"    ❌ FAILED: {e}")
            self.failed += 1
            self.test_results.append((test_name, "FAILED", str(e)))
    
    def run_sync_test(self, test_name, test_func):
        """Run a synchronous test function."""
        print(f"  🧪 {test_name}...")
        try:
            test_func()
            print(f"    ✅ PASSED")
            self.passed += 1
            self.test_results.append((test_name, "PASSED", None))
        except Exception as e:
            print(f"    ❌ FAILED: {e}")
            self.failed += 1
            self.test_results.append((test_name, "FAILED", str(e)))
    
    async def test_query_understanding(self):
        """Test query understanding with temporal context detection."""
        
        # Mock Gemini client
        with patch('retrieval.query_engine._get_client') as mock_client:
            mock_response = Mock()
            mock_response.text = json.dumps({
                "intent": "temporal_context",
                "primary_entity": "deployment",
                "temporal_context_needed": True,
                "time_scope": "weeks"
            })
            mock_client.return_value.models.generate_content.return_value = mock_response
            
            # Test temporal context query
            result = await understand_query("What's the background context on the deployment issue?")
            
            self.assert_equal(result["intent"], "temporal_context")
            self.assert_true(result["temporal_context_needed"])
            self.assert_equal(result["primary_entity"], "deployment")
    
    def test_context_assembly(self):
        """Test context assembly with temporal metadata."""
        
        graph_results = [
            {
                "content": "Primary message",
                "timestamp": "2026-03-01T14:00:00Z",
                "author": "limo.ew",
                "channel": "dev-ops",
                "related_discussions": [
                    {
                        "content": "Related message from yesterday",
                        "timestamp": "2026-02-28T14:00:00Z",
                        "author": "sidtheitguy",
                        "channel": "dev-ops",
                        "time_gap": 1
                    }
                ]
            }
        ]
        
        vector_results = [
            {
                "content": "Vector result",
                "author_name": "quantadude",
                "channel_id": "123456",
                "created_at": "2026-03-01T15:00:00Z",
                "similarity": 0.8
            }
        ]
        
        context = assemble_context(graph_results, vector_results, "temporal_context")
        
        # Should have primary message + related discussion + vector result
        self.assert_true(len(context) >= 3)
        
        # Check temporal metadata
        temporal_items = [item for item in context if item.get("temporal_context")]
        self.assert_true(len(temporal_items) > 0)
        
        # Check that related discussion has temporal metadata
        related_item = next((item for item in context 
                           if item.get("temporal_context", {}).get("context_type") == "related_discussion"), None)
        self.assert_true(related_item is not None)
        self.assert_equal(related_item["temporal_context"]["time_gap_days"], 1)
    
    async def test_answer_generation(self):
        """Test answer generation with temporal context."""
        
        pipeline_result = {
            "context": [
                {
                    "source": "graph",
                    "content": "Deployment started successfully",
                    "author": "limo.ew",
                    "channel": "dev-ops",
                    "timestamp": "2026-03-01T14:00:00Z",
                    "temporal_context": {
                        "context_type": "primary",
                        "related_to_entity": "deployment"
                    }
                }
            ],
            "understanding": {
                "intent": "temporal_context",
                "primary_entity": "deployment"
            },
            "temporal_connections": 1,
            "conversation_threads": 0
        }
        
        with patch('generation.answer_generator._get_client') as mock_client:
            mock_response = Mock()
            mock_response.text = "Based on the temporal context, the deployment was successfully executed by limo.ew in #dev-ops."
            mock_client.return_value.models.generate_content.return_value = mock_response
            
            answer = await generate_answer(
                query="What's the context behind the deployment?",
                pipeline_result=pipeline_result,
                user_name="test_user"
            )
            
            self.assert_true(len(answer) > 0)
            self.assert_in("deployment", answer.lower())
            self.assert_in("limo.ew", answer)
    
    async def test_temporal_pipeline_integration(self):
        """Test temporal pipeline integration."""
        
        query = "What's the background on the server migration project?"
        
        # Mock query understanding
        understanding = {
            "intent": "temporal_context",
            "primary_entity": "server migration",
            "temporal_context_needed": True,
            "search_terms": ["server", "migration", "project"]
        }
        
        # Mock the complete pipeline
        with patch('retrieval.query_engine.understand_query', return_value=understanding), \
             patch('retrieval.temporal_engine.run_temporal_query_pipeline') as mock_temporal:
            
            mock_temporal.return_value = {
                "context": [
                    {
                        "source": "graph",
                        "content": "Server migration completed successfully",
                        "author": "limo.ew",
                        "timestamp": "2026-03-01T16:00:00Z",
                        "temporal_context": {
                            "context_type": "primary"
                        }
                    }
                ],
                "understanding": understanding,
                "temporal_connections": 2,
                "conversation_threads": 1
            }
            
            result = await run_query_pipeline(
                query=query,
                server_id=12345
            )
            
            self.assert_in("context", result)
            self.assert_equal(result["temporal_connections"], 2)
            self.assert_equal(result["conversation_threads"], 1)
            
            # Verify temporal pipeline was called
            mock_temporal.assert_called_once()
    
    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for name, status, error in self.test_results:
                if status == "FAILED":
                    print(f"  - {name}: {error}")
        
        print("\n📋 DETAILED RESULTS:")
        for name, status, _ in self.test_results:
            status_icon = "✅" if status == "PASSED" else "❌"
            print(f"  {status_icon} {name}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! Your temporal Graph RAG system is working perfectly!")
        else:
            print(f"\n⚠️ {self.failed} test(s) failed. Please review and fix the issues.")


async def main():
    """Main test function."""
    
    print("🧪 Simple Temporal Graph RAG Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    runner = SimpleTestRunner()
    
    print("\n📝 Testing Query Understanding...")
    await runner.run_test("Temporal Context Detection", runner.test_query_understanding)
    
    print("\n🔧 Testing Context Assembly...")
    runner.run_sync_test("Temporal Context Assembly", runner.test_context_assembly)
    
    print("\n💬 Testing Answer Generation...")
    await runner.run_test("Temporal Answer Generation", runner.test_answer_generation)
    
    print("\n🔗 Testing Integration...")
    await runner.run_test("Temporal Pipeline Integration", runner.test_temporal_pipeline_integration)
    
    runner.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if runner.failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
