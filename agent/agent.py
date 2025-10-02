# agent/agent.py
from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
import os
from openai import OpenAI

from agent.tools import TOOL_SPECS, dispatch
from agent.rag import retrieve

_SYSTEM = """\
You are a finance copilot that answers CFO questions from monthly CSV data.
Decide which tool to call based on the question and the retrieved context.
If the question asks for a trend or breakdown, prefer chart outputs.
Never guess numbers; tools compute all values. Keep answers concise and board-ready.
"""

_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")  # pick a model that supports tools
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _extract_tool_use(resp) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Extract a tool call from a Responses API response robustly.
    Returns (tool_name, args) or (None, {}).
    """
    # 1) SDK object attributes
    try:
        for block in (getattr(resp, "output", []) or []):
            if getattr(block, "type", "") == "message":
                for part in (getattr(block, "content", []) or []):
                    if getattr(part, "type", "") == "tool_use":
                        return getattr(part, "name", None), (getattr(part, "input", {}) or {})
    except Exception:
        pass

    # 2) Fallback to dict form
    try:
        data = resp.to_dict() if hasattr(resp, "to_dict") else resp
        for block in (data.get("output", []) or []):
            if block.get("type") == "message":
                for part in (block.get("content", []) or []):
                    if part.get("type") == "tool_use":
                        return part.get("name"), (part.get("input") or {})
    except Exception:
        pass

    return None, {}


def _heuristic_tool(question: str) -> str:
    """
    If the model didn't call a tool, pick one heuristically so we still answer.
    """
    q = (question or "").lower()
    
    # Revenue analysis (comprehensive)
    if "revenue" in q and ("total" in q or "overall" in q or "how much" in q or "analysis" in q or "performance" in q):
        return "revenue_analysis"
    # Revenue vs budget (specific comparison)
    if "revenue" in q and "budget" in q:
        return "revenue_vs_budget"
    
    # Margin analysis
    if "gross margin" in q or "gm%" in q or "gm %" in q or "margin" in q:
        return "gm_trend"
    
    # Expense analysis
    if ("marketing" in q or "sales" in q or "r&d" in q or "admin" in q or "opex" in q) and ("spend" in q or "spent" in q or "cost" in q or "expense" in q or "breakdown" in q or "by category" in q):
        return "opex_breakdown"
    
    # Financial performance (comprehensive)
    if ("performance" in q or "dashboard" in q or "summary" in q or "overview" in q) and ("financial" in q or "business" in q or "company" in q):
        return "financial_performance"
    
    # Cash analysis
    if "runway" in q or ("cash" in q and ("runway" in q or "burn" in q)):
        return "cash_runway"
    
    # Dataset questions
    if "how many months" in q or "months of data" in q or "which months" in q or "what months" in q or "dataset" in q:
        return "data_coverage"
    
    # General expense questions
    if "spend" in q or "spent" in q or "cost" in q or "expense" in q:
        return "opex_breakdown"
    
    # Revenue questions (catch remaining)
    if "revenue" in q:
        return "revenue_analysis"
    
    # Default to data coverage for meta questions
    return "data_coverage"


def run_agent(question: str, fin, cash, kb) -> Dict[str, Any]:
    # Retrieve a bit of context (schema, tool docs, coverage, examples)
    context = retrieve(kb, question, k=3)
    msgs = [
        {
            "role": "system",
            "content": _SYSTEM + "\n\nContext:\n" + "\n".join(f"- {c}" for c in context),
        },
        {"role": "user", "content": question or ""},
    ]

    # Call Responses API with proper tool schema
    try:
        resp = client.responses.create(
            model=_MODEL,
            input=msgs,
            tools=TOOL_SPECS,
        )
    except Exception as e:
        # If the API call fails entirely, fall back heuristically
        name = _heuristic_tool(question)
        result = dispatch(name, {}, fin, cash, question, entity=None)
        return {"tool": name, "result": result, "note": f"LLM call failed: {e}"}

    # Extract tool call (robustly). If none, fall back.
    name, args = _extract_tool_use(resp)
    if not name:
        name = _heuristic_tool(question)

    result = dispatch(name, args, fin, cash, question, entity=None)
    return {"tool": name, "result": result}
