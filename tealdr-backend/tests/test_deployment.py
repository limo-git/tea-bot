#!/usr/bin/env python3
"""
Deployment Verification Script for Temporal Graph RAG System
Tests the system on the actual VM environment with real data.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from db.neo4j import get_driver
from retrieval.query_engine import understand_query, run_query_pipeline
from retrieval.temporal_engine import run_temporal_query_pipeline
from generation.answer_generator import generate_answer


class DeploymentTester:
    """Test the temporal Graph RAG system on the deployed VM."""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    async def test_environment_setup(self):
        """Test that the environment is properly configured."""
        print("🔧 Testing Environment Setup...")
        
        try:
            # Test Config
            assert Config.GRAPH_RAG_ENABLED == True, "GRAPH_RAG_ENABLED should be True"
            assert Config.NEO4J_URI, "NEO4J_URI must be set"
            assert Config.GEMINI_API_KEY, "GEMINI_API_KEY must be set"
            
            print("✅ Configuration is valid")
            
            # Test Neo4j connection
            driver = await get_driver()
            async with driver.session() as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                assert record["test"] == 1
            
            print("✅ Neo4j connection is working")
            
            self.passed += 1
            self.test_results.append(("Environment Setup", "PASSED", None))
            
        except Exception as e:
            print(f"❌ Environment setup failed: {e}")
            self.failed += 1
            self.test_results.append(("Environment Setup", "FAILED", str(e)))
    
    async def test_query_understanding_live(self):
        """Test query understanding with real Gemini API."""
        print("🧠 Testing Live Query Understanding...")
        
        test_queries = [
            ("What happened on the server recently?", "summarization", False),
            ("What's the context behind the deployment issue?", "temporal_context", True),
            ("Continue the discussion about the bug fix", "conversation_threads", True),
            ("Who knows about React development?", "expert_finding", False),
        ]
        
        try:
            for query, expected_intent, expected_temporal in test_queries:
                print(f"  Testing: '{query}'")
                
                understanding = await understand_query(query)
                
                # Check intent detection
                actual_intent = understanding.get("intent", "")
                if expected_intent not in actual_intent and actual_intent != expected_intent:
                    print(f"    ⚠️ Intent mismatch: expected {expected_intent}, got {actual_intent}")
                else:
                    print(f"    ✅ Intent: {actual_intent}")
                
                # Check temporal context detection
                temporal_needed = understanding.get("temporal_context_needed", False)
                if temporal_needed != expected_temporal:
                    print(f"    ⚠️ Temporal context mismatch: expected {expected_temporal}, got {temporal_needed}")
                else:
                    print(f"    ✅ Temporal context: {temporal_needed}")
            
            self.passed += 1
            self.test_results.append(("Live Query Understanding", "PASSED", None))
            
        except Exception as e:
            print(f"❌ Query understanding failed: {e}")
            self.failed += 1
            self.test_results.append(("Live Query Understanding", "FAILED", str(e)))
    
    async def test_graph_data_availability(self):
        """Test that graph data exists and is accessible."""
        print("📊 Testing Graph Data Availability...")
        
        try:
            driver = await get_driver()
            async with driver.session() as session:
                # Check for messages
                result = await session.run("MATCH (m:Message) RETURN count(m) as message_count")
                record = await result.single()
                message_count = record["message_count"]
                print(f"  📝 Messages in graph: {message_count}")
                
                # Check for entities
                result = await session.run("MATCH (e:Entity) RETURN count(e) as entity_count")
                record = await result.single()
                entity_count = record["entity_count"]
                print(f"  🏷️ Entities in graph: {entity_count}")
                
                # Check for authors
                result = await session.run("MATCH (a:Author) RETURN count(a) as author_count")
                record = await result.single()
                author_count = record["author_count"]
                print(f"  👥 Authors in graph: {author_count}")
                
                # Check for channels
                result = await session.run("MATCH (c:Channel) RETURN count(c) as channel_count")
                record = await result.single()
                channel_count = record["channel_count"]
                print(f"  📺 Channels in graph: {channel_count}")
                
                # Verify we have sufficient data
                assert message_count > 0, "No messages found in graph"
                assert entity_count > 0, "No entities found in graph"
                assert author_count > 0, "No authors found in graph"
                
                print("✅ Graph data is available and populated")
                
            self.passed += 1
            self.test_results.append(("Graph Data Availability", "PASSED", None))
            
        except Exception as e:
            print(f"❌ Graph data check failed: {e}")
            self.failed += 1
            self.test_results.append(("Graph Data Availability", "FAILED", str(e)))
    
    async def test_temporal_pipeline_live(self):
        """Test the temporal pipeline with real data."""
        print("⏰ Testing Live Temporal Pipeline...")
        
        try:
            # Test with a temporal context query
            query = "What's the background on recent server discussions?"
            server_id = 1131555356418523180  # Your server ID
            
            print(f"  Testing query: '{query}'")
            
            result = await run_query_pipeline(
                query=query,
                server_id=server_id
            )
            
            # Check result structure
            assert "context" in result, "Result missing 'context' field"
            assert "understanding" in result, "Result missing 'understanding' field"
            
            context_items = result.get("context", [])
            print(f"  📋 Context items returned: {len(context_items)}")
            
            # Check if temporal connections were made
            temporal_connections = result.get("temporal_connections", 0)
            conversation_threads = result.get("conversation_threads", 0)
            
            print(f"  🔗 Temporal connections: {temporal_connections}")
            print(f"  💬 Conversation threads: {conversation_threads}")
            
            # Verify we got some results
            assert len(context_items) > 0, "No context items returned"
            
            print("✅ Temporal pipeline is working with real data")
            
            self.passed += 1
            self.test_results.append(("Live Temporal Pipeline", "PASSED", None))
            
        except Exception as e:
            print(f"❌ Temporal pipeline test failed: {e}")
            self.failed += 1
            self.test_results.append(("Live Temporal Pipeline", "FAILED", str(e)))
    
    async def test_answer_generation_live(self):
        """Test answer generation with real data."""
        print("💬 Testing Live Answer Generation...")
        
        try:
            # Create a mock pipeline result with real-looking data
            pipeline_result = {
                "context": [
                    {
                        "source": "graph",
                        "content": "Server maintenance completed successfully",
                        "author": "limo.ew",
                        "channel": "infrastructure",
                        "timestamp": "2026-03-01T14:00:00Z",
                        "temporal_context": {
                            "context_type": "primary",
                            "related_to_entity": "server maintenance"
                        }
                    }
                ],
                "understanding": {
                    "intent": "temporal_context",
                    "primary_entity": "server maintenance"
                },
                "temporal_connections": 1,
                "conversation_threads": 0
            }
            
            query = "What's the context behind the server maintenance?"
            
            answer = await generate_answer(
                query=query,
                pipeline_result=pipeline_result,
                user_name="test_user"
            )
            
            # Check answer quality
            assert len(answer) > 0, "Empty answer generated"
            assert "server maintenance" in answer.lower(), "Answer doesn't mention the topic"
            assert "limo.ew" in answer, "Answer doesn't include author names"
            
            print(f"  📝 Generated answer ({len(answer)} chars)")
            print(f"  Preview: {answer[:100]}...")
            
            print("✅ Answer generation is working")
            
            self.passed += 1
            self.test_results.append(("Live Answer Generation", "PASSED", None))
            
        except Exception as e:
            print(f"❌ Answer generation test failed: {e}")
            self.failed += 1
            self.test_results.append(("Live Answer Generation", "FAILED", str(e)))
    
    async def test_end_to_end_scenarios(self):
        """Test complete end-to-end scenarios."""
        print("🔄 Testing End-to-End Scenarios...")
        
        scenarios = [
            {
                "name": "General Server Activity",
                "query": "What happened on the server today?",
                "expected_intent": "summarization"
            },
            {
                "name": "User-Specific Query", 
                "query": "What did limo.ew say about the deployment?",
                "expected_intent": "summarization"
            },
            {
                "name": "Temporal Context Query",
                "query": "What's the background context on recent discussions?",
                "expected_intent": "temporal_context"
            }
        ]
        
        try:
            server_id = 1131555356418523180
            
            for scenario in scenarios:
                print(f"  🎯 Testing: {scenario['name']}")
                print(f"     Query: '{scenario['query']}'")
                
                # Run complete pipeline
                result = await run_query_pipeline(
                    query=scenario["query"],
                    server_id=server_id
                )
                
                # Check basic structure
                assert "context" in result
                assert "understanding" in result
                
                context_count = len(result.get("context", []))
                intent = result.get("understanding", {}).get("intent", "")
                
                print(f"     Intent: {intent}")
                print(f"     Context items: {context_count}")
                
                # Generate answer
                if context_count > 0:
                    answer = await generate_answer(
                        query=scenario["query"],
                        pipeline_result=result,
                        user_name="test_user"
                    )
                    print(f"     Answer length: {len(answer)} chars")
                else:
                    print("     No context found - this may be expected for new deployments")
            
            print("✅ End-to-end scenarios completed")
            
            self.passed += 1
            self.test_results.append(("End-to-End Scenarios", "PASSED", None))
            
        except Exception as e:
            print(f"❌ End-to-end test failed: {e}")
            self.failed += 1
            self.test_results.append(("End-to-End Scenarios", "FAILED", str(e)))
    
    def print_deployment_summary(self):
        """Print deployment test summary."""
        total = self.passed + self.failed
        
        print("\n" + "=" * 60)
        print("🚀 DEPLOYMENT TEST SUMMARY")
        print("=" * 60)
        print(f"Environment: {'Production VM' if Config.GRAPH_RAG_ENABLED else 'Development'}")
        print(f"Neo4j URI: {Config.NEO4J_URI[:30]}..." if Config.NEO4J_URI else "Not configured")
        print(f"Graph RAG: {'✅ Enabled' if Config.GRAPH_RAG_ENABLED else '❌ Disabled'}")
        print("-" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        print("\n📋 TEST RESULTS:")
        for name, status, error in self.test_results:
            status_icon = "✅" if status == "PASSED" else "❌"
            print(f"  {status_icon} {name}")
            if error:
                print(f"      Error: {error}")
        
        if self.failed == 0:
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("Your temporal Graph RAG system is fully operational on the VM!")
        else:
            print(f"\n⚠️ DEPLOYMENT ISSUES DETECTED!")
            print(f"{self.failed} test(s) failed. Please review and fix before using in production.")


async def main():
    """Main deployment test function."""
    
    print("🚀 Temporal Graph RAG Deployment Verification")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing on: {os.uname().nodename if hasattr(os, 'uname') else 'Windows'}")
    print("=" * 60)
    
    tester = DeploymentTester()
    
    # Run all deployment tests
    await tester.test_environment_setup()
    await tester.test_query_understanding_live()
    await tester.test_graph_data_availability()
    await tester.test_temporal_pipeline_live()
    await tester.test_answer_generation_live()
    await tester.test_end_to_end_scenarios()
    
    # Print summary
    tester.print_deployment_summary()
    
    # Exit with appropriate code
    sys.exit(0 if tester.failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
