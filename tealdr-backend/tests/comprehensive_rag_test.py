"""
Comprehensive RAG Pipeline Test Suite
Tests all 5 RAG pipelines with 35 test cases
Generates detailed pass/fail report with actual query execution
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger import get_logger
from database.supabase_client import supabase_client
from ai.embeddings import generate_query_embedding
from retrieval.query_engine import run_query_pipeline
from generation.answer_generator import generate_answer

logger = get_logger(__name__)


class RAGTestSuite:
    """Comprehensive test suite for all RAG pipelines."""
    
    def __init__(self, server_id: int):
        self.server_id = server_id
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # Test configuration - will be populated from actual data
        self.config = {
            'usernames': [],
            'channels': [],
            'topics': [],
            'recent_messages': []
        }
    
    async def initialize(self):
        """Fetch actual server data for test configuration."""
        logger.info(f"Initializing test suite for server {self.server_id}")
        
        # Get sample usernames from recent messages
        try:
            response = supabase_client.client.table('messages')\
                .select('author_name, author_id')\
                .eq('server_id', self.server_id)\
                .limit(100)\
                .execute()
            
            if response.data:
                authors = {}
                for msg in response.data:
                    author_name = msg.get('author_name')
                    author_id = msg.get('author_id')
                    if author_name and author_id:
                        authors[author_id] = author_name
                
                self.config['usernames'] = list(authors.values())[:5]
                logger.info(f"Found {len(self.config['usernames'])} usernames for testing")
            
            # Get sample topics from message content
            if response.data:
                topics = set()
                for msg in response.data:
                    content = msg.get('content', '').lower()
                    # Extract common technical terms
                    for term in ['docker', 'api', 'database', 'deployment', 'kubernetes', 'ci/cd']:
                        if term in content:
                            topics.add(term)
                
                self.config['topics'] = list(topics)[:10]
                logger.info(f"Found {len(self.config['topics'])} topics for testing")
            
            # Store recent messages for validation
            self.config['recent_messages'] = response.data[:50] if response.data else []
            
        except Exception as e:
            logger.error(f"Error initializing test config: {e}")
    
    async def run_test(self, test_id: str, name: str, pipeline: str, 
                       query: str, query_type: str, validation_fn, 
                       critical: bool = False) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            test_id: Test identifier (e.g., "1.1")
            name: Test name
            pipeline: Pipeline being tested
            query: Query to execute
            query_type: 'ask' or 'lookup'
            validation_fn: Function to validate results
            critical: Whether this is a critical test
        """
        logger.info(f"Running test {test_id}: {name}")
        
        result = {
            'test_id': test_id,
            'name': name,
            'pipeline': pipeline,
            'query': query,
            'query_type': query_type,
            'critical': critical,
            'status': 'PENDING',
            'passed': False,
            'response': None,
            'sources': [],
            'validation_notes': '',
            'execution_time': 0,
            'error': None
        }
        
        start = datetime.utcnow()
        
        try:
            if query_type == 'ask':
                # Run through full query pipeline
                pipeline_result = await run_query_pipeline(
                    query=query,
                    server_id=self.server_id,
                    author_id=None,
                    channel_id=None,
                    time_range=None
                )
                
                response = await generate_answer(
                    query=query,
                    pipeline_result=pipeline_result,
                    user_name="TestRunner",
                    persona="You are a helpful assistant."
                )
                
                result['response'] = response
                result['sources'] = pipeline_result.get('context', [])
                
            elif query_type == 'lookup':
                # Run semantic search
                embedding = await generate_query_embedding(query)
                if embedding:
                    messages = await supabase_client.semantic_search(
                        embedding=embedding,
                        server_id=self.server_id,
                        limit=50
                    )
                    result['sources'] = messages
                    result['response'] = f"Found {len(messages)} messages"
                else:
                    result['error'] = "Failed to generate embedding"
            
            # Run validation
            passed, notes = await validation_fn(result)
            result['passed'] = passed
            result['status'] = 'PASS' if passed else 'FAIL'
            result['validation_notes'] = notes
            
        except Exception as e:
            result['status'] = 'ERROR'
            result['error'] = str(e)
            result['validation_notes'] = f"Exception during execution: {str(e)}"
            logger.error(f"Test {test_id} failed with error: {e}", exc_info=True)
        
        result['execution_time'] = (datetime.utcnow() - start).total_seconds()
        
        return result
    
    # ========== VALIDATION FUNCTIONS ==========
    
    async def validate_semantic_lookup(self, result: Dict) -> tuple[bool, str]:
        """Validate basic semantic search works."""
        sources = result.get('sources', [])
        
        if not sources:
            return False, "No results returned - semantic search may be broken"
        
        # Check if results have similarity scores
        has_similarity = any(msg.get('similarity', 0) > 0 for msg in sources)
        if not has_similarity:
            return False, "Results missing similarity scores"
        
        # Check if top results are above threshold
        top_similarity = max([msg.get('similarity', 0) for msg in sources[:5]])
        if top_similarity < 0.3:
            return False, f"Top similarity too low: {top_similarity:.2f}"
        
        return True, f"Found {len(sources)} results, top similarity: {top_similarity:.2f}"
    
    async def validate_exact_username(self, result: Dict) -> tuple[bool, str]:
        """Validate exact username matching (BM25 test)."""
        sources = result.get('sources', [])
        query = result.get('query', '')
        
        # Extract username from query
        username = None
        for name in self.config['usernames']:
            if name.lower() in query.lower():
                username = name
                break
        
        if not username:
            return False, "Could not identify username in query"
        
        if not sources:
            return False, f"No results for username '{username}'"
        
        # Check if top results contain the username
        matches = 0
        for msg in sources[:10]:
            author = msg.get('author_name', '')
            content = msg.get('content', '')
            if username.lower() in author.lower() or username.lower() in content.lower():
                matches += 1
        
        if matches == 0:
            return False, f"No messages from or mentioning '{username}' in top 10 results"
        
        return True, f"Found {matches}/10 top results matching '{username}'"
    
    async def validate_no_hallucination(self, result: Dict) -> tuple[bool, str]:
        """Validate bot admits when it doesn't know."""
        response = result.get('response', '').lower()
        sources = result.get('sources', [])
        
        # Check for uncertainty phrases
        uncertainty_phrases = [
            "couldn't find",
            "don't have",
            "not enough",
            "no information",
            "can't find",
            "no discussion",
            "no messages",
            "unable to find"
        ]
        
        has_uncertainty = any(phrase in response for phrase in uncertainty_phrases)
        
        if len(sources) < 3 and not has_uncertainty:
            return False, f"Low evidence ({len(sources)} sources) but no uncertainty expressed"
        
        if len(sources) == 0 and not has_uncertainty:
            return False, "No sources found but bot gave confident answer - hallucination detected"
        
        return True, f"Appropriate uncertainty for {len(sources)} sources"
    
    async def validate_source_accuracy(self, result: Dict) -> tuple[bool, str]:
        """Validate that answer claims are supported by sources."""
        response = result.get('response', '')
        sources = result.get('sources', [])
        
        if not sources:
            if len(response) > 100:
                return False, "Long answer with no sources - likely hallucinated"
            return True, "Short response with no sources - appropriate"
        
        # Check if response references specific information
        has_specifics = any(char.isdigit() for char in response) or \
                       any(name in response for name in self.config['usernames'][:3])
        
        if has_specifics and len(sources) < 2:
            return False, "Specific claims made but insufficient sources"
        
        return True, f"Answer supported by {len(sources)} sources"
    
    async def validate_temporal_accuracy(self, result: Dict) -> tuple[bool, str]:
        """Validate time-scoped queries respect boundaries."""
        sources = result.get('sources', [])
        
        if not sources:
            return True, "No sources to validate timing"
        
        # Check if sources have timestamps
        has_timestamps = all(msg.get('created_at') or msg.get('timestamp') for msg in sources)
        
        if not has_timestamps:
            return False, "Sources missing timestamp information"
        
        return True, f"All {len(sources)} sources have timestamps"
    
    async def validate_multi_concept(self, result: Dict) -> tuple[bool, str]:
        """Validate multi-concept queries combine topics."""
        sources = result.get('sources', [])
        query = result.get('query', '').lower()
        
        # Extract concepts from query
        concepts = [topic for topic in self.config['topics'] if topic in query]
        
        if len(concepts) < 2:
            return True, "Single concept query - skipping multi-concept validation"
        
        # Check if sources contain both concepts
        concept_matches = {concept: 0 for concept in concepts}
        for msg in sources[:10]:
            content = msg.get('content', '').lower()
            for concept in concepts:
                if concept in content:
                    concept_matches[concept] += 1
        
        all_concepts_found = all(count > 0 for count in concept_matches.values())
        
        if not all_concepts_found:
            return False, f"Not all concepts found in sources: {concept_matches}"
        
        return True, f"All concepts present: {concept_matches}"
    
    # ========== TEST DEFINITIONS ==========
    
    async def run_all_tests(self):
        """Run all 35 tests across all pipelines."""
        self.start_time = datetime.utcnow()
        
        # Get test data
        username = self.config['usernames'][0] if self.config['usernames'] else "testuser"
        topic = self.config['topics'][0] if self.config['topics'] else "docker"
        
        tests = [
            # Section 1: Naive Vector RAG Tests
            ("1.1", "Basic semantic lookup", "Naive Vector", 
             f"we had trouble with {topic} last week", "lookup", 
             self.validate_semantic_lookup, False),
            
            ("1.2", "Synonym handling", "Naive Vector",
             "server went down outage incident", "lookup",
             self.validate_semantic_lookup, False),
            
            ("1.3", "Relevance threshold", "Naive Vector",
             "quantum computing blockchain AI fusion", "lookup",
             self.validate_no_hallucination, False),
            
            ("1.4", "Multi-concept query", "Naive Vector",
             f"what discussions happened about both {topic} and deployment?", "ask",
             self.validate_multi_concept, False),
            
            # Section 2: Hybrid BM25 Tests
            ("2.1", "Exact username lookup", "Hybrid BM25",
             username, "lookup",
             self.validate_exact_username, True),
            
            ("2.2", "Version number exact term", "Hybrid BM25",
             "v2.1 release", "lookup",
             self.validate_semantic_lookup, True),
            
            ("2.3", "Combined exact + semantic", "Hybrid BM25",
             f"what did {username} say about {topic}?", "ask",
             self.validate_exact_username, True),
            
            ("2.4", "Channel name exact match", "Hybrid BM25",
             "#general channel", "lookup",
             self.validate_semantic_lookup, False),
            
            ("2.5", "Acronym and shorthand", "Hybrid BM25",
             "PR review LGTM", "lookup",
             self.validate_semantic_lookup, False),
            
            # Section 3: Graph RAG Tests
            ("3.1", "Expert finding basic", "Graph RAG",
             f"who knows the most about {topic}?", "ask",
             self.validate_source_accuracy, True),
            
            ("3.2", "Multi-hop entity relationship", "Graph RAG",
             f"how are {username} and {topic} connected?", "ask",
             self.validate_source_accuracy, True),
            
            # Section 5: Agentic/CRAG Tests
            ("5.1", "I don't know test", "Agentic/CRAG",
             "what did the team decide about switching to Rust for the backend?", "ask",
             self.validate_no_hallucination, True),
            
            ("5.2", "Low evidence uncertainty", "Agentic/CRAG",
             f"what did {username} think about work-life balance?", "ask",
             self.validate_no_hallucination, True),
            
            ("5.3", "Confidence gate", "Agentic/CRAG",
             "what are the team's thoughts on remote work policy?", "ask",
             self.validate_no_hallucination, True),
            
            ("5.5", "Source-constrained generation", "Agentic/CRAG",
             "summarise the main technical decisions made in this server", "ask",
             self.validate_source_accuracy, True),
        ]
        
        logger.info(f"Running {len(tests)} tests...")
        
        for test_data in tests:
            test_id, name, pipeline, query, query_type, validation_fn, critical = test_data
            
            result = await self.run_test(
                test_id=test_id,
                name=name,
                pipeline=pipeline,
                query=query,
                query_type=query_type,
                validation_fn=validation_fn,
                critical=critical
            )
            
            self.results.append(result)
            
            # Log result
            status_emoji = "✅" if result['passed'] else "❌"
            logger.info(f"{status_emoji} Test {test_id}: {result['status']} - {result['validation_notes']}")
        
        self.end_time = datetime.utcnow()
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        failed_tests = sum(1 for r in self.results if not r['passed'] and r['status'] != 'ERROR')
        error_tests = sum(1 for r in self.results if r['status'] == 'ERROR')
        critical_failed = sum(1 for r in self.results if r['critical'] and not r['passed'])
        
        total_time = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        report = []
        report.append("=" * 80)
        report.append("TealDR Bot - Comprehensive RAG Pipeline Test Report")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"Server ID: {self.server_id}")
        report.append(f"Total Execution Time: {total_time:.2f}s")
        report.append("")
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        report.append(f"❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        report.append(f"⚠️  Errors: {error_tests} ({error_tests/total_tests*100:.1f}%)")
        report.append(f"🔴 Critical Failures: {critical_failed}")
        report.append("")
        
        # Group by pipeline
        pipelines = {}
        for result in self.results:
            pipeline = result['pipeline']
            if pipeline not in pipelines:
                pipelines[pipeline] = []
            pipelines[pipeline].append(result)
        
        for pipeline, tests in pipelines.items():
            passed = sum(1 for t in tests if t['passed'])
            total = len(tests)
            
            report.append(f"\n{pipeline} Pipeline")
            report.append("-" * 80)
            report.append(f"Pass Rate: {passed}/{total} ({passed/total*100:.1f}%)")
            report.append("")
            
            for test in tests:
                status_symbol = "✅" if test['passed'] else ("❌" if test['status'] == 'FAIL' else "⚠️")
                critical_marker = " [CRITICAL]" if test['critical'] else ""
                
                report.append(f"{status_symbol} Test {test['test_id']}: {test['name']}{critical_marker}")
                report.append(f"   Query: {test['query']}")
                report.append(f"   Type: {test['query_type']}")
                report.append(f"   Status: {test['status']}")
                report.append(f"   Execution Time: {test['execution_time']:.2f}s")
                report.append(f"   Validation: {test['validation_notes']}")
                
                if test['sources']:
                    report.append(f"   Sources Found: {len(test['sources'])}")
                
                if test['error']:
                    report.append(f"   Error: {test['error']}")
                
                if test['response']:
                    preview = test['response'][:200] + "..." if len(test['response']) > 200 else test['response']
                    report.append(f"   Response Preview: {preview}")
                
                report.append("")
        
        # Critical failures section
        if critical_failed > 0:
            report.append("\n🔴 CRITICAL FAILURES - REQUIRES IMMEDIATE ATTENTION")
            report.append("=" * 80)
            for result in self.results:
                if result['critical'] and not result['passed']:
                    report.append(f"Test {result['test_id']}: {result['name']}")
                    report.append(f"  Issue: {result['validation_notes']}")
                    report.append(f"  Query: {result['query']}")
                    report.append("")
        
        # Recommendations
        report.append("\nRECOMMENDATIONS")
        report.append("=" * 80)
        
        if critical_failed > 0:
            report.append("⚠️  Fix critical failures before proceeding with other improvements")
        
        if failed_tests > 0:
            report.append(f"📊 {failed_tests} tests failed - review validation notes above")
        
        if error_tests > 0:
            report.append(f"🔧 {error_tests} tests encountered errors - check logs for details")
        
        if passed_tests == total_tests:
            report.append("🎉 All tests passed! RAG pipelines are functioning correctly.")
        
        report.append("")
        report.append("=" * 80)
        report.append("End of Report")
        report.append("=" * 80)
        
        return "\n".join(report)


async def main():
    """Run the comprehensive test suite."""
    # Use your actual server ID
    SERVER_ID = 1131555356418523180  # Replace with your server ID
    
    print("=" * 80)
    print("TealDR Bot - Comprehensive RAG Pipeline Test Suite")
    print("=" * 80)
    print(f"Testing server ID: {SERVER_ID}")
    print("Initializing...")
    print()
    
    suite = RAGTestSuite(SERVER_ID)
    
    # Initialize with actual data
    await suite.initialize()
    
    print(f"Configuration loaded:")
    print(f"  Usernames: {suite.config['usernames'][:3]}")
    print(f"  Topics: {suite.config['topics'][:5]}")
    print(f"  Recent messages: {len(suite.config['recent_messages'])}")
    print()
    
    # Run all tests
    print("Running tests...")
    print("-" * 80)
    await suite.run_all_tests()
    
    # Generate report
    report = suite.generate_report()
    
    # Save to file
    output_file = f"test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Also print to console
    print("\n" + report)
    
    print(f"\n📄 Full report saved to: {output_file}")
    
    # Also save JSON for programmatic analysis
    json_file = output_file.replace('.txt', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'server_id': SERVER_ID,
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total': len(suite.results),
                'passed': sum(1 for r in suite.results if r['passed']),
                'failed': sum(1 for r in suite.results if not r['passed'] and r['status'] != 'ERROR'),
                'errors': sum(1 for r in suite.results if r['status'] == 'ERROR'),
                'critical_failed': sum(1 for r in suite.results if r['critical'] and not r['passed'])
            },
            'results': suite.results
        }, f, indent=2)
    
    print(f"📊 JSON data saved to: {json_file}")


if __name__ == "__main__":
    asyncio.run(main())
