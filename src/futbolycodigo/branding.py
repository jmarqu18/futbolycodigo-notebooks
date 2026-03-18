"""Brand constants and helpers for Fútbol y Código."""

import matplotlib.pyplot as plt

COLORS: dict[str, str] = {
    "primary":    "#1A472A",
    "secondary":  "#4a7c59",
    "accent":     "#D4AF37",
    "background": "#FAFAFA",
    "text":       "#333333",
    "grid":       "#E0E0E0",
}

BLOG_NAME = "Fútbol y Código"
BLOG_URL = "https://futbolycodigo.com"
AUTHOR = "Juanje Márquez"


def apply_style() -> None:
    """Apply the Fútbol y Código matplotlib style globally.

    Call this once at the top of each notebook to ensure consistent
    visual style across all figures.
    """
    plt.rcParams.update({
        "figure.facecolor":  COLORS["background"],
        "axes.facecolor":    COLORS["background"],
        "axes.edgecolor":    COLORS["grid"],
        "axes.labelcolor":   COLORS["text"],
        "text.color":        COLORS["text"],
        "xtick.color":       COLORS["text"],
        "ytick.color":       COLORS["text"],
        "font.family":       "sans-serif",
        "font.size":         11,
        "figure.dpi":        100,
        "savefig.dpi":       200,
        "savefig.bbox":      "tight",
    })


def watermark(fig: plt.Figure) -> None:
    """Add a subtle footer watermark to a figure.

    Args:
        fig: Matplotlib figure to annotate.
    """
    fig.text(
        0.95, 0.02,
        f"{BLOG_URL} · {AUTHOR}",
        ha="right", va="bottom",
        fontsize=7, color=COLORS["secondary"], alpha=0.6,
    )
