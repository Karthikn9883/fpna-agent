# agent/rag.py
from __future__ import annotations
from typing import List, Dict
import os
import numpy as np
import pandas as pd
from openai import OpenAI

from agent.data import get_available_months

_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

def _embed_texts(texts: List[str]) -> np.ndarray:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.embeddings.create(model=_EMBED_MODEL, input=texts)
    vecs = [d.embedding for d in resp.data]
    return np.array(vecs, dtype=np.float32)

def _cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-8)
    b = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)
    return a @ b.T

def build_kb(fin: pd.DataFrame, cash: pd.DataFrame) -> Dict:
    months = get_available_months(fin)
    schema = sorted(fin.columns.tolist())
    entities = sorted(fin["entity"].dropna().unique().tolist())

    docs = []
    docs.append("Metric: Revenue vs Budget — Compare actual revenue to budget for a month or range. Inputs: month(s), optional entity. Output: grouped bar chart.")
    docs.append("Metric: Gross Margin % — (Revenue - COGS) / Revenue, computed on actuals. Inputs: range. Output: line chart GM% over months.")
    docs.append("Metric: Opex breakdown — Sum Opex:* categories for a month. Output: categorical bar or pie chart.")
    docs.append("Metric: Cash runway — latest cash divided by average monthly net burn (last 3 months), where burn = max(0, -EBITDA). Output: cash trend line; answer may be ∞ if burn=0.")
    docs.append(f"Dataset schema (financials): {', '.join(schema)}")
    docs.append(f"Entities present: {', '.join(entities) if entities else 'none'}")
    if len(months):
        docs.append(f"Months available: {str(months.min())} to {str(months.max())} (total {len(months)})")
    examples = [
        "What was June 2025 revenue vs budget in USD?",
        "Show Gross Margin % trend for the last 3 months.",
        "Break down Opex by category for June.",
        "What is our cash runway right now?",
        "How many months of data are here?"
    ]
    docs.append("Example questions: " + " | ".join(examples))

    embs = _embed_texts(docs)
    return {"docs": docs, "embs": embs}

def retrieve(kb: Dict, query: str, k: int = 3) -> List[str]:
    qv = _embed_texts([query])
    sims = _cosine_sim(qv, kb["embs"])[0]
    idx = sims.argsort()[::-1][:k]
    return [kb["docs"][i] for i in idx]
