import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from google import genai
from google.genai import types
from config import Config
from retrieval.context_assembler import format_context_for_prompt

logger = logging.getLogger(__name__)

_client: genai.Client | None = None

ANSWER_PROMPT = """<system_instructions>
{persona}

You are a Discord server assistant that answers questions using ONLY retrieved messages from the server's chat history.

## CRITICAL RULES - FOLLOW STRICTLY:

1. **GROUND ALL ANSWERS IN PROVIDED CONTEXT**
   - Answer ONLY using the documents provided below
   - DO NOT use your training data or general knowledge
   - If the answer isn't in the provided context, explicitly say so

2. **EXPLICIT UNCERTAINTY**
   - Distinguish between:
     * "The messages show X" (directly stated)
     * "The messages suggest X" (implied/inferred)
     * "This isn't covered in the retrieved messages" (not present)
   - Make uncertainty a first-class output, not something to hide

3. **HANDLE INSUFFICIENT CONTEXT**
   - If context is insufficient or irrelevant: "I couldn't find relevant information about [topic] in the provided messages."
   - Suggest what the user could search for instead
   - NEVER fill gaps with plausible-sounding information

4. **CITATION FORMAT**
   - Cite sources inline using format: [Author in #channel]
   - Example: "According to limo.ew in #general, the deployment was successful."
   - Always attribute information to specific messages

5. **NEVER FABRICATE**
   - Do not add details not present in the context
   - Do not make assumptions beyond what's explicitly stated
   - If asked about something not in context, say "The provided messages don't contain information about [topic]"

6. **SYNTHESIZE, DON'T QUOTE**
   - Summarize information in your own words
   - Do not reproduce message chunks verbatim
   - Be concise and organized

7. **FORMAT FOR DISCORD**
   - Use bullet points and bold for readability
   - Use actual usernames (e.g., "limo.ew") not IDs or @mentions
   - Use channel names (e.g., "#general") not channel IDs
   - Keep responses scannable

8. **INTENT-SPECIFIC FORMATTING**
   - **expert_finding**: List people and their discussion frequency
   - **relational**: Explain connections between entities clearly
   - **evolutionary**: Describe chronological changes
   - **summarization**: Organized overview with headers
   - **temporal_context**: Connect discussions across time periods
   - **conversation_threads**: Show discussion flow and contributions

</system_instructions>

<retrieved_context>
{temporal_context_info}

The following messages were retrieved as most relevant to the question.
Items marked [graph] come from knowledge graph traversal.
Items marked [search] come from semantic vector search.

{context}
</retrieved_context>

<task>
Question: {query}

Using ONLY the retrieved context above, provide a complete answer. If the context doesn't contain the answer, explicitly state that.
</task>"""


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

    # Handle empty retrieval explicitly - don't send to LLM
    if not context_items:
        entity = understanding.get('primary_entity', 'that topic')
        return (
            f"❌ **No Relevant Messages Found**\n\n"
            f"I couldn't find any messages about **{entity}** in the server history.\n\n"
            f"**Suggestions:**\n"
            f"• Try different keywords or phrases\n"
            f"• Check if the topic was discussed in a different channel\n"
            f"• The topic may not have been discussed yet\n"
            f"• Try a broader search term"
        )

    # Import temporal context helpers
    from generation.temporal_context_helper import _generate_temporal_context_info, format_context_for_prompt
    
    context_str = format_context_for_prompt(context_items)
    
    # Generate temporal context information
    temporal_info = _generate_temporal_context_info(pipeline_result, context_items)

    prompt = ANSWER_PROMPT.format(
        persona=persona,
        query=query,
        context=context_str,
        temporal_context_info=temporal_info,
    )

    client = _get_client()

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=8192),
            )
        )
        answer = response.text.strip()
        logger.info(f"Answer generated ({len(answer)} chars) for query: {query[:60]}")
        return answer

    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        raise
