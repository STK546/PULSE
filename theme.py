"""Design system: Tech Mahindra brand tokens, Plotly defaults, and Streamlit CSS.

Color theory (60-30-10):
- ~60% warm neutrals (Clarity Grey / White) for page surfaces — reduces eye strain vs pure white.
- ~30% Anchor/Blueprint tones for sidebar chrome and headings — corporate depth.
- ~10% Mahindra Red for primary actions, alerts, and high-severity signals only.
"""
import os

# Tech Mahindra 2025 palette (official guidelines)
MAHINDRA_RED = "#E31837"
IMPACT_RED = "#5F0229"
CLARITY_RED = "#F8B4A3"
STEEL_GREY = "#4D4D4F"
INK_BLACK = "#231F20"
CLARITY_GREY_1 = "#F6F2EA"
CLARITY_GREY_2 = "#E5DFD3"
ANCHOR_GREY_1 = "#4A453D"
ANCHOR_GREY_2 = "#29251D"
BLUEPRINT_NAVY = "#1E1E20"  # Rich dark charcoal replacing blue sidebar bg
WHITE = "#FFFFFF"

# Semantic aliases used across the app
INK = INK_BLACK
INK_SOFT = ANCHOR_GREY_1
PAPER = CLARITY_GREY_1
CARD = WHITE
LINE = CLARITY_GREY_2
MUTED = STEEL_GREY

BRAND = MAHINDRA_RED
BRAND_DEEP = IMPACT_RED
BRAND_TINT = "#FDE8EC"

GOLD = "#B5832E"
GOLD_TINT = "#F5E4B8"
SAGE = "#2D6A4F"
SAGE_TINT = "#DDECE6"
SLATE_BLUE = "#4D4D4F"      # Steel Grey replacing slate blue for cohesive branding

# Updated Color Palettes based on Color Theory plan
COLOR_RED = "#E31837"
COLOR_CRIMSON = "#C53030"
COLOR_CORAL = "#DE6B48"

COLOR_AMBER = "#D97706"
COLOR_GOLD = "#D69E2E"
COLOR_OCHRE = "#E9C46A"

COLOR_TEAL = "#2A9D8F"
COLOR_SAGE = "#2D6A4F"

COLOR_SLATE_BLUE = "#4D4D4F" # Steel Grey replacing slate blue
COLOR_AMETHYST = "#7A5C8A"
COLOR_STEEL = "#8D99AE"

SEVERITY_COLORS = {"High": COLOR_RED, "Moderate": COLOR_AMBER, "Low": COLOR_TEAL}
STATUS_COLORS = {"Open": COLOR_RED, "In-progress": COLOR_AMBER, "Closed": COLOR_TEAL}
SENTIMENT_COLORS = {"Positive": COLOR_SAGE, "Neutral": COLOR_STEEL, "Mixed": COLOR_GOLD, "Negative": COLOR_CRIMSON}

CARES_COLORS = {
    "Alignment": COLOR_CORAL,
    "Career": COLOR_SLATE_BLUE,
    "Empowerment": COLOR_OCHRE,
    "Recognition": COLOR_AMETHYST,
    "Strive": COLOR_SAGE,
    "Unspecified": CLARITY_GREY_2,
}

FONT_DISPLAY = "'Newsreader', Georgia, serif"
FONT_BODY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
FONT_MONO = "'IBM Plex Mono', ui-monospace, monospace"

PLOTLY_FONT = dict(family=FONT_BODY, color=INK, size=13)


def plotly_layout_defaults() -> dict:
    return dict(
        template="plotly_white",
        font=PLOTLY_FONT,
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        margin=dict(l=8, r=8, t=36, b=8),
        xaxis=dict(
            title_font=dict(family=FONT_BODY, size=12, color=INK),
            tickfont=dict(family=FONT_BODY, size=11, color=INK),
            linecolor=LINE,
            gridcolor=CLARITY_GREY_2,
            zeroline=False,
        ),
        yaxis=dict(
            title_font=dict(family=FONT_BODY, size=12, color=INK),
            tickfont=dict(family=FONT_BODY, size=11, color=INK),
            linecolor=LINE,
            gridcolor=CLARITY_GREY_2,
            zeroline=False,
        ),
        legend=dict(
            font=dict(family=FONT_BODY, size=12, color=INK),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor=LINE,
            borderwidth=1,
        ),
        colorway=[COLOR_SLATE_BLUE, COLOR_TEAL, COLOR_AMBER, COLOR_RED, COLOR_STEEL, COLOR_AMETHYST],
        hoverlabel=dict(font=dict(family=FONT_BODY, size=12), bgcolor=BLUEPRINT_NAVY, font_color="white"),
        title=dict(text="", font=dict(family=FONT_DISPLAY, size=17, color=INK)),
    )




# ---------------------------------------------------------------------------
# Tech Mahindra logo (Loads from saved SVG files in the repository)
# ---------------------------------------------------------------------------
_logo_dir = os.path.dirname(os.path.abspath(__file__))
_logo_white_path = os.path.join(_logo_dir, "logo_white.svg")
_logo_dark_path = os.path.join(_logo_dir, "logo_dark.svg")

if os.path.exists(_logo_white_path):
    with open(_logo_white_path, "r", encoding="utf-8") as _f:
        TM_LOGO_SVG = _f.read()
else:
    TM_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 32" height="28" aria-label="Tech Mahindra">
  <polygon points="14,4 24,16 14,28 4,16" fill="#E31837"/>
  <polygon points="14,4 24,16 14,16 4,16" fill="#5F0229" opacity="0.55"/>
  <text x="30" y="22" font-family="Georgia, serif" font-size="13" font-weight="600" fill="#FFFFFF" letter-spacing="0.3">Tech Mahindra</text>
</svg>
"""

if os.path.exists(_logo_dark_path):
    with open(_logo_dark_path, "r", encoding="utf-8") as _f:
        TM_LOGO_DARK_SVG = _f.read()
else:
    TM_LOGO_DARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 32" height="28" aria-label="Tech Mahindra">
  <polygon points="14,4 24,16 14,28 4,16" fill="#E31837"/>
  <polygon points="14,4 24,16 14,16 4,16" fill="#5F0229" opacity="0.55"/>
  <text x="30" y="22" font-family="Georgia, serif" font-size="13" font-weight="600" fill="#231F20" letter-spacing="0.3">Tech Mahindra</text>
</svg>
"""


_SVG_BASE64_CACHE = {}

def get_svg_icon_b64(name: str, color: str) -> str:
    import base64
    import os
    
    cache_key = (name, color)
    if cache_key in _SVG_BASE64_CACHE:
        return _SVG_BASE64_CACHE[cache_key]
    
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", f"{name}.svg")
    if os.path.exists(icon_path):
        try:
            with open(icon_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            # Replace currentColor with specific color
            svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
            svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')
            b64_str = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
            _SVG_BASE64_CACHE[cache_key] = b64_str
            return b64_str
        except Exception:
            pass
    return ""


def inject_css() -> str:
    icons_css = ""
    nav_keys = [
        "overview",
        "priority_risk",
        "coverage_themes",
        "action_center",
        "insight_library",
        "data_explorer",
    ]
    for key in nav_keys:
        white_b64 = get_svg_icon_b64(key, "#FFFFFF")
        dark_b64 = get_svg_icon_b64(key, "#231F20")
        
        icons_css += f"""
/* ── {key} icon ── */
div.st-key-nav_btn_{key} button::before {{
    content: "";
    display: inline-block;
    width: 28px;
    height: 28px;
    background-color: rgba(255, 255, 255, 0.08);
    background-image: url('data:image/svg+xml;base64,{white_b64}') !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: 16px 16px !important;
    border-radius: 6px;
    margin-right: 12px;
    flex-shrink: 0;
    transition: background-color 0.14s ease, background-image 0.14s ease;
}}
div.st-key-nav_btn_{key} button[data-testid="stBaseButton-primary"]::before {{
    background-color: rgba(255, 255, 255, 0.15) !important;
}}
div.st-key-nav_btn_{key} button:hover::before {{
    background-color: rgba(0, 0, 0, 0.06) !important;
    background-image: url('data:image/svg+xml;base64,{dark_b64}') !important;
}}
"""
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600;6..72,700&family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {{
    --ink: {INK}; --ink-soft: {INK_SOFT}; --paper: {PAPER}; --card: {CARD};
    --line: {LINE}; --muted: {MUTED}; --brand: {BRAND}; --brand-deep: {BRAND_DEEP};
    --brand-tint: {BRAND_TINT}; --gold: {GOLD}; --gold-tint: {GOLD_TINT};
    --sage: {SAGE}; --sage-tint: {SAGE_TINT}; --navy: {BLUEPRINT_NAVY};
    --sidebar-bg: {BLUEPRINT_NAVY}; --sidebar-border: {ANCHOR_GREY_1};
    --font-display: {FONT_DISPLAY};
    --font-body: {FONT_BODY};
    --font-mono: {FONT_MONO};
}}

html, body, [class*="css"] {{ font-family: var(--font-body) !important; color: var(--ink); background: var(--paper); font-size: 15px; line-height: 1.6; }}
.stApp {{ background: radial-gradient(circle at 10% 10%, #FCFAF6 0%, #F5F1E7 100%) !important; color: var(--ink); }}

/* ── Sleek custom scrollbars ── */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: rgba(77, 77, 79, 0.15);
    border-radius: 99px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: rgba(77, 77, 79, 0.3);
}}

/* Sidebar scrollbars */
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{
    background: rgba(255, 255, 255, 0.15);
}}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {{
    background: rgba(255, 255, 255, 0.3);
}}

/* ── Typographic scale ─────────────────────────────────────────────────── */
:root {{
    /* Type ramp — fluid sizing with clamp() */
    --fs-hero:    clamp(1.5rem,  2.2vw, 1.85rem);   /* hero banner title  */
    --fs-h1:      clamp(1.35rem, 1.9vw, 1.6rem);    /* page section title */
    --fs-h2:      clamp(1.1rem,  1.5vw, 1.25rem);   /* chart group header */
    --fs-h3:      clamp(0.95rem, 1.2vw, 1.05rem);   /* chart title / sub  */
    --fs-h4:      clamp(0.88rem, 1.1vw, 0.95rem);   /* card / row title   */
    --fs-body:    0.9375rem;                          /* 15px base          */
    --fs-small:   0.8125rem;                          /* 13px captions      */
    --fs-label:   0.75rem;                            /* 12px eyebrow/tag   */
    --fs-mono:    0.8125rem;                          /* 13px mono          */

    /* Weights */
    --fw-display:  600;
    --fw-bold:     700;
    --fw-medium:   500;
    --fw-regular:  400;

    /* Leading */
    --lh-tight:   1.25;
    --lh-snug:    1.45;
    --lh-normal:  1.6;
    --lh-relaxed: 1.75;

    /* Tracking */
    --ls-tight:   -0.02em;
    --ls-normal:  -0.01em;
    --ls-wide:     0.04em;
    --ls-wider:    0.08em;
    --ls-widest:   0.14em;
}}

/* ── Heading hierarchy ────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-display) !important;
    color: var(--navy) !important;
    letter-spacing: var(--ls-tight) !important;
    line-height: var(--lh-tight) !important;
    margin-top: 0 !important;
}}
h1 {{ font-size: var(--fs-h1) !important; font-weight: var(--fw-display) !important; margin-bottom: 0.5rem !important; }}
h2 {{ font-size: var(--fs-h2) !important; font-weight: var(--fw-display) !important; margin-bottom: 0.4rem !important; }}
h3 {{ font-size: var(--fs-h3) !important; font-weight: var(--fw-medium)  !important; margin-bottom: 0.3rem !important; }}
h4 {{ font-size: var(--fs-h4) !important; font-weight: var(--fw-medium)  !important; margin-bottom: 0.25rem !important; letter-spacing: var(--ls-normal) !important; }}
h5, h6 {{ font-size: var(--fs-small) !important; font-weight: var(--fw-medium) !important; letter-spacing: var(--ls-wide) !important; text-transform: uppercase !important; }}

/* Streamlit injects markdown h4 as chart/section titles — standardise */
div[data-testid="stMarkdownContainer"] h4 {{
    font-family: var(--font-display) !important;
    font-size: var(--fs-h3) !important;
    font-weight: var(--fw-display) !important;
    color: var(--navy) !important;
    letter-spacing: var(--ls-tight) !important;
    line-height: var(--lh-snug) !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.8rem !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid rgba(77, 77, 79, 0.12) !important;
}}

/* ── Body text & prose ────────────────────────────────────────────────── */
p, li, td, th {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-body) !important;
    line-height: var(--lh-normal) !important;
    color: var(--ink) !important;
}}
.stMarkdown p {{ margin-bottom: 0.5rem !important; }}

/* Streamlit captions */
div[data-testid="stCaptionContainer"] p,
.stCaption, small {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-small) !important;
    color: var(--muted) !important;
    line-height: var(--lh-snug) !important;
}}

/* Metric values */
[data-testid="stMetricValue"] {{
    font-family: var(--font-mono) !important;
    font-size: clamp(1.4rem, 2vw, 1.8rem) !important;
    font-weight: var(--fw-display) !important;
    color: var(--navy) !important;
    letter-spacing: var(--ls-tight) !important;
}}
[data-testid="stMetricLabel"] {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-label) !important;
    font-weight: var(--fw-medium) !important;
    color: var(--muted) !important;
    letter-spacing: var(--ls-wide) !important;
    text-transform: uppercase !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-small) !important;
}}

/* Tab labels */
button[data-baseweb="tab"] {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-small) !important;
    font-weight: var(--fw-medium) !important;
    letter-spacing: var(--ls-wide) !important;
    text-transform: uppercase !important;
}}

/* Data table */
div[data-testid="stDataFrame"] th {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-label) !important;
    font-weight: var(--fw-medium) !important;
    letter-spacing: var(--ls-wide) !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}}
div[data-testid="stDataFrame"] td {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-small) !important;
}}

/* Widget labels — sidebar + main */
label, [data-testid="stWidgetLabel"] p {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-small) !important;
    font-weight: var(--fw-medium) !important;
    letter-spacing: var(--ls-normal) !important;
}}


#MainMenu, footer {{ visibility: hidden; height: 0; }}
[data-testid="stHeader"] {{
    background: transparent !important;
}}
/* Hide only Deploy and Main Menu buttons in header, leaving the collapse/reopen toggle visible */
[data-testid="stHeader"] button[data-testid="stBaseButton-header"],
[data-testid="stHeader"] button[data-testid="stMainMenuButton"] {{
    display: none !important;
}}
.block-container {{ padding-top: 0rem !important; padding-bottom: 3rem !important; max-width: 1320px; }}

/* Page hero — upgraded with an elegant glowing red radial aurora */
.voa-hero {{
    background: radial-gradient(circle at 85% 50%, rgba(227, 24, 55, 0.16) 0%, transparent 60%), linear-gradient(135deg, {BLUEPRINT_NAVY} 0%, {ANCHOR_GREY_2} 100%) !important;
    border-radius: 0 0 16px 16px; padding: 26px 32px 24px; margin: 0rem -2rem 1.8rem -2rem;
    border-bottom: 4px solid var(--brand); box-shadow: 0 8px 30px rgba(35, 31, 32, 0.15);
    position: relative;
    overflow: hidden;
}}
.voa-hero::before {{
    content: "";
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(227, 24, 55, 0.15) 0%, transparent 70%);
    pointer-events: none;
}}
.voa-hero .title {{
    font-family: var(--font-display);
    font-size: var(--fs-hero);
    font-weight: var(--fw-display);
    letter-spacing: var(--ls-tight);
    line-height: var(--lh-tight);
    color: white;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 14px;
    z-index: 1;
    position: relative;
}}
.voa-hero .subtitle {{
    font-family: var(--font-body);
    color: rgba(255, 255, 255, 0.7);
    font-size: var(--fs-small);
    font-weight: var(--fw-regular);
    line-height: var(--lh-snug);
    margin-top: 8px;
    letter-spacing: var(--ls-normal);
    z-index: 1;
    position: relative;
}}
.voa-hero .nav-chip {{
    display: inline-block; margin-top: 12px; padding: 4px 14px; border-radius: 999px;
    background: rgba(227, 24, 55, 0.2); border: 1px solid rgba(227, 24, 55, 0.5);
    color: #fff;
    font-family: var(--font-mono);
    font-size: var(--fs-label);
    letter-spacing: var(--ls-wider);
    text-transform: uppercase;
    font-weight: var(--fw-medium);
    z-index: 1;
    position: relative;
}}

/* Cool multi-ring pulse mark beside the Pulse title */
.voa-pulse-mark {{
    position: relative;
    display: inline-flex;
    width: 12px;
    height: 12px;
    flex-shrink: 0;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #ff6b81 0%, {MAHINDRA_RED} 55%, {IMPACT_RED} 100%);
    box-shadow: 0 0 10px rgba(227, 24, 55, 0.55), 0 0 22px rgba(227, 24, 55, 0.25);
    animation: voa-pulse-core 2.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}}
.voa-pulse-mark::before,
.voa-pulse-mark::after {{
    content: "";
    position: absolute;
    inset: -2px;
    border-radius: 50%;
    border: 2px solid rgba(227, 24, 55, 0.65);
    animation: voa-pulse-wave 2.2s cubic-bezier(0.22, 1, 0.36, 1) infinite;
    pointer-events: none;
}}
.voa-pulse-mark::after {{
    animation-delay: 0.7s;
    border-color: rgba(248, 180, 163, 0.55);
}}
@keyframes voa-pulse-core {{
    0%, 100% {{ transform: scale(1); filter: brightness(1); }}
    45% {{ transform: scale(1.12); filter: brightness(1.25); }}
    70% {{ transform: scale(0.96); filter: brightness(1.05); }}
}}
@keyframes voa-pulse-wave {{
    0% {{ transform: scale(0.85); opacity: 0.85; }}
    70% {{ transform: scale(2.6); opacity: 0; }}
    100% {{ transform: scale(2.6); opacity: 0; }}
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-border) !important;
}}

/* Eliminate any horizontal scroll in sidebar */
section[data-testid="stSidebar"] * {{
    max-width: 100% !important;
    box-sizing: border-box !important;
}}

/* Scale and fit the inner user content container */
section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] .stSidebarUserContent,
div[data-testid="stSidebarUserContent"] {{
    padding: 0rem 0.5rem 1.5rem 0.5rem !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}}

/* Sidebar Logo Sizing Class */
.voa-sidebar-logo {{
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    width: 200px !important;
    transition: transform 0.25s ease-in-out !important;
}}
.voa-sidebar-logo:hover {{
    transform: scale(1.03) !important;
}}

/* Force radio labels text wrapping and white color inside sidebar */
section[data-testid="stSidebar"] [data-baseweb="radio"] label,
section[data-testid="stSidebar"] [data-baseweb="radio"] label *,
section[data-testid="stSidebar"] div[data-testid="stRadio"] *,
section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
    white-space: normal !important;
    word-break: break-word !important;
    font-size: 15.5px !important;
    line-height: 1.4 !important;
    color: #F8FAFC !important;
}}

/* Reduce margin/padding of the radio widget list to prevent horizontal scroll */
section[data-testid="stSidebar"] div[data-testid="stRadio"],
section[data-testid="stSidebar"] [role="radiogroup"],
section[data-testid="stSidebar"] [data-baseweb="radio"] {{
    margin-left: 0 !important;
    margin-right: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}}

/* Main content layout (dynamic) */
section[data-testid="stMain"],
section.main {{
    flex-grow: 1 !important;
}}

/* Color only the text inside the sidebar */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: #F8FAFC !important;
}}

/* ── Sidebar: File uploader — force dark theme ── */
section[data-testid="stSidebar"] div[data-testid="stFileUploaderDropzone"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px dashed rgba(255, 255, 255, 0.25) !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}}
section[data-testid="stSidebar"] div[data-testid="stFileUploaderDropzone"]:hover {{
    background-color: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
}}

/* All text inside the dropzone — light so legible on dark bg */
section[data-testid="stSidebar"] div[data-testid="stFileUploaderDropzone"] *,
section[data-testid="stSidebar"] div[data-testid="stFileUploaderDropzone"] p,
section[data-testid="stSidebar"] div[data-testid="stFileUploaderDropzone"] span,
section[data-testid="stSidebar"] div[data-testid="stFileUploaderDropzone"] small {{
    color: #C8C4BC !important;
}}

/* Upload button inside sidebar dropzone */
section[data-testid="stSidebar"] div[data-testid="stFileUploaderDropzone"] button,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {{
    background-color: rgba(255, 255, 255, 0.10) !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255, 255, 255, 0.28) !important;
    border-radius: 6px !important;
}}
section[data-testid="stSidebar"] div[data-testid="stFileUploaderDropzone"] button:hover {{
    background-color: rgba(227, 24, 55, 0.22) !important;
    border-color: rgba(227, 24, 55, 0.5) !important;
}}

/* ── Sidebar: Expander — force dark theme ── */
section[data-testid="stSidebar"] div[data-testid="stExpander"],
section[data-testid="stSidebar"] [data-testid="stExpander"] {{
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
}}
section[data-testid="stSidebar"] div[data-testid="stExpander"] summary,
section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
    background-color: rgba(255, 255, 255, 0.06) !important;
    border-radius: 8px !important;
    color: #F8FAFC !important;
    min-height: max(2.75rem, 3.45vw) !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 14px !important;
    box-sizing: border-box !important;
}}
section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {{
    background-color: rgba(255, 255, 255, 0.1) !important;
}}
section[data-testid="stSidebar"] div[data-testid="stExpander"] summary span,
section[data-testid="stSidebar"] div[data-testid="stExpander"] summary p,
section[data-testid="stSidebar"] div[data-testid="stExpander"] summary svg {{
    color: #F8FAFC !important;
    fill: #F8FAFC !important;
}}

/* Style sidebar collapse toggle button (inside sidebar when expanded) */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"],
section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button {{
    display: inline-flex !important;
    visibility: visible !important;
    background-color: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
    width: 32px !important;
    height: 32px !important;
    align-items: center !important;
    justify-content: center !important;
    opacity: 1 !important;
    transition: background-color 0.15s ease !important;
    position: static !important;
}}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"]:hover,
section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button:hover {{
    background-color: rgba(255, 255, 255, 0.18) !important;
}}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] span,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] div[data-testid="stSidebarCollapseButton"] button span {{
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}}

/* Hide expand/reopen control while sidebar is open */
body:has(section[data-testid="stSidebar"][aria-expanded="true"]) div[data-testid="collapsedControl"],
body:has(section[data-testid="stSidebar"][aria-expanded="true"]) div[data-testid="stSidebarCollapsedControl"],
body:has(section[data-testid="stSidebar"][aria-expanded="true"]) button[data-testid="stExpandSidebarButton"] {{
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    opacity: 0 !important;
}}

/* Expand/reopen control — only when sidebar is collapsed (light page bg) */
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="collapsedControl"],
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="stSidebarCollapsedControl"],
body.voa-sidebar-collapsed div[data-testid="collapsedControl"],
body.voa-sidebar-collapsed div[data-testid="stSidebarCollapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
    pointer-events: auto !important;
}}
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="collapsedControl"] button,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="stSidebarCollapsedControl"] button,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) button[data-testid="stExpandSidebarButton"],
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stHeader"] button[data-testid="stExpandSidebarButton"],
body.voa-sidebar-collapsed div[data-testid="collapsedControl"] button,
body.voa-sidebar-collapsed div[data-testid="stSidebarCollapsedControl"] button,
body.voa-sidebar-collapsed button[data-testid="stExpandSidebarButton"],
body.voa-sidebar-collapsed [data-testid="stHeader"] button[data-testid="stExpandSidebarButton"] {{
    display: inline-flex !important;
    visibility: visible !important;
    background-color: var(--navy) !important;  /* Charcoal black button in collapsed mode */
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
    width: 32px !important;
    height: 32px !important;
    align-items: center !important;
    justify-content: center !important;
    opacity: 1 !important;
    box-shadow: 0 2px 10px rgba(35, 31, 32, 0.35) !important;
    transition: background-color 0.15s ease !important;
    position: absolute !important;
    left: 12px !important;
    top: 12px !important;
    z-index: 999999 !important;
    pointer-events: auto !important;
}}
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="collapsedControl"] button:hover,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="stSidebarCollapsedControl"] button:hover,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) button[data-testid="stExpandSidebarButton"]:hover,
body.voa-sidebar-collapsed div[data-testid="collapsedControl"] button:hover,
body.voa-sidebar-collapsed div[data-testid="stSidebarCollapsedControl"] button:hover,
body.voa-sidebar-collapsed button[data-testid="stExpandSidebarButton"]:hover {{
    background-color: {MAHINDRA_RED} !important;
}}
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="collapsedControl"] button span,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="collapsedControl"] button [data-testid="stIconMaterial"],
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="collapsedControl"] button svg,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="stSidebarCollapsedControl"] button span,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) div[data-testid="stSidebarCollapsedControl"] button svg,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) button[data-testid="stExpandSidebarButton"] span,
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
body:has(section[data-testid="stSidebar"][aria-expanded="false"]) button[data-testid="stExpandSidebarButton"] svg,
body.voa-sidebar-collapsed div[data-testid="collapsedControl"] button span,
body.voa-sidebar-collapsed div[data-testid="collapsedControl"] button [data-testid="stIconMaterial"],
body.voa-sidebar-collapsed div[data-testid="collapsedControl"] button svg,
body.voa-sidebar-collapsed div[data-testid="stSidebarCollapsedControl"] button span,
body.voa-sidebar-collapsed div[data-testid="stSidebarCollapsedControl"] button svg,
body.voa-sidebar-collapsed button[data-testid="stExpandSidebarButton"] span,
body.voa-sidebar-collapsed button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
body.voa-sidebar-collapsed button[data-testid="stExpandSidebarButton"] svg {{
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
}}

/* When sidebar is open, force-hide any floating expand overlays */
body.voa-sidebar-expanded div[data-testid="collapsedControl"],
body.voa-sidebar-expanded div[data-testid="stSidebarCollapsedControl"],
body.voa-sidebar-expanded button[data-testid="stExpandSidebarButton"] {{
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    opacity: 0 !important;
}}

section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.12); }}
section[data-testid="stSidebar"] [data-baseweb="radio"] label {{
    padding: 8px 10px; border-radius: 6px; transition: background 0.15s ease;
}}
section[data-testid="stSidebar"] [data-baseweb="radio"] label:hover {{
    background: rgba(255,255,255,0.06);
}}
section[data-testid="stSidebar"] [data-baseweb="radio"] input:checked ~ div {{
    background: rgba(227, 24, 55, 0.22) !important;
}}

/* ── Sidebar inputs: premium dark glass styling with white text ── */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-testid="stTextInput"] [data-baseweb="input"] > div,
section[data-testid="stSidebar"] div[data-testid="stDateInput"] [data-baseweb="input"] > div,
section[data-testid="stSidebar"] div[data-testid="stNumberInput"] [data-baseweb="input"] > div {{
    min-height: 34px !important;
    padding-top: 2px !important;
    padding-bottom: 2px !important;
    padding-left: 10px !important;
    background-color: rgba(24, 24, 26, 0.4) !important; /* Matte charcoal dark glass background */
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    transition: all 0.2s ease-in-out !important;
}}

section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover,
section[data-testid="stSidebar"] div[data-testid="stTextInput"] [data-baseweb="input"] > div:hover,
section[data-testid="stSidebar"] div[data-testid="stDateInput"] [data-baseweb="input"] > div:hover {{
    border-color: rgba(255, 255, 255, 0.22) !important;
    background-color: rgba(255, 255, 255, 0.05) !important;
}}

section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within,
section[data-testid="stSidebar"] div[data-testid="stTextInput"] [data-baseweb="input"] > div:focus-within {{
    border-color: {MAHINDRA_RED} !important;
    box-shadow: 0 0 0 2px rgba(227, 24, 55, 0.2) !important;
}}

/* Sidebar input text, value and placeholder text — clean white */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] div,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="value"],
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] div,
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] span {{
    background-color: transparent !important;
    color: #FFFFFF !important;
    font-size: 13.5px !important;
}}

/* Sidebar actual <input> and <textarea> elements */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {{
    background-color: transparent !important;
    color: #FFFFFF !important;
    font-size: 13.5px !important;
}}

/* Sidebar placeholder text — soft light-gray */
section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder {{
    color: rgba(255, 255, 255, 0.4) !important;
    opacity: 1 !important;
}}

/* Sidebar select placeholder / no-value state */
section[data-testid="stSidebar"] [data-baseweb="select"] [aria-placeholder],
section[data-testid="stSidebar"] [data-baseweb="select"] [data-value=""],
section[data-testid="stSidebar"] [data-baseweb="select"] > div > div:first-child {{
    color: rgba(255, 255, 255, 0.45) !important;
}}

/* Sidebar multiselect tag chips */
section[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background-color: rgba(255, 255, 255, 0.12) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 4px !important;
}}
section[data-testid="stSidebar"] [data-baseweb="tag"] span {{
    color: #FFFFFF !important;
}}

/* Sidebar select caret/arrow icon — white for legibility */
section[data-testid="stSidebar"] [data-baseweb="select"] svg {{
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
}}

.voa-eyebrow {{
    font-family: var(--font-mono);
    font-size: var(--fs-label);
    letter-spacing: var(--ls-widest);
    text-transform: uppercase;
    font-weight: var(--fw-display);
    color: var(--brand);
    margin-bottom: 6px;
    line-height: var(--lh-snug);
}}
.voa-eyebrow.on-dark {{ color: {CLARITY_RED}; }}

/* KPI cards — Upgraded with glassmorphism backdrop filters and double border styling */
.voa-kpi {{
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(12px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    border-radius: 14px !important;
    padding: 20px 22px !important;
    height: 100%; 
    box-shadow: 0 8px 32px 0 rgba(77, 77, 79, 0.04), inset 0 0 0 1px rgba(255, 255, 255, 0.6) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}}
.voa-kpi:hover {{ 
    box-shadow: 0 16px 36px 0 rgba(227, 24, 55, 0.08), 0 4px 12px 0 rgba(0, 0, 0, 0.02) !important;
    transform: translateY(-4px) scale(1.01) !important;
    border-color: rgba(227, 24, 55, 0.18) !important;
}}
.voa-kpi .label {{
    font-family: var(--font-body);
    font-size: var(--fs-label);
    letter-spacing: var(--ls-wide);
    text-transform: uppercase;
    color: var(--muted);
    font-weight: var(--fw-medium);
}}
.voa-kpi .value {{
    font-family: var(--font-mono);
    font-size: clamp(1.4rem, 2.2vw, 1.9rem);
    font-weight: var(--fw-bold);
    color: var(--navy);
    line-height: var(--lh-tight);
    margin-top: 6px;
    letter-spacing: var(--ls-tight);
}}
.voa-kpi .sub {{
    font-family: var(--font-body);
    font-size: var(--fs-small);
    color: var(--muted);
    margin-top: 6px;
    line-height: var(--lh-snug);
}}
.voa-kpi.accent-brand {{ border-left: 5px solid var(--brand) !important; }}
.voa-kpi.accent-gold  {{ border-left: 5px solid var(--gold) !important;  }}
.voa-kpi.accent-sage  {{ border-left: 5px solid var(--sage) !important;  }}
.voa-kpi.accent-ink   {{ border-left: 5px solid var(--navy) !important;  }}

.voa-callout {{
    background: var(--brand-tint); border: 1px solid rgba(227, 24, 55, 0.18); border-left: 4px solid var(--brand);
    border-radius: 12px; padding: 16px 18px; margin-bottom: 12px;
    font-family: var(--font-body);
    font-size: var(--fs-body);
    line-height: var(--lh-relaxed);
    color: var(--ink);
}}
.voa-callout.tone-gold {{ background: {GOLD_TINT}; border-color: rgba(181, 131, 46, 0.25); border-left-color: var(--gold); }}
.voa-callout.tone-sage {{ background: {SAGE_TINT}; border-color: rgba(45, 106, 79, 0.2); border-left-color: var(--sage); }}

.voa-pill {{
    display: inline-block; padding: 3px 10px; border-radius: 100px;
    font-family: var(--font-body);
    font-size: var(--fs-label);
    font-weight: var(--fw-display);
    letter-spacing: var(--ls-wide);
    margin-right: 4px;
    text-transform: uppercase;
}}
.voa-pill.sev-High {{ background: var(--brand-tint); color: var(--brand-deep); }}
.voa-pill.sev-Moderate {{ background: var(--gold-tint); color: #7A5A22; }}
.voa-pill.sev-Low {{ background: var(--sage-tint); color: #275038; }}
.voa-pill.st-Open {{ background: var(--brand-tint); color: var(--brand-deep); }}
.voa-pill.st-In-progress {{ background: var(--gold-tint); color: #7A5A22; }}
.voa-pill.st-Closed {{ background: var(--sage-tint); color: #275038; }}

/* Cards — Upgraded with glassmorphism backdrop filters and double border styling */
.voa-card {{
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(12px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    border-radius: 14px !important;
    padding: 20px 22px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 8px 32px 0 rgba(77, 77, 79, 0.03), inset 0 0 0 1px rgba(255, 255, 255, 0.5) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}}
.voa-card:hover {{
    box-shadow: 0 12px 28px 0 rgba(227, 24, 55, 0.05), 0 4px 10px 0 rgba(0, 0, 0, 0.01) !important;
    transform: translateY(-3px) !important;
    border-color: rgba(227, 24, 55, 0.12) !important;
}}
.voa-card .title {{
    font-family: var(--font-display);
    font-weight: var(--fw-display);
    font-size: var(--fs-h4);
    margin-bottom: 6px;
    color: var(--navy) !important;
    letter-spacing: var(--ls-normal);
    line-height: var(--lh-snug);
}}
.voa-card .meta {{
    font-family: var(--font-body);
    font-size: var(--fs-small);
    color: var(--muted);
    margin-top: 8px;
    line-height: var(--lh-snug);
}}
.voa-quote {{
    font-family: var(--font-body);
    font-style: italic;
    color: var(--ink-soft);
    font-size: var(--fs-small);
    line-height: var(--lh-relaxed);
    border-left: 3px solid var(--brand);
    padding-left: 12px;
    margin-top: 8px;
}}

.voa-filter-bar {{
    display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 1.2rem;
    padding: 12px 16px; background: {WHITE}; border: 1px solid var(--line); border-radius: 8px;
    box-shadow: 0 2px 8px rgba(10, 8, 56, 0.02);
}}
.voa-filter-chip {{
    display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 12px;
    background: {CLARITY_GREY_1}; border: 1px solid var(--line); color: var(--ink-soft);
    font-weight: 500;
}}

.stButton>button, .stDownloadButton>button {{
    background: var(--navy) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.15s ease !important;
}}
.stButton>button *, .stDownloadButton>button * {{
    color: #FFFFFF !important;
}}
.stButton>button:hover, .stDownloadButton>button:hover {{ 
    background: var(--brand) !important; 
    color: #FFFFFF !important; 
    box-shadow: 0 4px 12px rgba(227, 24, 55, 0.2) !important;
    transform: translateY(-1px) !important;
}}
.stButton>button:hover *, .stDownloadButton>button:hover * {{
    color: #FFFFFF !important;
}}
/* Main content area secondary buttons */
div[data-testid="stAppViewContainer"] [data-testid="stMain"] .stButton>button[kind="secondary"] {{
    background: transparent !important;
    color: var(--navy) !important;
    border: 1px solid var(--line) !important;
}}
div[data-testid="stAppViewContainer"] [data-testid="stMain"] .stButton>button[kind="secondary"] * {{
    color: var(--navy) !important;
}}
div[data-testid="stAppViewContainer"] [data-testid="stMain"] .stButton>button[kind="secondary"]:hover {{
    background: rgba(77, 77, 79, 0.04) !important;
    border-color: var(--navy) !important;
    box-shadow: none !important;
    transform: none !important;
}}
div[data-testid="stAppViewContainer"] [data-testid="stMain"] .stButton>button[kind="secondary"]:hover * {{
    color: var(--navy) !important;
}}

/* Sidebar area secondary buttons (including inactive nav buttons) */
section[data-testid="stSidebar"] .stButton>button[kind="secondary"] {{
    background: transparent !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}}
section[data-testid="stSidebar"] .stButton>button[kind="secondary"] * {{
    color: #FFFFFF !important;
}}
section[data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover {{
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
    box-shadow: none !important;
    transform: none !important;
}}
section[data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover * {{
    color: #FFFFFF !important;
}}

/* ── Autocomplete suggestion chips in sidebar ── */
section[data-testid="stSidebar"] div[data-testid^="stButton-sugg_"] > button,
section[data-testid="stSidebar"] div[data-testid*="sugg_"] > button {{
    background: rgba(255,255,255,0.06) !important;
    color: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 6px !important;
    font-size: 12.5px !important;
    font-weight: 400 !important;
    letter-spacing: 0.01em !important;
    padding: 6px 12px !important;
    min-height: 0 !important;
    height: auto !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: all 0.15s ease !important;
}}
section[data-testid="stSidebar"] div[data-testid^="stButton-sugg_"] > button:hover,
section[data-testid="stSidebar"] div[data-testid*="sugg_"] > button:hover {{
    background: rgba(227,24,55,0.2) !important;
    border-color: rgba(227,24,55,0.4) !important;
    color: #FFFFFF !important;
    transform: translateX(2px) !important;
}}

/* Remove the default stButton margin so tiles are tight */
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"],
section[data-testid="stSidebar"] div[data-testid^="stButton-nav_btn_"] {{
    margin-bottom: 0 !important;
}}

button[data-baseweb="tab"] {{ font-family: var(--font-body); font-weight: 600; color: var(--muted); }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--brand) !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: var(--brand) !important; }}

[data-testid="stMetricValue"] {{ font-family: var(--font-mono); color: var(--navy); }}
hr {{ border-color: var(--line); }}

/* ── Sliders ──────────────────────────────────────────────────────────── */
div[data-testid="stSlider"] label,
div[data-testid="stSlider"] p {{
    color: var(--ink-soft) !important;
    font-weight: 600 !important;
}}
div[data-testid="stSlider"] [role="slider"] {{
    background-color: var(--brand) !important;
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 2px rgba(227, 24, 55, 0.2) !important;
    transition: transform 0.15s ease !important;
}}
div[data-testid="stSlider"] [role="slider"]:hover {{
    transform: scale(1.2) !important;
}}
div[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div:first-child {{
    background: var(--line) !important;
}}
div[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div:nth-child(2) {{
    background: var(--brand) !important;
}}
div[data-testid="stSlider"] [data-baseweb="slider"] div {{
    color: var(--ink-soft) !important;
}}

/* ── Text & Widget Readability (Forces light theme contrast in main area) ── */
div[data-testid="stAppViewContainer"] [data-testid="stMain"] [data-baseweb="input"] > div,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] [data-baseweb="select"] > div,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] [data-baseweb="base-input"] > div,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stTextInput"] input,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stTextArea"] textarea,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stSelectbox"] select,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stDateInput"] input {{
    background-color: #FFFFFF !important;
    color: #231F20 !important;
    border: 1px solid #E5DFD3 !important;
    border-radius: 8px !important;
    transition: border-color 0.2s ease !important;
}}
div[data-testid="stAppViewContainer"] [data-testid="stMain"] [data-baseweb="input"] > div:focus-within,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] [data-baseweb="select"] > div:focus-within {{
    border-color: var(--brand) !important;
}}

/* For selectbox and multiselect selection containers */
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stSelectbox"] [data-baseweb="select"] div,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stSelectbox"] [data-baseweb="select"] span,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stSelectbox"] [role="button"],
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stSelectbox"] [role="combobox"],
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stMultiSelect"] [data-baseweb="select"] div,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stMultiSelect"] [data-baseweb="select"] span {{
    background-color: #FFFFFF !important;
    color: #231F20 !important;
}}

div[data-testid="stAppViewContainer"] [data-testid="stMain"] input,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] textarea,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] select {{
    color: #231F20 !important;
}}

/* Dropdown option menus — solid cream rows so options are readable without hover */
[data-baseweb="popover"]:has([role="listbox"]),
[data-baseweb="popover"]:has([data-baseweb="menu"]),
[data-baseweb="popover"]:has([role="listbox"]) > div,
[data-baseweb="popover"]:has([role="listbox"]) > div > div,
[data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"],
[role="listbox"] {{
    background: #EBE5DA !important;
    background-color: #EBE5DA !important;
    color: #231F20 !important;
    border-color: rgba(74, 69, 61, 0.35) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 18px rgba(10, 8, 56, 0.15) !important;
}}

li[role="option"],
[role="option"],
[data-baseweb="menu"] li,
[role="listbox"] > li,
[role="listbox"] li {{
    background: #EBE5DA !important;
    background-color: #EBE5DA !important;
    color: #231F20 !important;
}}

li[role="option"] *,
[role="option"] *,
[data-baseweb="menu"] li *,
[role="listbox"] li * {{
    color: #231F20 !important;
    background: transparent !important;
    background-color: transparent !important;
    -webkit-text-fill-color: #231F20 !important;
}}

li[role="option"]:hover,
[role="option"]:hover,
li[role="option"][aria-selected="true"],
[role="option"][aria-selected="true"],
[data-baseweb="menu"] li:hover,
[role="listbox"] li:hover {{
    background: #F8F4EC !important;
    background-color: #F8F4EC !important;
    color: #231F20 !important;
}}

li[role="option"]:hover *,
[role="option"]:hover *,
li[role="option"][aria-selected="true"] *,
[role="option"][aria-selected="true"] * {{
    color: #231F20 !important;
    -webkit-text-fill-color: #231F20 !important;
}}

section[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background-color: rgba(255, 255, 255, 0.12) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
}}

section[data-testid="stSidebar"] [data-baseweb="tag"] span {{
    color: #FFFFFF !important;
}}

/* Expanders */
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stExpander"] {{
    background-color: #FFFFFF !important;
    border: 1px solid #E5DFD3 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 10px rgba(35, 31, 32, 0.02) !important;
}}
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stExpander"] summary {{
    background-color: #FFFFFF !important;
    color: #231F20 !important;
    border-radius: 12px !important;
}}
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stExpander"] summary:hover {{
    background-color: #F6F2EA !important;
}}
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stExpander"] summary span,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stExpander"] summary p {{
    color: #231F20 !important;
}}

/* Radio label & radio options in main content */
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stRadio"] label,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stRadio"] p,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] div[data-testid="stRadio"] span {{
    color: #231F20 !important;
}}

/* Standard text labels above form fields */
div[data-testid="stAppViewContainer"] [data-testid="stMain"] label,
div[data-testid="stAppViewContainer"] [data-testid="stMain"] [data-testid="stWidgetLabel"] p {{
    color: #4A453D !important;
    font-weight: 600 !important;
}}

/* ── Hurry Panel (Executive snap summary) — Upgraded with glassmorphism and custom brand left-border ── */
.voa-hurry-panel {{
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(12px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    border-left: 5px solid var(--brand) !important; /* Rich red accent left-border */
    border-radius: 14px !important;
    padding: 20px 24px !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 8px 32px 0 rgba(77, 77, 79, 0.05), inset 0 0 0 1px rgba(255, 255, 255, 0.5) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}}
.voa-hurry-panel:hover {{
    box-shadow: 0 16px 36px 0 rgba(227, 24, 55, 0.08), 0 4px 12px 0 rgba(0, 0, 0, 0.02) !important;
    transform: translateY(-2px) !important;
    border-color: rgba(227, 24, 55, 0.12) !important;
    border-left-color: var(--brand) !important;
}}
.voa-hurry-panel .hurry-title {{
    font-family: var(--font-display) !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: var(--navy) !important;
    margin-bottom: 12px !important;
    letter-spacing: -0.01em !important;
}}
.voa-hurry-panel ul {{
    margin: 0 !important;
    padding-left: 20px !important;
    font-size: 14px !important;
    color: var(--ink) !important;
    font-family: var(--font-body) !important;
    list-style-type: square !important;
}}
.voa-hurry-panel li {{
    margin-bottom: 8px !important;
    line-height: 1.6 !important;
}}
.voa-hurry-panel li::marker {{
    color: var(--brand) !important;
}}

/* ── Active Nav Buttons — Upgraded with glowing red gradient and clean white border-left ── */
div[class*="st-key-nav_btn_"] button[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, {MAHINDRA_RED} 0%, #B8142C 100%) !important;
    color: #FFFFFF !important;
    border-color: {MAHINDRA_RED} !important;
    border-left: 4px solid #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(227, 24, 55, 0.3) !important;
}}
div[class*="st-key-nav_btn_"] button[data-testid="stBaseButton-primary"]:hover {{
    background: linear-gradient(135deg, {MAHINDRA_RED} 0%, #B8142C 100%) !important;
    color: #FFFFFF !important;
    opacity: 0.95 !important;
    box-shadow: 0 6px 18px rgba(227, 24, 55, 0.4) !important;
}}

/* Nav button left-border indicator for hover states */
div[class*="st-key-nav_btn_"] button::after {{
    content: "";
    position: absolute;
    left: 0;
    top: 20%;
    height: 60%;
    width: 3px;
    background-color: var(--brand);
    border-radius: 0 4px 4px 0;
    opacity: 0;
    transform: scaleY(0.3);
    transition: transform 0.2s ease, opacity 0.2s ease;
}}
div[class*="st-key-nav_btn_"] button[data-testid="stBaseButton-primary"]::after {{
    display: none !important; /* Hide after indicator because active button uses a solid border-left */
}}

/* Print Button styling */
.voa-print-btn {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: rgba(255, 255, 255, 0.12) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 999px !important;
    padding: 6px 14px !important;
    color: #FFFFFF !important;
    font-family: var(--font-body) !important;
    font-size: var(--fs-label) !important;
    font-weight: var(--fw-medium) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    z-index: 10 !important;
    position: relative !important;
}}
.voa-print-btn:hover {{
    background: var(--brand) !important;
    border-color: var(--brand) !important;
    box-shadow: 0 4px 12px rgba(227, 24, 55, 0.3) !important;
}}

/* Print CSS overrides */
@media print {{
    * {{
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}
    div[data-testid="stAppViewContainer"],
    div[data-testid="stAppViewContainer"] *,
    [data-testid="stMain"],
    .stApp {{
        opacity: 1 !important;
        filter: none !important;
    }}
    section[data-testid="stSidebar"],
    .voa-print-btn,
    [data-testid="stHeader"],
    div[data-testid="collapsedControl"],
    div[data-testid="stSidebarCollapsedControl"],
    button[data-testid="stExpandSidebarButton"] {{
        display: none !important;
        visibility: hidden !important;
    }}
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }}
    .stApp {{
        background: none !important;
        background-color: #FFFFFF !important;
    }}
    .voa-hero {{
        background: rgba(77, 77, 79, 0.06) !important;
        border: 1px solid rgba(77, 77, 79, 0.12) !important;
        box-shadow: none !important;
        border-radius: 8px !important;
        margin: 0 0 1.2rem 0 !important;
        padding: 20px !important;
    }}
    .voa-hero .title {{
        color: var(--navy) !important;
    }}
    .voa-hero .subtitle {{
        color: var(--ink) !important;
    }}
    .voa-card, .voa-kpi, .voa-hurry-panel {{
        page-break-inside: avoid !important;
        background: #FFFFFF !important;
        box-shadow: none !important;
        border: 1px solid rgba(77, 77, 79, 0.15) !important;
    }}
}}

{icons_css}
</style>
<script>
(function() {{
  function applyDarkSidebarStyles() {{
    var sidebar = document.querySelector('section[data-testid="stSidebar"]');
    if (!sidebar) return;

    /* ── File uploader dropzones ── */
    var dropzones = sidebar.querySelectorAll('[data-testid="stFileUploaderDropzone"]');
    dropzones.forEach(function(dz) {{
      dz.style.setProperty('background-color', 'rgba(255, 255, 255, 0.05)', 'important');
      dz.style.setProperty('border', '1px dashed rgba(255, 255, 255, 0.25)', 'important');
      dz.style.setProperty('border-radius', '8px', 'important');

      /* All descendant text nodes */
      dz.querySelectorAll('p, span, small, label').forEach(function(el) {{
        el.style.setProperty('color', '#C8C4BC', 'important');
      }});

      /* Upload button(s) */
      dz.querySelectorAll('button').forEach(function(btn) {{
        btn.style.setProperty('background-color', 'rgba(255, 255, 255, 0.10)', 'important');
        btn.style.setProperty('color', '#F8FAFC', 'important');
        btn.style.setProperty('border', '1px solid rgba(255, 255, 255, 0.30)', 'important');
        btn.style.setProperty('border-radius', '6px', 'important');
      }});

      /* The inner <section> wrapper Streamlit wraps around dropzone content */
      dz.querySelectorAll('section').forEach(function(s) {{
        s.style.setProperty('background-color', 'transparent', 'important');
      }});
    }});

    /* ── Expander containers (details/summary) ── */
    var expanders = sidebar.querySelectorAll('[data-testid="stExpander"]');
    expanders.forEach(function(exp) {{
      exp.style.setProperty('background-color', 'rgba(255, 255, 255, 0.04)', 'important');
      exp.style.setProperty('border', '1px solid rgba(255, 255, 255, 0.10)', 'important');
      exp.style.setProperty('border-radius', '8px', 'important');

      /* details element */
      exp.querySelectorAll('details').forEach(function(d) {{
        d.style.setProperty('background-color', 'transparent', 'important');
      }});

      /* summary header */
      exp.querySelectorAll('summary').forEach(function(s) {{
        s.style.setProperty('background-color', 'rgba(255, 255, 255, 0.06)', 'important');
        s.style.setProperty('border-radius', '8px', 'important');
        s.style.setProperty('color', '#F8FAFC', 'important');
        /* Expander chevron icon */
        s.querySelectorAll('svg').forEach(function(svg) {{
          svg.style.setProperty('fill', '#F8FAFC', 'important');
          svg.style.setProperty('color', '#F8FAFC', 'important');
        }});
        s.querySelectorAll('p, span').forEach(function(el) {{
          el.style.setProperty('color', '#F8FAFC', 'important');
        }});
      }});
    }});
  }}

  function paintCream(el) {{
    if (!el || !el.style) return;
    el.style.setProperty('background', '#EBE5DA', 'important');
    el.style.setProperty('background-color', '#EBE5DA', 'important');
    el.style.setProperty('color', '#231F20', 'important');
  }}

  function paintInk(el) {{
    if (!el || !el.style) return;
    el.style.setProperty('color', '#231F20', 'important');
    el.style.setProperty('-webkit-text-fill-color', '#231F20', 'important');
  }}

  function forceDropdownContrast() {{
    var menus = document.querySelectorAll('[role="listbox"], [data-baseweb="menu"]');
    menus.forEach(function(menu) {{
      paintCream(menu);
      var node = menu.parentElement;
      var depth = 0;
      while (node && depth < 4) {{
        paintCream(node);
        if (node.getAttribute && node.getAttribute('data-baseweb') === 'popover') break;
        node = node.parentElement;
        depth += 1;
      }}
      menu.querySelectorAll('[role="option"], li').forEach(function(opt) {{
        paintCream(opt);
        opt.querySelectorAll('*').forEach(paintInk);
      }});
    }});
  }}

  function syncSidebarExpandControl() {{
    var sidebar = document.querySelector('section[data-testid="stSidebar"]');
    var collapsed = false;
    if (!sidebar) {{
      collapsed = true;
    }} else {{
      var aria = sidebar.getAttribute('aria-expanded');
      if (aria === 'false') {{
        collapsed = true;
      }} else if (aria === 'true') {{
        collapsed = false;
      }} else {{
        var rect = sidebar.getBoundingClientRect();
        var style = window.getComputedStyle(sidebar);
        collapsed = rect.width < 40 || style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity || '1') === 0;
      }}
    }}
    document.body.classList.toggle('voa-sidebar-collapsed', collapsed);
    document.body.classList.toggle('voa-sidebar-expanded', !collapsed);

    var expandNodes = document.querySelectorAll(
      'div[data-testid="collapsedControl"], div[data-testid="stSidebarCollapsedControl"], button[data-testid="stExpandSidebarButton"]'
    );
    expandNodes.forEach(function(el) {{
      /* Never show floating expand while sidebar is open */
      if (!collapsed) {{
        el.style.setProperty('display', 'none', 'important');
        el.style.setProperty('visibility', 'hidden', 'important');
        el.style.setProperty('pointer-events', 'none', 'important');
        el.style.setProperty('opacity', '0', 'important');
      }} else {{
        el.style.removeProperty('display');
        el.style.removeProperty('visibility');
        el.style.removeProperty('pointer-events');
        el.style.removeProperty('opacity');
      }}
    }});
  }}

  function runUiFixes() {{
    applyDarkSidebarStyles();
    forceDropdownContrast();
    syncSidebarExpandControl();
  }}

  /* Run once on load */
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', runUiFixes);
  }} else {{
    runUiFixes();
  }}

  /* Run again after every DOM mutation (Streamlit re-renders / dropdown open) */
  var observer = new MutationObserver(function(mutations) {{
    var childChanged = false;
    var ariaChanged = false;
    mutations.forEach(function(m) {{
      if (m.type === 'childList' && m.addedNodes.length > 0) childChanged = true;
      if (m.type === 'attributes') ariaChanged = true;
    }});
    if (childChanged) runUiFixes();
    else if (ariaChanged) syncSidebarExpandControl();
  }});

  observer.observe(document.body, {{ childList: true, subtree: true, attributes: true, attributeFilter: ['aria-expanded', 'style', 'class'] }});
  setInterval(syncSidebarExpandControl, 500);

}})();
</script>
"""


def page_header(title: str, subtitle: str, section: str) -> str:
    pulse_mark = '<span class="voa-pulse-mark" aria-hidden="true"></span>' if title.strip().lower() == "pulse" else ""
    return f"""
<div class="voa-hero">
  <div class="title">{pulse_mark}{title}</div>
  <div class="subtitle">{subtitle}</div>
  <span class="nav-chip">{section}</span>
</div>
"""


def pill(text: str, kind: str) -> str:
    css_kind = kind.replace(" ", "-")
    return f'<span class="voa-pill {css_kind}">{text}</span>'

