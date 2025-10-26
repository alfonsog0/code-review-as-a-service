import json
import os
from typing import Dict, Optional
from openai import OpenAI

_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_client: Optional[OpenAI] = None

def _client_singleton() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

SYSTEM_PROMPT = (
    "You are a senior code reviewer. Return ONLY a compact JSON object that conforms to the schema: "
    "{summary: string, suggestions: string[], findings: object[], rating: int}. "
    "findings may include objects like {type: 'bug'|'style'|'security'|'perf'|'doc', detail: string, line?: number}. "
    "Rate from 0-10 where 10 is production-ready. Be concise but actionable."
)

USER_TEMPLATE = (
    "Language: {language}\n\n"
    "Optional lines metadata: {lines}\n\n"
    "Code snippet (between <code> tags):\n<code>\n{code}\n</code>\n"
)

def review_code(language: str, code: str, lines: Optional[str]) -> Dict:
    """
    Call OpenAI to review code and return a dict matching ReviewPayload.
    """
    user_msg = USER_TEMPLATE.format(language=language, code=code, lines=lines or "(none)")
    resp = _client_singleton().responses.create(
        model=_OPENAI_MODEL,
        temperature=0.2,
        response_format={"type": "json_object"},
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    text = resp.output_text
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {
            "summary": text[:2000],
            "suggestions": [],
            "findings": [],
            "rating": 5,
        }
    # Fill required keys if missing
    data.setdefault("summary", "")
    data.setdefault("suggestions", [])
    data.setdefault("findings", [])
    data.setdefault("rating", 5)
    return data
