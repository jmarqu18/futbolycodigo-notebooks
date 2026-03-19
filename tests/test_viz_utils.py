"""Tests para futbolycodigo.viz_utils — visualización profesional."""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch

from futbolycodigo.branding import LIGHT, DARK, BLOG_URL, set_theme
from futbolycodigo.viz_utils import (
    create_pitch,
    add_header,
    add_footer,
    create_comparison,
    plot_heatmap,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def cleanup():
    """Cierra figuras y resetea tema tras cada test."""
    set_theme("light")
    yield
    plt.close("all")
    matplotlib.rcdefaults()
    set_theme("light")


@pytest.fixture
def sample_coords():
    """Coordenadas de ejemplo en sistema StatsBomb."""
    rng = np.random.default_rng(42)
    return rng.uniform(0, 120, 50), rng.uniform(0, 80, 50)


# ---------------------------------------------------------------------------
# Colormap
# ---------------------------------------------------------------------------

def test_fyc_heat_colormap_registered():
    assert "fyc_heat" in matplotlib.colormaps


# ---------------------------------------------------------------------------
# create_pitch
# ---------------------------------------------------------------------------

def test_create_pitch_returns_correct_types():
    fig, ax, pitch = create_pitch()
    assert isinstance(fig, plt.Figure)
    assert isinstance(pitch, Pitch)


def test_create_pitch_vertical_returns_vertical_pitch():
    fig, ax, pitch = create_pitch("vertical")
    assert isinstance(pitch, VerticalPitch)


def test_create_pitch_default_figsize_horizontal():
    fig, ax, pitch = create_pitch("horizontal")
    w, h = fig.get_size_inches()
    assert (round(w), round(h)) == (10, 7)


def test_create_pitch_default_figsize_vertical():
    fig, ax, pitch = create_pitch("vertical")
    w, h = fig.get_size_inches()
    assert (round(w), round(h)) == (7, 10)


def test_create_pitch_custom_figsize():
    fig, ax, pitch = create_pitch(figsize=(15, 10))
    w, h = fig.get_size_inches()
    assert (round(w), round(h)) == (15, 10)


def test_create_pitch_uses_theme_background():
    fig, ax, pitch = create_pitch(theme=DARK)
    fc = matplotlib.colors.to_hex(fig.get_facecolor())
    assert fc == DARK.background


def test_create_pitch_light_theme_has_grass():
    fig, ax, pitch = create_pitch(theme=LIGHT)
    assert pitch.pitch_color == "grass"
    assert pitch.stripe is True


def test_create_pitch_dark_theme_no_stripe():
    fig, ax, pitch = create_pitch(theme=DARK)
    assert pitch.stripe is False


# ---------------------------------------------------------------------------
# add_header
# ---------------------------------------------------------------------------

def test_add_header_adds_title():
    fig = plt.figure()
    add_header(fig, "Test Title")
    texts = [t.get_text() for t in fig.texts]
    assert "Test Title" in texts


def test_add_header_with_subtitle():
    fig = plt.figure()
    add_header(fig, "Title", "Subtitle")
    texts = [t.get_text() for t in fig.texts]
    assert "Title" in texts
    assert "Subtitle" in texts


def test_add_header_left_aligned():
    fig = plt.figure()
    add_header(fig, "Title")
    title_text = fig.texts[0]
    assert title_text.get_ha() == "left"


def test_add_header_uses_accent_color():
    fig = plt.figure()
    add_header(fig, "Title", theme=LIGHT)
    title_text = fig.texts[0]
    assert matplotlib.colors.to_hex(title_text.get_color()) == LIGHT.accent


# ---------------------------------------------------------------------------
# add_footer
# ---------------------------------------------------------------------------

def test_add_footer_adds_text():
    fig = plt.figure()
    add_footer(fig)
    assert len(fig.texts) >= 1


def test_add_footer_contains_blog_url():
    fig = plt.figure()
    add_footer(fig)
    texts = [t.get_text() for t in fig.texts]
    assert any(BLOG_URL in t for t in texts)


def test_add_footer_with_extra_text():
    fig = plt.figure()
    add_footer(fig, extra_text="Datos: StatsBomb")
    texts = [t.get_text() for t in fig.texts]
    assert any("StatsBomb" in t for t in texts)


# ---------------------------------------------------------------------------
# create_comparison
# ---------------------------------------------------------------------------

def test_create_comparison_returns_correct_types():
    fig, axes, pitch = create_comparison()
    assert isinstance(fig, plt.Figure)
    assert isinstance(axes, np.ndarray)
    assert isinstance(pitch, VerticalPitch)


def test_create_comparison_1x2_has_2_axes():
    fig, axes, pitch = create_comparison(ncols=2, nrows=1)
    assert axes.flatten().shape[0] == 2


def test_create_comparison_2x2_has_4_axes():
    fig, axes, pitch = create_comparison(ncols=2, nrows=2)
    assert axes.flatten().shape[0] == 4


def test_create_comparison_uses_theme():
    fig, axes, pitch = create_comparison(theme=DARK)
    fc = matplotlib.colors.to_hex(fig.get_facecolor())
    assert fc == DARK.background


# ---------------------------------------------------------------------------
# plot_heatmap
# ---------------------------------------------------------------------------

def test_plot_heatmap_returns_figure(sample_coords):
    x, y = sample_coords
    fig = plot_heatmap(x, y, title="Test")
    assert isinstance(fig, plt.Figure)


def test_plot_heatmap_accepts_series(sample_coords):
    x, y = sample_coords
    fig = plot_heatmap(pd.Series(x), pd.Series(y))
    assert isinstance(fig, plt.Figure)


def test_plot_heatmap_adds_header_and_footer(sample_coords):
    x, y = sample_coords
    fig = plot_heatmap(x, y, title="My Title", subtitle="Sub")
    texts = [t.get_text() for t in fig.texts]
    assert "My Title" in texts
    assert any(BLOG_URL in t for t in texts)
