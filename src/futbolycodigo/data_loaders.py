"""Data loading utilities for StatsBomb and other football data sources."""

from pathlib import Path

import pandas as pd
from statsbombpy import sb

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_CACHE_DIR = _PROJECT_ROOT / "data" / ".cache"


def get_match_events(
    match_id: int,
    *,
    cache: bool = True,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Load match events from StatsBomb Open Data.

    Args:
        match_id: StatsBomb match identifier.
        cache: If True, reads from and writes to local parquet cache.
        force_refresh: If True and cache=True, re-downloads and overwrites cache.

    Returns:
        DataFrame with all events for the match.
    """
    cache_path = _CACHE_DIR / f"events_{match_id}.parquet"

    if cache and not force_refresh and cache_path.exists():
        return pd.read_parquet(cache_path)

    events = sb.events(match_id=match_id)

    if cache:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        events.to_parquet(cache_path, index=False)

    return events


def get_competition_matches(
    competition_id: int,
    season_id: int,
    *,
    cache: bool = True,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Load all matches for a competition/season from StatsBomb.

    Args:
        competition_id: StatsBomb competition identifier.
        season_id: StatsBomb season identifier.
        cache: If True, reads from and writes to local parquet cache.
        force_refresh: If True and cache=True, re-downloads and overwrites cache.

    Returns:
        DataFrame with all matches for the competition and season.
    """
    cache_path = _CACHE_DIR / f"matches_{competition_id}_{season_id}.parquet"

    if cache and not force_refresh and cache_path.exists():
        return pd.read_parquet(cache_path)

    matches = sb.matches(competition_id=competition_id, season_id=season_id)

    if cache:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        matches.to_parquet(cache_path, index=False)

    return matches


def get_season_events(
    competition_id: int,
    season_id: int,
) -> pd.DataFrame:
    """Load all events for every match in a competition/season.

    Uses match-level cache from get_match_events. Heavy operation on first run;
    subsequent calls are fast once individual match caches are populated.

    Args:
        competition_id: StatsBomb competition identifier.
        season_id: StatsBomb season identifier.

    Returns:
        DataFrame with all events for the full season, concatenated.
    """
    matches = get_competition_matches(competition_id, season_id, cache=True)
    all_events = [
        get_match_events(match_id, cache=True)
        for match_id in matches["match_id"]
    ]
    return pd.concat(all_events, ignore_index=True)
