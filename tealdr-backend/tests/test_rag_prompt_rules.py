"""
Test suite for RAG prompt rules implementation.
Validates that the answer generation follows strict RAG best practices.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generation.answer_generator import generate_answer, ANSWER_PROMPT
from generation.temporal_context_helper import format_context_for_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGPromptRulesTest:
    """Test RAG prompt rules implementation"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test_empty_retrieval_handling(self):
        """Test Rule: Handle empty retrieval explicitly without calling LLM"""
        logger.info("\n=== TEST 1: Empty Retrieval Handling ===")
        
        # Simulate empty retrieval
        pipeline_result = {
            "context": [],
            "understanding": {
                "primary_entity": "nonexistent topic",
                "intent": "lookup"
            }
        }
        
        try:
            # This should return immediately without calling LLM
            result = asyncio.run(generate_answer(
                query="what is nonexistent topic?",
                pipeline_result=pipeline_result,
                user_name="test_user"
            ))
            
            # Validate response
            checks = [
                ("Contains 'No Relevant Messages Found'", "No Relevant Messages Found" in result),
                ("Contains suggestions", "Suggestions:" in result or "Try" in result),
                ("Does not hallucinate", "nonexistent topic" in result.lower()),
                ("Provides helpful guidance", any(word in result.lower() for word in ["keywords", "different", "broader"]))
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info("✅ PASS: Empty retrieval handled correctly")
                self.passed += 1
                self.results.append(("Empty Retrieval Handling", "PASS", result[:100]))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Empty retrieval handling - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Empty Retrieval Handling", "FAIL", f"Failed checks: {failed_checks}"))
            
            logger.info(f"Response preview: {result[:200]}")
            
        except Exception as e:
            logger.error(f"❌ FAIL: Empty retrieval test threw exception: {e}")
            self.failed += 1
            self.results.append(("Empty Retrieval Handling", "FAIL", str(e)))
    
    def test_structured_context_format(self):
        """Test Rule: Structured context injection with metadata"""
        logger.info("\n=== TEST 2: Structured Context Format ===")
        
        # Create test context items
        context_items = [
            {
                "content": "We deployed the new API endpoint yesterday",
                "author_name": "john_doe",
                "channel": "dev",
                "timestamp": "2024-04-05T10:30:00Z",
                "source": "search"
            },
            {
                "content": "The deployment was successful after fixing the config",
                "author_name": "jane_smith",
                "channel": "general",
                "timestamp": "2024-04-05T14:20:00Z",
                "source": "graph"
            }
        ]
        
        try:
            formatted = format_context_for_prompt(context_items)
            
            # Validate structured format
            checks = [
                ("Contains Doc numbers", "[Doc 1" in formatted and "[Doc 2" in formatted),
                ("Contains timestamps", "2024-04-05" in formatted),
                ("Contains source types", "source: search" in formatted and "source: graph" in formatted),
                ("Contains authors", "author: john_doe" in formatted and "author: jane_smith" in formatted),
                ("Contains channels", "channel: #dev" in formatted and "channel: #general" in formatted),
                ("Separates documents", "---" in formatted)
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info("✅ PASS: Context formatted with structured metadata")
                self.passed += 1
                self.results.append(("Structured Context Format", "PASS", formatted[:150]))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Structured context format - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Structured Context Format", "FAIL", f"Failed checks: {failed_checks}"))
            
            logger.info(f"Formatted context preview:\n{formatted[:300]}")
            
        except Exception as e:
            logger.error(f"❌ FAIL: Structured context test threw exception: {e}")
            self.failed += 1
            self.results.append(("Structured Context Format", "FAIL", str(e)))
    
    def test_prompt_structure(self):
        """Test Rule: Separate system instructions from context"""
        logger.info("\n=== TEST 3: Prompt Structure ===")
        
        try:
            # Check prompt has proper XML structure
            checks = [
                ("Has system_instructions section", "<system_instructions>" in ANSWER_PROMPT),
                ("Has retrieved_context section", "<retrieved_context>" in ANSWER_PROMPT),
                ("Has task section", "<task>" in ANSWER_PROMPT),
                ("Closes system_instructions", "</system_instructions>" in ANSWER_PROMPT),
                ("Closes retrieved_context", "</retrieved_context>" in ANSWER_PROMPT),
                ("Closes task", "</task>" in ANSWER_PROMPT),
                ("Instructions come before context", ANSWER_PROMPT.index("<system_instructions>") < ANSWER_PROMPT.index("<retrieved_context>"))
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info("✅ PASS: Prompt properly structured with XML sections")
                self.passed += 1
                self.results.append(("Prompt Structure", "PASS", "XML sections properly separated"))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Prompt structure - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Prompt Structure", "FAIL", f"Failed checks: {failed_checks}"))
            
        except Exception as e:
            logger.error(f"❌ FAIL: Prompt structure test threw exception: {e}")
            self.failed += 1
            self.results.append(("Prompt Structure", "FAIL", str(e)))
    
    def test_grounding_instructions(self):
        """Test Rule: Explicit grounding in context only"""
        logger.info("\n=== TEST 4: Grounding Instructions ===")
        
        try:
            prompt_lower = ANSWER_PROMPT.lower()
            
            # Check for grounding instructions
            checks = [
                ("Instructs to use ONLY provided context", "only" in prompt_lower and "provided" in prompt_lower),
                ("Prohibits training data use", "do not use" in prompt_lower or "don't use" in prompt_lower),
                ("Requires explicit uncertainty", "uncertainty" in prompt_lower or "don't know" in prompt_lower or "isn't covered" in prompt_lower),
                ("Prohibits fabrication", "never fabricate" in prompt_lower or "do not add" in prompt_lower),
                ("Requires citations", "cite" in prompt_lower or "citation" in prompt_lower or "attribute" in prompt_lower),
                ("Handles insufficient context", "insufficient" in prompt_lower or "couldn't find" in prompt_lower)
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info("✅ PASS: Prompt contains all critical grounding instructions")
                self.passed += 1
                self.results.append(("Grounding Instructions", "PASS", "All critical rules present"))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Grounding instructions - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Grounding Instructions", "FAIL", f"Failed checks: {failed_checks}"))
            
        except Exception as e:
            logger.error(f"❌ FAIL: Grounding instructions test threw exception: {e}")
            self.failed += 1
            self.results.append(("Grounding Instructions", "FAIL", str(e)))
    
    def test_citation_format_instruction(self):
        """Test Rule: Citation format specified upfront"""
        logger.info("\n=== TEST 5: Citation Format Instructions ===")
        
        try:
            # Check for citation format instructions
            checks = [
                ("Specifies citation format", "cite" in ANSWER_PROMPT.lower() or "citation" in ANSWER_PROMPT.lower()),
                ("Provides citation example", "example:" in ANSWER_PROMPT.lower() or "[" in ANSWER_PROMPT),
                ("Requires inline attribution", "inline" in ANSWER_PROMPT.lower() or "attribute" in ANSWER_PROMPT.lower())
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info("✅ PASS: Citation format clearly specified")
                self.passed += 1
                self.results.append(("Citation Format Instructions", "PASS", "Format and examples provided"))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Citation format instructions - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Citation Format Instructions", "FAIL", f"Failed checks: {failed_checks}"))
            
        except Exception as e:
            logger.error(f"❌ FAIL: Citation format test threw exception: {e}")
            self.failed += 1
            self.results.append(("Citation Format Instructions", "FAIL", str(e)))
    
    def test_uncertainty_handling_instruction(self):
        """Test Rule: Explicit uncertainty as first-class output"""
        logger.info("\n=== TEST 6: Uncertainty Handling Instructions ===")
        
        try:
            # Check for uncertainty handling instructions
            checks = [
                ("Distinguishes direct vs inferred", "show" in ANSWER_PROMPT.lower() and "suggest" in ANSWER_PROMPT.lower()),
                ("Makes uncertainty explicit", "uncertainty" in ANSWER_PROMPT.lower() or "not covered" in ANSWER_PROMPT.lower()),
                ("Provides uncertainty examples", "directly stated" in ANSWER_PROMPT.lower() or "implied" in ANSWER_PROMPT.lower())
            ]
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                logger.info("✅ PASS: Uncertainty handling properly instructed")
                self.passed += 1
                self.results.append(("Uncertainty Handling", "PASS", "Explicit uncertainty required"))
            else:
                failed_checks = [check[0] for check in checks if not check[1]]
                logger.error(f"❌ FAIL: Uncertainty handling - Failed: {failed_checks}")
                self.failed += 1
                self.results.append(("Uncertainty Handling", "FAIL", f"Failed checks: {failed_checks}"))
            
        except Exception as e:
            logger.error(f"❌ FAIL: Uncertainty handling test threw exception: {e}")
            self.failed += 1
            self.results.append(("Uncertainty Handling", "FAIL", str(e)))
    
    def run_all_tests(self):
        """Run all RAG prompt rules tests"""
        logger.info("\n" + "="*60)
        logger.info("STARTING RAG PROMPT RULES TEST SUITE")
        logger.info("="*60)
        
        # Run all tests
        self.test_empty_retrieval_handling()
        self.test_structured_context_format()
        self.test_prompt_structure()
        self.test_grounding_instructions()
        self.test_citation_format_instruction()
        self.test_uncertainty_handling_instruction()
        
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
    tester = RAGPromptRulesTest()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
