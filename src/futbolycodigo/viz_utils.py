"""Visualization utilities built on top of mplsoccer."""

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch, VerticalPitch

from futbolycodigo.branding import COLORS


def create_pitch(
    orientation: Literal["horizontal", "vertical"] = "horizontal",
    *,
    half: bool = False,
    figsize: tuple[float, float] | None = None,
) -> tuple[plt.Figure, plt.Axes, Pitch | VerticalPitch]:
    """Create a styled football pitch ready for plotting.

    Args:
        orientation: Pitch orientation — 'horizontal' or 'vertical'.
        half: If True, show only half pitch.
        figsize: Custom figure size. Defaults to (12, 8) or (8, 12).

    Returns:
        Tuple of (figure, axes, pitch object).
    """
    if figsize is None:
        figsize = (8, 12) if orientation == "vertical" else (12, 8)

    PitchClass = VerticalPitch if orientation == "vertical" else Pitch
    pitch = PitchClass(
        pitch_type="statsbomb",
        pitch_color=COLORS["background"],
        line_color=COLORS["grid"],
        line_zorder=2,
        half=half,
    )
    fig, ax = pitch.draw(figsize=figsize)
    fig.set_facecolor(COLORS["background"])
    return fig, ax, pitch


def add_title(
    fig: plt.Figure,
    title: str,
    subtitle: str = "",
) -> None:
    """Add a styled title and optional subtitle to a figure.

    Args:
        fig: Matplotlib figure to annotate.
        title: Main title text.
        subtitle: Optional subtitle text (displayed in italics below the title).
    """
    fig.text(
        0.5, 0.95, title,
        ha="center", va="center",
        fontsize=16, fontweight="bold",
        color=COLORS["primary"],
    )
    if subtitle:
        fig.text(
            0.5, 0.92, subtitle,
            ha="center", va="center",
            fontsize=11, color=COLORS["text"], style="italic",
        )


def plot_heatmap(
    x: np.ndarray | pd.Series,
    y: np.ndarray | pd.Series,
    *,
    title: str = "",
    subtitle: str = "",
    orientation: Literal["horizontal", "vertical"] = "vertical",
    cmap: str = "Greens",
) -> plt.Figure:
    """Generate a heatmap of player/team actions on the pitch.

    Args:
        x: X coordinates (StatsBomb pitch units).
        y: Y coordinates (StatsBomb pitch units).
        title: Plot title.
        subtitle: Plot subtitle.
        orientation: Pitch orientation.
        cmap: Matplotlib colormap name.

    Returns:
        Matplotlib figure.
    """
    fig, ax, pitch = create_pitch(orientation)
    pitch.kdeplot(
        x, y, ax=ax,
        cmap=cmap, fill=True,
        levels=100, thresh=0.05, zorder=3,
    )
    if title:
        add_title(fig, title, subtitle)
    return fig
