import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend'))

import streamlit as st
import pandas as pd
import sqlite3
import json
from config.settings import DB_ETICARET
from i18n.translations import t, get_current_language, set_language
from database.chat_db import init_db, create_session, get_session, add_message, update_session_title, get_sessions, delete_session, get_messages
from llm_manager import llm_sorgu_zinciri_kur

st.set_page_config(
    page_title=t("app_title"),
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

THEMES = {
    "light": {
        "bg": "#fdfdf8",
        "ink": "#3d3a2a",
        "terra": "#cb785c",
        "terra_hover": "#b06a52",
        "sage": "#059669",
        "sand": "#fbbf24",
        "surface": "#ffffff",
        "muted": "rgba(61, 58, 42, 0.62)",
        "border": "#d3d2ca",
        "code_bg": "#ecebe4",
        "code_text": "#3d3a2a",
        "sql_bg": "#2b2d42",
        "sql_text": "#f4f1de",
        "shadow": "rgba(61, 58, 42, 0.12)",
        "sidebar_bg": "#f0f0ec",
        "sidebar_surface": "#ecebe3",
        "sidebar_border": "#d3d2ca",
        "sidebar_button_bg": "transparent",
        "sidebar_button_hover_bg": "rgba(203, 120, 92, 0.15)",
        "sidebar_button_border": "rgba(61, 58, 42, 0.15)",
        "sidebar_button_text": "#3d3a2a",
        "sidebar_heading": "#3d3a2a",
        "welcome_shadow": "rgba(61, 58, 42, 0.12)",
        "stats_border": "rgba(61, 58, 42, 0.08)",
        "stats_shadow": "rgba(61, 58, 42, 0.08)",
        "stats_hover_shadow": "rgba(61, 58, 42, 0.14)",
        "chat_input_border": "rgba(61, 58, 42, 0.18)",
        "chat_input_placeholder": "rgba(61, 58, 42, 0.55)",
        "dataframe_bg": "#ffffff",
        "dataframe_text": "#3d3a2a",
        "dataframe_header_bg": "#f0f0ec",
        "dataframe_header_text": "#3d3a2a",
        "dataframe_border": "#d3d2ca",
        "dataframe_row_alt": "#f6f5ef",
        "dataframe_hover": "rgba(203, 120, 92, 0.12)",
    },
    "dark": {
        "bg": "#0d1117",
        "ink": "#e6edf3",
        "terra": "#238636",
        "terra_hover": "#2ea043",
        "sage": "#58a6ff",
        "sand": "#d29922",
        "surface": "#161b22",
        "muted": "#8b949e",
        "border": "#30363d",
        "code_bg": "#161b22",
        "code_text": "#e6edf3",
        "sql_bg": "#161b22",
        "sql_text": "#7ee787",
        "shadow": "rgba(1, 4, 9, 0.6)",
        "sidebar_bg": "#0d1117",
        "sidebar_surface": "#161b22",
        "sidebar_border": "#30363d",
        "sidebar_button_bg": "transparent",
        "sidebar_button_hover_bg": "rgba(177, 186, 196, 0.12)",
        "sidebar_button_border": "rgba(240, 246, 252, 0.15)",
        "sidebar_button_text": "#e6edf3",
        "sidebar_heading": "#e6edf3",
        "welcome_shadow": "rgba(1, 4, 9, 0.6)",
        "stats_border": "rgba(240, 246, 252, 0.1)",
        "stats_shadow": "rgba(1, 4, 9, 0.6)",
        "stats_hover_shadow": "rgba(1, 4, 9, 0.7)",
        "chat_input_border": "rgba(240, 246, 252, 0.15)",
        "chat_input_placeholder": "#6e7681",
        "dataframe_bg": "#ffffff",
        "dataframe_text": "#1f2328",
        "dataframe_header_bg": "#eaeef2",
        "dataframe_header_text": "#1f2328",
        "dataframe_border": "#d0d7de",
        "dataframe_row_alt": "#f6f8fa",
        "dataframe_hover": "rgba(31, 35, 40, 0.06)",
    },
}

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
init_db()
with st.sidebar:
    st.markdown(f"**{t('chat_history')}**")
    
    sessions = get_sessions()
    
    if st.button(t("new_chat"), key="new_chat_btn", width="stretch"):
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.rerun()
    
    for session in sessions:
        session_id = session["id"]
        title = session["title"] or t("session_title_unnamed")
        if len(title) > 20:
            title = title[:20] + "..."
        is_active = st.session_state.get("current_session_id") == session_id
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"{'📌 ' if is_active else '💬 '}{title}",
                key=f"session_{session_id}",
                width="stretch",
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_session_id = session_id
                db_messages = get_messages(session_id)
                st.session_state.messages = []
                for msg in db_messages:
                    content = json.loads(msg["content"])
                    st.session_state.messages.append({
                        "role": msg["role"],
                        "content": content.get("content", content) if isinstance(content, dict) else content,
                    })
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{session_id}"):
                delete_session(session_id)
                if st.session_state.get("current_session_id") == session_id:
                    st.session_state.current_session_id = None
                    st.session_state.messages = []
                st.rerun()
    
    with st.sidebar.container():
        st.markdown("---")
        current_lang = get_current_language()
        if st.button("🇹🇷", key="lang_tr", type="primary" if current_lang == "tr" else "secondary", width="stretch"):
            set_language("tr")
            st.rerun()
        if st.button("EN", key="lang_en", type="primary" if current_lang == "en" else "secondary", width="stretch"):
            set_language("en")
            st.rerun()
        is_dark = st.toggle("🌙 Dark Mode", value=st.session_state.theme_mode == "dark", key="dark_mode_toggle")
        if is_dark and st.session_state.theme_mode != "dark":
            st.session_state.theme_mode = "dark"
            st.rerun()
        elif not is_dark and st.session_state.theme_mode != "light":
            st.session_state.theme_mode = "light"
            st.rerun()
        st.markdown("---")

theme = THEMES[st.session_state.theme_mode]


def _escape_cell(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_results_table(df):
    """Render database results. Dark mode uses a themed HTML table because
    Streamlit's st.dataframe is canvas-rendered and cannot be reliably
    restyled for dark mode. Light mode keeps the native st.dataframe."""
    if st.session_state.theme_mode == "dark":
        headers = [str(c) for c in df.columns]
        body = ["<div class='db-table-wrap'><table class='db-table'>"]
        body.append("<thead><tr>")
        body.extend(f"<th>{_escape_cell(h)}</th>" for h in headers)
        body.append("</tr></thead><tbody>")
        for _, row in df.iterrows():
            body.append("<tr>")
            body.extend(f"<td>{_escape_cell(v)}</td>" for v in row.tolist())
            body.append("</tr>")
        body.append("</tbody></table></div>")
        st.markdown("".join(body), unsafe_allow_html=True)
    else:
        st.dataframe(df, width="stretch", hide_index=True)


if st.session_state.theme_mode == "dark":
    dataframe_css = """
/* ===== Dark mode: database output table (custom HTML table) ===== */
.db-table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin: 8px 0;
}
.db-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
}
.db-table th {
    background: var(--sidebar-surface);
    color: var(--ink);
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
}
.db-table td {
    padding: 8px 12px;
    color: var(--ink);
    border-bottom: 1px solid var(--border);
}
.db-table tbody tr:nth-child(odd) {
    background: var(--surface);
}
.db-table tbody tr:nth-child(even) {
    background: rgba(240, 246, 252, 0.04);
}
.db-table tbody tr:hover {
    background: var(--sidebar-button-hover-bg);
}
"""
else:
    dataframe_css = ""

st.markdown(f"""
<style>
:root {{
    --bg: {theme['bg']};
    --ink: {theme['ink']};
    --terra: {theme['terra']};
    --sage: {theme['sage']};
    --sand: {theme['sand']};
    --surface: {theme['surface']};
    --muted: {theme['muted']};
    --border: {theme['border']};
    --code-bg: {theme['code_bg']};
    --code-text: {theme['code_text']};
    --sql-bg: {theme['sql_bg']};
    --sql-text: {theme['sql_text']};
    --shadow: {theme['shadow']};
    --sidebar-bg: {theme['sidebar_bg']};
    --sidebar-surface: {theme['sidebar_surface']};
    --sidebar-border: {theme['sidebar_border']};
    --sidebar-button-bg: {theme['sidebar_button_bg']};
    --sidebar-button-hover-bg: {theme['sidebar_button_hover_bg']};
    --sidebar-button-border: {theme['sidebar_button_border']};
    --sidebar-button-text: {theme['sidebar_button_text']};
    --sidebar-heading: {theme['sidebar_heading']};
    --welcome-shadow: {theme['welcome_shadow']};
    --stats-border: {theme['stats_border']};
    --stats-shadow: {theme['stats_shadow']};
    --stats-hover-shadow: {theme['stats_hover_shadow']};
    --chat-input-border: {theme['chat_input_border']};
    --chat-input-placeholder: {theme['chat_input_placeholder']};
    --dataframe-bg: {theme['dataframe_bg']};
    --dataframe-text: {theme['dataframe_text']};
    --dataframe-header-bg: {theme['dataframe_header_bg']};
    --dataframe-header-text: {theme['dataframe_header_text']};
    --dataframe-border: {theme['dataframe_border']};
    --dataframe-row-alt: {theme['dataframe_row_alt']};
    --dataframe-hover: {theme['dataframe_hover']};
    --terra-hover: {theme['terra_hover']};
}}

* {{ box-sizing: border-box; }}

.stApp {{
    background-color: var(--bg);
    font-family: 'Inter', sans-serif;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    min-height: 100vh;
}}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] div {{
    font-family: 'Inter', sans-serif;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    font-family: 'Space Grotesk', sans-serif;
    color: var(--sidebar-heading);
}}

/* Primary button */
.stButton > button[kind="primary"] {{
    background: var(--terra);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    letter-spacing: 0.3px;
    padding: 0.6rem 1rem;
    box-shadow: 0 4px 12px var(--shadow);
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}}
.stButton > button[kind="primary"]:hover {{
    background: var(--terra-hover);
    transform: translateY(-1px);
    box-shadow: 0 6px 16px var(--shadow);
}}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {{
    border-radius: 10px;
    text-align: left;
    border: 1px solid var(--sidebar-button-border);
    background: var(--sidebar-button-bg);
    color: var(--sidebar-button-text);
    font-weight: 500;
    transition: all 0.15s ease;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: var(--sage);
    background: var(--sidebar-button-hover-bg);
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: var(--terra);
    color: #ffffff;
    border: none;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {{
    background: var(--terra-hover);
}}

/* Welcome screen */
.welcome-screen {{
    max-width: 760px;
    margin: 48px auto;
    text-align: center;
    animation: fadeUp 0.5s ease both;
}}
.welcome-icon {{
    font-size: 52px;
    width: 96px;
    height: 96px;
    margin: 0 auto 18px;
    display: grid;
    place-items: center;
    background: var(--surface);
    border-radius: 28px;
    box-shadow: 0 10px 30px var(--welcome-shadow);
}}
.welcome-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 40px;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.1;
    letter-spacing: -0.5px;
}}
.welcome-subtitle {{
    font-size: 16px;
    color: var(--muted);
    margin: 14px auto 0;
    max-width: 540px;
    line-height: 1.5;
}}

/* Stats cards */
.stats-card {{
    background: var(--surface);
    border: 1px solid var(--stats-border);
    border-radius: 20px;
    padding: 28px 20px;
    text-align: center;
    box-shadow: 0 8px 24px var(--stats-shadow);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}}
.stats-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 14px 32px var(--stats-hover-shadow);
}}
.stats-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: var(--terra);
}}
.stats-label {{
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 8px;
}}

/* SQL block */
.sql-block {{
    background: var(--sql-bg);
    color: var(--sql-text);
    padding: 14px 16px;
    border-radius: 12px;
    margin: 10px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    overflow-x: auto;
    border: 1px solid var(--border);
    box-shadow: inset 0 0 0 1px var(--shadow);
}}
.sql-block::before {{
    content: "\\25CF  \\25CF  \\25CF   sql";
    display: block;
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--sand);
    margin-bottom: 10px;
    opacity: 0.85;
}}

/* Chat input */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {{
    background: var(--surface) !important;
    border: 1px solid var(--chat-input-border) !important;
    border-radius: 16px !important;
    box-shadow: none !important;
    overflow: hidden;
}}
[data-testid="stChatInput"] > div {{
    border: none !important;
}}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {{
    border-radius: 16px !important;
    border: none !important;
    background: var(--surface) !important;
    font-family: 'Inter', sans-serif;
    color: var(--ink) !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: var(--chat-input-placeholder) !important;
    opacity: 1;
}}
[data-testid="stChatInput"] button {{
    background: transparent !important;
    color: var(--muted) !important;
    border: none !important;
    box-shadow: none !important;
}}

/* Dataframe overrides - dark theme only */
{dataframe_css}

/* Bottom bar / developer toolbar */
.stBottom,
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
.stToolbar,
[data-testid="stToolbar"],
.viewerFloating {{
    background: var(--bg) !important;
    border-top: 1px solid var(--border) !important;
}}
[data-testid="stBottom"] button,
.stToolbar button,
[data-testid="stToolbar"] button {{
    color: var(--muted) !important;
}}

/* Animations */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
/* Sidebar footer sticky */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]:last-child,
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]:nth-last-child(2) {{
    position: sticky !important;
    bottom: 0 !important;
    background: linear-gradient(180deg, transparent, var(--sidebar-bg) 50%) !important;
    z-index: 10 !important;
    padding-top: 0.5rem !important;
}}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]:last-child {{
    background: var(--sidebar-bg) !important;
    padding-bottom: 0.5rem !important;
}}
</style>
""", unsafe_allow_html=True)

init_db()


chain, db, schema = llm_sorgu_zinciri_kur()

if chain is None or db is None:
    st.error(t("error_db"))
else:
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="welcome-screen">
            <div class="welcome-icon">👋</div>
            <div class="welcome-title">{t("welcome_title")}</div>
            <div class="welcome-subtitle">
                {t("welcome_subtitle")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{t("stats_tables_count")}</div>
                <div class="stats-label">{t("stats_tables")}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{t("stats_orders_count")}</div>
                <div class="stats-label">{t("stats_orders")}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{t("stats_products_count")}</div>
                <div class="stats-label">{t("stats_products")}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                with st.chat_message("user"):
                    st.markdown(str(content))
            else:
                with st.chat_message("assistant"):
                    if isinstance(content, dict):
                        sql = content.get("sql")
                        results = content.get("results")
                        error = content.get("error")

                        if error:
                            st.error(f"{t('error_prefix')}: {error}")
                        else:
                            if sql:
                                st.markdown(f"**{t('sql_label')}**")
                                st.markdown(
                                    f'<div class="sql-block"><code>{sql}</code></div>',
                                    unsafe_allow_html=True,
                                )

                            if results:
                                st.markdown(f"**{t('results_label')}**")
                                try:
                                    df = pd.DataFrame(results)
                                    render_results_table(df)
                                except Exception:
                                    st.markdown(str(results))
                    else:
                        st.markdown(str(content))
    
    if prompt := st.chat_input(t("chat_input_hint")):
        if st.session_state.get("current_session_id") is None:
            session_id = create_session(t("session_title_new"))
            st.session_state.current_session_id = session_id
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        add_message(st.session_state.current_session_id, "user", json.dumps({"role": "user", "content": prompt}))
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner(t("thinking_spinner")):
                try:
                    uretilen_sql = chain.invoke({"schema": schema, "question": prompt})
                    uretilen_sql = uretilen_sql.strip()
                    
                    conn = sqlite3.connect(str(DB_ETICARET))
                    df = pd.read_sql_query(uretilen_sql, conn)
                    conn.close()
                    
                    st.markdown(f"**{t('sql_label')}**")
                    st.markdown(
                        f'<div class="sql-block"><code>{uretilen_sql}</code></div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**{t('results_label')}**")
                    render_results_table(df)
                    
                    result_data = {
                        "role": "assistant",
                        "content": {
                            "sql": uretilen_sql,
                            "results": df.to_dict(orient="records"),
                            "error": None,
                        },
                    }
                    st.session_state.messages.append(result_data)
                    add_message(
                        st.session_state.current_session_id,
                        "assistant",
                        json.dumps(result_data),
                    )
                    
                    session = get_session(st.session_state.current_session_id)
                    if session and (session["title"] == t("session_title_new") or not session["title"]):
                        update_session_title(st.session_state.current_session_id, prompt[:50])
                        
                except Exception as e:
                    error_data = {
                        "role": "assistant",
                        "content": {
                            "sql": None,
                            "results": None,
                            "error": str(e),
                        },
                    }
                    st.error(f"{t('error_db_query')}: {e}")
                    st.session_state.messages.append(error_data)
                    add_message(
                        st.session_state.current_session_id,
                        "assistant",
                        json.dumps(error_data),
                    )
