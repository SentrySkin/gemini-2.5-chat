import os
import time
from flask import Request, jsonify, make_response
import functions_framework
from markdown import markdown as md_to_html
from selectolax.parser import HTMLParser
from datetime import datetime

# Use the SAME systemprompt.py you use for Claude (copy/paste that file)
from systemprompt import (
    get_system_prompt_for_request,
    detect_enrollment_completion_state,
    extract_contact_info,
    detect_enrollment_ready,
    detect_enrollment_info_collected,
    detect_pricing_inquiry,
    detect_payment_inquiry,
)

# Cloud logging / BQ
from google.cloud import logging as cloud_logging
from google.cloud import bigquery

# Vertex RAG REST
import google.auth
from google.auth.transport.requests import AuthorizedSession

# -------- google-genai SDK (new) --------
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    SafetySetting, HarmCategory, HarmBlockThreshold,
    Content, Part
)

from concurrent.futures import ThreadPoolExecutor


# ---------------- Config ----------------
PROJECT_ID = os.getenv("GCP_PROJECT", "christinevalmy")
REGION = os.environ.get("FUNCTION_REGION", "us-east5")
RAG_REGION = os.environ.get("RAG_REGION", "us-central1")

# Use Gemini for both generation and summarization
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

CORPUS_RESOURCE = os.environ.get(
    "RAG_CORPUS",
    "projects/christinevalmy/locations/us-central1/ragCorpora/5685794529555251200"
)

# Tuning
USE_SUMMARIZER = True
MAX_TURNS = 15
RAG_TOP_K = 10
RAG_SNIPPET_LENGTH = 2500

# New google-genai client (routes to Vertex if GOOGLE_GENAI_USE_VERTEXAI=true)
client = genai.Client(project=PROJECT_ID, location="us-central1")

# Logging / BQ
logging_client = cloud_logging.Client()
logger = logging_client.logger("gemini-conversations")
bq_client = bigquery.Client()
# Keep table name for schema parity with Claude path if you share dashboards
BQ_TABLE = f"{PROJECT_ID}.assistant_logs.claude_conversations"

executor = ThreadPoolExecutor(max_workers=3)


def log_to_bigquery(row: dict):
    def _log():
        try:
            errors = bq_client.insert_rows_json(BQ_TABLE, [row])
            if errors:
                logger.log_struct({"event": "bq_insert_error", "errors": errors, "row": row}, severity="ERROR")
        except Exception as e:
            logger.log_struct({"event": "bq_exception", "detail": str(e)}, severity="ERROR")
    executor.submit(_log)


# ---------------- Helpers ----------------
def _folder_from_uri(label: str):
    if label and label.startswith("gs://"):
        path = label[len("gs://"):]
        if "/" in path:
            bucket, rest = path.split("/", 1)
            return f"gs://{bucket}/" + rest.rsplit("/", 1)[0] if "/" in rest else f"gs://{bucket}"
    return None


def md_to_plaintext(md: str) -> str:
    if not md or len(md) < 10:
        return md
    html = md_to_html(md)
    tree = HTMLParser(html)
    body = tree.body or tree.root
    return body.text(separator="\n").replace("\\u2019", "'").replace("\\u2014", "—").strip()


def normalize_history(raw_history):
    """
    Accepts history like:
      [{"role":"user","text":"..."}, {"role":"assistant","text":"..."}]
    and converts to:
      [{"role":"user","content":[{"type":"text","text":"..."}]}, ...]
    If already normalized, passes through.
    """
    norm = []
    for item in (raw_history or []):
        role = (item.get("role") or "").lower()
        if "content" in item and isinstance(item["content"], list):
            norm.append({"role": role, "content": item["content"]})
        else:
            text = item.get("text", "")
            norm.append({"role": role, "content": [{"type": "text", "text": text}]} )
    return norm


# --------- Ultra-fast completion detection ---------
def ultra_fast_completion_check(user_query, history):
    user_query_lower = user_query.lower().strip()
    if user_query_lower.startswith("[topic:"):
        user_query_lower = user_query_lower.split("]", 1)[1].strip() if "]" in user_query_lower else user_query_lower

    completion_signals = {
        "thanks", "thank you", "nope", "no", "sounds good", "that's correct",
        "im good", "i'm good", "that's all", "nothing else", "looks good",
        "perfect", "ok", "okay", "cool", "great", "awesome", "yep", "yes that's correct"
    }

    if user_query_lower in completion_signals:
        recent_messages = history[-8:] if len(history) > 8 else history
        recent_text = " ".join([
            msg.get("content", [{}])[0].get("text", "")[:200]
            for msg in recent_messages if msg.get("content")
        ])
        has_email = "@" in recent_text
        has_digits = sum(1 for c in recent_text if c.isdigit()) >= 7
        has_enrollment = "enrollment" in recent_text.lower()
        return has_email and has_digits and has_enrollment
    return False


# --------- RAG retrieval (Vertex REST) ---------
def smart_retrieve_from_rag(query_text: str, conversation_stage: str = "active"):
    if conversation_stage == "completion":
        return [], []

    top_k = 3 if conversation_stage in ["post_enrollment", "enrollment_collection"] else RAG_TOP_K

    try:
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        session = AuthorizedSession(creds)

        url = (
            f"https://{RAG_REGION}-aiplatform.googleapis.com/v1beta1/"
            f"projects/{PROJECT_ID}/locations/{RAG_REGION}:retrieveContexts"
        )
        payload = {
            "vertex_rag_store": {"rag_resources": {"rag_corpus": CORPUS_RESOURCE}},
            "query": {"text": query_text, "similarity_top_k": top_k}
        }

        resp = session.post(url, json=payload, timeout=20)
        if resp.status_code != 200:
            logger.log_struct({"event": "retrieval_error", "status": resp.status_code}, severity="WARNING")
            return [], []

        data = resp.json() or {}
        items = data.get("contexts", {}).get("contexts", [])
        snippets, sources = [], []
        relevance_keywords = [
            query_text.lower(), 'esthetic', 'nail', 'wax', 'makeup', 'barbering',
            'program', 'course', 'schedule', 'start date', 'start dates', 'when',
            'price', 'tuition', 'admission', 'enrollment', 'financial aid',
            '2025', 'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]

        for c in items[:top_k]:
            text = (c.get("chunk") or {}).get("text") or c.get("text") or ""
            if text.strip():
                tl = text.lower()
                if any(k in tl for k in relevance_keywords):
                    snippets.append(text.strip()[:RAG_SNIPPET_LENGTH])

            src = c.get("sourceUri") or c.get("sourceDisplayName") or "unknown_source"
            folder = _folder_from_uri(src)
            sources.append({"label": src, **({"folder": folder} if folder else {})})

        return snippets[:3], sources[:3]

    except Exception as e:
        logger.log_struct({"event": "rag_error", "detail": str(e)}, severity="WARNING")
        return [], []


# --------- Summarizer (Gemini via google-genai) ---------
def gemini_summarize(text: str) -> str:
    prompt = (
        "Summarize key enrollment details in 2 sentences:\n"
        "- Program interest and location\n"
        "- Contact info status\n\n"
        "Conversation:\n"
        f"{text}"
    )
    try:
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[Content(role="user", parts=[Part.from_text(text=prompt)])],
            config=GenerateContentConfig(
                system_instruction="You are a helpful assistant that summarizes conversations.",
                temperature=0.1, top_p=0.9, max_output_tokens=200,
                response_mime_type="text/plain",
            ),
        )
        return extract_model_text(resp)
    except Exception as e:
        logger.log_struct({"event": "gemini_summary_error", "detail": str(e)}, severity="WARNING")
        return ""


# --------- Conversation state analysis ---------
def analyze_conversation_state(history, user_query):
    try:
        has_contact_info, completion_signal, enrollment_shared = detect_enrollment_completion_state(history, user_query)
        if completion_signal and has_contact_info and enrollment_shared:
            return "completion"
        elif has_contact_info and enrollment_shared:
            return "post_enrollment"
        elif has_contact_info:
            return "enrollment_ready"
        else:
            if detect_pricing_inquiry(user_query):
                return "pricing"
            if detect_payment_inquiry(user_query):
                return "payment_options"
            if detect_enrollment_ready(history, user_query) and not detect_enrollment_info_collected(history):
                return "enrollment_collection"
            return "active"
    except Exception:
        return "active"


# --------- Build Gemini contents from normalized history ---------
def build_gemini_contents(normalized_history, user_query: str, conversation_stage: str):
    contents = []

    # Optional: summarization hint from older turns
    if conversation_stage != "completion":
        older = normalized_history[:-MAX_TURNS]
        if USE_SUMMARIZER and older and len(older) > 3:
            try:
                key_exchanges = []
                for m in older:
                    if m.get("content"):
                        t = m["content"][0].get("text", "")
                        if any(k in t.lower() for k in [
                            'esthetic', 'nail', 'wax', 'makeup', 'program', 'course',
                            'new york', 'new jersey', 'ny', 'nj',
                            'full time', 'part time', 'evening', 'weekend',
                            'price', 'cost', 'tuition', 'financial aid',
                            'name', 'email', 'phone', 'contact', '@', 'enrollment'
                        ]):
                            key_exchanges.append(f"{m['role']}: {t[:300]}")
                if key_exchanges:
                    convo_text = "\n".join(key_exchanges[-6:])
                    summary_text = gemini_summarize(convo_text)
                    if summary_text:
                        contents.append(Content(role="user", parts=[Part.from_text(text=f"Context: {summary_text}")]))
            except Exception as e:
                logger.log_struct({"event": "summary_skip", "detail": str(e)}, severity="WARNING")

    # recent window
    if conversation_stage == "completion":
        recent = normalized_history[-3:]
    else:
        recent = normalized_history[-MAX_TURNS:]

    # Map normalized history to google-genai Content
    for m in recent:
        role = (m.get("role") or "").lower()
        if role not in {"user", "assistant"}:
            continue
        text = m.get("content", [{}])[0].get("text", "")
        if not text:
            continue
        # google-genai expects role "user" or "model"
        g_role = "user" if role == "user" else "model"
        contents.append(Content(role=g_role, parts=[Part.from_text(text=text)]))

    # current user message
    contents.append(Content(role="user", parts=[Part.from_text(text=f"User question: {user_query}")]))
    return contents


def get_optimized_gemini_params(conversation_stage, user_query_length):
    # ↑ bump default max_output_tokens to reduce truncation
    base = {"temperature": 0.2, "top_p": 0.8, "top_k": 40, "max_output_tokens": 768}
    if conversation_stage == "completion":
        return {**base, "temperature": 0.1, "max_output_tokens": 160}
    if conversation_stage == "post_enrollment":
        return {**base, "max_output_tokens": 320}
    if conversation_stage == "enrollment_collection":
        return {**base, "max_output_tokens": 512}
    if conversation_stage in ["pricing", "payment_options"]:
        return {**base, "max_output_tokens": 900}
    if user_query_length < 20:
        return {**base, "max_output_tokens": 320}
    return base


def extract_model_text(resp) -> str:
    """
    Robustly pull all text from the response.
    Prefer resp.text if present, otherwise collect all text parts from candidates.
    """
    try:
        if hasattr(resp, "text") and isinstance(resp.text, str) and resp.text.strip():
            return resp.text.strip()
    except Exception:
        pass

    texts = []
    try:
        for cand in getattr(resp, "candidates", []) or []:
            # If safety blocked, skip this candidate
            if getattr(cand, "finish_reason", "") == "SAFETY":
                continue
            content = getattr(cand, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                t = getattr(part, "text", None)
                if isinstance(t, str) and t.strip():
                    texts.append(t.strip())
    except Exception:
        pass

    return "\n".join(texts).strip()


# ---------------- Main HTTP Entry ----------------
@functions_framework.http
def app(request: Request):
    start_total = time.time()

    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id", "unknown")
        thread_id = data.get("thread_id", "unknown")

        # normalize incoming history (supports {"role": "...", "text": "..."} shape)
        raw_history = data.get("history") or []
        history = normalize_history(raw_history)[-30:]

        user_query = (data.get("query") or data.get("message") or data.get("text") or "").strip()
        if user_query.startswith("[TOPIC:"):
            user_query = user_query.split("]", 1)[1].strip() if "]" in user_query else user_query

        # Ultra-fast completion path
        if ultra_fast_completion_check(user_query, history):
            completion_message = (
                "Perfect! Thank you for your interest in Christine Valmy International School. "
                "Our enrollment advisor will reach out to you soon. We look forward to welcoming you to the Christine Valmy family!"
            )

            logger.log_struct({
                "event": "ultra_fast_completion_gemini",
                "user_id": user_id,
                "thread_id": thread_id,
                "message": user_query,
                "total_latency": round(time.time() - start_total, 3)
            }, severity="INFO")

            log_to_bigquery({
                "user_id": user_id,
                "thread_id": thread_id,
                "role": "assistant",
                "message": completion_message,
                "model": GEMINI_MODEL,
                "latency_sec": 0.05
            })

            return make_response(jsonify(
                response=completion_message,
                latency_retrieve=0,
                model=GEMINI_MODEL,
                latency_sec=0.05,
                rag_corpus=CORPUS_RESOURCE,
                rag_snippets=[],
                latency_after_claude=0,  # keep schema parity with front-end
                rag_sources=[],
                should_complete_conversation=True,
                total_latency=round(time.time() - start_total, 3)
            ), 200)

        # Conversation stage analysis
        conversation_stage = analyze_conversation_state(history, user_query)

        logger.log_struct({
            "event": "user_message_gemini",
            "user_id": user_id,
            "thread_id": thread_id,
            "message": user_query,
            "conversation_stage": conversation_stage,
            "role": "user"
        }, severity="INFO")

        log_to_bigquery({
            "user_id": user_id,
            "thread_id": thread_id,
            "role": "user",
            "message": user_query,
            "model": None,
            "latency_sec": None
        })

        # RAG retrieve
        start_rag = time.time()
        snippets, sources = smart_retrieve_from_rag(user_query, conversation_stage)
        context_str = "\n\n---\n".join(snippets)
        latency_retrieve = round(time.time() - start_rag, 3)

        # Build system prompt (same as Claude path)
        system_prompt = get_system_prompt_for_request(history, user_query, context_str)
        system_prompt += (
            f"\n\nCRITICAL DATE VALIDATION: Today's date is {datetime.now().strftime('%Y-%m-%d')}."
            " MANDATORY REQUIREMENTS: 1) VERIFY every date from RAG context is after today before displaying,"
            " 2) Show EXACTLY TWO upcoming future start dates only, 3) Check conversation history to avoid repeating identical schedule information,"
            " 4) If RAG lacks future dates, request current information. NEVER guess or assume dates."
        )

        # Build Gemini contents & params
        contents = build_gemini_contents(history, user_query, conversation_stage)
        gem_params = get_optimized_gemini_params(conversation_stage, len(user_query))

        # Gemini generation
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,  # list[Content]
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=gem_params["temperature"],
                top_p=gem_params["top_p"],
                top_k=gem_params.get("top_k", 40),
                max_output_tokens=gem_params["max_output_tokens"],
                safety_settings=[
                    SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                                  threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                    SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                                  threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                    SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                                  threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                    SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                  threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
                ],
                # Force plain text to avoid tool/JSON outputs that sometimes trim oddly
                response_mime_type="text/plain",
                candidate_count=1,
            ),
        )

        # Robust text extraction to avoid truncation
        answer_text = extract_model_text(resp)

        total_latency = round(time.time() - start_total, 3)

        logger.log_struct({
            "event": "assistant_reply_gemini",
            "user_id": user_id,
            "thread_id": thread_id,
            "message": answer_text,
            "role": "assistant",
            "model": GEMINI_MODEL,
            "conversation_stage": conversation_stage,
            "performance": {
                "total_latency": total_latency,
                "rag_latency": latency_retrieve,
                "gemini_latency": None,
                "system_prompt_length": len(system_prompt),
                "message_count": len(contents),
                "rag_snippets": len(snippets)
            }
        }, severity="INFO")

        log_to_bigquery({
            "user_id": user_id,
            "thread_id": thread_id,
            "role": "assistant",
            "message": answer_text,
            "model": GEMINI_MODEL,
            "latency_sec": None
        })

        return make_response(jsonify(
            response=answer_text,
            latency_retrieve=latency_retrieve,
            model=GEMINI_MODEL,
            latency_sec=0,
            rag_corpus=CORPUS_RESOURCE,
            rag_snippets=snippets,
            latency_after_claude=0,   # preserved for frontend compatibility
            rag_sources=sources,
            conversation_stage=conversation_stage,
            total_latency=total_latency,
            performance_metrics={
                "rag_latency": latency_retrieve,
                "prompt_latency": 0,
                "claude_latency": 0,
                "processing_latency": 0
            }
        ), 200)

    except Exception as e:
        total_latency = round(time.time() - start_total, 3)
        logger.log_struct({
            "event": "error_gemini",
            "error_type": type(e).__name__,
            "detail": str(e),
            "total_latency": total_latency
        }, severity="ERROR")
        return make_response(jsonify(
            error=type(e).__name__,
            detail=str(e),
            total_latency=total_latency
        ), 500)
