from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document(self, document_id: str):
    """
    Main async task: extract text → scrub PII → embed → categorise → save.
    Runs in background after every document upload.
    """
    from apps.documents.models import Document
    from apps.documents.utils import extract_text, scrub_pii, chunk_text
    from apps.ai_engine.gemini import categorise_document
    from apps.ai_engine.embeddings import store_embeddings

    try:
        # 1. Load document
        document = Document.objects.get(id=document_id)
        document.status = 'processing'
        document.save(update_fields=['status'])

        logger.info(f"[Hita] Processing document {document_id}: {document.original_name}")

        # 2. Extract raw text from file
        raw_text = extract_text(document.file_path)
        if not raw_text:
            raise ValueError("No text could be extracted from this document")

        # 3. Scrub PII before any AI call
        clean_text = scrub_pii(raw_text)

        # 4. Chunk text for embedding
        chunks = chunk_text(clean_text)
        logger.info(f"[Hita] {len(chunks)} chunks created for {document_id}")

        # 5. Generate and store embeddings
        store_embeddings(document_id, chunks)
        logger.info(f"[Hita] Embeddings stored for {document_id}")

        # 6. Categorise and extract metadata via Gemini
        ai_result = categorise_document(clean_text)

        # 7. Update document record with AI results
        document.extracted_text   = raw_text[:5000]     # store first 5000 chars
        document.category         = ai_result.get('category', 'other')
        document.summary          = ai_result.get('summary', '')
        document.extracted_vendor = ai_result.get('extracted_vendor') or ''
        document.status           = 'ready'
        document.error_message    = ''

        # Handle date
        date_str = ai_result.get('extracted_date')
        if date_str:
            from datetime import date
            try:
                document.extracted_date = date.fromisoformat(date_str)
            except ValueError:
                pass

        # Handle amount
        amount = ai_result.get('extracted_amount')
        if amount is not None:
            try:
                document.extracted_amount = float(amount)
            except (ValueError, TypeError):
                pass

        document.save()
        logger.info(f"[Hita] Document {document_id} processing complete. Category: {document.category}")

        return {'status': 'success', 'document_id': document_id, 'category': document.category}

    except Document.DoesNotExist:
        logger.error(f"[Hita] Document {document_id} not found")
        return {'status': 'error', 'message': 'Document not found'}

    except Exception as exc:
        logger.error(f"[Hita] Error processing {document_id}: {str(exc)}")
        # Update document with error status
        try:
            doc = Document.objects.get(id=document_id)
            doc.status        = 'failed'
            doc.error_message = str(exc)[:500]
            doc.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        # Retry up to 3 times
        raise self.retry(exc=exc)
