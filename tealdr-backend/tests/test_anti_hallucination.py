"""
Test suite for anti-hallucination features in RAG system.
Tests P0.1: "I don't know" instruction in Gemini prompts.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from ai.gemini_client import gemini_client, ANTI_HALLUCINATION_INSTRUCTION


class TestAntiHallucinationInstruction:
    """Test that anti-hallucination instruction is properly applied."""
    
    @pytest.mark.asyncio
    async def test_anti_hallucination_instruction_applied_with_context(self):
        """Test that anti-hallucination instruction is prepended when context_messages is provided."""
        with patch.object(gemini_client.client.models, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_generate.return_value = mock_response
            
            prompt = "What did user say about deployment?"
            context_messages = [{"content": "Some context"}]
            
            await gemini_client.generate_response(
                prompt=prompt,
                context_messages=context_messages,
                use_cache=False,
                apply_anti_hallucination=True
            )
            
            # Verify the prompt includes anti-hallucination instruction
            call_args = mock_generate.call_args
            actual_prompt = call_args[1]['contents']
            
            assert ANTI_HALLUCINATION_INSTRUCTION in actual_prompt
            assert prompt in actual_prompt
    
    @pytest.mark.asyncio
    async def test_anti_hallucination_instruction_not_applied_without_context(self):
        """Test that anti-hallucination instruction is NOT applied when no context_messages."""
        with patch.object(gemini_client.client.models, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_generate.return_value = mock_response
            
            prompt = "What is Python?"
            
            await gemini_client.generate_response(
                prompt=prompt,
                context_messages=None,
                use_cache=False,
                apply_anti_hallucination=True
            )
            
            # Verify the prompt does NOT include anti-hallucination instruction
            call_args = mock_generate.call_args
            actual_prompt = call_args[1]['contents']
            
            assert ANTI_HALLUCINATION_INSTRUCTION not in actual_prompt
            assert actual_prompt == prompt
    
    @pytest.mark.asyncio
    async def test_anti_hallucination_can_be_disabled(self):
        """Test that anti-hallucination instruction can be disabled via parameter."""
        with patch.object(gemini_client.client.models, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_generate.return_value = mock_response
            
            prompt = "What did user say?"
            context_messages = [{"content": "Some context"}]
            
            await gemini_client.generate_response(
                prompt=prompt,
                context_messages=context_messages,
                use_cache=False,
                apply_anti_hallucination=False
            )
            
            # Verify the prompt does NOT include anti-hallucination instruction
            call_args = mock_generate.call_args
            actual_prompt = call_args[1]['contents']
            
            assert ANTI_HALLUCINATION_INSTRUCTION not in actual_prompt
    
    @pytest.mark.asyncio
    async def test_llm_responds_with_insufficient_evidence_message(self):
        """Test that LLM can respond with 'I don't have enough information' when appropriate."""
        with patch.object(gemini_client.client.models, 'generate_content') as mock_generate:
            # Simulate LLM following the instruction and saying it doesn't know
            mock_response = Mock()
            mock_response.text = "I don't have enough information in the server history to answer this."
            mock_generate.return_value = mock_response
            
            prompt = "What did user say about quantum computing?"
            context_messages = [{"content": "User talked about Python and Docker"}]
            
            response = await gemini_client.generate_response(
                prompt=prompt,
                context_messages=context_messages,
                use_cache=False,
                apply_anti_hallucination=True
            )
            
            # Verify the response indicates insufficient information
            assert "don't have enough information" in response.lower()
            assert "server history" in response.lower()
    
    def test_anti_hallucination_instruction_content(self):
        """Test that the anti-hallucination instruction contains key phrases."""
        instruction = ANTI_HALLUCINATION_INSTRUCTION
        
        # Check for critical phrases
        assert "ONLY on the Discord messages" in instruction
        assert "do not contain sufficient information" in instruction
        assert "I don't have enough information" in instruction
        assert "Do not infer, assume, or use knowledge beyond" in instruction
        assert "Do not fabricate" in instruction


class TestAntiHallucinationIntegration:
    """Integration tests for anti-hallucination in query pipeline."""
    
    def test_anti_hallucination_instruction_exists(self):
        """Test that anti-hallucination instruction constant exists and has correct content."""
        from ai.gemini_client import ANTI_HALLUCINATION_INSTRUCTION
        
        assert ANTI_HALLUCINATION_INSTRUCTION is not None
        assert "ONLY on the Discord messages" in ANTI_HALLUCINATION_INSTRUCTION
        assert "don't have enough information" in ANTI_HALLUCINATION_INSTRUCTION
        assert "Do not infer, assume, or use knowledge beyond" in ANTI_HALLUCINATION_INSTRUCTION
    
    @pytest.mark.asyncio
    async def test_generate_response_applies_instruction_with_context(self):
        """Test that generate_response applies anti-hallucination instruction when context is provided."""
        from ai.gemini_client import gemini_client, ANTI_HALLUCINATION_INSTRUCTION
        
        with patch.object(gemini_client.client.models, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_generate.return_value = mock_response
            
            prompt = "What did user say?"
            context_messages = [{"content": "Some context"}]
            
            await gemini_client.generate_response(
                prompt=prompt,
                context_messages=context_messages,
                use_cache=False,
                apply_anti_hallucination=True
            )
            
            # Verify the instruction was included in the prompt
            call_args = mock_generate.call_args
            actual_prompt = call_args[1]['contents']
            assert ANTI_HALLUCINATION_INSTRUCTION in actual_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
