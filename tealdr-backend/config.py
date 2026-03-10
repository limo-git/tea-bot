import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Centralized configuration from environment variables. Provides defaults
    for optional settings while requiring critical secrets (Discord token, API keys).
    Type coercion happens at load time to catch conversion errors early.
    """

    # Discord & Core Infrastructure
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
    SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    """
    EXCLUDED_CHANNELS is comma-separated IDs (e.g., "123456,789012").
    Split and filter to handle edge cases: missing env var, trailing commas, empty strings.
    """
    EXCLUDED_CHANNELS = (
        os.getenv("EXCLUDED_CHANNELS", "").split(",")
        if os.getenv("EXCLUDED_CHANNELS")
        else []
    )
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Message retention & cleanup (type-coerced to int with sensible defaults)
    MESSAGE_RETENTION_DAYS = int(os.getenv("MESSAGE_RETENTION_DAYS", "30"))
    CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))

    # Gemini model for Graph RAG (reuses GEMINI_API_KEY)
    GRAPH_RAG_MODEL = os.getenv("GRAPH_RAG_MODEL", "gemini-3-flash-preview")

    # Neo4j (Graph RAG)
    NEO4J_URI = os.getenv("NEO4J_URI", "")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

    """
    Graph RAG tuning parameters. Integer coercion at load time prevents
    downstream type errors when these values are used in comparisons or calculations.
    Defaults set to empirically-tested values.
    """
    EXPERT_IN_THRESHOLD = int(os.getenv("EXPERT_IN_THRESHOLD", "5"))
    CHUNK_WINDOW_MINUTES = int(os.getenv("CHUNK_WINDOW_MINUTES", "15"))
    RELATIONSHIP_DECAY_DAYS = int(os.getenv("RELATIONSHIP_DECAY_DAYS", "30"))
    VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "10"))

    """
    GRAPH_RAG_ENABLED controls whether the bot uses Neo4j + knowledge graph features.
    String 'true'/'false' from env must be normalized to boolean for conditional logic.
    .lower() handles case variations in env files.
    """
    GRAPH_RAG_ENABLED = os.getenv("GRAPH_RAG_ENABLED", "true").lower() == "true"

    @classmethod
    def validate(cls):
        """
        Validate presence of critical secrets before bot startup.
        Fails fast with clear error message to prevent runtime failures.
        Only checks secrets that gate functionality; optional features (Neo4j, etc.)
        checked at feature-init time for graceful degradation.
        """
        required = {
            "DISCORD_BOT_TOKEN": cls.DISCORD_BOT_TOKEN,
            "SUPABASE_PROJECT_URL": cls.SUPABASE_PROJECT_URL,
            "SUPABASE_SECRET_KEY": cls.SUPABASE_SECRET_KEY,
            "GEMINI_API_KEY": cls.GEMINI_API_KEY,
        }

        missing = [key for key, value in required.items() if not value]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return True

    @classmethod
    def get_excluded_channel_ids(cls):
        """
        Parse EXCLUDED_CHANNELS into integer IDs. Filters out non-numeric entries
        and strips whitespace to handle formatting variations in .env files
        (e.g., "123, 456" or "123,456").
        """
        return [
            int(ch_id.strip())
            for ch_id in cls.EXCLUDED_CHANNELS
            if ch_id.strip().isdigit()
        ]
