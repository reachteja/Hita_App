"""
Gemini API integration — uses google-genai package.
Client created at module level to avoid premature garbage collection.
"""
import os
import json
import logging
import datetime

logger            = logging.getLogger(__name__)
_GENERATION_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite')
_EMBEDDING_MODEL  = 'models/gemini-embedding-001'

# ── Module-level client — stays alive for entire worker lifetime ──
_gemini_client = None

def _get_client():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    return _gemini_client


def categorise_document(text: str) -> dict:
    global _gemini_client
    try:
        client   = _get_client()
        response = client.models.generate_content(
            model    = _GENERATION_MODEL,
            contents = [f"""Analyse this document and return JSON only.

Document:
{text[:3000]}

Return exactly this JSON (null if not found):
{{
    "category": "grocery|medical|maintenance|personal|events|finance|education|other",
    "extracted_date": "YYYY-MM-DD or null",
    "extracted_amount": number or null,
    "extracted_vendor": "name or null",
    "summary": "one sentence"
}}

Category guide:
- grocery: supermarket, BigBasket, DMart, food bills, grocery stores
- medical: pharmacy, hospital, prescriptions, lab reports, health checkups
- maintenance: plumber, electrician, carpenter, painter, home repair,
               vehicle service, utility bills, TNEB, BESCOM, electricity board,
               water board, gas connection, internet/broadband bills
- finance: bank statements, insurance, investments, tax returns, loan documents
- education: syllabus, certificates, training materials, marksheets, course fees
- events: invitations, bookings, event programs, tickets
- personal: personal notes, general documents, letters
- other: nothing else fits
IMPORTANT: Electricity bills, water bills, utility bills → always maintenance, never finance.
JSON only. No markdown."""],
        )

        raw = response.text.strip()
        if '```' in raw:
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        return json.loads(raw.strip())

    except Exception as e:
        logger.error(f'Gemini categorisation error: {e}')
        # Reset client on error so next call gets a fresh one
        
        _gemini_client = None
        return {
            'category':         'other',
            'extracted_date':   None,
            'extracted_amount': None,
            'extracted_vendor': None,
            'summary':          'Unable to process',
        }


def generate_embeddings(text: str) -> list:
    global _gemini_client
    try:
        client = _get_client()
        result = client.models.embed_content(
            model    = _EMBEDDING_MODEL,
            contents = [text],
        )
        if hasattr(result, 'embeddings') and result.embeddings:
            return list(result.embeddings[0].values)[:768]
        raise ValueError(f'Unexpected embedding response: {result}')

    except Exception as e:
        logger.error(f'Embedding generation error: {e}')
        # Reset client on error
        
        _gemini_client = None
        raise


def detect_query_intent(question: str, history: list = []) -> dict:
    global _gemini_client
    today = datetime.date.today().isoformat()

    # Build recent context from history
    recent = ''
    if history:
        last_pairs = history[-4:]  # last 2 exchanges
        recent = '\n'.join([
            f"{'User' if m['role'] == 'user' else 'Hita'}: {m['content']}"
            for m in last_pairs
        ])

    try:
        client   = _get_client()
        response = client.models.generate_content(
            model    = _GENERATION_MODEL,
            contents = [f"""Analyse this question from a document vault app user.

Recent conversation:
{recent if recent else 'No previous messages'}

Current question: "{question}"

Return ONLY this JSON, no markdown:
{{
  "intent": "list_documents or answer_question",
  "filters": {{
    "category": "grocery|medical|maintenance|personal|events|finance|education|other or null",
    "date_from": "YYYY-MM-DD or null",
    "date_to": "YYYY-MM-DD or null",
    "search_term": "string or null",
    "vendor": "string or null"
  }},
  "reasoning": "one line"
}}

INTENT RULES — read carefully:

Use "list_documents" ONLY when user wants to:
- See a list of document files
- "show my bills", "list my documents", "find my receipts"
- Questions about which documents exist
- show, find, list, fetch, get, display documents.

Use "answer_question" when user wants to:
- Know what they bought, spent, or did
- Get details FROM document content
- "what did I buy", "what medicines", "what items", "how much"
- "what did I purchase", "what was in my bill"
- ANY question starting with "what did I..."
- Follow-up questions like "give details", "tell me more","what products"
- how much, total, amount, what medicines, details from content, follow-up questions.

EXAMPLES:
"what did I buy from bigbasket" → answer_question (wants item details)
"show my bigbasket bill" → list_documents (wants document card)
"how much did I spend" → answer_question (wants amount from content)
"list my medical bills" → list_documents (wants document list)
"what medicines am I taking" → answer_question (wants content details)
"find my Apollo receipt" → list_documents (wants document card)

CATEGORY EXTRACTION HINTS:
- bigbasket, dmart, reliance fresh, more supermarket → grocery
- apollo pharmacy, medplus, hospital, clinic → medical  
- plumber, electrician, carpenter, painter → maintenance
- tneb, bescom, electricity board, water bill → finance
If vendor name implies a category — set that category even if not explicitly stated.

Today: {today}. Calculate real dates for "last month", "this year"."""],
        )

        raw = response.text.strip()
        if '```' in raw:
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        return json.loads(raw.strip())

    except Exception as e:
        logger.error(f'Intent detection error: {e}')
        
        _gemini_client = None
        # Retry once
        try:
            client   = _get_client()
            response = client.models.generate_content(
                model    = _GENERATION_MODEL,
                contents = [prompt],
            )
            raw = response.text.strip()
            if '```' in raw:
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception:
            return {'intent': 'answer_question', 'filters': {}, 'reasoning': 'fallback'}


def answer_query(question: str, chunks: list, history: list = []) -> str:
    global _gemini_client
    try:
        client   = _get_client()
        context  = '\n\n---\n\n'.join(chunks[:5])

        # Build conversation history string
        history_str = ''
        if history:
            last_pairs  = history[-6:]   # last 3 exchanges
            history_str = '\n'.join([
                f"{'User' if m['role'] == 'user' else 'Hita'}: {m['content']}"
                for m in last_pairs
            ])

        today     = datetime.date.today()
        last_month = (today.replace(day=1) - datetime.timedelta(days=1)).strftime('%B %Y')

        response = client.models.generate_content(
            model    = _GENERATION_MODEL,
            contents = [f"""You are Hita, a personal document assistant for Indian users.
{f'Previous conversation:{chr(10)}{history_str}{chr(10)}' if history_str else ''}
Answer using ONLY the document excerpts below.
- For lists of items (medicines, products, expenses) → use bullet points, deduplicate
- Always mention the vendor/pharmacy name in your answer
- Always break down amounts by source when multiple documents are involved
- Use ₹ for amounts
- For "last month" questions: today is {today}, so last month is last month is {last_month}
- For follow-up questions like "give more details" or "what products" —
  use both the conversation history AND documents to give a detailed answer
- If multiple documents are relevant, combine the information
- If multiple documents have the same item → mention it once only
- Give a complete sentence answer, not just a number
- If answer not found say exactly: "I couldn't find this information in your documents."
- Never make up information not present in the documents

MEDICINE QUESTIONS — format like this using markdown:
"Based on your pharmacy bills, you are regularly taking:
- Metformin 500mg
- Atorvastatin 10mg
- Aspirin 75mg
- Vitamin D3 60K IU"
Use markdown format with - for bullet points. Each item on its own line.
Never use • character. Use - instead.
List medicines only. Do not mention pharmacy name per item.
Mention pharmacy names separately at the end if needed.
CRITICAL: Each bullet point must be on a separate line. Never put bullets inline.

SPENDING QUESTIONS — format like this:
"In January, you spent ₹545 at Apollo Pharmacy and ₹500 at MediAssist Pharmacy, totalling ₹1,045."

Documents:
{context}

Current question: {question}

Answer:"""],
        )
        return response.text.strip()

    except Exception as e:
        logger.error(f'Query answering error: {e}')
        
        _gemini_client = None
        # Retry once with fresh client
        try:
            logger.info('Retrying answer_query with fresh client...')
            client   = _get_client()
            response = client.models.generate_content(
                model    = _GENERATION_MODEL,
                contents = [prompt],
            )
            return response.text.strip()
        except Exception as retry_err:
            logger.error(f'Retry also failed: {retry_err}')
            return 'Sorry, I encountered an error processing your query.'