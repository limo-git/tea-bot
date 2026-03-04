"""
Test suite for P2: Entity extraction improvements and expert threshold.
Tests entity quality scoring, validation, deduplication, and expert detection.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from extraction.entity_extractor import (
    calculate_entity_quality_score,
    validate_entity,
    filter_low_quality_entities,
    deduplicate_entities,
    MIN_ENTITY_QUALITY_SCORE,
    ENTITY_NAME_MIN_LENGTH,
    ENTITY_NAME_MAX_LENGTH,
)


class TestEntityQualityScoring:
    """Test entity quality score calculation."""
    
    def test_high_quality_entity(self):
        """Test that high-quality entities get good scores."""
        entity = {
            "name": "docker",
            "type": "technology",
            "description": "Container platform for deploying applications in isolated environments",
            "mentioned_by": "alice"
        }
        
        score = calculate_entity_quality_score(entity)
        
        # Should score high (all factors present)
        assert score >= 0.8
    
    def test_low_quality_entity_short_name(self):
        """Test that entities with too-short names get low scores."""
        entity = {
            "name": "x",
            "type": "topic",
            "description": "Some topic",
            "mentioned_by": "bob"
        }
        
        score = calculate_entity_quality_score(entity)
        
        # Should score 0 (name too short)
        assert score == 0.0
    
    def test_low_quality_entity_no_description(self):
        """Test that entities without descriptions get lower scores."""
        entity = {
            "name": "python",
            "type": "technology",
            "description": "",
            "mentioned_by": "alice"
        }
        
        score = calculate_entity_quality_score(entity)
        
        # Should score lower (missing description)
        assert score < 0.8
    
    def test_medium_quality_entity(self):
        """Test medium-quality entity scoring."""
        entity = {
            "name": "api design",
            "type": "topic",
            "description": "REST API design patterns",
            "mentioned_by": "charlie"
        }
        
        score = calculate_entity_quality_score(entity)
        
        # Should be in medium range
        assert 0.6 <= score <= 0.9
    
    def test_invalid_type_lowers_score(self):
        """Test that invalid entity types lower the score."""
        entity = {
            "name": "something",
            "type": "invalid_type",
            "description": "Some description here",
            "mentioned_by": "dave"
        }
        
        score = calculate_entity_quality_score(entity)
        
        # Should score lower (invalid type)
        assert score < 0.8
    
    def test_missing_mentioned_by_lowers_score(self):
        """Test that missing mentioned_by field lowers score."""
        entity = {
            "name": "kubernetes",
            "type": "technology",
            "description": "Container orchestration platform"
        }
        
        score = calculate_entity_quality_score(entity)
        
        # Should score lower (missing mentioned_by)
        assert score < 0.9


class TestEntityValidation:
    """Test entity validation logic."""
    
    def test_valid_entity(self):
        """Test that valid entities pass validation."""
        entity = {
            "name": "postgresql",
            "type": "technology",
            "description": "Relational database system",
            "mentioned_by": "alice"
        }
        
        assert validate_entity(entity) is True
    
    def test_invalid_entity_no_name(self):
        """Test that entities without names fail validation."""
        entity = {
            "type": "technology",
            "description": "Some description"
        }
        
        assert validate_entity(entity) is False
    
    def test_invalid_entity_no_type(self):
        """Test that entities without types fail validation."""
        entity = {
            "name": "something",
            "description": "Some description"
        }
        
        assert validate_entity(entity) is False
    
    def test_invalid_entity_name_too_short(self):
        """Test that entities with too-short names fail validation."""
        entity = {
            "name": "x",
            "type": "topic",
            "description": "Some topic"
        }
        
        assert validate_entity(entity) is False
    
    def test_invalid_entity_name_too_long(self):
        """Test that entities with too-long names fail validation."""
        entity = {
            "name": "x" * 150,  # Way too long
            "type": "topic",
            "description": "Some topic"
        }
        
        assert validate_entity(entity) is False
    
    def test_invalid_entity_wrong_type(self):
        """Test that entities with invalid types fail validation."""
        entity = {
            "name": "something",
            "type": "invalid_type",
            "description": "Some description"
        }
        
        assert validate_entity(entity) is False
    
    def test_invalid_entity_low_quality_score(self):
        """Test that low-quality entities fail validation."""
        entity = {
            "name": "ab",  # Minimum length but poor quality
            "type": "topic",
            "description": ""  # No description
        }
        
        assert validate_entity(entity) is False


class TestEntityFiltering:
    """Test entity filtering based on quality."""
    
    def test_filter_removes_low_quality(self):
        """Test that low-quality entities are filtered out."""
        entities = [
            {
                "name": "docker",
                "type": "technology",
                "description": "Container platform for applications",
                "mentioned_by": "alice"
            },
            {
                "name": "x",  # Too short
                "type": "topic",
                "description": "Something",
                "mentioned_by": "bob"
            },
            {
                "name": "python",
                "type": "technology",
                "description": "Programming language for development",
                "mentioned_by": "charlie"
            }
        ]
        
        filtered = filter_low_quality_entities(entities)
        
        # Should keep only the 2 high-quality entities
        assert len(filtered) == 2
        assert all(e["name"] in ["docker", "python"] for e in filtered)
    
    def test_filter_adds_quality_scores(self):
        """Test that filtering adds quality scores to entities."""
        entities = [
            {
                "name": "kubernetes",
                "type": "technology",
                "description": "Container orchestration platform",
                "mentioned_by": "alice"
            }
        ]
        
        filtered = filter_low_quality_entities(entities)
        
        assert len(filtered) == 1
        assert "quality_score" in filtered[0]
        assert 0.0 <= filtered[0]["quality_score"] <= 1.0
    
    def test_filter_empty_list(self):
        """Test filtering an empty list."""
        filtered = filter_low_quality_entities([])
        assert filtered == []
    
    def test_filter_all_invalid(self):
        """Test filtering when all entities are invalid."""
        entities = [
            {"name": "x", "type": "topic", "description": ""},
            {"name": "y", "type": "invalid", "description": ""},
        ]
        
        filtered = filter_low_quality_entities(entities)
        assert filtered == []


class TestEntityDeduplication:
    """Test entity deduplication logic."""
    
    def test_deduplicate_exact_duplicates(self):
        """Test deduplication of exact duplicate entities."""
        entities = [
            {
                "name": "docker",
                "type": "technology",
                "description": "Container platform"
            },
            {
                "name": "docker",
                "type": "technology",
                "description": "Container platform for apps"
            }
        ]
        
        deduped = deduplicate_entities(entities)
        
        # Should keep only one, preferring longer description
        assert len(deduped) == 1
        assert "for apps" in deduped[0]["description"]
    
    def test_deduplicate_case_insensitive_for_tech(self):
        """Test that technology entities are deduplicated case-insensitively."""
        entities = [
            {
                "name": "Docker",
                "type": "technology",
                "description": "Container platform"
            },
            {
                "name": "docker",
                "type": "technology",
                "description": "Container system"
            }
        ]
        
        deduped = deduplicate_entities(entities)
        
        # Should merge into one
        assert len(deduped) == 1
    
    def test_deduplicate_preserves_case_for_people(self):
        """Test that person entities preserve case."""
        entities = [
            {
                "name": "Alice",
                "type": "person",
                "description": "Developer"
            },
            {
                "name": "alice",
                "type": "person",
                "description": "Engineer"
            }
        ]
        
        deduped = deduplicate_entities(entities)
        
        # Should keep both (different cases for people)
        assert len(deduped) == 2
    
    def test_deduplicate_different_types(self):
        """Test that entities with same name but different types are kept."""
        entities = [
            {
                "name": "python",
                "type": "technology",
                "description": "Programming language"
            },
            {
                "name": "python",
                "type": "project",
                "description": "Python migration project"
            }
        ]
        
        deduped = deduplicate_entities(entities)
        
        # Should keep both (different types)
        assert len(deduped) == 2
    
    def test_deduplicate_empty_list(self):
        """Test deduplication of empty list."""
        deduped = deduplicate_entities([])
        assert deduped == []
    
    def test_deduplicate_prefers_longer_description(self):
        """Test that deduplication prefers entities with longer descriptions."""
        entities = [
            {
                "name": "kubernetes",
                "type": "technology",
                "description": "k8s"
            },
            {
                "name": "kubernetes",
                "type": "technology",
                "description": "Container orchestration platform for managing deployments"
            }
        ]
        
        deduped = deduplicate_entities(entities)
        
        assert len(deduped) == 1
        assert "orchestration platform" in deduped[0]["description"]


class TestEntityExtractionIntegration:
    """Integration tests for entity extraction with quality improvements."""
    
    @pytest.mark.asyncio
    async def test_extraction_applies_filtering(self):
        """Test that entity extraction applies quality filtering."""
        from extraction.entity_extractor import extract_entities_from_chunk
        
        with patch('extraction.entity_extractor._get_client') as mock_client:
            # Mock Gemini response
            mock_response = Mock()
            mock_response.text = '''{
                "entities": [
                    {
                        "name": "docker",
                        "type": "technology",
                        "description": "Container platform for deploying applications",
                        "mentioned_by": "alice"
                    },
                    {
                        "name": "x",
                        "type": "topic",
                        "description": "",
                        "mentioned_by": "bob"
                    }
                ],
                "relationships": [],
                "sentiment": "neutral",
                "importance_score": 7
            }'''
            
            mock_client_instance = Mock()
            mock_client_instance.models.generate_content.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            chunk_text = "[2026-03-04] #dev | alice: Using Docker for deployment"
            chunk_metadata = {"channel_id": 123, "guild_id": 456}
            
            result = await extract_entities_from_chunk(chunk_text, chunk_metadata)
            
            # Should filter out the low-quality entity "x"
            assert len(result["entities"]) == 1
            assert result["entities"][0]["name"] == "docker"
    
    @pytest.mark.asyncio
    async def test_extraction_applies_deduplication(self):
        """Test that entity extraction applies deduplication."""
        from extraction.entity_extractor import extract_entities_from_chunk
        
        with patch('extraction.entity_extractor._get_client') as mock_client:
            # Mock Gemini response with duplicates
            mock_response = Mock()
            mock_response.text = '''{
                "entities": [
                    {
                        "name": "Docker",
                        "type": "technology",
                        "description": "Container platform",
                        "mentioned_by": "alice"
                    },
                    {
                        "name": "docker",
                        "type": "technology",
                        "description": "Container platform for applications",
                        "mentioned_by": "bob"
                    }
                ],
                "relationships": [],
                "sentiment": "neutral",
                "importance_score": 7
            }'''
            
            mock_client_instance = Mock()
            mock_client_instance.models.generate_content.return_value = mock_response
            mock_client.return_value = mock_client_instance
            
            chunk_text = "[2026-03-04] #dev | alice: Docker deployment"
            chunk_metadata = {"channel_id": 123, "guild_id": 456}
            
            result = await extract_entities_from_chunk(chunk_text, chunk_metadata)
            
            # Should deduplicate to 1 entity
            assert len(result["entities"]) == 1


class TestExpertDetection:
    """Test expert detection with confidence scores."""
    
    def test_expert_threshold_constant_exists(self):
        """Test that EXPERT_IN_THRESHOLD constant exists in config."""
        from config import Config
        
        assert hasattr(Config, 'EXPERT_IN_THRESHOLD')
        assert Config.EXPERT_IN_THRESHOLD >= 1
    
    def test_get_experts_for_entity_function_exists(self):
        """Test that get_experts_for_entity function exists."""
        from graph.builder import get_experts_for_entity
        
        assert callable(get_experts_for_entity)


class TestQualityThresholds:
    """Test quality threshold constants."""
    
    def test_min_quality_score_threshold(self):
        """Test that minimum quality score threshold is reasonable."""
        assert 0.0 <= MIN_ENTITY_QUALITY_SCORE <= 1.0
        assert MIN_ENTITY_QUALITY_SCORE >= 0.5  # Should be at least 0.5
    
    def test_entity_name_length_constraints(self):
        """Test entity name length constraints are reasonable."""
        assert ENTITY_NAME_MIN_LENGTH >= 2
        assert ENTITY_NAME_MAX_LENGTH >= 50
        assert ENTITY_NAME_MIN_LENGTH < ENTITY_NAME_MAX_LENGTH


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
