"""
MedHub — Plotly Theme Helper
Importar e usar: apply_medhub_theme(fig)
"""

MEDHUB_COLORS = {
    "bg": "rgba(0,0,0,0)",
    "grid": "#202A36",
    "text": "#A8B3C2",
    "title": "#F3F7FC",
    "accent": "#2F6BFF",
    "accent_soft": "#7FB8FF",
    "success": "#1FA971",
    "warning": "#D9A441",
    "danger": "#D9534F",
    "surface": "#11161D",
}


def apply_medhub_theme(fig, title=None):
    """Apply MedHub dark theme to a Plotly figure."""
    fig.update_layout(
        paper_bgcolor=MEDHUB_COLORS["bg"],
        plot_bgcolor=MEDHUB_COLORS["bg"],
        font=dict(
            family="Inter, system-ui, sans-serif",
            color=MEDHUB_COLORS["text"],
            size=13,
        ),
        title=dict(
            text=title,
            font=dict(
                color=MEDHUB_COLORS["title"],
                size=18,
                family="Inter, sans-serif",
            ),
        ) if title else None,
        xaxis=dict(
            gridcolor=MEDHUB_COLORS["grid"],
            linecolor=MEDHUB_COLORS["grid"],
            zerolinecolor=MEDHUB_COLORS["grid"],
            tickfont=dict(color=MEDHUB_COLORS["text"], size=12),
        ),
        yaxis=dict(
            gridcolor=MEDHUB_COLORS["grid"],
            linecolor=MEDHUB_COLORS["grid"],
            zerolinecolor=MEDHUB_COLORS["grid"],
            tickfont=dict(color=MEDHUB_COLORS["text"], size=12),
        ),
        legend=dict(
            font=dict(color=MEDHUB_COLORS["text"], size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=MEDHUB_COLORS["surface"],
            font_color=MEDHUB_COLORS["title"],
            font_size=13,
            font_family="Inter, sans-serif",
            bordercolor=MEDHUB_COLORS["grid"],
        ),
        margin=dict(l=20, r=20, t=40 if title else 20, b=20),
    )
    return fig


# Default bar color sequence (single blue, per branding)
MEDHUB_BAR_COLORS = [MEDHUB_COLORS["accent"]]
MEDHUB_LINE_COLORS = [MEDHUB_COLORS["accent"], MEDHUB_COLORS["accent_soft"]]
