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
            
            CREATE INDEX IF NOT EXISTS idx_embeddings_document ON hita_embeddings(document_id);
        """)

        # Create vector similarity search index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS hita_embeddings_vector_idx
            ON hita_embeddings
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 50);
        """)


def store_embeddings(document_id: str, chunks: list):
    """
    Store text chunks and their embeddings in pgvector.
    document_id: UUID of document
    chunks: list of text chunks
    """
    try:
        from apps.ai_engine.gemini import generate_embeddings
        
        _ensure_table()
        
        with connection.cursor() as cursor:
            for i, chunk in enumerate(chunks):
                embedding = generate_embeddings(chunk)
                
                # Convert embedding list to pgvector format
                embedding_str = '[' + ','.join(str(e) for e in embedding) + ']'
                
                cursor.execute("""
                    INSERT INTO hita_embeddings (document_id, chunk_index, chunk_text, embedding)
                    VALUES (%s, %s, %s, %s)
                """, [document_id, i, chunk, embedding_str])
        
        logger.info(f"Stored {len(chunks)} embeddings for document {document_id}")
    
    except Exception as e:
        logger.error(f"Error storing embeddings: {str(e)}")
        raise


def search_similar_chunks(question: str, user_id: str, limit: int = 5) -> list:
    """
    Search for chunks similar to the question using pgvector.
    Filters by user_id for security.
    Returns: list of (chunk_text, document_name) tuples
    """
    try:
        from apps.ai_engine.gemini import generate_embeddings
        from apps.documents.models import Document
        
        question_embedding = generate_embeddings(question)
        embedding_str = '[' + ','.join(str(e) for e in question_embedding) + ']'
        
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    e.chunk_text,
                    d.original_name,
                    e.document_id,
                    e.embedding <=> %s::vector AS distance
                FROM hita_embeddings e
                JOIN documents_document d ON d.id = e.document_id::uuid
                WHERE d.user_id = %s::uuid AND d.is_deleted = false AND d.status IN ('processed', 'ready')
                ORDER BY distance
                LIMIT %s
            """, [embedding_str, str(user_id), limit])
            
            results = cursor.fetchall()
            return [{'chunk': row[0], 'document': row[1], 'doc_id': row[2]} for row in results]
    
    except Exception as e:
        logger.error(f"Error searching embeddings: {str(e)}")
        return []


def delete_document_embeddings(document_id: str):
    """Delete all embeddings for a document."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM hita_embeddings WHERE document_id = %s
            """, [document_id])
        
        logger.info(f"Deleted embeddings for document {document_id}")
    
    except Exception as e:
        logger.error(f"Error deleting embeddings: {str(e)}")
