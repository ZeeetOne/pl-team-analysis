import pandas as pd
import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import DATASETS_DIR, SEASON_FILES


@st.cache_data
def load_season_data(season: str) -> pd.DataFrame:
    """Load a single season's CSV file.

    Args:
        season: Season identifier (e.g., "2023-2024")

    Returns:
        DataFrame with raw season data
    """
    if season not in SEASON_FILES:
        raise ValueError(f"Unknown season: {season}. Available: {list(SEASON_FILES.keys())}")

    file_path = SEASON_FILES[season]
    df = pd.read_csv(file_path)
    df["season"] = season
    return df


@st.cache_data
def load_all_seasons() -> pd.DataFrame:
    """Load and concatenate all available seasons.

    Returns:
        DataFrame with all seasons combined
    """
    dfs = []
    for season in SEASON_FILES.keys():
        df = load_season_data(season)
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


def get_team_data(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Filter data for a specific team.

    Args:
        df: DataFrame with match data
        team: Team name to filter for

    Returns:
        DataFrame filtered to the specified team
    """
    return df[df["Team"] == team].copy()


def get_comparison_data(df: pd.DataFrame, teams: list) -> pd.DataFrame:
    """Get data for multiple teams for comparison.

    Args:
        df: DataFrame with match data
        teams: List of team names

    Returns:
        DataFrame filtered to the specified teams
    """
    return df[df["Team"].isin(teams)].copy()


def get_available_teams(df: pd.DataFrame) -> list:
    """Get list of all teams in the dataset.

    Args:
        df: DataFrame with match data

    Returns:
        Sorted list of team names
    """
    return sorted(df["Team"].unique().tolist())


def get_available_seasons(df: pd.DataFrame) -> list:
    """Get list of all seasons in the dataset.

    Args:
        df: DataFrame with match data

    Returns:
        List of season identifiers
    """
    return df["season"].unique().tolist()
