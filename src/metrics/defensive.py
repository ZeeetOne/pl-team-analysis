import pandas as pd
import numpy as np


def goals_conceded_per_game(df: pd.DataFrame) -> float:
    """Calculate average goals conceded per game."""
    if len(df) == 0:
        return 0.0
    return df["Goal conceded"].sum() / len(df)


def clean_sheets(df: pd.DataFrame) -> int:
    """Count total clean sheets."""
    return int((df["Goal conceded"] == 0).sum())


def clean_sheet_percentage(df: pd.DataFrame) -> float:
    """Calculate clean sheet percentage."""
    if len(df) == 0:
        return 0.0
    return (clean_sheets(df) / len(df)) * 100


def tackles_per_game(df: pd.DataFrame) -> float:
    """Calculate average tackles per game."""
    if len(df) == 0:
        return 0.0
    return df["Tackles"].sum() / len(df)


def interceptions_per_game(df: pd.DataFrame) -> float:
    """Calculate average interceptions per game."""
    if len(df) == 0:
        return 0.0
    return df["Interceptions"].sum() / len(df)


def blocks_per_game(df: pd.DataFrame) -> float:
    """Calculate average blocks per game."""
    if len(df) == 0:
        return 0.0
    return df["Blocks"].sum() / len(df)


def clearances_per_game(df: pd.DataFrame) -> float:
    """Calculate average clearances per game."""
    if len(df) == 0:
        return 0.0
    return df["Clearances"].sum() / len(df)


def defensive_actions_per_game(df: pd.DataFrame) -> float:
    """Calculate total defensive actions per game."""
    if len(df) == 0:
        return 0.0
    total = (
        df["Tackles"].sum() +
        df["Interceptions"].sum() +
        df["Blocks"].sum() +
        df["Clearances"].sum()
    )
    return total / len(df)


def saves_per_game(df: pd.DataFrame) -> float:
    """Calculate average keeper saves per game."""
    if len(df) == 0:
        return 0.0
    return df["Keeper saves"].sum() / len(df)


def duels_won_percentage(df: pd.DataFrame) -> float:
    """Calculate average duels won percentage."""
    if len(df) == 0 or "Duels won_pct" not in df.columns:
        return 0.0
    return df["Duels won_pct"].mean() * 100


def get_defensive_metrics(df: pd.DataFrame) -> dict:
    """Get all defensive metrics for a team.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary of defensive metrics
    """
    return {
        "matches": len(df),
        "total_goals_conceded": int(df["Goal conceded"].sum()),
        "goals_conceded_per_game": round(goals_conceded_per_game(df), 2),
        "clean_sheets": clean_sheets(df),
        "clean_sheet_pct": round(clean_sheet_percentage(df), 1),
        "tackles_per_game": round(tackles_per_game(df), 1),
        "interceptions_per_game": round(interceptions_per_game(df), 1),
        "blocks_per_game": round(blocks_per_game(df), 1),
        "clearances_per_game": round(clearances_per_game(df), 1),
        "defensive_actions_per_game": round(defensive_actions_per_game(df), 1),
        "saves_per_game": round(saves_per_game(df), 1),
        "total_tackles": int(df["Tackles"].sum()),
        "total_interceptions": int(df["Interceptions"].sum()),
        "total_blocks": int(df["Blocks"].sum()),
        "total_clearances": int(df["Clearances"].sum()),
    }


def get_defensive_comparison(df: pd.DataFrame, teams: list) -> pd.DataFrame:
    """Get defensive metrics comparison for multiple teams.

    Args:
        df: Full DataFrame
        teams: List of team names

    Returns:
        DataFrame with metrics as rows and teams as columns
    """
    results = {}
    for team in teams:
        team_df = df[df["Team"] == team]
        results[team] = get_defensive_metrics(team_df)

    return pd.DataFrame(results)
