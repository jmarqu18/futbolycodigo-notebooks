"""Tests para futbolycodigo.branding — sistema de temas y fuentes."""

import matplotlib
matplotlib.use("Agg")

import pytest
import matplotlib.pyplot as plt

from futbolycodigo.branding import (
    BLOG_NAME,
    BLOG_URL,
    AUTHOR,
    LIGHT,
    DARK,
    Theme,
    set_theme,
    get_theme,
    apply_style,
    load_logo,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_state():
    """Reset matplotlib rcParams y tema activo tras cada test."""
    yield
    matplotlib.rcdefaults()
    set_theme("light")


# ---------------------------------------------------------------------------
# Constantes de marca
# ---------------------------------------------------------------------------

def test_blog_name_is_string():
    assert isinstance(BLOG_NAME, str) and len(BLOG_NAME) > 0


def test_blog_url_starts_with_https():
    assert BLOG_URL.startswith("https://")


def test_author_is_string():
    assert isinstance(AUTHOR, str) and len(AUTHOR) > 0


# ---------------------------------------------------------------------------
# Temas
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("theme", [LIGHT, DARK])
def test_themes_have_all_required_fields(theme):
    """Ambos temas deben tener todos los campos de Theme como strings no vacíos."""
    for field_name in Theme.__dataclass_fields__:
        val = getattr(theme, field_name)
        if isinstance(val, str):
            assert len(val) > 0, f"Campo {field_name} está vacío en {theme.name}"


def test_light_theme_name():
    assert LIGHT.name == "light"


def test_dark_theme_name():
    assert DARK.name == "dark"


def test_themes_have_different_backgrounds():
    assert LIGHT.background != DARK.background


def test_set_theme_by_string():
    set_theme("dark")
    assert get_theme() is DARK


def test_set_theme_by_instance():
    set_theme(DARK)
    assert get_theme() is DARK


def test_set_theme_invalid_string_raises():
    with pytest.raises(KeyError):
        set_theme("nonexistent")


def test_get_theme_default_is_light():
    set_theme("light")
    assert get_theme() is LIGHT


# ---------------------------------------------------------------------------
# apply_style
# ---------------------------------------------------------------------------

def test_apply_style_sets_facecolor():
    apply_style()
    assert plt.rcParams["figure.facecolor"] == LIGHT.background


def test_apply_style_sets_text_color():
    apply_style()
    assert plt.rcParams["text.color"] == LIGHT.text


def test_apply_style_sets_font_size():
    apply_style()
    assert plt.rcParams["font.size"] == 11


def test_apply_style_sets_figure_dpi():
    apply_style()
    assert plt.rcParams["figure.dpi"] == 100


def test_apply_style_with_dark_theme():
    apply_style("dark")
    assert plt.rcParams["figure.facecolor"] == DARK.background
    assert plt.rcParams["text.color"] == DARK.text
    assert get_theme() is DARK


def test_apply_style_with_theme_instance():
    apply_style(DARK)
    assert plt.rcParams["figure.facecolor"] == DARK.background


def test_apply_style_registers_font():
    """Verifica que después de apply_style, la fuente es Inter o DejaVu Sans."""
    apply_style()
    font = plt.rcParams["font.family"]
    # rcParams devuelve una lista para font.family
    if isinstance(font, list):
        font = font[0]
    assert font in ("Inter", "DejaVu Sans")


# ---------------------------------------------------------------------------
# load_logo
# ---------------------------------------------------------------------------

def test_load_logo_returns_image_or_none():
    """load_logo devuelve una imagen PIL o None si no existe el archivo."""
    result = load_logo(width=300)
    # Puede ser None si los PNGs no se generaron, o Image si existen
    if result is not None:
        from PIL import Image
        assert isinstance(result, Image.Image)


def test_load_logo_nonexistent_width_returns_none():
    assert load_logo(width=9999) is None
