import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import types
from config import Config
from retrieval.context_assembler import format_context_for_prompt

logger = logging.getLogger(__name__)

_client: genai.Client | None = None

ANSWER_PROMPT = """{persona}

---

## Your Role
You are an intelligent assistant for a Discord server. You answer questions using retrieved messages and knowledge graph data from the server's chat history. Your answers are grounded — you only state what is supported by the context below.

## Retrieved Context
The following messages and graph data were retrieved as most relevant to this question. Items marked `[graph]` come from the knowledge graph (structurally relevant). Items marked `[search]` come from semantic vector search.

```
{context}
```

## Instructions
1. **Answer directly and completely** using only the context above.
2. **Use readable names** — Always use the actual username (e.g., "limo.ew") and channel name (e.g., "#the-lounge"), never use IDs or @mentions.
3. **For expert_finding intent** — list the people who know about this topic and how often they've discussed it.
4. **For relational intent** — explain the connection/path between the two entities clearly.
5. **For evolutionary intent** — describe how the topic changed over time chronologically.
6. **For summarization** — give a comprehensive organized overview with headers.
7. **Format for Discord** — use bullet points, bold for names/links, keep it scannable.
8. **If context is insufficient** — say so briefly and suggest what the user could search for instead.
9. **Never fabricate** — do not add information not present in the context.

Answer the question now:"""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_answer(
    query: str,
    pipeline_result: dict,
    user_name: str = "the user",
    persona: str = None,
) -> str:
    """
    Step 5: Generate a grounded answer using Claude with assembled context.

    Args:
        query: Original user question
        pipeline_result: Output from run_query_pipeline()
        user_name: Discord display name of the requester
        persona: Optional server persona string

    Returns:
        Answer string ready to send to Discord
    """
    if persona is None:
        persona = "You are a helpful, knowledgeable Discord assistant. Be direct, well-organized, and thorough."

    context_items = pipeline_result.get("context", [])
    understanding = pipeline_result.get("understanding", {})

    if not context_items:
        return (
            f"I couldn't find any relevant information about **{understanding.get('primary_entity', 'that topic')}** "
            f"in the server history. Try asking with different keywords, or the topic may not have been discussed yet."
        )

    context_str = format_context_for_prompt(context_items)

    prompt = ANSWER_PROMPT.format(
        persona=persona,
        user_name=user_name,
        query=query,
        intent=understanding.get("intent", "summarization"),
        primary_entity=understanding.get("primary_entity", ""),
        context=context_str,
    )

    client = _get_client()

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=4096),
            )
        )
        answer = response.text.strip()
        logger.info(f"Answer generated ({len(answer)} chars) for query: {query[:60]}")
        return answer

    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        raise
