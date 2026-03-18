"""Tests for futbolycodigo.branding — written before implementation (TDD)."""

import matplotlib
matplotlib.use('Agg')  # Must be set before any matplotlib imports

import pytest
import matplotlib.pyplot as plt

from futbolycodigo.branding import (
    COLORS,
    BLOG_NAME,
    BLOG_URL,
    AUTHOR,
    apply_style,
    watermark,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_rcparams():
    """Reset matplotlib rcParams to defaults after each test."""
    yield
    matplotlib.rcdefaults()


@pytest.fixture
def empty_figure():
    fig = plt.figure()
    yield fig
    plt.close(fig)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_blog_name_is_string():
    assert isinstance(BLOG_NAME, str) and len(BLOG_NAME) > 0


def test_blog_url_starts_with_https():
    assert BLOG_URL.startswith("https://")


def test_author_is_string():
    assert isinstance(AUTHOR, str) and len(AUTHOR) > 0


# ---------------------------------------------------------------------------
# apply_style
# ---------------------------------------------------------------------------

def test_apply_style_sets_figure_facecolor():
    apply_style()
    assert plt.rcParams["figure.facecolor"] == COLORS["background"]


def test_apply_style_sets_axes_facecolor():
    apply_style()
    assert plt.rcParams["axes.facecolor"] == COLORS["background"]


def test_apply_style_sets_text_color():
    apply_style()
    assert plt.rcParams["text.color"] == COLORS["text"]


def test_apply_style_sets_font_size_to_11():
    apply_style()
    assert plt.rcParams["font.size"] == 11


def test_apply_style_sets_figure_dpi():
    apply_style()
    assert plt.rcParams["figure.dpi"] == 100


# ---------------------------------------------------------------------------
# watermark
# ---------------------------------------------------------------------------

def test_watermark_adds_one_text_to_figure(empty_figure):
    before = len(empty_figure.texts)
    watermark(empty_figure)
    assert len(empty_figure.texts) == before + 1


def test_watermark_text_contains_blog_url(empty_figure):
    watermark(empty_figure)
    texts = [t.get_text() for t in empty_figure.texts]
    assert any(BLOG_URL in t for t in texts)


def test_watermark_text_contains_author(empty_figure):
    watermark(empty_figure)
    texts = [t.get_text() for t in empty_figure.texts]
    assert any(AUTHOR in t for t in texts)
