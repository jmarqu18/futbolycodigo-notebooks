"""Sistema de temas y branding para Fútbol y Código.

Gestiona paletas de colores (light/dark), tipografía Inter,
y carga de assets (logos PNG) para las visualizaciones.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from PIL import Image

# ---------------------------------------------------------------------------
# Rutas de assets
# ---------------------------------------------------------------------------
_ASSETS_DIR = Path(__file__).parent / "assets"
_FONTS_DIR = _ASSETS_DIR / "fonts"

# ---------------------------------------------------------------------------
# Constantes de marca
# ---------------------------------------------------------------------------
BLOG_NAME = "Fútbol y Código"
BLOG_URL = "https://futbolycodigo.com"
AUTHOR = "Juanje Márquez"


# ---------------------------------------------------------------------------
# Sistema de temas
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Theme:
    """Tema visual completo para figuras de Fútbol y Código."""

    name: str
    # Colores de figura
    background: str
    text: str
    accent: str
    secondary_text: str
    # Colores de campo (pitch)
    pitch_color: str          # hex o "grass" para césped verde
    stripe: bool
    stripe_color: str
    line_color: str
    # Ejes y grids (para gráficos no-pitch)
    grid: str


LIGHT = Theme(
    name="light",
    background="#ffffff",
    text="#0a0a0a",
    accent="#ea580c",
    secondary_text="#6b7280",
    pitch_color="grass",
    stripe=True,
    stripe_color="#c2d59d",
    line_color="white",
    grid="#e5e7eb",
)

DARK = Theme(
    name="dark",
    background="#0f172a",
    text="#f1f5f9",
    accent="#f97316",
    secondary_text="#94a3b8",
    pitch_color="#1a2332",
    stripe=False,
    stripe_color="#1a2332",
    line_color="#334155",
    grid="#1e293b",
)

_THEMES: dict[str, Theme] = {"light": LIGHT, "dark": DARK}

# Estado global — tema activo (por defecto light)
_active_theme: Theme = LIGHT


def set_theme(theme: Theme | Literal["light", "dark"]) -> None:
    """Cambia el tema activo globalmente.

    Args:
        theme: Instancia de Theme o string 'light'/'dark'.
    """
    global _active_theme
    if isinstance(theme, str):
        _active_theme = _THEMES[theme]
    else:
        _active_theme = theme


def get_theme() -> Theme:
    """Devuelve el tema activo."""
    return _active_theme


# ---------------------------------------------------------------------------
# Gestión de fuentes
# ---------------------------------------------------------------------------
_fonts_registered = False


def _register_fonts() -> None:
    """Registra Inter (Regular + Bold) en matplotlib si están disponibles.

    Se ejecuta una sola vez. Si los archivos TTF no existen en assets/fonts/,
    se silencia el error y matplotlib usará su fuente sans-serif por defecto.
    """
    global _fonts_registered
    if _fonts_registered:
        return

    for ttf_name in ("Inter-Regular.ttf", "Inter-Bold.ttf"):
        ttf_path = _FONTS_DIR / ttf_name
        if ttf_path.exists():
            fm.fontManager.addfont(str(ttf_path))

    _fonts_registered = True


def _get_font_family() -> str:
    """Devuelve 'Inter' si está registrada, sino 'DejaVu Sans'."""
    _register_fonts()
    available = {f.name for f in fm.fontManager.ttflist}
    return "Inter" if "Inter" in available else "DejaVu Sans"


# ---------------------------------------------------------------------------
# Aplicar estilo global
# ---------------------------------------------------------------------------
def apply_style(theme: Theme | Literal["light", "dark"] | None = None) -> None:
    """Aplica el estilo FyC a matplotlib globalmente.

    Configura rcParams con los colores del tema activo y registra la fuente
    Inter. Llamar una vez al inicio de cada notebook.

    Args:
        theme: Tema a aplicar. Si None, usa el tema activo actual.
    """
    if theme is not None:
        set_theme(theme)

    t = get_theme()
    font = _get_font_family()

    plt.rcParams.update({
        # Colores de figura
        "figure.facecolor": t.background,
        "axes.facecolor": t.background,
        "axes.edgecolor": t.grid,
        "axes.labelcolor": t.text,
        "text.color": t.text,
        "xtick.color": t.text,
        "ytick.color": t.text,
        # Tipografía
        "font.family": font,
        "font.size": 11,
        # Resolución
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


# ---------------------------------------------------------------------------
# Carga de logos
# ---------------------------------------------------------------------------
def load_logo(width: int = 300) -> Image.Image | None:
    """Carga el logo FyC como imagen PIL.

    Busca el PNG pre-renderizado en assets/ con el ancho indicado.
    Devuelve None si el archivo no existe (fallback graceful).

    Args:
        width: Ancho deseado en píxeles (debe existir el PNG correspondiente).
    """
    png_path = _ASSETS_DIR / f"logo_thin_1_{width}w.png"
    if not png_path.exists():
        return None
    return Image.open(png_path)
