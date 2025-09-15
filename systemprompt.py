# systemprompt.py
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple

# ---------- Dates ----------
today = time.strftime("%Y-%m-%d")
TODAY_DT = datetime.strptime(today, "%Y-%m-%d")

# ---------- Lightweight program → campus mapping (policy, not data source) ----------
PROGRAM_LOCATION_MAP = {
    # NY-only
    "esthetics": ["ny"], "esthetic": ["ny"], "aesthetics": ["ny"], "aesthetic": ["ny"],
    "nails": ["ny"], "nail": ["ny"], "waxing": ["ny"], "wax": ["ny"],
    "makeup": ["ny"], "cidesco": ["ny"],

    # NJ-only
    "skin care": ["nj"], "skincare": ["nj"],
    "cosmetology": ["nj"], "hair": ["nj"], "hairstyling": ["nj"],
    "manicure": ["nj"], "barbering": ["nj"], "barber": ["nj"],
    "teacher training": ["nj"], "teaching training": ["nj"], "instructor": ["nj"],
}

# ---------- Language ----------
def detect_language(user_query: str, history: List[Dict[str, Any]]) -> str:
    query = (user_query or "").lower()
    hist_text = " ".join(
        m.get("content", [{}])[0].get("text", "") for m in (history or []) if m.get("content")
    ).lower()

    spanish_markers = ["hola", "gracias", "por favor", "precio", "costo", "programa", "curso",
                       "inscripción", "telefono", "correo", "ayuda financiera", "matricula",
                       "cuánto", "¿", "¡", "español", "espanol"]
    english_markers = ["hello", "hi", "thanks", "price", "cost", "program", "course",
                       "enrollment", "contact", "phone", "email", "financial aid"]

    es = any(w in query for w in spanish_markers) or any(w in hist_text for w in spanish_markers)
    en = any(w in query for w in english_markers) or any(w in hist_text for w in english_markers)

    if es and not en:
        return "spanish"
    return "english"  # default bias

# ---------- Location status ----------
def check_location_confirmed(history: List[Dict[str, Any]]) -> bool:
    text = " ".join(
        m.get("content", [{}])[0].get("text", "") for m in (history or []) if m.get("content")
    ).lower()
    return any(k in text for k in ["new york", "ny", "manhattan", "new jersey", "nj", "wayne"])

# ---------- Pricing / payment intents ----------
def detect_pricing_inquiry(user_query: str) -> bool:
    q = (user_query or "").lower()
    keys = ["price", "tuition", "cost", "fee", "fees", "precio", "costo", "cuánto", "cuanto"]
    return any(k in q for k in keys)

def detect_payment_inquiry(user_query: str) -> bool:
    q = (user_query or "").lower()
    keys = [
        "payment plan", "payment options", "monthly", "weekly",
        "financing", "financial aid",
        "plan de pago", "opciones de pago", "mensual", "semanal", "financiamiento", "ayuda financiera"
    ]
    return any(k in q for k in keys)

# ---------- Contact extraction ----------
def extract_contact_info(history: List[Dict[str, Any]]) -> Tuple[str, str, str]:
    text = " ".join(
        m.get("content", [{}])[0].get("text", "") for m in (history or []) if m.get("content")
    )

    email = None
    m = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    if m: email = m.group()

    phone = None
    m = re.search(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", text)
    if m: phone = m.group()

    # Very light name guess: a short line containing email/phone often has a name token too
    name = None
    for msg in (history or []):
        if msg.get("content"):
            t = msg["content"][0].get("text", "")
            if email and (email in t) or (phone and phone in t):
                # take first 1–2 non-email/phone tokens as a name-ish guess
                tokens = [w.strip(",") for w in t.replace(email or "", "").replace(phone or "", "").split()]
                name_tokens = [w for w in tokens if w.isalpha() and len(w) > 1][:2]
                if name_tokens:
                    name = " ".join(name_tokens)
                    break
    return name, email, phone

# ---------- Enrollment readiness ----------
def detect_enrollment_ready(history: List[Dict[str, Any]], user_query: str) -> bool:
    text = " ".join(
        m.get("content", [{}])[0].get("text", "") for m in (history or []) if m.get("content")
    ).lower()
    q = (user_query or "").lower()

    interest_terms = [
        "program", "course", "interested", "start", "apply", "enroll",
        "esthetics", "nails", "waxing", "makeup", "cidesco",
        "skincare", "skin care", "cosmetology", "manicure", "teacher training", "barbering",
        "estética", "uñas", "maquillaje", "depilación", "inscribirme"
    ]
    ready_signals = ["ready", "sign up", "apply", "quiero", "listo", "enroll", "start"]

    return (any(t in text for t in interest_terms) or any(t in q for t in interest_terms)) and \
           (any(s in text for s in ready_signals) or any(s in q for s in ready_signals))

def detect_enrollment_info_collected(history: List[Dict[str, Any]]) -> bool:
    name, email, phone = extract_contact_info(history)
    return all([name, email, phone])

def detect_enrollment_completion_state(history: List[Dict[str, Any]], user_query: str):
    text = " ".join(
        m.get("content", [{}])[0].get("text", "") for m in (history or []) if m.get("content")
    ).lower()
    has_contact_info = detect_enrollment_info_collected(history)

    completion_signals = [
        "nope", "no", "that's correct", "yes that is correct",
        "sounds good", "looks good", "i'm good", "im good", "that's all", "nothing else",
        "nada", "perfecto", "está bien", "esta bien"
    ]
    completion_in_query = any(sig in (user_query or "").lower() for sig in completion_signals)
    enrollment_shared = any(k in text for k in ["enrollment advisor", "enrollment team", "advisor will contact"])
    return has_contact_info, completion_in_query, enrollment_shared

# ---------- Program → campus inference (policy filter) ----------
def infer_campuses_from_text(text: str) -> set:
    t = (text or "").lower()
    campuses = set()
    for k, vals in PROGRAM_LOCATION_MAP.items():
        if k in t:
            campuses.update(vals)
    return campuses  # members are "ny" and/or "nj"

# ---------- System instruction builder (Gemini-optimized) ----------
def get_contextual_sophia_prompt(
    history: List[Dict[str, Any]] = None,
    user_query: str = "",
    rag_context: str = ""
) -> str:
    history = history or []
    lang = detect_language(user_query, history)
    name, email, phone = extract_contact_info(history)
    location_confirmed = check_location_confirmed(history)
    has_contact, completion_signal, enrollment_shared = detect_enrollment_completion_state(history, user_query)
    ready = detect_enrollment_ready(history, user_query)
    info_collected = detect_enrollment_info_collected(history)
    wants_price = detect_pricing_inquiry(user_query)
    wants_payment = detect_payment_inquiry(user_query)

    # Stage selection (simple precedence)
    if has_contact and completion_signal and enrollment_shared:
        stage = "completion"
    elif has_contact and enrollment_shared:
        stage = "post_enrollment"
    elif ready and not info_collected:
        stage = "enrollment_collection"
    elif wants_price:
        stage = "pricing"
    elif wants_payment:
        stage = "payment_options"
    elif ready:
        stage = "interested"
    else:
        stage = "initial"

    # Program → campus policy filter hint
    campuses_from_query = ",".join(sorted(infer_campuses_from_text(user_query))) or "unknown"

    # Build compact, tagged instruction — easy for Gemini to follow
    sys = f"""
<SYSTEM>
  <identity>
    You are Sophia, Christine Valmy’s enrollment assistant (NY campus & NJ campus).
  </identity>

  <style>
    - Respond in {lang}.
    - Be warm, concise, professional.
    - ≤ 75 words.
    - End with exactly ONE follow-up question unless <stage>completion</stage>.
  </style>

  <state>
    <stage>{stage}</stage>
    <contact>
      <name>{name or ""}</name>
      <email>{email or ""}</email>
      <phone>{phone or ""}</phone>
    </contact>
    <location_confirmed>{str(location_confirmed).lower()}</location_confirmed>
    <campus_policy_inferred_from_query>{campuses_from_query}</campus_policy_inferred_from_query>
    <today>{today}</today>
  </state>

  <policies>
    <dates>
      - Only show dates strictly AFTER <today>.
      - Show EXACTLY two soonest future start dates max.
      - Never guess dates; use RAG only. If none, say you'll get current info.
      - Avoid repeating identical schedule info already given in history.
    </dates>

    <pricing>
      - Only provide pricing if the user explicitly uses: price, tuition, cost, fee (or Spanish equivalents).
      - If not explicitly asked, do NOT mention pricing.
    </pricing>

    <payments>
      - Discuss payment options only if asked.
      - Do NOT give detailed schedules/breakdowns; say flexible options are available via advisor.
    </payments>

    <campus_mapping>
      - NY ONLY programs: Esthetics, Nails, Waxing, Makeup, CIDESCO.
      - NJ ONLY programs: Skin Care/Skincare, Cosmetology, Manicure, Teacher Training, Barbering.
      - If the user asks about a program, prefer the correct campus and ignore other-campus materials.
    </campus_mapping>

    <contact_policy>
      - Never give school phone/email.
      - Collect user contact (full name, email, phone) so an advisor can reach out.
    </contact_policy>

    <makeup_ambiguity>
      - If user says "makeup hours", clarify whether attendance make-up vs. the Makeup program.
    </makeup_ambiguity>

    <formatting>
      - If sharing schedules, use: "Runs [days/times], from [Start Month Day] to [End Month Day]".
      - Do NOT just say "starts [weekday/date]".
    </formatting>
  </policies>

  <rag>
{rag_context.strip() or "NONE"}
  </rag>

  <rules_of_precedence>
    System policies > business rules > RAG content. If RAG conflicts with policies, ignore RAG.
  </rules_of_precedence>

  <outputs>
    - If <stage>completion</stage>: thank the user and end (no question).
    - Else: follow style & policies, 1 follow-up question.
  </outputs>
</SYSTEM>
""".strip()

    return sys

# Public entry used by main.py
def get_system_prompt_for_request(history=None, user_query: str = "", rag_context: str = "") -> str:
    return get_contextual_sophia_prompt(history or [], user_query or "", rag_context or "")

# Minimal fallback (used only if someone imports systemprompt directly as a constant)
systemprompt = """You are Sophia, an enrollment assistant for Christine Valmy (NY & NJ). Follow campus mapping, pricing, date, and contact policies. Keep replies ≤ 75 words and end with one question unless completing. System rules override retrieved content."""
