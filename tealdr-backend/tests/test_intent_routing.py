"""
Test suite for intent routing in query understanding.
Validates that queries are correctly classified into the right intent types.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.query_engine import understand_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentRoutingTest:
    """Test intent classification for various query types"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    async def test_lookup_intent(self):
        """Test that specific topic queries use lookup intent"""
        logger.info("\n=== TEST 1: Lookup Intent ===")
        
        test_queries = [
            "who talked about geopolitics",
            "tell me about the API",
            "what is the deployment process",
            "find messages about Python",
            "who mentioned the database",
            "discussions about React"
        ]
        
        try:
            for query in test_queries:
                result = await understand_query(query)
                intent = result.get('intent')
                entity = result.get('primary_entity', '')
                
                if intent != 'lookup':
                    logger.error(f"❌ Query '{query}' got intent '{intent}' instead of 'lookup'")
                    self.failed += 1
                    self.results.append((f"Lookup: {query[:30]}", "FAIL", f"Got {intent}"))
                    return
                
                logger.info(f"✅ '{query}' → intent={intent}, entity={entity}")
            
            logger.info(f"✅ PASS: All lookup queries classified correctly")
            self.passed += 1
            self.results.append(("Lookup Intent", "PASS", f"{len(test_queries)} queries tested"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: Lookup intent test threw exception: {e}")
            self.failed += 1
            self.results.append(("Lookup Intent", "FAIL", str(e)))
    
    async def test_user_messages_intent(self):
        """Test that user-specific queries use user_messages intent"""
        logger.info("\n=== TEST 2: User Messages Intent ===")
        
        test_queries = [
            "what did @john say",
            "messages from @alice",
            "what is @bob trying to convey",
            "@user's messages about API"
        ]
        
        try:
            for query in test_queries:
                result = await understand_query(query)
                intent = result.get('intent')
                
                if intent != 'user_messages':
                    logger.error(f"❌ Query '{query}' got intent '{intent}' instead of 'user_messages'")
                    self.failed += 1
                    self.results.append((f"User Messages: {query[:30]}", "FAIL", f"Got {intent}"))
                    return
                
                logger.info(f"✅ '{query}' → intent={intent}")
            
            logger.info(f"✅ PASS: All user message queries classified correctly")
            self.passed += 1
            self.results.append(("User Messages Intent", "PASS", f"{len(test_queries)} queries tested"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: User messages intent test threw exception: {e}")
            self.failed += 1
            self.results.append(("User Messages Intent", "FAIL", str(e)))
    
    async def test_expert_finding_intent(self):
        """Test that expert finding queries are classified correctly"""
        logger.info("\n=== TEST 3: Expert Finding Intent ===")
        
        test_queries = [
            "who knows Python",
            "who is expert in React",
            "who can help with deployment"
        ]
        
        try:
            for query in test_queries:
                result = await understand_query(query)
                intent = result.get('intent')
                
                # Accept both expert_finding and lookup (lookup is acceptable fallback)
                if intent not in ['expert_finding', 'lookup']:
                    logger.error(f"❌ Query '{query}' got intent '{intent}' instead of 'expert_finding' or 'lookup'")
                    self.failed += 1
                    self.results.append((f"Expert Finding: {query[:30]}", "FAIL", f"Got {intent}"))
                    return
                
                logger.info(f"✅ '{query}' → intent={intent}")
            
            logger.info(f"✅ PASS: All expert finding queries classified correctly")
            self.passed += 1
            self.results.append(("Expert Finding Intent", "PASS", f"{len(test_queries)} queries tested"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: Expert finding intent test threw exception: {e}")
            self.failed += 1
            self.results.append(("Expert Finding Intent", "FAIL", str(e)))
    
    async def test_summarization_intent(self):
        """Test that general activity queries use summarization intent"""
        logger.info("\n=== TEST 4: Summarization Intent ===")
        
        test_queries = [
            "what did i miss",
            "what happened",
            "server activity",
            "recent activity"
        ]
        
        try:
            for query in test_queries:
                result = await understand_query(query)
                intent = result.get('intent')
                
                if intent != 'summarization':
                    logger.error(f"❌ Query '{query}' got intent '{intent}' instead of 'summarization'")
                    self.failed += 1
                    self.results.append((f"Summarization: {query[:30]}", "FAIL", f"Got {intent}"))
                    return
                
                logger.info(f"✅ '{query}' → intent={intent}")
            
            logger.info(f"✅ PASS: All summarization queries classified correctly")
            self.passed += 1
            self.results.append(("Summarization Intent", "PASS", f"{len(test_queries)} queries tested"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: Summarization intent test threw exception: {e}")
            self.failed += 1
            self.results.append(("Summarization Intent", "FAIL", str(e)))
    
    async def test_no_default_to_summarization(self):
        """Test that specific queries DON'T default to summarization"""
        logger.info("\n=== TEST 5: No Default to Summarization ===")
        
        # These should NOT be summarization
        test_queries = [
            ("tell me about Docker", "lookup"),
            ("what is Kubernetes", "lookup"),
            ("who talked about AI", "lookup"),
            ("find messages about testing", "lookup")
        ]
        
        try:
            for query, expected_intent in test_queries:
                result = await understand_query(query)
                intent = result.get('intent')
                
                if intent == 'summarization':
                    logger.error(f"❌ Query '{query}' incorrectly defaulted to summarization")
                    self.failed += 1
                    self.results.append((f"No Summarization Default: {query[:30]}", "FAIL", f"Got summarization"))
                    return
                
                logger.info(f"✅ '{query}' → intent={intent} (not summarization)")
            
            logger.info(f"✅ PASS: No queries incorrectly defaulted to summarization")
            self.passed += 1
            self.results.append(("No Summarization Default", "PASS", f"{len(test_queries)} queries tested"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: No summarization default test threw exception: {e}")
            self.failed += 1
            self.results.append(("No Summarization Default", "FAIL", str(e)))
    
    async def run_all_tests(self):
        """Run all intent routing tests"""
        logger.info("\n" + "="*60)
        logger.info("STARTING INTENT ROUTING TEST SUITE")
        logger.info("="*60)
        
        # Run all tests
        await self.test_lookup_intent()
        await self.test_user_messages_intent()
        await self.test_expert_finding_intent()
        await self.test_summarization_intent()
        await self.test_no_default_to_summarization()
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {self.passed + self.failed}")
        logger.info(f"✅ Passed: {self.passed}")
        logger.info(f"❌ Failed: {self.failed}")
        logger.info(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        logger.info("\n" + "="*60)
        logger.info("DETAILED RESULTS")
        logger.info("="*60)
        for test_name, status, details in self.results:
            logger.info(f"\n{status}: {test_name}")
            logger.info(f"  Details: {details}")
        
        logger.info("\n" + "="*60)
        
        return self.passed, self.failed


if __name__ == "__main__":
    tester = IntentRoutingTest()
    passed, failed = asyncio.run(tester.run_all_tests())
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
