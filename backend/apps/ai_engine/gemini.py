"""
Gemini API integration for document processing.
Handles categorization, summarization, and embedding generation.
"""
import os
import json
import logging

logger = logging.getLogger(__name__)


def categorise_document(text: str) -> dict:
    """
    Use Gemini to categorize document and extract metadata.
    Returns: {category, extracted_date, extracted_amount, extracted_vendor, summary}
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY not set')
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = f"""Analyze this document and extract the following information in JSON format:
        
Document text (first 3000 chars):
{text[:3000]}

Return a JSON object with these fields (use null if not found):
{{
    "category": "grocery|medical|maintenance|personal|events|finance|education|other",
    "extracted_date": "YYYY-MM-DD or null",
    "extracted_amount": number or null (in rupees),
    "extracted_vendor": "shop/hospital/vendor name or null",
    "summary": "one-line summary of document"
}}

Only return valid JSON, no markdown or extra text."""
        
        response = model.generate_content(prompt)
        
        # Parse response
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            # Extract JSON from response if wrapped in markdown
            json_str = response.text
            if '```' in json_str:
                json_str = json_str.split('```')[1].replace('json', '', 1)
            result = json.loads(json_str)
        
        return result
    
    except Exception as e:
        logger.error(f"Gemini categorization error: {str(e)}")
        return {
            'category': 'other',
            'extracted_date': None,
            'extracted_amount': None,
            'extracted_vendor': None,
            'summary': 'Unable to process'
        }


def generate_embeddings(text: str) -> list:
    """
    Generate vector embeddings for text using Gemini.
    Returns: embedding vector (768 dimensions)
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY not set')
        
        genai.configure(api_key=api_key)
        
        result = genai.embed_content(
            model='models/gemini-embedding-001',
            content=text,
            task_type='retrieval_document',
            
        )
        
        return result['embedding'][:768]
    
    except Exception as e:
        logger.error(f"Embedding generation error: {str(e)}")
        return [0.0] * 768


def answer_query(question: str, chunks: list) -> str:
    """
    Use Gemini to answer question based on document chunks.
    chunks: list of relevant text chunks from documents
    Returns: answer string
    """
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY not set')
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        context = '\n\n---\n\n'.join(chunks[:5])  # Use top 5 chunks
        
        prompt = f"""Answer the user's question based ONLY on the provided document excerpts.
If the answer is not in the documents, say "I couldn't find this information in your documents."

Question: {question}

Document excerpts:
{context}

Provide a clear, concise answer in plain language."""
        
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        logger.error(f"Query answering error: {str(e)}")
        return "Sorry, I encountered an error processing your query."
