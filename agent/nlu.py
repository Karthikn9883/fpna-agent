# agent/nlu.py
from __future__ import annotations
import os, json
from typing import Optional, Dict, Any
from openai import OpenAI

# Use env vars; never hardcode your key
# export OPENAI_API_KEY="sk-..."      (mac/linux)
# setx OPENAI_API_KEY "sk-..."        (windows)
_CLIENT = None
_API_KEY = os.getenv("OPENAI_API_KEY")
_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")  # small + cheap text model is fine

def _client() -> Optional[OpenAI]:
    global _CLIENT
    if _CLIENT is None and _API_KEY:
        _CLIENT = OpenAI(api_key=_API_KEY)
    return _CLIENT

# JSON schema for structured output
_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["revenue_vs_budget", "gm_trend", "opex_breakdown", "cash_runway"]
        },
        "months": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["single", "last_n", "quarter", "range", "unspecified"]},
                "value": {"type": "string"}
            },
            "required": ["kind", "value"]
        },
        "entity": {"type": ["string", "null"]}
    },
    "required": ["intent", "months", "entity"],
    "additionalProperties": False
}

_SYSTEM = (
    "You are a parser for CFO finance questions about monthly financials. "
    "Return ONLY JSON that matches the provided JSON schema. "
    "Do not perform any math. Only identify: intent, months selection, entity."
)

_USER_TEMPLATE = """\
Question: {q}

Rules:
- intent must be one of: revenue_vs_budget, gm_trend, opex_breakdown, cash_runway
- months.kind:
  - 'single' with value 'YYYY-MM' if a specific month given (e.g. '2025-06')
  - 'last_n' with value like '3' if 'last 3 months'
  - 'quarter' with value like 'Q2 2025'
  - 'range' with value 'YYYY-MM..YYYY-MM'
  - 'unspecified' if no time hint
- entity: a literal string if clearly specified, else null
"""

def llm_parse(question: str) -> Optional[Dict[str, Any]]:
    """
    Try to parse the question using the OpenAI Responses API with a strict JSON schema.
    Returns a dict {intent, months:{kind,value}, entity} or None on any error.
    """
    try:
        cli = _client()
        if not cli:
            return None
        resp = cli.responses.create(
            model=_MODEL,
            input=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": _USER_TEMPLATE.format(q=question or "")},
            ],
            response_format={"type": "json_schema", "json_schema": {"name": "query_schema", "schema": _SCHEMA}},
        )
        text = resp.output_text  # SDK helper to concatenate all text parts
        data = json.loads(text)
        return data
    except Exception:
        return None

def llm_copyedit(sentence: str) -> str:
    """
    Optional: rewrite the final sentence to be board-ready.
    If LLM is unavailable, returns the original sentence.
    """
    try:
        cli = _client()
        if not cli:
            return sentence
        resp = cli.responses.create(
            model=_MODEL,
            input=[
                {"role": "system", "content": "Rewrite the sentence to be concise, board-ready, and numerically precise."},
                {"role": "user", "content": sentence},
            ],
        )
        return resp.output_text.strip()
    except Exception:
        return sentence
