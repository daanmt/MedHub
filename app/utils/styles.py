import streamlit as st

# MedHub Design System - Flat & Clinical Aesthetic
# Based on medhub-ui-refresh-main tokens with strictly FLAT implementation

COLORS = {
    "background": "#05070A",
    "foreground": "#F3F7FC",
    "card": "#11161D",
    "secondary": "#0E1116",
    "secondary_fg": "#A8B3C2",
    "muted_fg": "#738093",
    "primary": "#2F6BFF",
    "border": "#202A36",
    "border_soft": "#2A3544",
    "success": "#1FA971",
    "warning": "#D9A441",
    "danger": "#D9534F",
    "info": "#3F7CFF",
    "navy": "#0B1F3A",
    "accent_hint": "#7FB8FF",
}

GLOBAL_STYLES = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Base reset and typography */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        background-color: {COLORS['background']};
        color: {COLORS['foreground']};
    }}

    /* Sidebar Styling - Flat & Dark */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['secondary']};
        border-right: 1px solid {COLORS['border']};
    }}

    /* Global Header Styling */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['foreground']} !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }}

    /* Custom Card Style - Pure Flat */
    .medhub-card {{
        background-color: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }}

    .medhub-metric-label {{
        color: {COLORS['secondary_fg']};
        font-size: 0.8rem;
        margin-bottom: 4px;
    }}

    .medhub-metric-value {{
        color: {COLORS['foreground']};
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1.2;
    }}

    /* FSRS Rating Buttons - CSS Targeting for Streamlit Buttons in Columns */
    div[data-testid="column"]:nth-child(1) .stButton > button {{
        background-color: #1A0A0A !important;
        color: #D9534F !important;
        border-color: rgba(217, 83, 79, 0.3) !important;
        border: 1px solid !important;
    }}
    div[data-testid="column"]:nth-child(2) .stButton > button {{
        background-color: #1A1200 !important;
        color: #D9A441 !important;
        border-color: rgba(217, 164, 65, 0.3) !important;
        border: 1px solid !important;
    }}
    div[data-testid="column"]:nth-child(3) .stButton > button {{
        background-color: {COLORS['secondary']} !important;
        color: {COLORS['secondary_fg']} !important;
        border-color: {COLORS['border_soft']} !important;
        border: 1px solid !important;
    }}
    div[data-testid="column"]:nth-child(4) .stButton > button {{
        background-color: #091A12 !important;
        color: {COLORS['success']} !important;
        border-color: rgba(31, 169, 113, 0.3) !important;
        border: 1px solid !important;
    }}

    .stButton > button {{
        border-radius: 10px !important;
        transition: brightness 0.15s ease !important;
    }}
    .stButton > button:hover {{
        filter: brightness(1.2) !important;
    }}

    /* Prova/Warning labels */
    .medhub-box {{
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 12px;
        border-left: 3px solid;
    }}
    .box-master {{ background-color: {COLORS['navy']}; border-left-color: {COLORS['primary']}; }}
    .box-trap   {{ background-color: #1A1200; border-left-color: {COLORS['warning']}; }}
    
    .medhub-box-title {{
        font-size: 0.7rem; 
        font-weight: 600; 
        margin-bottom: 4px;
        /* No text-transform: uppercase - Sentence case only */
    }}

    /* Clean Divider */
    hr {{
        border: 0;
        border-top: 1px solid {COLORS['border']};
        margin: 2rem 0;
    }}
</style>
"""

def inject_styles():
    """Injects global CSS into the Streamlit app."""
    st.markdown(GLOBAL_STYLES, unsafe_allow_html=True)

def metric_card(label, value, delta=None, delta_type="up"):
    """Render a high-fidelity flat metric card."""
    delta_html = ""
    if delta:
        color = COLORS['success'] if delta_type == "up" else COLORS['danger']
        arrow = "↑" if delta_type == "up" else "↓"
        delta_html = f'<div style="color: {color}; font-size: 0.75rem; margin-top: 4px;">{arrow} {delta}</div>'
    
    html = f"""
    <div class="medhub-card">
        <div class="medhub-metric-label">{label}</div>
        <div class="medhub-metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def content_card(title, content, subtitle=None):
    """Render a titled content card."""
    subtitle_html = f'<div style="color: {COLORS["muted_fg"]}; font-size: 0.75rem; margin-bottom: 8px;">{subtitle}</div>' if subtitle else ""
    html = f"""
    <div class="medhub-card">
        <div style="font-weight: 600; font-size: 1rem; margin-bottom: 4px;">{title}</div>
        {subtitle_html}
        <div style="font-size: 0.9rem; line-height: 1.6;">{content}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def flashcard_front(category, question):
    """Render a premium flashcard front."""
    header = f'<div style="font-style: italic; color: {COLORS["muted_fg"]}; font-size: 0.75rem; margin-bottom: 12px;">{category}</div>'
    st.markdown(f"""
    <div class="medhub-card" style="border-color: {COLORS['border_soft']}">
        {header}
        <div style="font-size: 1.15rem; font-weight: 500; line-height: 1.5;">{question}</div>
    </div>
    """, unsafe_allow_html=True)

def flashcard_back(answer, master_rule=None, trap=None):
    """Render a premium flashcard back."""
    master_html = f"""
    <div class="medhub-box box-master">
        <div class="medhub-box-title" style="color: {COLORS['accent_hint']};">Regra Mestre</div>
        <div style="font-size: 0.85rem;">{master_rule}</div>
    </div>
    """ if master_rule else ""
    
    trap_html = f"""
    <div class="medhub-box box-trap">
        <div class="medhub-box-title" style="color: {COLORS['warning']};">Armadilha</div>
        <div style="font-size: 0.85rem;">{trap}</div>
    </div>
    """ if trap else ""

    st.markdown(f"""
    <div class="medhub-card" style="border-color: {COLORS['primary']}44">
        <div style="font-size: 1rem; line-height: 1.6; margin-bottom: 12px;">{answer}</div>
        {master_html}
        {trap_html}
    </div>
    """, unsafe_allow_html=True)
