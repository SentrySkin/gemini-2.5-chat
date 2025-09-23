# main.py
import os
import json
import time
import functions_framework
from typing import List, Dict, Any

from flask import jsonify, request
from google import genai
from google.cloud import logging as cloud_logging

from google.genai.types import (
    Tool,
    Retrieval,
    VertexAISearch,
    GenerateContentConfig,
    Content,
    Part,
)

from markdown import markdown as md_to_html
from selectolax.parser import HTMLParser
from bs4 import BeautifulSoup

# Import the dynamic system prompt function (without RAG context)
from sophia_prompt import get_system_prompt_for_request

# -----------------------------
# Config
# -----------------------------
PROJECT_ID = os.getenv("GCP_PROJECT", "christinevalmy")
LOCATION = os.getenv("FUNCTION_REGION", "us-central1")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "1000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
TOP_P = float(os.getenv("TOP_P", "0.8"))

VERTEX_SEARCH_ENGINE = os.getenv(
    "VERTEX_SEARCH_ENGINE",
    "projects/christinevalmy/locations/global/collections/default_collection/engines/cv-aug27_1756347217695",
)

# Instantiate clients (Vertex routing enabled by vertexai=True)
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
logging_client = cloud_logging.Client()
logger = logging_client.logger("assistant_conversations")


# -----------------------------
# Helpers
# -----------------------------
def html_to_text(markdown_text: str) -> str:
    """Markdown → HTML → plain text with selectolax, fallback to BeautifulSoup."""
    html_doc = md_to_html(markdown_text or "")
    try:
        tree = HTMLParser(html_doc)
        if tree.body:
            text = tree.body.text(separator="\n").strip()
        else:
            text = tree.root.text(separator="\n").strip()
        if text:
            return (
                text.replace("\\u2019", "'")
                .replace("\\u2014", "—")
                .replace("\xa0", " ")
                .strip()
            )
    except Exception:
        pass
    plain = BeautifulSoup(html_doc, "html.parser").get_text(separator="\n").strip()
    return (
        plain.replace("\\u2019", "'")
        .replace("\\u2014", "—")
        .replace("\xa0", " ")
        .strip()
    )


def normalize_history_to_genai(history: List[Dict[str, Any]]) -> List[Content]:
    """
    Convert incoming history:
      [{"role":"user|assistant", "text":"..."}]
    to google-genai `Content` list:
      [Content(role="user|model", parts=[Part(text="...")]), ...]
    """
    contents: List[Content] = []
    for item in history or []:
        role_in = (item.get("role") or "").strip().lower()
        text = (item.get("text") or "").strip()
        if not text:
            continue

        # google-genai expects role to be "user" or "model"
        if role_in == "assistant":
            role = "model"
        elif role_in == "user":
            role = "user"
        else:
            # Skip unknown roles
            continue

        contents.append(Content(role=role, parts=[Part(text=text)]))
    return contents


# -----------------------------
# HTTP Entrypoint
# -----------------------------
@functions_framework.http
def app(request):
    start_time = time.time()
    
    try:
        data = request.get_json(silent=True) or {}
        # Accept "message" or "query"
        user_message = (data.get("message") or data.get("query") or "").strip()
        user_id = data.get("user_id", "unknown")
        thread_id = data.get("thread_id", "unknown")
        history_in = data.get("history", [])

        if not user_message:
            return jsonify({"error": "Missing 'message' or 'query' in request."}), 400

        # Log user message
        logger.log_struct(
            {
                "event": "user_message",
                "user_id": user_id,
                "thread_id": thread_id,
                "message": user_message,
            },
            severity="INFO",
        )

        # Build chat history for google-genai
        contents: List[Content] = normalize_history_to_genai(history_in)
        # Current user turn
        contents.append(Content(role="user", parts=[Part(text=user_message)]))

        # Tool: Vertex AI Search
        search_tool = Tool(
            retrieval=Retrieval(
                vertex_ai_search=VertexAISearch(engine=VERTEX_SEARCH_ENGINE)
            )
        )

        # Generate dynamic system prompt (without RAG context)
        dynamic_system_prompt = get_system_prompt_for_request(
            history=history_in, 
            user_query=user_message
        )

        # Generation config with dynamic system prompt
        config = GenerateContentConfig(
            system_instruction=dynamic_system_prompt,
            tools=[search_tool],
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

        # Generate (streaming)
        full_text = ""
        try:
            resp_stream = client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )
            for chunk in resp_stream:
                if getattr(chunk, "text", None):
                    full_text += chunk.text
        except Exception:
            # Fallback to non-streaming
            resp = client.models.generate_content(
                model=MODEL_NAME, contents=contents, config=config
            )
            full_text = (getattr(resp, "text", "") or "").strip()

        # Normalize markdown → plain text
        final_text = html_to_text(full_text)
        
        total_latency = round(time.time() - start_time, 3)

        # Log assistant reply
        logger.log_struct(
            {
                "event": "assistant_reply",
                "user_id": user_id,
                "thread_id": thread_id,
                "message": final_text,
                "role": "assistant",
                "model": MODEL_NAME,
                "total_latency": total_latency,
            },
            severity="INFO",
        )

        return jsonify({
            "response": final_text, 
            "status_code": 200,
            "model": MODEL_NAME,
            "total_latency": total_latency
        })

    except Exception as e:
        total_latency = round(time.time() - start_time, 3)
        
        # best-effort logging even if parsing failed
        try:
            body = request.get_json(silent=True) or {}
            uid = body.get("user_id", "unknown")
            tid = body.get("thread_id", "unknown")
        except Exception:
            uid, tid = "unknown", "unknown"

        logger.log_struct(
            {
                "event": "assistant_error",
                "user_id": uid,
                "thread_id": tid,
                "error": str(e),
                "total_latency": total_latency,
            },
            severity="ERROR",
        )
        return jsonify({"error": str(e), "total_latency": total_latency}), 500
