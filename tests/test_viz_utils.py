"""Tests for futbolycodigo.viz_utils — written before implementation (TDD)."""

import matplotlib
matplotlib.use('Agg')  # Must be set before any matplotlib/mplsoccer imports

import numpy as np
import pytest
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from mplsoccer import Pitch, VerticalPitch

import futbolycodigo.viz_utils as vz
from futbolycodigo.branding import COLORS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def close_figures():
    """Close all matplotlib figures after each test to free memory."""
    yield
    plt.close('all')


# ---------------------------------------------------------------------------
# branding — sanity check
# ---------------------------------------------------------------------------

def test_colors_has_required_keys():
    required = {"primary", "secondary", "accent", "background", "text", "grid"}
    assert required.issubset(COLORS.keys())


def test_colors_values_are_hex_strings():
    for key, value in COLORS.items():
        assert isinstance(value, str), f"COLORS[{key!r}] is not a string"
        assert value.startswith("#"), f"COLORS[{key!r}] is not a hex color"


# ---------------------------------------------------------------------------
# create_pitch
# ---------------------------------------------------------------------------

def test_create_pitch_returns_figure_axes_pitch():
    fig, ax, pitch = vz.create_pitch()
    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)
    assert isinstance(pitch, (Pitch, VerticalPitch))


def test_create_pitch_horizontal_returns_pitch_not_vertical():
    _, _, pitch = vz.create_pitch(orientation="horizontal")
    assert isinstance(pitch, Pitch)
    assert not isinstance(pitch, VerticalPitch)


def test_create_pitch_vertical_returns_vertical_pitch():
    _, _, pitch = vz.create_pitch(orientation="vertical")
    assert isinstance(pitch, VerticalPitch)


def test_create_pitch_default_figsize_horizontal():
    fig, _, _ = vz.create_pitch(orientation="horizontal")
    w, h = fig.get_size_inches()
    assert (round(w), round(h)) == (12, 8)


def test_create_pitch_default_figsize_vertical():
    fig, _, _ = vz.create_pitch(orientation="vertical")
    w, h = fig.get_size_inches()
    assert (round(w), round(h)) == (8, 12)


def test_create_pitch_custom_figsize_is_respected():
    fig, _, _ = vz.create_pitch(figsize=(10, 6))
    w, h = fig.get_size_inches()
    assert (round(w), round(h)) == (10, 6)


# ---------------------------------------------------------------------------
# add_title
# ---------------------------------------------------------------------------

def test_add_title_adds_at_least_one_text_to_figure():
    fig, _, _ = vz.create_pitch()
    before = len(fig.texts)
    vz.add_title(fig, "Test Title")
    assert len(fig.texts) > before


def test_add_title_with_subtitle_adds_two_texts():
    fig, _, _ = vz.create_pitch()
    before = len(fig.texts)
    vz.add_title(fig, "Title", "Subtitle")
    assert len(fig.texts) == before + 2


def test_add_title_without_subtitle_adds_one_text():
    fig, _, _ = vz.create_pitch()
    before = len(fig.texts)
    vz.add_title(fig, "Title Only")
    assert len(fig.texts) == before + 1


# ---------------------------------------------------------------------------
# plot_heatmap
# ---------------------------------------------------------------------------

SAMPLE_X = np.array([30.0, 50.0, 70.0, 40.0, 60.0])
SAMPLE_Y = np.array([20.0, 40.0, 30.0, 50.0, 35.0])


def test_plot_heatmap_returns_figure():
    fig = vz.plot_heatmap(SAMPLE_X, SAMPLE_Y)
    assert isinstance(fig, Figure)


def test_plot_heatmap_with_title_adds_text():
    fig = vz.plot_heatmap(SAMPLE_X, SAMPLE_Y, title="Pedri — Acciones")
    assert len(fig.texts) > 0


def test_plot_heatmap_without_title_returns_clean_figure():
    fig = vz.plot_heatmap(SAMPLE_X, SAMPLE_Y)
    assert isinstance(fig, Figure)


def test_plot_heatmap_accepts_pandas_series():
    import pandas as pd
    x = pd.Series(SAMPLE_X)
    y = pd.Series(SAMPLE_Y)
    fig = vz.plot_heatmap(x, y)
    assert isinstance(fig, Figure)
