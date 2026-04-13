"""
Vector embeddings storage and retrieval using pgvector.
"""
import logging
from django.db import connection

logger = logging.getLogger(__name__)


def _ensure_table():
    """Create hita_embeddings table if it doesn't exist."""
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hita_embeddings (
                id BIGSERIAL PRIMARY KEY,
                document_id UUID NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding vector(768),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_embeddings_document
                ON hita_embeddings(document_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS hita_embeddings_vector_idx
            ON hita_embeddings
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 50);
        """)


def store_embeddings(document_id: str, chunks: list):
    try:
        from apps.ai_engine.gemini import generate_embeddings
        _ensure_table()

        with connection.cursor() as cursor:
            for i, chunk in enumerate(chunks):
                try:
                    embedding     = generate_embeddings(chunk)
                    embedding_str = '[' + ','.join(str(e) for e in embedding) + ']'
                    cursor.execute("""
                        INSERT INTO hita_embeddings
                            (document_id, chunk_index, chunk_text, embedding)
                        VALUES (%s, %s, %s, %s)
                    """, [document_id, i, chunk, embedding_str])
                except Exception as chunk_err:
                    logger.error(f'Skipping chunk {i} — embedding failed: {chunk_err}')
                    continue   # skip bad chunk, store the rest

        logger.info(f'Stored embeddings for document {document_id}')

    except Exception as e:
        logger.error(f'Error storing embeddings: {e}')
        raise


def _run_similarity_query(embedding_str: str, user_id: str, limit: int) -> list:
    """Run the pgvector similarity search query. Shared by main + retry."""
    """Return best matching chunk per document — no duplicates."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT chunk_text, document_id, original_name, category, similarity
            FROM (
                SELECT DISTINCT ON (e.document_id)
                    e.chunk_text,
                    e.document_id,
                    d.original_name,
                    d.category,
                    1 - (e.embedding <=> %s::vector) AS similarity
                FROM hita_embeddings e
                JOIN documents_document d
                    ON e.document_id::uuid = d.id
                WHERE d.user_id      = %s::uuid
                AND d.is_deleted   = FALSE
                AND d.status       IN ('processed', 'ready')
                AND 1 - (e.embedding <=> %s::vector) > 0.4   -- ← minimum threshold
                ORDER BY e.document_id, e.embedding <=> %s::vector
            ) best_chunks
            ORDER BY similarity DESC
            LIMIT %s
        """, [embedding_str, str(user_id), embedding_str, embedding_str, limit])

        rows = cursor.fetchall()

    return [
        {
            'chunk':         row[0],   # ← consistent key used everywhere
            'doc_id':        row[1],
            'document_name': row[2],
            'category':      row[3],
            'similarity':    float(row[4]),
        }
        for row in rows
    ]


def search_similar_chunks(question: str, user_id: str, limit: int = 5) -> list:
    """
    Search for chunks similar to the question using pgvector.
    Filters by user_id for security.
    Returns list of dicts with keys: chunk, doc_id, document_name, category, similarity
    """
    from apps.ai_engine.gemini import generate_embeddings

    try:
        # Force fresh connection — avoids Supabase idle timeout
        connection.close()
        question_embedding = generate_embeddings(question)
        embedding_str      = '[' + ','.join(str(e) for e in question_embedding) + ']'

        # Ensure connection is alive before querying
        #connection.ensure_connection()

        return _run_similarity_query(embedding_str, user_id, limit)

    except Exception as e:
        logger.error(f'Error searching embeddings: {e}')

        # Connection dropped — close and retry once
        try:
            logger.info('Resetting DB connection and retrying...')
            connection.close()

            question_embedding = generate_embeddings(question)
            embedding_str      = '[' + ','.join(str(e) for e in question_embedding) + ']'

            return _run_similarity_query(embedding_str, user_id, limit)

        except Exception as retry_err:
            logger.error(f'Retry also failed: {retry_err}')
            return []


def delete_document_embeddings(document_id: str):
    """Delete all embeddings for a document."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM hita_embeddings WHERE document_id = %s",
                [document_id]
            )
        logger.info(f'Deleted embeddings for document {document_id}')

    except Exception as e:
        logger.error(f'Error deleting embeddings: {e}')