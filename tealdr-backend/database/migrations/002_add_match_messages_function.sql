        -- Migration: Add match_messages function for hybrid search
        -- Purpose: Enable BM25 + pgvector hybrid search for /lookup command
        -- Date: March 2026
        -- Depends on: 001_add_bm25_support.sql

        -- Create the match_messages function for hybrid search
        CREATE OR REPLACE FUNCTION match_messages(
            query_embedding vector(768),
            server_id_filter bigint,
            match_threshold float DEFAULT 0.3,
            match_count int DEFAULT 10
        )
        RETURNS TABLE (
            message_id bigint,
            server_id bigint,
            channel_id bigint,
            thread_id bigint,
            author_id bigint,
            author_name text,
            content text,
            created_at timestamptz,
            embedding vector(768),
            similarity float
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                m.message_id,
                m.server_id,
                m.channel_id,
                m.thread_id,
                m.author_id,
                m.author_name,
                m.content,
                m.created_at,
                m.embedding,
                1 - (m.embedding <=> query_embedding) AS similarity
            FROM messages m
            WHERE m.server_id = server_id_filter
                AND m.embedding IS NOT NULL
                AND (1 - (m.embedding <=> query_embedding)) > match_threshold
            ORDER BY m.embedding <=> query_embedding
            LIMIT match_count;
        END;
        $$;

        -- Grant execute permission to authenticated users
        GRANT EXECUTE ON FUNCTION match_messages TO authenticated;
        GRANT EXECUTE ON FUNCTION match_messages TO anon;

        -- Verification query:
        -- SELECT * FROM match_messages(
        --     (SELECT embedding FROM messages WHERE embedding IS NOT NULL LIMIT 1),
        --     1131555356418523180,
        --     0.3,
        --     5
        -- );
