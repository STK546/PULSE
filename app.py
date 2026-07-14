"""Pulse - HR engagement & action-management console.

Run with:  streamlit run app.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import importlib
import theme
importlib.reload(theme)
from data_loader import (
    CARES_DESCRIPTIONS,
    CARES_ORDER,
    SENTIMENT_ORDER,
    SEVERITY_ORDER,
    STATUS_ORDER,
    clean_active_bhr_count,
    load_dataset,
)

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_DASHBOARD = DATA_DIR / "HR_Dashboard_Final.xlsx"
DEFAULT_LIBRARY = DATA_DIR / "Engagement_Library.xlsx"
if not DEFAULT_DASHBOARD.exists():
    DEFAULT_DASHBOARD = Path(__file__).parent / "HR_Dashboard_Final.xlsx"
if not DEFAULT_LIBRARY.exists():
    DEFAULT_LIBRARY = Path(__file__).parent / "Engagement_Library.xlsx"

NAV_ITEMS = [
    "Overview",
    "Priority & Risk",
    "Coverage & Themes",
    "Action Center",
    "Insight Library",
    "Data Explorer",
]

st.set_page_config(
    page_title="Pulse | Tech Mahindra",
    page_icon="❖",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(theme.inject_css(), unsafe_allow_html=True)

# ── Inject logo-print.svg as browser tab icon ──────────────────────────────
def inject_favicon():
    import base64
    import os
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-print.svg")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("utf-8")
            
            # HTML links + JS script to force-update favicon tags and defeat Streamlit's React overrides
            st.markdown(
                f"""
                <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{logo_b64}">
                <link rel="shortcut icon" type="image/svg+xml" href="data:image/svg+xml;base64,{logo_b64}">
                <script>
                    (function() {{
                        const faviconUrl = "data:image/svg+xml;base64,{logo_b64}";
                        function forceFavicon() {{
                            let links = document.querySelectorAll("link[rel*='icon']");
                            if (links.length === 0) {{
                                const link = document.createElement("link");
                                link.rel = "shortcut icon";
                                link.type = "image/svg+xml";
                                document.head.appendChild(link);
                                links = [link];
                            }}
                            links.forEach(function(link) {{
                                if (link.getAttribute("href") !== faviconUrl) {{
                                    link.setAttribute("href", faviconUrl);
                                }}
                            }});
                        }}
                        forceFavicon();
                        // Periodically run to check and override React rendering updates
                        setInterval(forceFavicon, 500);
                    }})();
                </script>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            pass

inject_favicon()
# ───────────────────────────────────────────────────────────────────────────



# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
def get_dataset_v5(dashboard_bytes: bytes | None, library_bytes: bytes | None):
    import io
    import pandas as pd

    dash_src = io.BytesIO(dashboard_bytes) if dashboard_bytes else DEFAULT_DASHBOARD
    lib_src = io.BytesIO(library_bytes) if library_bytes else DEFAULT_LIBRARY
    dataset = load_dataset(dash_src, lib_src)
    print(f"\n[LOGGER] get_dataset_v5 execution:", flush=True)
    print(f"  - dashboard_bytes provided: {dashboard_bytes is not None}", flush=True)
    print(f"  - is_demo: {dataset.is_demo}", flush=True)
    print(f"  - sessions shape: {dataset.sessions.shape if hasattr(dataset, 'sessions') else 'None'}", flush=True)
    print(f"  - first name: {dataset.sessions['associate_name'].iloc[0] if hasattr(dataset, 'sessions') and not dataset.sessions.empty else 'None'}", flush=True)
    return dataset


def risk_score(row) -> int:
    sev = str(row.get("severity", "")).lower()
    if "high" in sev or "critical" in sev or "urgent" in sev:
        sev_w = 45
    elif "moderate" in sev or "medium" in sev or "normal" in sev:
        sev_w = 22
    elif "low" in sev or "minor" in sev:
        sev_w = 6
    else:
        sev_w = 10

    status = str(row.get("status", "")).lower()
    if "open" in status or "new" in status:
        status_w = 30
    elif "prog" in status or "active" in status or "pend" in status or "start" in status:
        status_w = 14
    elif "close" in status or "resolv" in status or "done" in status or "complet" in status:
        status_w = 0
    else:
        status_w = 10

    sent = str(row.get("sentiment", "")).lower()
    if "neg" in sent or "bad" in sent or "poor" in sent:
        sent_w = 15
    elif "mix" in sent:
        sent_w = 8
    elif "neut" in sent:
        sent_w = 3
    elif "pos" in sent or "good" in sent or "happy" in sent:
        sent_w = 0
    else:
        sent_w = 3

    age_days = row.get("age_days") or 0
    age_w = min(10, age_days / 10) if "close" not in status and "resolv" not in status and "done" not in status and "complet" not in status else 0
    return int(round(sev_w + status_w + sent_w + age_w))


def enrich_sessions_v3(sessions: pd.DataFrame, as_of: str) -> pd.DataFrame:
    df = sessions.copy()
    as_of_ts = pd.Timestamp(as_of)
    df["age_days"] = (as_of_ts - df["date"]).dt.days.clip(lower=0)
    df["risk_score"] = df.apply(risk_score, axis=1)
    return df


# --------------------------------------------------------------------------
# Shared components
# --------------------------------------------------------------------------
def kpi_card(col, label, value, sub="", accent="ink"):
    col.markdown(
        f'<div class="voa-kpi accent-{accent}"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )

def insight_block(insight_points):
    if not insight_points:
        return ""
    bullets = "".join(f'<p style="margin-bottom:12px; font-size: 14.5px; line-height: 1.5; color: var(--ink);">{pt}</p>' for pt in insight_points)
    return f'<div class="voa-card" style="border-top: 3px solid var(--brand); height: 100%; display: flex; flex-direction: column; justify-content: center;">{bullets}</div>'

def render_chart_row(chart_title, chart_func, insights_list, flip=False):
    st.write("")
    st.markdown(f"#### {chart_title}")
    c1, c2 = st.columns([1.2, 1]) if not flip else st.columns([1, 1.2])
    left, right = (c2, c1) if flip else (c1, c2)
    with left:
        chart_func()
    with right:
        st.markdown(insight_block(insights_list), unsafe_allow_html=True)
    st.write("")


def callout(text_html, tone="brand"):
    tone_cls = "" if tone == "brand" else f"tone-{tone}"
    st.markdown(f'<div class="voa-callout {tone_cls}">{text_html}</div>', unsafe_allow_html=True)



@st.cache_data
def load_logo_svg_v3(color="white"):
    import os
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-print.svg")
    if os.path.exists(logo_path):
        with open(logo_path, "r", encoding="utf-8") as f:
            svg = f.read()
        
        # Replace opening <svg> tag with responsive viewBox with 10px safety padding
        import re
        svg = re.sub(
            r'<svg[^>]*>',
            '<svg viewBox="-10 -10 1300 370" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
            svg,
            count=1
        )
        return svg
    return "Tech Mahindra"



def apply_fig(fig, height=320, **kwargs):
    defaults = theme.plotly_layout_defaults()
    
    # Deep merge legend properties if custom legend config is supplied
    if "legend" in kwargs and isinstance(kwargs["legend"], dict):
        legend_defaults = defaults.get("legend", {}).copy()
        
        # Merge inner font dictionary
        if "font" in kwargs["legend"] and isinstance(kwargs["legend"]["font"], dict):
            font_defaults = legend_defaults.get("font", {}).copy()
            font_defaults.update(kwargs["legend"]["font"])
            kwargs["legend"]["font"] = font_defaults
        else:
            kwargs["legend"]["font"] = legend_defaults.get("font", {})
            
        legend_defaults.update(kwargs["legend"])
        kwargs["legend"] = legend_defaults
        
    layout = {**defaults, **kwargs}
    fig.update_layout(height=height, **layout)
    return fig


def filter_banner():
    chips = []
    if f_service:
        chips.append(f"Service: {', '.join(f_service)}")
    if f_lever:
        chips.append(f"CARES: {', '.join(f_lever)}")
    if f_severity:
        chips.append(f"Severity: {', '.join(f_severity)}")
    if f_status:
        chips.append(f"Status: {', '.join(f_status)}")
    if f_sentiment:
        chips.append(f"Sentiment: {', '.join(f_sentiment)}")
    if f_mode:
        chips.append(f"Mode: {', '.join(f_mode)}")
    if f_search.strip():
        chips.append(f'Search: "{f_search.strip()}"')
    if isinstance(d_range, tuple) and len(d_range) == 2:
        chips.append(f"Dates: {d_range[0]:%d %b} – {d_range[1]:%d %b %Y}")

    if chips:
        chip_html = "".join(f'<span class="voa-filter-chip">{c}</span>' for c in chips)
        st.markdown(
            f'<div class="voa-filter-bar">{chip_html}'
            f'<span class="voa-filter-chip">{len(sessions)} of {len(sessions_all)} sessions</span></div>',
            unsafe_allow_html=True,
        )
    if len(sessions) == 0:
        st.info("No sessions match the current filters. Adjust or clear filters in the sidebar.")
        st.stop()


def render_hero(section: str):
    subtitles = {
        "Overview": "Engagement pulse across CARES levers, sentiment, and closure health.",
        "Priority & Risk": "Ranked queue of open items by composite risk score.",
        "Coverage & Themes": "Themes surfaced in connect coverage and cohort patterns.",
        "Action Center": "Status board and owner workload for action follow-through.",
        "Insight Library": "Known-issue playbook from the engagement library.",
        "Data Explorer": "Full session table with export for offline analysis.",
    }
    st.markdown(
        theme.page_header("Pulse", subtitles.get(section, ""), section),
        unsafe_allow_html=True,
    )


def donut(df: pd.DataFrame, col: str, color_map, title: str = None):
    counts = df[col].astype(str).value_counts().reset_index()
    counts.columns = [col, "count"]
    counts = counts[counts[col] != "nan"]
    if counts.empty:
        st.caption("No data for current filters.")
        return
    fig = px.pie(
        counts,
        names=col,
        values="count",
        hole=0.58,
        color=col,
        color_discrete_map=color_map,
        title=None,
    )
    fig.update_traces(
        textinfo="label+percent",
        textposition="auto",
        textfont_size=10,
        textfont_color=theme.INK,
        marker=dict(line=dict(color=theme.PAPER, width=2)),
    )
    st.plotly_chart(
        apply_fig(fig, height=260, showlegend=False),
        use_container_width=True,
    )


def cares_chart(df: pd.DataFrame):
    g = df.groupby("cares_lever", observed=True).agg(
        sessions=("ID", "count"),
        High=("severity", lambda s: (s == "High").sum()),
        Moderate=("severity", lambda s: (s == "Moderate").sum()),
        Low=("severity", lambda s: (s == "Low").sum()),
    ).reset_index()
    g = g[g["sessions"] > 0]
    unique_levers = g["cares_lever"].astype(str).tolist()
    order = [c for c in CARES_ORDER if c in unique_levers]
    for c in unique_levers:
        if c not in order:
            order.append(c)
    g["cares_lever"] = pd.Categorical(g["cares_lever"].astype(str), categories=order, ordered=True)
    g = g.sort_values("cares_lever")

    fig = go.Figure()
    for sev, color in theme.SEVERITY_COLORS.items():
        fig.add_bar(
            y=g["cares_lever"].astype(str),
            x=g[sev],
            name=sev,
            orientation="h",
            marker_color=color,
            hovertemplate="%{y}: %{x} " + sev + " sessions<extra></extra>",
        )
    fig.update_layout(barmode="stack", yaxis=dict(autorange="reversed"))
    st.plotly_chart(apply_fig(fig, height=320, legend=dict(orientation="h", y=-0.15)), use_container_width=True)

    for _, r in g.iterrows():
        st.caption(f"**{r['cares_lever']}** — {CARES_DESCRIPTIONS.get(str(r['cares_lever']), '')}")


def session_timeline(df: pd.DataFrame):
    if df.empty or df["date"].isna().all():
        st.caption("No dated sessions in the current view.")
        return
    weekly = (
        df.dropna(subset=["date"])
        .assign(week=lambda d: d["date"].dt.to_period("W").dt.start_time)
        .groupby("week", observed=True)
        .agg(sessions=("ID", "count"), high=("severity", lambda s: (s == "High").sum()))
        .reset_index()
        .sort_values("week")
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=weekly["week"],
            y=weekly["sessions"],
            name="Sessions",
            mode="lines+markers",
            line=dict(color=theme.SLATE_BLUE, width=2.5),
            marker=dict(size=6),
        )
    )
    fig.add_trace(
        go.Bar(
            x=weekly["week"],
            y=weekly["high"],
            name="High severity",
            marker_color=theme.BRAND,
            opacity=0.75,
        )
    )
    fig.update_layout(barmode="overlay", yaxis_title="Count")
    st.plotly_chart(apply_fig(fig, height=300, legend=dict(orientation="h", y=-0.18)), use_container_width=True)


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    logo_svg = load_logo_svg_v3("white")
    st.markdown(
        f'<div class="voa-sidebar-logo" style="width: 200px; margin-top: -10px; margin-bottom: 24px; max-width: 100%;">{logo_svg}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Nav tiles (replaces radio) ──────────────────────────────────────────
    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = NAV_ITEMS[0]

    def change_nav(page_name):
        st.session_state["nav_page"] = page_name

    for _item in NAV_ITEMS:
        _active = st.session_state["nav_page"] == _item
        _clean = _item.lower().replace(" & ", "_").replace(" ", "_")
        st.button(
            _item,
            key=f"nav_btn_{_clean}",
            use_container_width=True,
            type="primary" if _active else "secondary",
            on_click=change_nav,
            args=(_item,),
        )

    nav = st.session_state["nav_page"]
    st.markdown("<hr/>", unsafe_allow_html=True)

    if "uploader_reset_id" not in st.session_state:
        st.session_state["uploader_reset_id"] = 0

    with st.expander("Data source", expanded=False):
        up_dash = st.file_uploader(
            "Replace HR_Dashboard_Final.xlsx",
            type=["xlsx"],
            key=f"up_dash_{st.session_state['uploader_reset_id']}",
        )
        up_lib = st.file_uploader(
            "Replace Engagement_Library.xlsx",
            type=["xlsx"],
            key=f"up_lib_{st.session_state['uploader_reset_id']}",
        )
        st.caption("Leave blank to use bundled workbooks, or demo data if none are present.")

        # Remove uploaded workbook button
        if up_dash is not None or up_lib is not None:
            if st.button("Remove Uploaded Workbook (Use Default)", type="primary", use_container_width=True):
                st.session_state["uploader_reset_id"] += 1
                st.rerun()

        # Clear cache button
        if st.button("Force Clear Cache & Reload Data", type="secondary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with st.expander("AI Insights Configuration", expanded=False):
        api_provider = st.selectbox("API Provider", ["OpenAI", "Gemini", "Azure OpenAI"], key="api_provider")
        import os

        if api_provider == "OpenAI":
            default_key = os.environ.get("OPENAI_API_KEY", "")
            st.text_input("API Key (typing hidden)", value=default_key, type="password", key="api_key_input")
            st.caption("Paste your OpenAI API key to fetch executive AI insights.")

        elif api_provider == "Gemini":
            default_key = os.environ.get("GEMINI_API_KEY", "")
            st.text_input("API Key (typing hidden)", value=default_key, type="password", key="api_key_input")
            st.caption("Paste your Gemini API key to fetch executive AI insights.")

        else:
            st.text_input("Azure API Key", value=os.environ.get("AZURE_OPENAI_API_KEY", ""), type="password", key="azure_api_key")
            st.text_input("Azure Endpoint", value=os.environ.get("AZURE_OPENAI_ENDPOINT", ""), placeholder="https://your-resource.openai.azure.com", key="azure_endpoint")
            st.text_input("Azure Deployment Name", value=os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""), placeholder="gpt-4o-mini", key="azure_deployment")
            st.caption("Provide Azure OpenAI credentials and deployment details for enterprise-hosted AI insights.")

    st.markdown("<hr/>", unsafe_allow_html=True)
    if st.button("🖨️ Export Dashboard as PDF", type="secondary", use_container_width=True, key="sidebar_export_pdf"):
        import time
        t_sec = int(time.time())
        st.components.v1.html(
            f"<script>setTimeout(function() {{ window.parent.print(); }}, 500);</script><!-- {t_sec} -->",
            height=0,
            width=0,
        )

    # Read uploaded bytes directly from widgets
    dashboard_bytes = up_dash.getvalue() if up_dash is not None else None
    library_bytes = up_lib.getvalue() if up_lib is not None else None

    # Detect upload change to clear filters automatically
    current_dash_name = up_dash.name if up_dash is not None else ""
    if "last_dash_name" not in st.session_state:
        st.session_state["last_dash_name"] = ""
    if current_dash_name != st.session_state["last_dash_name"]:
        st.session_state["last_dash_name"] = current_dash_name
        for _k in (
            "filter_service", "filter_lever", "filter_severity", "filter_status",
            "filter_sentiment", "filter_mode", "filter_search", "filter_dates"
        ):
            if _k in st.session_state:
                del st.session_state[_k]

    dataset = get_dataset_v5(dashboard_bytes, library_bytes)
    sessions_raw = dataset.sessions
    max_date = sessions_raw["date"].max()
    as_of = max_date if pd.notna(max_date) else pd.Timestamp.today()
    sessions_all = enrich_sessions_v3(sessions_raw, str(as_of))

    if getattr(dataset, "error", None):
        st.error(dataset.error)

    if getattr(dataset, "is_demo", False):
        st.info("Demo dataset loaded — upload workbooks for live data.")

    for w in dataset.warnings:
        if getattr(dataset, "error", None) and w == dataset.error:
            continue
        st.warning(w)


    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown('<div class="voa-eyebrow on-dark">Filters</div>', unsafe_allow_html=True)

    def _opts(col):
        return sorted([x for x in sessions_all[col].dropna().astype(str).unique() if x and x != "nan"])

    f_service = st.multiselect("Service line", _opts("service_line"), key="filter_service")
    unique_levers = sessions_all["cares_lever"].dropna().astype(str).unique()
    all_levers = [c for c in CARES_ORDER if c in unique_levers]
    for c in unique_levers:
        if c and c != "nan" and c not in all_levers:
            all_levers.append(c)
    f_lever = st.multiselect("CARES lever", all_levers, key="filter_lever")
    unique_sevs = sessions_all["severity"].dropna().astype(str).unique()
    all_severities = [s for s in SEVERITY_ORDER if s in unique_sevs]
    for s in unique_sevs:
        if s and s != "nan" and s not in all_severities:
            all_severities.append(s)
    f_severity = st.multiselect("Severity", all_severities, key="filter_severity")

    unique_statuses = sessions_all["status"].dropna().astype(str).unique()
    all_statuses = [s for s in STATUS_ORDER if s in unique_statuses]
    for s in unique_statuses:
        if s and s != "nan" and s not in all_statuses:
            all_statuses.append(s)
    f_status = st.multiselect("Status", all_statuses, key="filter_status")

    # Dynamic sentiment choices
    unique_sentiments = sessions_all["sentiment"].dropna().astype(str).unique()
    all_sentiments = [s for s in SENTIMENT_ORDER if s in unique_sentiments]
    for s in unique_sentiments:
        if s and s != "nan" and s not in all_sentiments:
            all_sentiments.append(s)
    f_sentiment = st.multiselect("Sentiment", all_sentiments, key="filter_sentiment")
    f_mode = st.multiselect("Engagement mode", _opts("engagement_mode"), key="filter_mode")
    f_search = st.text_input("Search BHR / cohort / query", "", key="filter_search")

    # ── Live autocomplete suggestions ──────────────────────────────────────
    _q = f_search.strip().lower()
    if _q:
        # Build a deduplicated candidate pool from searchable columns
        _suggestion_cols = {
            "bhr_name_canonical": "👤",
            "cohort": "🔗",
            "service_line": "🏢",
            "ibu_scope": "🌐",
            "engagement_query": "💬",
        }
        _seen: set = set()
        _suggestions: list[tuple[str, str]] = []
        for _col, _icon in _suggestion_cols.items():
            if _col not in sessions_all.columns:
                continue
            for _val in sessions_all[_col].dropna().astype(str).unique():
                _val_clean = _val.strip()
                if not _val_clean or _val_clean.lower() == "nan":
                    continue
                # For engagement_query: only show first 60 chars as label
                _label = _val_clean[:60] + ("…" if len(_val_clean) > 60 else "")
                _match_key = _val_clean.lower()
                if _q in _match_key and _match_key not in _seen:
                    _seen.add(_match_key)
                    _suggestions.append((_label, _icon))
                if len(_suggestions) >= 8:
                    break
            if len(_suggestions) >= 8:
                break

        if _suggestions:
            st.markdown(
                '<div style="font-size:11px;color:rgba(255,255,255,0.55);'
                'letter-spacing:0.06em;text-transform:uppercase;margin:4px 0 6px;">Suggestions</div>',
                unsafe_allow_html=True,
            )
            for _label, _icon in _suggestions:
                _btn_key = f"sugg_{_label[:40]}"
                if st.button(f"{_icon} {_label}", key=_btn_key, use_container_width=True):
                    st.session_state["filter_search"] = _label.rstrip("…")
                    st.rerun()


    min_d, max_d = sessions_all["date"].min(), sessions_all["date"].max()
    if pd.notna(min_d) and pd.notna(max_d) and min_d.date() != max_d.date():
        d_range = st.date_input(
            "Date of connect",
            value=(min_d.date(), max_d.date()),
            min_value=min_d.date(),
            max_value=max_d.date(),
            key="filter_dates",
        )
    else:
        d_range = None

    def clear_filters_callback():
        for key in (
            "filter_service",
            "filter_lever",
            "filter_severity",
            "filter_status",
            "filter_sentiment",
            "filter_mode",
            "filter_search",
            "filter_dates",
        ):
            if key in st.session_state:
                del st.session_state[key]

    st.button("Clear all filters", key="clear_filters", type="secondary", on_click=clear_filters_callback)

    st.markdown("<hr/>", unsafe_allow_html=True)
    source_info = "default local file (HR_Dashboard_Final.xlsx)"
    if getattr(dataset, "is_demo", False):
        source_info = "synthetic demo dataset (fallback)"
    elif up_dash is not None:
        source_info = f"uploaded file ({up_dash.name})"
    st.caption(f"Loaded {len(sessions_all)} sessions from {source_info} · as of {as_of:%d %b %Y}")


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    out = df
    if f_service:
        out = out[out["service_line"].astype(str).isin(f_service)]
    if f_lever:
        out = out[out["cares_lever"].astype(str).isin(f_lever)]
    if f_severity:
        out = out[out["severity"].astype(str).isin(f_severity)]
    if f_status:
        out = out[out["status"].astype(str).isin(f_status)]
    if f_sentiment:
        out = out[out["sentiment"].astype(str).isin(f_sentiment)]
    if f_mode:
        out = out[out["engagement_mode"].astype(str).isin(f_mode)]
    if isinstance(d_range, tuple) and len(d_range) == 2:
        start, end = d_range
        out = out[(out["date"].dt.date >= start) & (out["date"].dt.date <= end)]
    if f_search.strip():
        q = f_search.strip().lower()
        cols = ["bhr_name_canonical", "cohort", "engagement_query", "service_line", "bhr_id", "ibu_scope"]
        mask = False
        for c in cols:
            if c in out.columns:
                mask = mask | out[c].astype(str).str.lower().str.contains(q, na=False)
        out = out[mask]
    return out


@st.cache_data(show_spinner="Analyzing priority data with AI...")
def fetch_priority_insights(summary_dict: dict, api_key: str, provider: str, default_insights: dict) -> dict:
    import json
    import requests
    
    if not api_key:
        return default_insights

    prompt = (
        "You are an expert HR analyst and executive strategist.\n"
        "Analyze the following summary of associate engagement Priority & Risk data:\n"
        f"{json.dumps(summary_dict, indent=2)}\n\n"
        "Generate highly specific, actionable insights.\n"
        "Output MUST be exactly a JSON object with these exact 3 keys:\n"
        '{"score_dist": [], "risk_age": [], "owner_load": []}\n'
        "Each key should map to an array of 2 to 3 strings. Each string should be a concise, bold-titled insight (e.g. '<b>Observation:</b> details...').\n"
        "Return ONLY the raw JSON object string.\n"
    )

    try:
        if provider == "OpenAI":
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that outputs only raw JSON arrays of strings."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=8)
            res.raise_for_status()
            data = res.json()
            content_text = data["choices"][0]["message"]["content"].strip()
        else: # Gemini
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}
            }
            res = requests.post(url, json=payload, timeout=8)
            res.raise_for_status()
            data = res.json()
            content_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        if content_text.startswith("```"):
            lines = content_text.splitlines()
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            content_text = "\n".join(lines).strip()

        parsed = json.loads(content_text)
        if isinstance(parsed, dict) and "score_dist" in parsed:
            return parsed
    except Exception:
        pass

    return default_insights


@st.cache_data(show_spinner=False)
def fetch_hurry_insights(summary_str: str, summary_dict: dict, api_key: str, provider: str) -> list:
    """Return 5 punchy plain-English findings for the 'in a hurry' panel."""
    import json, requests

    # Always build compelling stat-backed fallback bullets
    total      = summary_dict.get("total_sessions", 0)
    open_n     = summary_dict.get("open_sessions", 0)
    high_n     = summary_dict.get("high_severity_sessions", 0)
    closure    = summary_dict.get("overall_closure_rate_pct", 0)
    hi_closure = summary_dict.get("high_severity_closure_rate_pct", 0)
    lever      = summary_dict.get("top_complaint_lever", "N/A")
    lever_pct  = summary_dict.get("top_complaint_lever_percentage", 0)
    sl         = summary_dict.get("hottest_service_line", "N/A")
    sl_pct     = summary_dict.get("hottest_service_line_percentage", 0)
    avg_risk   = summary_dict.get("average_risk_score", 0)
    gap        = round(closure - hi_closure, 1)

    fallback = [
        f"{high_n} of {total} sessions carry a High severity rating — {round(high_n/total*100,1) if total else 0}% of the total engagement signal.",
        f"High-severity cases close at only {hi_closure}%, which is {gap} points below the overall closure rate of {closure}%. The most critical issues are resolving slowest.",
        f"{lever} accounts for {lever_pct}% of all sessions, making it the dominant theme across associate concerns.",
        f"{sl} is the highest-volume service line at {sl_pct}% of sessions — a concentration that warrants focused leadership attention.",
        f"{open_n} sessions remain Open with no resolution action taken. The average risk score across the dataset stands at {round(avg_risk,1)}.",
    ]

    if not api_key:
        return fallback

    prompt = (
        "You are a senior HR data analyst briefing a busy executive.\n"
        "Here is a live snapshot of employee engagement data (Pulse):\n"
        f"{json.dumps(summary_dict, indent=2)}\n\n"
        "Write exactly 5 insights that are specific, data-backed, and professionally worded. Each must:\n"
        "  - Lead with the most significant NUMBER from the data\n"
        "  - Be one concise sentence (max 28 words)\n"
        "  - Use clear, professional language — no emojis, no casual phrasing\n"
        "  - Sound like a trusted advisor summarising findings for a C-suite audience\n"
        "  - Draw on the sample employee comments where relevant for specificity\n"
        "Return ONLY a raw JSON array of 5 strings. No markdown. No preamble."
    )

    try:
        if provider == "OpenAI":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Output only a raw JSON array of 5 strings."},
                    {"role": "user",   "content": prompt},
                ],
                "temperature": 0.45,
            }
            res = requests.post("https://api.openai.com/v1/chat/completions",
                                json=payload, headers=headers, timeout=12)
            res.raise_for_status()
            content_text = res.json()["choices"][0]["message"]["content"].strip()
        else:  # Gemini
            url = (f"https://generativelanguage.googleapis.com/v1beta/"
                   f"models/gemini-1.5-flash:generateContent?key={api_key}")
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.45},
            }
            res = requests.post(url, json=payload, timeout=12)
            res.raise_for_status()
            content_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Strip markdown fences if present
        if content_text.startswith("```"):
            lines = content_text.splitlines()
            lines = lines[1:] if lines[0].startswith("```") else lines
            lines = lines[:-1] if lines and lines[-1].startswith("```") else lines
            content_text = "\n".join(lines).strip()

        parsed = json.loads(content_text)
        if isinstance(parsed, list) and len(parsed) >= 3:
            return [str(s) for s in parsed[:5]]
    except Exception:
        pass

    return fallback


def fetch_ai_insights(summary_str: str, summary_dict: dict, api_key: str, provider: str, default_insights: dict) -> dict:
    import json
    import requests

    if provider == "Azure OpenAI":
        api_key = st.session_state.get("azure_api_key", "")
        azure_endpoint = st.session_state.get("azure_endpoint", "")
        azure_deployment = st.session_state.get("azure_deployment", "")

        if not api_key or not azure_endpoint or not azure_deployment:
            st.warning("Azure OpenAI is selected, but Azure credentials or deployment details are missing. Showing fallback insights instead.")
            return default_insights
    elif not api_key:
        return default_insights

    prompt = (
        "You are a senior HR strategy advisor and workforce intelligence consultant responsible for generating executive-grade Pulse analysis.\n"
        "Analyze the following dashboard metrics and generate a comprehensive leadership narrative instead of short bullets.\n\n"
        f"Pulse Dashboard Data:\n{json.dumps(summary_dict, indent=2)}\n\n"
        "The analysis must provide deep operational context, quantified business impact, organizational implications, and practical leadership guidance.\n\n"
        "Required analytical sections include:\n"
        "1. Executive Summary: Deliver a high-level narrative explaining the current employee engagement pulse, workforce morale, operational risk posture, and leadership implications.\n"
        "2. Deep-Dive Breakdown: Thoroughly analyze the operational impact of High Severity cases versus overall closure rates. Explicitly discuss the significance of approximately 20.8% High Severity sessions compared to an overall closure rate of approximately 70.3%, including execution risk, retention exposure, and HR workload implications.\n"
        "3. Root Cause & Trends Analysis: Explain why Alignment-related concerns account for approximately 63.2% of sessions. Discuss likely causes such as role ambiguity, transformation fatigue, communication gaps, delivery pressure, or organizational restructuring. Reference the session volume trend over time and infer whether engagement intensity is stabilizing, rising, or becoming concentrated in specific organizational areas.\n"
        "4. Strategic Action Plan: Provide highly actionable recommendations for leadership teams to reduce unresolved Open cases, improve resolution velocity, strengthen accountability governance, and address the concentration risk associated with the DEA Service Line representing approximately 67.5% of sessions. Recommendations must be operationally specific and measurable.\n\n"
        "Output MUST be exactly a JSON object with these exact 6 keys:\n"
        '{"volume_timeline": [], "cares_mix": [], "severity_dist": [], "sentiment_mix": [], "engagement_mode": [], "service_line": []}\n'
        "Each key must contain 2 to 3 detailed executive insights written in narrative business language with substantial analytical depth.\n"
        "Return ONLY the raw JSON object string with no markdown formatting or code fences.\n"
    )

    try:
        if provider == "OpenAI":
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are an enterprise HR intelligence assistant that outputs only raw JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.35
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=12)
            res.raise_for_status()
            data = res.json()
            content_text = data["choices"][0]["message"]["content"].strip()

        elif provider == "Azure OpenAI":
            azure_api_key = st.session_state.get("azure_api_key", "")
            azure_endpoint = st.session_state.get("azure_endpoint", "").rstrip("/")
            azure_deployment = st.session_state.get("azure_deployment", "")
            api_version = "2024-05-01-preview"

            headers = {
                "api-key": azure_api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "messages": [
                    {"role": "system", "content": "You are an enterprise HR intelligence assistant that outputs only raw JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.35
            }

            azure_url = (
                f"{azure_endpoint}/openai/deployments/{azure_deployment}"
                f"/chat/completions?api-version={api_version}"
            )

            res = requests.post(azure_url, json=payload, headers=headers, timeout=12)
            res.raise_for_status()
            data = res.json()
            content_text = data["choices"][0]["message"]["content"].strip()

        else: # Gemini
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.35
                }
            }
            res = requests.post(url, json=payload, timeout=12)
            res.raise_for_status()
            data = res.json()
            content_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Parse the JSON array
        if content_text.startswith("```"):
            lines = content_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content_text = "\n".join(lines).strip()

        parsed = json.loads(content_text)
        if isinstance(parsed, dict) and "volume_timeline" in parsed:
            return parsed
    except Exception as e:
        pass

    return default_insights


sessions = apply_filters(sessions_all)


# --------------------------------------------------------------------------
# Views
# --------------------------------------------------------------------------
def view_overview():
    render_hero("Overview")
    filter_banner()

    # ── Insights for people in a hurry ─────────────────────────────────────
    _api_key_h  = st.session_state.get("api_key_input", "")
    _provider_h = st.session_state.get("api_provider", "OpenAI")

    # Quick snapshot for the hurry panel (computed before the main stats block)
    _snap = sessions
    _htotal    = len(_snap)
    _hopen     = int((_snap["status"] == "Open").sum())
    _hhigh     = int((_snap["severity"] == "High").sum())
    _hclosed   = int((_snap["status"] == "Closed").sum())
    _hclosure  = round(_hclosed / _htotal * 100, 1) if _htotal else 0.0
    _hhi_df    = _snap[_snap["severity"] == "High"]
    _hhi_cls   = round(int((_hhi_df["status"] == "Closed").sum()) / len(_hhi_df) * 100, 1) if len(_hhi_df) else 0.0
    _hlev_g    = _snap["cares_lever"].value_counts()
    _htop_lev  = str(_hlev_g.index[0]) if not _hlev_g.empty else "N/A"
    _htop_lev_pct = round(_hlev_g.iloc[0] / _htotal * 100, 1) if _htotal and not _hlev_g.empty else 0.0
    _hsl_g     = _snap["service_line"].value_counts()
    _htop_sl   = str(_hsl_g.index[0]) if not _hsl_g.empty else "N/A"
    _htop_sl_pct = round(_hsl_g.iloc[0] / _htotal * 100, 1) if _htotal and not _hsl_g.empty else 0.0
    _havg_risk = float(_snap["risk_score"].mean()) if _htotal else 0.0
    _hsample_q = [str(q)[:120] for q in _snap[_snap["severity"] == "High"]["engagement_query"].dropna().head(5).tolist()]

    _hurry_summary = {
        "total_sessions": _htotal,
        "open_sessions": _hopen,
        "high_severity_sessions": _hhigh,
        "overall_closure_rate_pct": _hclosure,
        "high_severity_closure_rate_pct": _hhi_cls,
        "top_complaint_lever": _htop_lev,
        "top_complaint_lever_percentage": _htop_lev_pct,
        "hottest_service_line": _htop_sl,
        "hottest_service_line_percentage": _htop_sl_pct,
        "average_risk_score": _havg_risk,
        "sample_critical_comments": _hsample_q,
    }
    _hurry_cache_key = f"hurry_{_htotal}_{_hopen}_{_hhigh}_{_hclosure}_{_htop_lev}_{_htop_sl}"

    # Render the panel — auto-refreshes whenever _hurry_cache_key changes
    with st.spinner("Generating insights…" if _api_key_h else ""):
        _hurry_bullets = fetch_hurry_insights(
            _hurry_cache_key, _hurry_summary, _api_key_h, _provider_h
        )

    _bullet_items = "".join(
        f"<li>{b}</li>"
        for b in _hurry_bullets
    )
    st.markdown(
        f'<div class="voa-hurry-panel">'
        f'<div class="hurry-title">Insights for people in a hurry</div>'
        f'<ul>{_bullet_items}</ul>'
        f'</div>',
        unsafe_allow_html=True,
    )
    # ───────────────────────────────────────────────────────────────────────

    total = len(sessions)
    open_n = int((sessions["status"] == "Open").sum())
    inprog_n = int((sessions["status"] == "In-progress").sum())
    closed_n = int((sessions["status"] == "Closed").sum())
    high_n = int((sessions["severity"] == "High").sum())
    closure_pct = round(closed_n / total * 100, 1) if total else 0.0
    bhr_clean = clean_active_bhr_count(sessions)
    sls = sessions["service_line"].nunique()
    pos_n = int((sessions["sentiment"] == "Positive").sum())
    sentiment_pct = round(pos_n / total * 100, 1) if total else 0.0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi_card(c1, "Total sessions", total, accent="ink")
    kpi_card(c2, "Open", open_n, "needs first action", accent="brand")
    kpi_card(c3, "In-progress", inprog_n, "being worked", accent="gold")
    kpi_card(c4, "Closed", closed_n, f"{closure_pct}% closure", accent="sage")
    kpi_card(c5, "High severity", high_n, f"{round(high_n/total*100,1) if total else 0}% of sessions", accent="brand")
    kpi_card(c6, "BHRs engaged", bhr_clean, f"across {sls} service lines", accent="ink")

    # Calculate stats for insights
    lev_g = (
        sessions.groupby("cares_lever", observed=True)
        .agg(sessions=("ID", "count"), high=("severity", lambda s: (s == "High").sum()))
        .reset_index()
    )
    lev_g = lev_g[lev_g["sessions"] > 0].sort_values("sessions", ascending=False)
    
    top_lev_name = "N/A"
    top_lev_count = 0
    top_lev_pct = 0
    if not lev_g.empty:
        top_lev_name = lev_g.iloc[0]["cares_lever"]
        top_lev_count = int(lev_g.iloc[0]["sessions"])
        top_lev_pct = round(top_lev_count / total * 100, 1) if total else 0
        
    sl_counts_g = sessions["service_line"].value_counts()
    top_sl = "N/A"
    top_sl_n = 0
    top_sl_pct = 0
    if not sl_counts_g.empty:
        top_sl = sl_counts_g.index[0]
        top_sl_n = sl_counts_g.values[0]
        top_sl_pct = round(top_sl_n / total * 100, 1) if total else 0
        
    high_df = sessions[sessions["severity"] == "High"]
    high_closure = 0.0
    gap = 0.0
    if len(high_df):
        high_closed = int((high_df["status"] == "Closed").sum())
        high_closure = round(high_closed / len(high_df) * 100, 1)
        gap = round(closure_pct - high_closure, 1)

    # Package dynamic summary for AI prompt
    sample_queries = sessions[sessions["severity"] == "High"]["engagement_query"].dropna().head(10).tolist()
    sample_queries = [str(q)[:100] for q in sample_queries]

    summary_dict = {
        "total_sessions": int(total),
        "open_sessions": int(open_n),
        "inprogress_sessions": int(inprog_n),
        "closed_sessions": int(closed_n),
        "high_severity_sessions": int(high_n),
        "overall_closure_rate_pct": float(closure_pct),
        "high_severity_closure_rate_pct": float(high_closure),
        "average_risk_score": float(sessions["risk_score"].mean()) if total else 0.0,
        "top_complaint_lever": str(top_lev_name),
        "top_complaint_lever_percentage": float(top_lev_pct),
        "hottest_service_line": str(top_sl),
        "hottest_service_line_percentage": float(top_sl_pct),
        "sample_critical_comments": sample_queries
    }

    # Unique cache key string representing the exact dynamic values of the current dataset/filters
    summary_str = f"{total}_{open_n}_{inprog_n}_{closed_n}_{high_n}_{closure_pct}_{high_closure}_{gap}_{sentiment_pct}_{top_sl}_{top_lev_name}"

    default_insights = {
        "volume_timeline": [
            f"<b>Pacing:</b> The total volume ({total} sessions) shows engagement pacing over time."
        ],
        "cares_mix": [
            f"<b>Primary Focus:</b> <b>{top_lev_name}</b> dominates with <b>{top_lev_pct}%</b> of all concerns.",
            f"<b>Strategic Shift:</b> Reallocate HR resources toward {top_lev_name} initiatives to drive immediate impact."
        ],
        "severity_dist": [
            f"<b>Critical Volume:</b> <b>{high_n}</b> High-severity sessions require immediate executive oversight.",
            f"<b>Resolution Gap:</b> High-severity cases close at {high_closure}% (Gap: {gap} points)."
        ],
        "sentiment_mix": [
            f"<b>Positive Tones:</b> {sentiment_pct}% positive sentiment overall.",
            f"<b>Hidden Risks:</b> A notable portion of neutral/positive connects still harbor high-severity flags."
        ],
        "engagement_mode": [
            f"<b>Dominant Channels:</b> Review how cohort connects scale compared to 1:1 sessions.",
        ],
        "service_line": [
            f"<b>Operational Hotspot:</b> <b>{top_sl}</b> is the leading service line ({top_sl_pct}% of total).",
            f"<b>Action:</b> Prioritize localized leadership intervention here to reduce attrition."
        ]
    }

    # Fetch AI insights
    api_key_val = st.session_state.get("api_key_input", "")
    provider_val = st.session_state.get("api_provider", "OpenAI")
    
    insights = fetch_ai_insights(summary_str, summary_dict, api_key_val, provider_val, default_insights)



    # Block 1: Volume Timeline
    render_chart_row(
        "Session volume over time", 
        lambda: session_timeline(sessions), 
        insights.get("volume_timeline", []), 
        flip=False
    )
    
    # Block 2: CARES Lever Mix
    render_chart_row(
        "CARES lever mix", 
        lambda: cares_chart(sessions), 
        insights.get("cares_mix", []), 
        flip=True
    )
    
    # Block 3: Severity distribution
    render_chart_row(
        "Severity distribution", 
        lambda: donut(sessions, "severity", theme.SEVERITY_COLORS), 
        insights.get("severity_dist", []), 
        flip=False
    )
    
    # Block 4: Sentiment mix
    render_chart_row(
        "Sentiment mix", 
        lambda: donut(sessions, "sentiment", theme.SENTIMENT_COLORS), 
        insights.get("sentiment_mix", []), 
        flip=True
    )
    
    # Block 5: Engagement mode
    render_chart_row(
        "Engagement mode", 
        lambda: donut(sessions, "engagement_mode", None), 
        insights.get("engagement_mode", []), 
        flip=False
    )
    
    # Block 6: Service line
    def sl_chart():
        sl_counts = sessions["service_line"].value_counts().reset_index()
        sl_counts.columns = ["service_line", "count"]
        fig = px.bar(sl_counts.sort_values("count"), x="count", y="service_line", orientation="h")
        fig.update_traces(marker_color=theme.SLATE_BLUE)
        st.plotly_chart(apply_fig(fig, height=320, showlegend=False))
        
    render_chart_row(
        "Sessions by service line", 
        sl_chart, 
        insights.get("service_line", []), 
        flip=True
    )



def view_priority():
    render_hero("Priority & Risk")
    filter_banner()

    only_open = st.checkbox("Show only Open / In-progress", value=True, key="prio_open_only")
    df = sessions.copy()
    if only_open:
        df = df[df["status"] != "Closed"]
    df = df.sort_values("risk_score", ascending=False)

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, "Items in view", len(df), accent="ink")
    kpi_card(c2, "Average risk score", round(df["risk_score"].mean(), 1) if len(df) else 0, "0–100 composite", accent="brand")
    kpi_card(c3, "Oldest unresolved", f"{int(df['age_days'].max())} days" if len(df) else "—", accent="gold")

    # Determine Owner Stats
    own = dataset.owners_long.merge(df[["ID"]], on="ID", how="inner")
    top_owners = []
    if len(own):
        agg = own.groupby("owner").agg(assigned=("ID", "count")).reset_index().sort_values("assigned", ascending=False).head(5)
        top_owners = agg["owner"].tolist()

    # Prepare AI Insights
    summary_dict = {
        "items_in_view": len(df),
        "average_risk_score": float(round(df["risk_score"].mean(), 1)) if len(df) else 0,
        "oldest_unresolved_days": int(df['age_days'].max()) if len(df) else 0,
        "top_overloaded_action_owners": top_owners
    }
    
    default_insights = {
        "score_dist": ["<b>Critical Mass:</b> Monitor the cluster of high-scoring sessions.", "<b>Intervention:</b> Immediate action required for scores > 75."],
        "risk_age": ["<b>Aging Risks:</b> Some high-risk items are aging beyond acceptable SLA.", "<b>Resolution Velocity:</b> Focus on accelerating closure for older tickets."],
        "owner_load": ["<b>Bottlenecks:</b> Top owners carry a disproportionate load of high-risk items.", "<b>Resource Reallocation:</b> Consider redistributing tasks among the HR team."]
    }

    api_key_val = st.session_state.get("api_key_input", "")
    provider_val = st.session_state.get("api_provider", "OpenAI")
    
    insights = fetch_priority_insights(summary_dict, api_key_val, provider_val, default_insights)

    # 1. Score Distribution
    def score_dist_chart():
        fig = px.histogram(df, x="risk_score", nbins=10, color_discrete_sequence=[theme.BRAND], labels={"risk_score": "Risk score", "count": "Sessions"})
        fig.update_traces(marker_line_color=theme.BRAND_DEEP, marker_line_width=0.5)
        fig.update_layout(margin=dict(b=20), height=320)
        st.plotly_chart(apply_fig(fig, showlegend=False), use_container_width=True)
        
    render_chart_row("Score distribution", score_dist_chart, insights.get("score_dist", []), flip=False)

    # 2. Risk vs Age
    def risk_age_chart():
        if "cares_lever" in df.columns and not df.empty:
            fig = px.scatter(
                df, x="age_days", y="risk_score", color="severity", symbol="status",
                color_discrete_map=theme.SEVERITY_COLORS,
                labels={"age_days": "Age (days)", "risk_score": "Risk score", "severity": "Severity", "status": "Status"},
                hover_data=["bhr_name_canonical", "cares_lever"]
            )
            fig.update_layout(
                legend_title_text="Severity & Status",
                legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(size=10)),
                margin=dict(b=80), height=320
            )
            st.plotly_chart(apply_fig(fig), use_container_width=True)
            
    if not df.empty:
        render_chart_row("Risk vs. age", risk_age_chart, insights.get("risk_age", []), flip=True)

    # 3. Owner Load
    def owner_load_chart():
        if len(own):
            agg = own.groupby("owner").agg(assigned=("ID", "count")).reset_index().sort_values("assigned", ascending=False).head(12)
            fig = px.bar(agg, x="assigned", y="owner", orientation="h", color_discrete_sequence=[theme.BRAND])
            fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(b=20), height=340)
            st.plotly_chart(apply_fig(fig, showlegend=False), use_container_width=True)
        else:
            st.caption("No owner data for the current filters.")
            
    render_chart_row("Action owner load", owner_load_chart, insights.get("owner_load", []), flip=False)

    st.write("")
    st.markdown("#### High-risk sessions (Data table)")
    show_cols = ["ID", "date", "associate_name", "bhr_name_canonical", "service_line", "cares_lever", "cohort", "severity", "status", "sentiment", "risk_score", "age_days", "engagement_query"]
    show_cols = [c for c in show_cols if c in df.columns]
    disp = df[show_cols].rename(columns={
        "associate_name": "Associate Name",
        "bhr_name_canonical": "BHR", "service_line": "Service line", "cares_lever": "CARES lever",
        "cohort": "Cohort / connect", "severity": "Severity", "status": "Status", "sentiment": "Sentiment",
        "risk_score": "Risk score", "age_days": "Age (days)", "engagement_query": "Engagement query",
        "date": "Date", "ID": "ID"
    })
    st.dataframe(
        disp, use_container_width=True, height=460, hide_index=True,
        column_config={
            "Risk score": st.column_config.ProgressColumn("Risk score", min_value=0, max_value=100, format="%d"),
            "Date": st.column_config.DateColumn("Date", format="DD MMM YYYY")
        }
    )


def view_coverage():
    render_hero("Coverage & Themes")
    filter_banner()

    cov = dataset.coverage_long.merge(sessions[["ID"]], on="ID", how="inner")
    if cov.empty:
        st.info("No coverage items logged for the current filters.")
        return

    top_n = st.slider("Show top N themes", 5, 30, 15, key="cov_top_n")
    counts = cov["coverage_item"].value_counts().reset_index().head(top_n)
    counts.columns = ["theme", "count"]
    fig = px.bar(counts.sort_values("count"), x="count", y="theme", orientation="h", color_discrete_sequence=[theme.BRAND])
    st.plotly_chart(apply_fig(fig, height=max(340, 22 * len(counts)), showlegend=False), use_container_width=True)

    st.write("")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Coverage by CARES lever")
        if "cares_lever" in cov.columns:
            by_lever = cov.groupby("cares_lever", observed=True)["coverage_item"].count().reset_index()
            by_lever.columns = ["cares_lever", "count"]
            by_lever = by_lever[by_lever["count"] > 0]
            fig = px.pie(
                by_lever,
                names="cares_lever",
                values="count",
                hole=0.5,
                color="cares_lever",
                color_discrete_map=theme.CARES_COLORS,
                title=None,
            )
            fig.update_traces(
                textinfo="label+percent",
                textposition="auto",
                textfont_size=10,
                textfont_color=theme.INK,
                marker=dict(line=dict(color=theme.PAPER, width=2)),
            )
            st.plotly_chart(apply_fig(fig, height=300, showlegend=False), use_container_width=True)
        else:
            st.caption("CARES lever not available for coverage items.")
    with col_b:
        st.markdown("#### Sessions by cohort / connect type")
        coh = sessions["cohort"].value_counts().reset_index().head(15)
        coh.columns = ["cohort", "count"]
        fig = px.bar(coh.sort_values("count"), x="count", y="cohort", orientation="h", color_discrete_sequence=[theme.SLATE_BLUE])
        st.plotly_chart(apply_fig(fig, height=340, showlegend=False), use_container_width=True)

    st.write("")
    st.markdown("#### Top coverage themes, in detail")
    detail = (
        cov.groupby("coverage_item")
        .agg(
            sessions=("ID", "count"),
            high_severity=("severity", lambda s: (s == "High").sum()),
        )
        .reset_index()
        .sort_values("sessions", ascending=False)
        .head(20)
    )
    detail.columns = ["Theme", "Sessions", "High-severity sessions"]
    st.dataframe(detail, use_container_width=True, hide_index=True)


def view_actions():
    render_hero("Action Center")
    filter_banner()

    cols = st.columns(3)
    for i, status in enumerate(STATUS_ORDER):
        sub = sessions[sessions["status"] == status]
        with cols[i]:
            st.markdown(f"**{status}** · {len(sub)}")
            
            sorted_sub = sub.sort_values("risk_score", ascending=False)
            
            def render_card(r):
                sev_pill = theme.pill(r["severity"], f"sev-{r['severity']}")
                q = (r["engagement_query"] or "")[:110] if pd.notna(r["engagement_query"]) else "No written comment logged."
                st.markdown(
                    f'<div class="voa-card" style="margin-bottom:12px;"><div class="title">{r["bhr_name_canonical"]} '
                    f'· {r["cohort"]}</div>{sev_pill}'
                    f'<div class="meta">{r["service_line"]} · {r["cares_lever"]}</div>'
                    f'<div class="voa-quote">{q}</div></div>',
                    unsafe_allow_html=True,
                )
                
            for _, r in sorted_sub.head(5).iterrows():
                render_card(r)
                
            if len(sorted_sub) > 5:
                with st.expander(f"View more ({len(sorted_sub) - 5})"):
                    for _, r in sorted_sub.iloc[5:].iterrows():
                        render_card(r)

    st.write("")
    st.markdown("#### Action items status × severity")
    tab = sessions.groupby(["status", "severity"], observed=True).size().reset_index(name="count")
    fig = px.bar(
        tab,
        x="status",
        y="count",
        color="severity",
        barmode="stack",
        color_discrete_map=theme.SEVERITY_COLORS,
        category_orders={"status": STATUS_ORDER, "severity": SEVERITY_ORDER},
    )
    st.plotly_chart(apply_fig(fig, height=340), use_container_width=True)

    st.write("")
    st.markdown("#### Owner performance")
    own = dataset.owners_long.merge(sessions[["ID"]], on="ID", how="inner")
    own = own.merge(sessions[["ID", "status"]], on="ID", suffixes=("", "_s"))
    if len(own):
        perf = (
            own.groupby("owner")
            .agg(
                assigned=("ID", "count"),
                closed=("status", lambda s: (s == "Closed").sum()),
                open_or_inprogress=("status", lambda s: (s != "Closed").sum()),
            )
            .reset_index()
        )
        perf["closure_pct"] = (perf["closed"] / perf["assigned"] * 100).round(1)
        perf = perf.sort_values("open_or_inprogress", ascending=False)
        perf.columns = ["Owner", "Assigned", "Closed", "Open / In-progress", "Closure %"]
        st.dataframe(perf, use_container_width=True, hide_index=True)
    else:
        st.caption("No owner data for the current filters.")


def view_library():
    render_hero("Insight Library")
    st.caption("Known-issues playbook — browse by CARES lever or cohort. Sidebar filters do not apply here.")

    mode = st.radio("Browse by", ["CARES lever", "Cohort / connect type"], horizontal=True, key="lib_mode")
    query = st.text_input("Search the library", "", key="lib_search")

    import re as _re

    def _highlight(text: str) -> str:
        if not query:
            return text
        return _re.sub(
            f"({_re.escape(query)})",
            r'<mark style="background:#FDE8EC;color:#5F0229;border-radius:2px;">\1</mark>',
            text, flags=_re.IGNORECASE,
        )

    if mode == "CARES lever":
        lib = dataset.lever_library
        levers = [l for l in CARES_ORDER if l in lib]
        for l in lib.keys():
            if l not in levers:
                levers.append(l)
        if not levers:
            st.info("No lever-based library data available.")
            return
        
        levers_opts = [""] + levers
        lever = st.selectbox(
            "CARES lever", levers_opts, index=0,
            format_func=lambda x: "All Levers (Show All)" if x == "" else x,
            key="lib_lever"
        )
        
        levers_to_show = levers if lever == "" else [lever]
        shown = 0
        for lev_name in levers_to_show:
            if lever == "":
                st.markdown(f"#### {lev_name}")
                st.caption(CARES_DESCRIPTIONS.get(lev_name, ""))
            else:
                st.caption(CARES_DESCRIPTIONS.get(lever, ""))
                
            areas = lib.get(lev_name, {})
            for area, entries in areas.items():
                if query and query.lower() not in area.lower() and not any(
                    query.lower() in e["insight"].lower() for e in entries
                ):
                    continue
                header_title = f"{lev_name} ◈ {area}" if lever == "" else area
                with st.expander(f"{header_title} · {len(entries)} known issue(s)", expanded=False):
                    for e in entries:
                        if query and query.lower() not in (area + e["insight"]).lower():
                            continue
                        shown += 1
                        st.markdown(
                            f'<div class="voa-card"><div class="title">{_highlight(e["insight"])}</div>'
                            f'<div class="meta">Recommended action</div>'
                            f'<div class="voa-quote">{e.get("action") or "Not specified"}</div></div>',
                            unsafe_allow_html=True,
                        )
        if query and shown == 0:
            st.info("No library entries match your search.")
            if st.button("Clear search", key="lib_clear_search", type="secondary"):
                st.session_state["lib_search"] = ""
                st.rerun()
    else:
        lib = dataset.cohort_library
        levers = [l for l in CARES_ORDER if l in lib]
        for l in lib.keys():
            if l not in levers:
                levers.append(l)
        if not levers:
            st.info("No cohort-based library data available.")
            return
        
        levers_opts = [""] + levers
        lever = st.selectbox(
            "CARES lever", levers_opts, index=0,
            format_func=lambda x: "All Levers" if x == "" else x,
            key="coh_lever"
        )
        
        if lever != "":
            cohorts = list(lib.get(lever, {}).keys())
        else:
            cohorts = sorted(list(set(c for l in levers for c in lib.get(l, {}).keys())))
            
        cohorts_opts = [""] + cohorts
        cohort = st.selectbox(
            "Cohort / connect type", cohorts_opts, index=0,
            format_func=lambda x: "All Cohorts (Show All)" if x == "" else x,
            key="lib_cohort"
        )
        
        levers_to_scan = levers if lever == "" else [lever]
        shown = 0
        for lev_name in levers_to_scan:
            cohort_map = lib.get(lev_name, {})
            cohorts_to_scan = list(cohort_map.keys()) if cohort == "" else [cohort]
            
            for coh_name in cohorts_to_scan:
                entries = cohort_map.get(coh_name, [])
                for e in entries:
                    if query and query.lower() not in e["insight"].lower():
                        continue
                    shown += 1
                    origin_label = f'<span style="font-size:10px;color:var(--muted);text-transform:uppercase;">{lev_name} · {coh_name}</span>'
                    st.markdown(
                        f'<div class="voa-card"><div class="title">{_highlight(e["insight"])}</div>'
                        f'<div class="meta">{e.get("description") or ""} &nbsp;&nbsp; {origin_label}</div>'
                        f'<div class="voa-quote">Recommended: {e.get("action") or "Not specified"}</div></div>',
                        unsafe_allow_html=True,
                    )
        if query and shown == 0:
            st.info("No library entries match your search.")
            if st.button("Clear search", key="coh_clear_search", type="secondary"):
                st.session_state["lib_search"] = ""
                st.rerun()


def view_explorer():
    render_hero("Data Explorer")
    filter_banner()

    show_cols = [
        "ID", "date", "associate_name", "bhr_name_canonical", "bhr_id", "service_line", "ibu_scope",
        "engagement_type", "band", "engagement_mode", "cares_lever", "cohort",
        "sentiment", "severity", "status", "risk_score", "age_days", "engagement_query", "action_owners",
    ]
    show_cols = [c for c in show_cols if c in sessions.columns]
    disp = sessions[show_cols].sort_values("ID")
    st.dataframe(
        disp,
        use_container_width=True,
        height=480,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "risk_score": st.column_config.NumberColumn("Risk score", format="%d"),
            "associate_name": st.column_config.TextColumn("Associate Name"),
            "bhr_name_canonical": st.column_config.TextColumn("BHR Name"),
            "bhr_id": st.column_config.TextColumn("BHR Employee ID"),
            "service_line": st.column_config.TextColumn("Service Line"),
            "ibu_scope": st.column_config.TextColumn("IBU Scope"),
            "engagement_type": st.column_config.TextColumn("Engagement Type"),
            "band": st.column_config.TextColumn("Band"),
            "engagement_mode": st.column_config.TextColumn("Engagement Mode"),
            "cares_lever": st.column_config.TextColumn("CARES Lever"),
            "cohort": st.column_config.TextColumn("Cohort / Connect"),
            "sentiment": st.column_config.TextColumn("Sentiment"),
            "severity": st.column_config.TextColumn("Severity"),
            "status": st.column_config.TextColumn("Status"),
            "age_days": st.column_config.NumberColumn("Age (days)", format="%d"),
            "engagement_query": st.column_config.TextColumn("Engagement Query"),
            "action_owners": st.column_config.TextColumn("Action Owners"),
        },
    )

    st.write("")
    if not disp.empty:
        sel_id = st.selectbox(
            "Inspect a session",
            options=disp["ID"].tolist(),
            format_func=lambda x: f"ID {x} — {sessions.loc[sessions['ID'] == x, 'associate_name'].iloc[0]} (by {sessions.loc[sessions['ID'] == x, 'bhr_name_canonical'].iloc[0]})",
            key="explorer_session",
        )
    else:
        sel_id = None
    if sel_id is not None:
        row = sessions[sessions["ID"] == sel_id].iloc[0]
        cov_items = dataset.coverage_long.loc[dataset.coverage_long["ID"] == sel_id, "coverage_item"].tolist()
        st.markdown(
            f'<div class="voa-card">'
            f'<div class="title">{row["associate_name"]} &middot; Connected by {row["bhr_name_canonical"]} &middot; {row["cohort"]}</div>'
            f'<div class="meta">{row["service_line"]} · {row["cares_lever"]} · '
            f"{theme.pill(row['severity'], 'sev-' + row['severity'])} "
            f"{theme.pill(row['status'], 'st-' + row['status'])}</div>"
            f'<div class="voa-quote">{row.get("engagement_query") or "No query logged."}</div>'
            f'<div class="meta">Coverage: {", ".join(cov_items) if cov_items else "None logged"}</div>'
            f'<div class="meta">Owners: {row.get("action_owners") or "Unassigned"}</div>'
            f"</div>",

            unsafe_allow_html=True,
        )

    csv = disp.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV",
        csv,
        file_name="voa_sessions_filtered.csv",
        mime="text/csv",
        key="download_csv",
    )


# --------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------
if nav == "Overview":
    view_overview()
elif nav == "Priority & Risk":
    view_priority()
elif nav == "Coverage & Themes":
    view_coverage()
elif nav == "Action Center":
    view_actions()
elif nav == "Insight Library":
    view_library()
elif nav == "Data Explorer":
    view_explorer()




