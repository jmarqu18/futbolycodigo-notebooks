"""Utilidades de visualización profesional para football analytics.

Proporciona funciones para crear campos de fútbol con estilo de broadcast,
headers/footers con branding, colormaps profesionales, y layouts comparativos.
Todas las funciones leen el tema activo de branding.get_theme().
"""

from __future__ import annotations

from typing import Literal

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch, VerticalPitch
from mplsoccer.utils import add_image
from PIL import Image

from futbolycodigo.branding import (
    AUTHOR,
    BLOG_URL,
    Theme,
    get_theme,
    load_logo,
)

# ---------------------------------------------------------------------------
# Colormap profesional — registrado al importar el módulo
# ---------------------------------------------------------------------------
# Gradiente navy → azul → amarillo → naranja → rojo
# Inspirado en colormaps de StatsBomb/Opta para densidad espacial
_FYC_HEAT_COLORS = ["#1a1a2e", "#16537e", "#f6d55c", "#ed553b", "#e63946"]
_FYC_HEAT = LinearSegmentedColormap.from_list("fyc_heat", _FYC_HEAT_COLORS, N=256)

if "fyc_heat" not in matplotlib.colormaps:
    matplotlib.colormaps.register(_FYC_HEAT, name="fyc_heat")


# ---------------------------------------------------------------------------
# Creación de campo
# ---------------------------------------------------------------------------
def create_pitch(
    orientation: Literal["horizontal", "vertical"] = "horizontal",
    *,
    half: bool = False,
    figsize: tuple[float, float] | None = None,
    theme: Theme | None = None,
) -> tuple[plt.Figure, plt.Axes, Pitch | VerticalPitch]:
    """Crea un campo de fútbol estilizado con el tema activo.

    El campo usa los colores del tema para pitch_color, line_color y stripes.
    Con el tema LIGHT se obtiene césped con rayas; con DARK, fondo oscuro sutil.

    Args:
        orientation: 'horizontal' o 'vertical'.
        half: Si True, muestra solo medio campo.
        figsize: Tamaño custom. Por defecto (10, 7) horiz o (7, 10) vert.
        theme: Tema a usar. Si None, usa el tema activo global.

    Returns:
        Tupla (figure, axes, pitch_object).
    """
    if theme is None:
        theme = get_theme()

    if figsize is None:
        figsize = (7, 10) if orientation == "vertical" else (10, 7)

    PitchClass = VerticalPitch if orientation == "vertical" else Pitch
    pitch = PitchClass(
        pitch_type="statsbomb",
        pitch_color=theme.pitch_color,
        line_color=theme.line_color,
        stripe=theme.stripe,
        stripe_color=theme.stripe_color,
        line_zorder=2,
        half=half,
    )
    fig, ax = pitch.draw(figsize=figsize)
    fig.set_facecolor(theme.background)
    return fig, ax, pitch


# ---------------------------------------------------------------------------
# Header y footer con branding
# ---------------------------------------------------------------------------
def add_header(
    fig: plt.Figure,
    title: str,
    subtitle: str = "",
    *,
    context_images: list[Image.Image] | None = None,
    theme: Theme | None = None,
) -> None:
    """Añade cabecera profesional: título a la izquierda, imágenes a la derecha.

    El título usa el color accent del tema (negrita, 18pt). El subtítulo
    usa secondary_text (italic, 11pt). Las imágenes de contexto (escudos,
    fotos de jugador, logos de competición) se posicionan a la derecha.

    Args:
        fig: Figura matplotlib.
        title: Título principal.
        subtitle: Subtítulo descriptivo.
        context_images: Lista de imágenes PIL para el lado derecho del header.
        theme: Tema a usar. Si None, usa el activo.
    """
    if theme is None:
        theme = get_theme()

    # Título alineado a la izquierda, color accent
    fig.text(
        0.05, 0.96, title,
        ha="left", va="top",
        fontsize=18, fontweight="bold",
        color=theme.accent,
    )

    if subtitle:
        fig.text(
            0.05, 0.93, subtitle,
            ha="left", va="top",
            fontsize=11, color=theme.secondary_text,
        )

    # Imágenes de contexto posicionadas a la derecha del header
    if context_images:
        # Cada imagen ocupa ~5% del ancho de la figura, separadas 1%
        img_width = 0.05
        right_edge = 0.95
        for i, img in enumerate(context_images):
            left = right_edge - (i + 1) * (img_width + 0.01)
            add_image(img, fig, left=left, bottom=0.92, height=0.06)


def add_footer(
    fig: plt.Figure,
    *,
    extra_text: str = "",
    theme: Theme | None = None,
) -> None:
    """Añade pie de página: watermark a la izquierda, logo FyC a la derecha.

    Si el PNG del logo no está disponible, solo muestra el texto.

    Args:
        fig: Figura matplotlib.
        extra_text: Texto adicional junto al watermark.
        theme: Tema a usar. Si None, usa el activo.
    """
    if theme is None:
        theme = get_theme()

    # Texto watermark a la izquierda
    watermark_text = f"{BLOG_URL} · {AUTHOR}"
    if extra_text:
        watermark_text = f"{extra_text}  |  {watermark_text}"

    fig.text(
        0.05, 0.02, watermark_text,
        ha="left", va="bottom",
        fontsize=7, color=theme.secondary_text, alpha=0.7,
    )

    # Logo a la derecha (fallback graceful si no existe el PNG)
    logo = load_logo(width=300)
    if logo is not None:
        add_image(logo, fig, left=0.82, bottom=0.005, height=0.035)


# ---------------------------------------------------------------------------
# Layout comparativo (multi-panel)
# ---------------------------------------------------------------------------
def create_comparison(
    orientation: Literal["horizontal", "vertical"] = "vertical",
    *,
    ncols: int = 2,
    nrows: int = 1,
    figsize: tuple[float, float] | None = None,
    theme: Theme | None = None,
) -> tuple[plt.Figure, np.ndarray, Pitch | VerticalPitch]:
    """Crea una cuadrícula de campos para visualizaciones comparativas.

    Útil para comparar jugadores, partidos o tipos de acción lado a lado.
    Reemplaza el patrón repetitivo de pitch.draw(nrows=, ncols=) en notebooks.

    Args:
        orientation: 'horizontal' o 'vertical'.
        ncols: Número de columnas.
        nrows: Número de filas.
        figsize: Tamaño custom. Auto-calculado si None.
        theme: Tema a usar. Si None, usa el activo.

    Returns:
        Tupla (figure, array_de_axes, pitch_object).
    """
    if theme is None:
        theme = get_theme()

    if figsize is None:
        # Proporciones razonables para notebook según layout
        if orientation == "vertical":
            figsize = (6 * ncols, 8 * nrows)
        else:
            figsize = (8 * ncols, 6 * nrows)

    PitchClass = VerticalPitch if orientation == "vertical" else Pitch
    pitch = PitchClass(
        pitch_type="statsbomb",
        pitch_color=theme.pitch_color,
        line_color=theme.line_color,
        stripe=theme.stripe,
        stripe_color=theme.stripe_color,
        line_zorder=2,
    )
    fig, axes = pitch.draw(figsize=figsize, nrows=nrows, ncols=ncols)
    fig.set_facecolor(theme.background)

    # Asegurar que axes sea siempre un ndarray para consistencia
    axes = np.atleast_1d(axes)

    return fig, axes, pitch


# ---------------------------------------------------------------------------
# Heatmap completo con branding
# ---------------------------------------------------------------------------
def plot_heatmap(
    x: np.ndarray | pd.Series,
    y: np.ndarray | pd.Series,
    *,
    title: str = "",
    subtitle: str = "",
    orientation: Literal["horizontal", "vertical"] = "vertical",
    cmap: str | None = None,
    figsize: tuple[float, float] | None = None,
    theme: Theme | None = None,
) -> plt.Figure:
    """Genera un heatmap KDE profesional con branding completo.

    Crea el campo, dibuja la densidad KDE, y añade header + footer
    automáticamente. Usa el colormap 'fyc_heat' por defecto.

    Args:
        x: Coordenadas X (unidades StatsBomb).
        y: Coordenadas Y (unidades StatsBomb).
        title: Título del plot.
        subtitle: Subtítulo descriptivo.
        orientation: Orientación del campo.
        cmap: Colormap. Si None, usa 'fyc_heat'.
        figsize: Tamaño custom de la figura.
        theme: Tema a usar. Si None, usa el activo.

    Returns:
        Figura matplotlib con el heatmap completo.
    """
    if cmap is None:
        cmap = "fyc_heat"

    fig, ax, pitch = create_pitch(orientation, figsize=figsize, theme=theme)

    pitch.kdeplot(
        x, y, ax=ax,
        cmap=cmap, fill=True,
        levels=100, thresh=0.05,
        zorder=3, alpha=0.7,
    )

    if title:
        add_header(fig, title, subtitle, theme=theme)
    add_footer(fig, theme=theme)

    return fig
