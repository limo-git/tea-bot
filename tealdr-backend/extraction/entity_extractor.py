import json
import logging
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import types
from config import Config

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _client


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


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def extract_entities_from_chunk(chunk_text: str, chunk_metadata: dict) -> dict[str, Any]:
    """
    Extract entities and relationships from a chunk of Discord messages using Gemini.

    Args:
        chunk_text: Formatted string of messages in the chunk
        chunk_metadata: Dict with channel_id, channel_name, start_time, end_time

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
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=2048),
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
