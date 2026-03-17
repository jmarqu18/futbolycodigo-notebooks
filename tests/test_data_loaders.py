"""Tests for futbolycodigo.data_loaders — written before implementation (TDD)."""

import pandas as pd
import pytest
from unittest.mock import patch

import futbolycodigo.data_loaders as dl

# ---------------------------------------------------------------------------
# Shared fixtures and constants
# ---------------------------------------------------------------------------

FAKE_MATCH_ID = 9999
FAKE_COMP_ID = 55
FAKE_SEASON_ID = 43

FAKE_EVENTS = pd.DataFrame({"event_type": ["pass", "shot"], "player": ["A", "B"]})
FAKE_MATCHES = pd.DataFrame({"match_id": [1, 2, 3], "home_team": ["X", "Y", "Z"]})


@pytest.fixture(autouse=True)
def patch_cache_dir(tmp_path, monkeypatch):
    """Redirect _CACHE_DIR to a temp directory so tests never touch data/.cache."""
    monkeypatch.setattr(dl, "_CACHE_DIR", tmp_path / ".cache")


# ---------------------------------------------------------------------------
# get_match_events
# ---------------------------------------------------------------------------


@patch("futbolycodigo.data_loaders.sb.events")
def test_events_calls_sb_when_cache_disabled(mock_events):
    mock_events.return_value = FAKE_EVENTS.copy()

    result = dl.get_match_events(FAKE_MATCH_ID, cache=False)

    mock_events.assert_called_once_with(match_id=FAKE_MATCH_ID)
    assert len(result) == 2


@patch("futbolycodigo.data_loaders.sb.events")
def test_events_writes_parquet_on_first_cached_call(mock_events):
    mock_events.return_value = FAKE_EVENTS.copy()

    dl.get_match_events(FAKE_MATCH_ID, cache=True)

    cache_path = dl._CACHE_DIR / f"events_{FAKE_MATCH_ID}.parquet"
    assert cache_path.exists()


@patch("futbolycodigo.data_loaders.sb.events")
def test_events_reads_parquet_on_second_call_without_network(mock_events):
    mock_events.return_value = FAKE_EVENTS.copy()

    dl.get_match_events(FAKE_MATCH_ID, cache=True)  # first call — writes cache
    dl.get_match_events(FAKE_MATCH_ID, cache=True)  # second call — must use cache

    assert mock_events.call_count == 1  # sb.events called only once


@patch("futbolycodigo.data_loaders.sb.events")
def test_events_force_refresh_redownloads_even_with_existing_cache(mock_events):
    mock_events.return_value = FAKE_EVENTS.copy()

    dl.get_match_events(FAKE_MATCH_ID, cache=True)                          # writes cache
    dl.get_match_events(FAKE_MATCH_ID, cache=True, force_refresh=True)      # must re-download

    assert mock_events.call_count == 2


@patch("futbolycodigo.data_loaders.sb.events")
def test_events_cache_false_never_writes_parquet(mock_events):
    mock_events.return_value = FAKE_EVENTS.copy()

    dl.get_match_events(FAKE_MATCH_ID, cache=False)

    cache_path = dl._CACHE_DIR / f"events_{FAKE_MATCH_ID}.parquet"
    assert not cache_path.exists()


# ---------------------------------------------------------------------------
# get_competition_matches
# ---------------------------------------------------------------------------


@patch("futbolycodigo.data_loaders.sb.matches")
def test_competition_matches_calls_sb_when_cache_disabled(mock_matches):
    mock_matches.return_value = FAKE_MATCHES.copy()

    result = dl.get_competition_matches(FAKE_COMP_ID, FAKE_SEASON_ID, cache=False)

    mock_matches.assert_called_once_with(
        competition_id=FAKE_COMP_ID, season_id=FAKE_SEASON_ID
    )
    assert len(result) == 3


@patch("futbolycodigo.data_loaders.sb.matches")
def test_competition_matches_reads_parquet_on_second_call(mock_matches):
    mock_matches.return_value = FAKE_MATCHES.copy()

    dl.get_competition_matches(FAKE_COMP_ID, FAKE_SEASON_ID, cache=True)
    dl.get_competition_matches(FAKE_COMP_ID, FAKE_SEASON_ID, cache=True)

    assert mock_matches.call_count == 1


@patch("futbolycodigo.data_loaders.sb.matches")
def test_competition_matches_force_refresh_redownloads(mock_matches):
    mock_matches.return_value = FAKE_MATCHES.copy()

    dl.get_competition_matches(FAKE_COMP_ID, FAKE_SEASON_ID, cache=True)
    dl.get_competition_matches(
        FAKE_COMP_ID, FAKE_SEASON_ID, cache=True, force_refresh=True
    )

    assert mock_matches.call_count == 2


@patch("futbolycodigo.data_loaders.sb.matches")
def test_competition_matches_writes_parquet_with_correct_key(mock_matches):
    mock_matches.return_value = FAKE_MATCHES.copy()

    dl.get_competition_matches(FAKE_COMP_ID, FAKE_SEASON_ID, cache=True)

    cache_path = dl._CACHE_DIR / f"matches_{FAKE_COMP_ID}_{FAKE_SEASON_ID}.parquet"
    assert cache_path.exists()


# ---------------------------------------------------------------------------
# get_season_events
# ---------------------------------------------------------------------------


@patch("futbolycodigo.data_loaders.get_match_events")
@patch("futbolycodigo.data_loaders.get_competition_matches")
def test_season_events_concatenates_events_for_all_matches(
    mock_get_matches, mock_get_events
):
    mock_get_matches.return_value = pd.DataFrame({"match_id": [1, 2]})
    mock_get_events.return_value = FAKE_EVENTS.copy()  # 2 rows each

    result = dl.get_season_events(FAKE_COMP_ID, FAKE_SEASON_ID)

    assert mock_get_events.call_count == 2
    assert len(result) == 4  # 2 matches × 2 events


@patch("futbolycodigo.data_loaders.get_match_events")
@patch("futbolycodigo.data_loaders.get_competition_matches")
def test_season_events_calls_underlying_functions_with_cache_enabled(
    mock_get_matches, mock_get_events
):
    mock_get_matches.return_value = pd.DataFrame({"match_id": [1]})
    mock_get_events.return_value = FAKE_EVENTS.copy()

    dl.get_season_events(FAKE_COMP_ID, FAKE_SEASON_ID)

    mock_get_matches.assert_called_once_with(FAKE_COMP_ID, FAKE_SEASON_ID, cache=True)
    mock_get_events.assert_called_once_with(1, cache=True)
