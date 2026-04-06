"""
Integration tests for the complete retrieval pipeline.
Tests RRF fusion, hybrid search, reranking, and compression.
"""

import asyncio
import logging
import sys
import os
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalPipelineTest:
    """Test complete retrieval pipeline with all components"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test_rrf_fusion(self):
        """Test Reciprocal Rank Fusion algorithm"""
        logger.info("\n=== TEST 1: RRF Fusion ===")
        
        from retrieval.rrf_fusion import reciprocal_rank_fusion
        
        # Mock results from different retrievers
        bm25_results = [
            {'id': 1, 'content': 'API deployment successful', 'message_id': 1},
            {'id': 2, 'content': 'Database migration complete', 'message_id': 2},
            {'id': 3, 'content': 'Frontend updated', 'message_id': 3},
        ]
        
        vector_results = [
            {'id': 2, 'content': 'Database migration complete', 'message_id': 2, 'similarity': 0.9},
            {'id': 4, 'content': 'API endpoint fixed', 'message_id': 4, 'similarity': 0.85},
            {'id': 1, 'content': 'API deployment successful', 'message_id': 1, 'similarity': 0.8},
        ]
        
        graph_results = [
            {'messages': [{'id': 1, 'content': 'API deployment successful', 'message_id': 1}]},
            {'messages': [{'id': 5, 'content': 'Config updated', 'message_id': 5}]},
        ]
        
        try:
            fused = reciprocal_rank_fusion(bm25_results, vector_results, graph_results)
            
            # Validate fusion
            checks = [
                ("Returns results", len(fused) > 0),
                ("Has RRF scores", all('rrf_score' in r for r in fused)),
                ("Has retrieval sources", all('retrieval_sources' in r for r in fused)),
                ("Sorted by RRF score", fused == sorted(fused, key=lambda x: x['rrf_score'], reverse=True)),
                ("Document 1 appears once", sum(1 for r in fused if r.get('message_id') == 1) == 1),
                ("Multi-retriever docs ranked higher", fused[0].get('num_retrievers', 0) > 1)
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info(f"✅ PASS: RRF fusion working correctly")
                logger.info(f"  Fused {len(fused)} unique documents")
                logger.info(f"  Top result: RRF={fused[0]['rrf_score']:.4f}, retrievers={fused[0]['num_retrievers']}")
                self.passed += 1
                self.results.append(("RRF Fusion", "PASS", f"{len(fused)} docs fused"))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: RRF fusion - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("RRF Fusion", "FAIL", f"Failed checks: {failed_checks}"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: RRF fusion threw exception: {e}")
            self.failed += 1
            self.results.append(("RRF Fusion", "FAIL", str(e)))
    
    def test_reranking(self):
        """Test reranking algorithm"""
        logger.info("\n=== TEST 2: Reranking ===")
        
        from retrieval.reranker import _heuristic_rerank
        
        # Mock results with varying quality
        results = [
            {
                'content': 'Short message',
                'rrf_score': 0.5,
                'num_retrievers': 1,
                'similarity': 0.6
            },
            {
                'content': 'This is a longer message with more context about the API deployment and configuration',
                'rrf_score': 0.4,
                'num_retrievers': 3,
                'similarity': 0.9
            },
            {
                'content': 'Medium length message about deployment',
                'rrf_score': 0.6,
                'num_retrievers': 2,
                'similarity': 0.7
            }
        ]
        
        query = "API deployment configuration"
        
        try:
            reranked = _heuristic_rerank(query, results.copy())
            
            # Validate reranking
            checks = [
                ("Has rerank scores", all('rerank_score' in r for r in reranked)),
                ("Sorted by rerank score", reranked == sorted(reranked, key=lambda x: x['rerank_score'], reverse=True)),
                ("Multi-retriever doc ranked high", reranked[0]['num_retrievers'] >= 2),
                ("Scores are positive", all(r['rerank_score'] > 0 for r in reranked))
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info(f"✅ PASS: Reranking working correctly")
                logger.info(f"  Top result: score={reranked[0]['rerank_score']:.2f}, retrievers={reranked[0]['num_retrievers']}")
                self.passed += 1
                self.results.append(("Reranking", "PASS", f"Scores: {[r['rerank_score'] for r in reranked]}"))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Reranking - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Reranking", "FAIL", f"Failed checks: {failed_checks}"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: Reranking threw exception: {e}")
            self.failed += 1
            self.results.append(("Reranking", "FAIL", str(e)))
    
    def test_compression(self):
        """Test context compression"""
        logger.info("\n=== TEST 3: Context Compression ===")
        
        from retrieval.compressor import compress_to_budget, estimate_token_count
        
        # Mock results with varying lengths
        results = [
            {'content': 'Short message ' * 10, 'rerank_score': 1.0},
            {'content': 'Medium length message ' * 20, 'rerank_score': 0.9},
            {'content': 'Very long message with lots of content ' * 50, 'rerank_score': 0.8},
            {'content': 'Another long message ' * 40, 'rerank_score': 0.7},
            {'content': 'Short ' * 5, 'rerank_score': 0.6},
        ]
        
        query = "test query"
        token_budget = 200  # Small budget to force compression
        
        try:
            compressed = compress_to_budget(query, results, token_budget)
            final_tokens = estimate_token_count(compressed)
            
            # Validate compression
            checks = [
                ("Compressed results", len(compressed) < len(results)),
                ("Within token budget", final_tokens <= token_budget),
                ("Kept top results", compressed[0]['rerank_score'] >= 0.8),
                ("Returns list", isinstance(compressed, list))
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info(f"✅ PASS: Compression working correctly")
                logger.info(f"  Compressed {len(results)} -> {len(compressed)} results")
                logger.info(f"  Token usage: {final_tokens}/{token_budget}")
                self.passed += 1
                self.results.append(("Compression", "PASS", f"{len(results)}->{len(compressed)} docs, {final_tokens} tokens"))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Compression - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Compression", "FAIL", f"Failed checks: {failed_checks}"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: Compression threw exception: {e}")
            self.failed += 1
            self.results.append(("Compression", "FAIL", str(e)))
    
    def test_redundancy_removal(self):
        """Test redundant content removal"""
        logger.info("\n=== TEST 4: Redundancy Removal ===")
        
        from retrieval.compressor import remove_redundant_content
        
        # Mock results with duplicates and similar content
        results = [
            {'content': 'The API deployment was successful'},
            {'content': 'The API deployment was successful'},  # Exact duplicate
            {'content': 'API deployment succeeded'},  # Similar
            {'content': 'Database migration complete'},  # Different
            {'content': 'The API deployment was successful and verified'},  # Highly similar
        ]
        
        try:
            unique = remove_redundant_content(results)
            
            # Validate deduplication
            checks = [
                ("Removed duplicates", len(unique) < len(results)),
                ("Kept at least 2 unique", len(unique) >= 2),
                ("Returns list", isinstance(unique, list))
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info(f"✅ PASS: Redundancy removal working")
                logger.info(f"  Removed {len(results) - len(unique)} redundant results")
                self.passed += 1
                self.results.append(("Redundancy Removal", "PASS", f"{len(results)}->{len(unique)} unique"))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Redundancy removal - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Redundancy Removal", "FAIL", f"Failed checks: {failed_checks}"))
        
        except Exception as e:
            logger.error(f"❌ FAIL: Redundancy removal threw exception: {e}")
            self.failed += 1
            self.results.append(("Redundancy Removal", "FAIL", str(e)))
    
    def run_all_tests(self):
        """Run all retrieval pipeline tests"""
        logger.info("\n" + "="*60)
        logger.info("STARTING RETRIEVAL PIPELINE TEST SUITE")
        logger.info("="*60)
        
        # Run all tests
        self.test_rrf_fusion()
        self.test_reranking()
        self.test_compression()
        self.test_redundancy_removal()
        
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
    tester = RetrievalPipelineTest()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
