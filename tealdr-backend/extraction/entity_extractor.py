import json
import logging
from typing import Any, Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import types
from config import Config

logger = logging.getLogger(__name__)

_client: genai.Client | None = None

# P2: Entity quality thresholds
MIN_ENTITY_QUALITY_SCORE = 0.6  # Minimum quality score to keep an entity
MIN_DESCRIPTION_LENGTH = 10  # Minimum description length for valid entities
ENTITY_NAME_MIN_LENGTH = 2  # Minimum entity name length
ENTITY_NAME_MAX_LENGTH = 100  # Maximum entity name length


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _client


def calculate_entity_quality_score(entity: dict, context: str = "") -> float:
    """
    Calculate quality score for an entity (0.0 to 1.0).
    
    Factors:
    - Name validity (length, format)
    - Description quality (length, specificity)
    - Type appropriateness
    - Context relevance
    
    Args:
        entity: Entity dict with name, type, description
        context: Original message context for relevance check
        
    Returns:
        Quality score between 0.0 and 1.0
    """
    score = 0.0
    
    # Factor 1: Name validity (0.3 weight)
    name = entity.get("name", "")
    if not name or len(name) < ENTITY_NAME_MIN_LENGTH:
        return 0.0  # Invalid entity
    
    if len(name) > ENTITY_NAME_MAX_LENGTH:
        score += 0.1  # Penalize overly long names
    elif ENTITY_NAME_MIN_LENGTH <= len(name) <= 50:
        score += 0.3  # Good name length
    else:
        score += 0.2
    
    # Factor 2: Description quality (0.3 weight)
    description = entity.get("description", "")
    if len(description) >= MIN_DESCRIPTION_LENGTH:
        score += 0.2
        # Bonus for detailed descriptions
        if len(description) >= 50:
            score += 0.1
    
    # Factor 3: Type validity (0.2 weight)
    valid_types = {"person", "topic", "technology", "decision", "bug", "question", "project"}
    entity_type = entity.get("type", "")
    if entity_type in valid_types:
        score += 0.2
    
    # Factor 4: Mentioned by field (0.2 weight)
    if entity.get("mentioned_by"):
        score += 0.2
    
    return min(score, 1.0)


def deduplicate_entities(entities: List[dict]) -> List[dict]:
    """
    Deduplicate entities by normalizing names and merging similar ones.
    
    Args:
        entities: List of entity dicts
        
    Returns:
        Deduplicated list of entities
    """
    if not entities:
        return []
    
    # Group by normalized name and type
    entity_map = {}
    
    for entity in entities:
        name = entity.get("name", "").strip()
        entity_type = entity.get("type", "")
        
        # Normalize name based on type
        if entity_type in {"topic", "technology", "project"}:
            # Lowercase for technical terms
            normalized_name = name.lower()
        else:
            # Keep original case for people
            normalized_name = name
        
        key = (normalized_name, entity_type)
        
        if key not in entity_map:
            entity_map[key] = entity
        else:
            # Merge: prefer longer description
            existing = entity_map[key]
            if len(entity.get("description", "")) > len(existing.get("description", "")):
                entity_map[key] = entity
    
    return list(entity_map.values())


def validate_entity(entity: dict) -> bool:
    """
    Validate entity structure and content.
    
    Args:
        entity: Entity dict to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Required fields
    if not entity.get("name") or not entity.get("type"):
        return False
    
    # Name length check
    name = entity["name"]
    if len(name) < ENTITY_NAME_MIN_LENGTH or len(name) > ENTITY_NAME_MAX_LENGTH:
        return False
    
    # Type check
    valid_types = {"person", "topic", "technology", "decision", "bug", "question", "project"}
    if entity["type"] not in valid_types:
        return False
    
    # Quality score check
    quality_score = calculate_entity_quality_score(entity)
    if quality_score < MIN_ENTITY_QUALITY_SCORE:
        return False
    
    return True


def filter_low_quality_entities(entities: List[dict], context: str = "") -> List[dict]:
    """
    Filter out low-quality entities based on validation and quality scores.
    
    Args:
        entities: List of entity dicts
        context: Original message context
        
    Returns:
        Filtered list of high-quality entities
    """
    filtered = []
    
    for entity in entities:
        if validate_entity(entity):
            quality_score = calculate_entity_quality_score(entity, context)
            entity["quality_score"] = quality_score
            
            if quality_score >= MIN_ENTITY_QUALITY_SCORE:
                filtered.append(entity)
            else:
                logger.debug(f"Filtered low-quality entity: {entity.get('name')} (score: {quality_score:.2f})")
        else:
            logger.debug(f"Filtered invalid entity: {entity.get('name')}")
    
    return filtered


EXTRACTION_PROMPT = """You are an expert knowledge graph builder for Discord communities.

Analyze the following Discord messages and extract structured information.

## Messages
```
{messages}
```

## Your Task
Extract entities and relationships from these messages. Return ONLY valid JSON matching the schema below — no explanation, no markdown, no extra text.

## JSON Schema
```json
{{
  "entities": [
    {{
      "name": "string (canonical name, lowercase for topics/tech, original case for people)",
      "type": "person | topic | technology | decision | bug | question | project",
      "description": "string (1 sentence describing this entity in context)",
      "mentioned_by": "string (Discord username of who mentioned this entity)"
    }}
  ],
  "relationships": [
    {{
      "from_entity": "string (entity name)",
      "from_type": "string (entity type)",
      "to_entity": "string (entity name)",
      "to_type": "string (entity type)",
      "relationship": "string (verb in UPPER_SNAKE_CASE, e.g. SUGGESTED, FIXED_BY, DEPENDS_ON, DISCUSSED, REPORTED, RESOLVED, ASKED_ABOUT, WORKS_ON)",
      "mentioned_by": "string (Discord username of who created this relationship)"
    }}
  ],
  "sentiment": "positive | negative | neutral | mixed",
  "importance_score": 5
}}
```

## Rules
- `importance_score` is 1-10 (10 = critical decision/announcement, 1 = casual chat)
- Only extract entities that are clearly present in the messages
- For `person` entities, use the Discord username exactly as it appears
- For `technology`, `topic`, `project` — use lowercase canonical names (e.g. "postgresql", "authentication", "mobile app")
- For `decision` — describe the decision briefly (e.g. "use redis for caching")
- For `bug` — describe the bug briefly (e.g. "login page crash on mobile")
- **CRITICAL:** Set `mentioned_by` to the exact Discord username of who mentioned/discussed each entity or relationship
- Relationships must reference entity names that exist in the entities array
- If no meaningful entities exist, return empty arrays

Return only the JSON object:"""


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    reraise=True
)
async def extract_entities_from_chunk(chunk_text: str, chunk_metadata: dict) -> dict:
    """
    Extract entities, relationships, and metadata from a chunk of messages.

    Args:
        chunk_text: Formatted messages from format_messages_for_extraction()
        chunk_metadata: Dict with channel_id, guild_id, start_time, end_time

    Returns:
        Dict with entities, relationships, sentiment, importance_score
    """
    import asyncio
    client = _get_client()

    prompt = EXTRACTION_PROMPT.format(messages=chunk_text)

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=4096),
            )
        )

        raw = response.text.strip()

        # Strip markdown code fences if Claude wraps it anyway
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        result = json.loads(raw)

        # Validate and fill defaults
        result.setdefault("entities", [])
        result.setdefault("relationships", [])
        result.setdefault("sentiment", "neutral")
        result.setdefault("importance_score", 5)
        result["chunk_metadata"] = chunk_metadata

        # P2: Apply entity quality filtering and deduplication
        original_count = len(result['entities'])
        
        # Filter low-quality entities
        result['entities'] = filter_low_quality_entities(result['entities'], chunk_text)
        
        # Deduplicate entities
        result['entities'] = deduplicate_entities(result['entities'])
        
        filtered_count = len(result['entities'])
        if filtered_count < original_count:
            logger.info(
                f"Entity quality filtering: {original_count} -> {filtered_count} entities "
                f"(removed {original_count - filtered_count} low-quality)"
            )

        logger.info(
            f"Extracted {len(result['entities'])} entities, "
            f"{len(result['relationships'])} relationships from chunk "
            f"(channel={chunk_metadata.get('channel_name')}, "
            f"importance={result['importance_score']})"
        )
        return result

    except json.JSONDecodeError as e:
        logger.warning(f"Gemini returned invalid JSON (likely truncated): {e}\nRaw: {raw[:300]}")
        # Try to salvage partial JSON by closing it
        try:
            # Add closing braces to attempt recovery
            fixed = raw.rstrip()
            if not fixed.endswith("}"):
                # Count open braces and close them
                open_braces = fixed.count("{") - fixed.count("}")
                open_brackets = fixed.count("[") - fixed.count("]")
                fixed += '"' * fixed.count('"') % 2  # Close any open strings
                fixed += "]" * open_brackets
                fixed += "}" * open_braces
            result = json.loads(fixed)
            logger.info("Recovered partial JSON from truncated response")
        except:
            logger.error(f"Could not recover JSON, returning empty result")
            return {"entities": [], "relationships": [], "sentiment": "neutral", "importance_score": 1, "chunk_metadata": chunk_metadata}
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        raise


def format_messages_for_extraction(messages: list[dict]) -> str:
    """Format a list of message dicts into a readable string for Claude."""
    lines = []
    for msg in messages:
        ts = msg.get("created_at", "")
        author = msg.get("author_name", "Unknown")
        content = msg.get("content", "")
        channel = msg.get("channel_name", "")
        lines.append(f"[{ts}] #{channel} | {author}: {content}")
    return "\n".join(lines)
