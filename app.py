import io
import os
import streamlit as st
import pandas as pd

from agent.data import load_from_xlsx, load_from_csv_dir, normalize, get_available_months
from agent.pdf import export_board_pack
from agent.charts import (
    revenue_vs_budget_fig,
    gm_trend_fig,
    opex_breakdown_fig,
    opex_breakdown_bar_fig,
    cash_trend_fig,
    dataset_overview_fig,
    category_trend_fig,
    revenue_trend_fig,
    fmt_usd,  # kept in case you use it later
)
from agent.metrics import (
    revenue_month,
    opex_breakdown_month,
)
from agent.rag import build_kb
from agent.agent import run_agent


# ---------------- Page ----------------
st.set_page_config(page_title="FP&A CFO Copilot — Agentic RAG", layout="wide")
st.title("🤖📊 FP&A CFO Copilot — Agentic RAG")
st.caption(
    "Ask finance questions; the agent retrieves context and calls the right tool. "
    "Deterministic Python does the math; charts render automatically."
)


# ---------------- Data loaders ----------------
@st.cache_data(show_spinner=False)
def _load_default():
    dfs = load_from_csv_dir("fixtures")
    return normalize(dfs)

@st.cache_data(show_spinner=False)
def _load_xlsx(file_bytes: bytes):
    with io.BytesIO(file_bytes) as f:
        dfs = load_from_xlsx(f)
    return normalize(dfs)


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Data Source")
    uploaded = st.file_uploader("Upload XLSX (optional)", type=["xlsx"])
    if uploaded:
        norm = _load_xlsx(uploaded.read())
    else:
        norm = _load_default()

    fin = norm["financials"]
    cash = norm["cash"]

    months_all = get_available_months(fin)
    st.divider()
    st.write("**Data coverage**")
    if not months_all.empty:
        st.write(f"{str(months_all.min())} → {str(months_all.max())} ({len(months_all)} months)")
        entities = fin['entity'].dropna().unique().tolist()
        st.write(f"Entities: {', '.join(sorted(entities)) if entities else '—'}")
    else:
        st.write("—")

    st.divider()
    st.caption("PDF export uses latest-month for Rev vs Budget and Opex, plus Cash trend.")
    if st.button("Export Board Pack (3 pages)"):
        if months_all.empty:
            st.warning("No data available to export.")
        else:
            m = months_all.max()
            actual, budget, *_ = revenue_month(fin, m, entity=None)
            fig_rev = revenue_vs_budget_fig(actual, budget, m, for_print=True)

            ser_opex = opex_breakdown_month(fin, m, entity=None)
            fig_opex = opex_breakdown_bar_fig(ser_opex, m, for_print=True)

            fig_cash = cash_trend_fig(cash, for_print=True)

            pdf_path = os.path.join(os.getcwd(), "board_pack.pdf")
            export_board_pack(
                pdf_path,
                title="CFO Board Pack",
                blocks=[
                    (f"Revenue vs Budget — {m}", fig_rev),
                    (f"Opex Breakdown — {m}", fig_opex),
                    ("Cash Balance Trend", fig_cash),
                ],
            )
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "Download board_pack.pdf",
                    f,
                    file_name="board_pack.pdf",
                    mime="application/pdf",
                )


# ---------------- Build tiny KB for RAG ----------------
@st.cache_resource(show_spinner=False)
def _kb(fin_df: pd.DataFrame, cash_df: pd.DataFrame):
    return build_kb(fin_df, cash_df)

kb = _kb(fin, cash)


# ---------------- Main input ----------------
st.divider()
prompt = st.text_input("Ask a question", placeholder="e.g., Show Gross Margin % trend for the last 3 months.")
run = st.button("Run", type="primary")


# ---------------- Chart renderer (robust) ----------------
def render_chart(chart_hint: dict):
    kind = (chart_hint or {}).get("kind")
    payload = (chart_hint or {}).get("payload", {}) or {}

    if not kind:
        return  # nothing to render

    if kind == "rev_vs_budget":
        m = payload.get("month")
        actual = payload.get("actual")
        budget = payload.get("budget")
        if m is None or actual is None or budget is None:
            st.warning("Missing data for Revenue vs Budget chart.")
            return
        fig = revenue_vs_budget_fig(actual, budget, pd.Period(m, freq="M"))
        st.plotly_chart(fig, use_container_width=True)

    elif kind == "gm_trend":
        pts = payload.get("points", [])
        if not pts:
            st.warning("No GM% points to plot.")
            return
        try:
            idx = [pd.Period(p["month"], freq="M") for p in pts if "month" in p]
            vals = [p["gm_pct"] for p in pts if "gm_pct" in p]
            if not idx or not vals or len(idx) != len(vals):
                st.warning("Incomplete GM% data.")
                return
            s = pd.Series(vals, index=idx)
            st.plotly_chart(gm_trend_fig(s), use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render GM% chart: {e}")

    elif kind == "opex_breakdown":
        bars = payload.get("bars", [])
        month_label = payload.get("month", "Selected month")
        if not bars:
            st.warning("No Opex bars to plot.")
            return
        cats = [b.get("category") for b in bars if "category" in b]
        vals = [b.get("amount") for b in bars if "amount" in b]
        if not cats or not vals or len(cats) != len(vals):
            st.warning("Incomplete Opex data.")
            return
        ser = pd.Series(vals, index=cats)
        st.plotly_chart(opex_breakdown_fig(ser, month_label), use_container_width=True)

    elif kind == "cash_trend":
        st.plotly_chart(cash_trend_fig(cash), use_container_width=True)
    
    elif kind == "dataset_overview":
        st.plotly_chart(dataset_overview_fig(fin, cash), use_container_width=True)
    
    elif kind == "category_trend":
        category = payload.get("category", "Category")
        data_points = payload.get("data", [])
        if data_points:
            st.plotly_chart(category_trend_fig(category, data_points), use_container_width=True)
    
    elif kind == "revenue_trend":
        data_points = payload.get("data", [])
        if data_points:
            st.plotly_chart(revenue_trend_fig(data_points), use_container_width=True)


# ---------------- Run agent ----------------
if run and (prompt or "").strip():
    out = run_agent(prompt, fin, cash, kb)
    result = out.get("result", {})
    ans = result.get("answer", "No answer returned.")
    st.markdown(f"**Answer:** {ans}")
    chart = result.get("chart")
    if chart:
        render_chart(chart)
