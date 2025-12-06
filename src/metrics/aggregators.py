import pandas as pd
import numpy as np
from .attacking import get_attacking_metrics
from .defensive import get_defensive_metrics
from .possession import get_possession_metrics


def get_season_summary(df: pd.DataFrame) -> dict:
    """Get comprehensive season summary for a team.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary with all summary statistics
    """
    if len(df) == 0:
        return {}

    return {
        "matches_played": len(df),
        "wins": int(df["is_win"].sum()),
        "draws": int(df["is_draw"].sum()),
        "losses": int(df["is_loss"].sum()),
        "total_points": int(df["points"].sum()),
        "points_per_game": round(df["points"].sum() / len(df), 2),
        "goals_scored": int(df["Goal scored"].sum()),
        "goals_conceded": int(df["Goal conceded"].sum()),
        "goal_difference": int(df["Goal scored"].sum() - df["Goal conceded"].sum()),
        "clean_sheets": int(df["is_clean_sheet"].sum()),
        "home_wins": int(df[df["Side"] == "Home"]["is_win"].sum()),
        "away_wins": int(df[df["Side"] == "Away"]["is_win"].sum()),
        **get_attacking_metrics(df),
        **get_defensive_metrics(df),
        **get_possession_metrics(df),
    }


def get_home_away_split(df: pd.DataFrame) -> dict:
    """Get performance split between home and away games.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary with home and away statistics
    """
    home_df = df[df["Side"] == "Home"]
    away_df = df[df["Side"] == "Away"]

    return {
        "home": {
            "matches": len(home_df),
            "wins": int(home_df["is_win"].sum()),
            "draws": int(home_df["is_draw"].sum()),
            "losses": int(home_df["is_loss"].sum()),
            "points": int(home_df["points"].sum()),
            "points_per_game": round(home_df["points"].sum() / len(home_df), 2) if len(home_df) > 0 else 0,
            "goals_scored": int(home_df["Goal scored"].sum()),
            "goals_conceded": int(home_df["Goal conceded"].sum()),
            "clean_sheets": int(home_df["is_clean_sheet"].sum()),
            "avg_possession": round(home_df["possession_pct"].mean(), 1) if len(home_df) > 0 else 0,
        },
        "away": {
            "matches": len(away_df),
            "wins": int(away_df["is_win"].sum()),
            "draws": int(away_df["is_draw"].sum()),
            "losses": int(away_df["is_loss"].sum()),
            "points": int(away_df["points"].sum()),
            "points_per_game": round(away_df["points"].sum() / len(away_df), 2) if len(away_df) > 0 else 0,
            "goals_scored": int(away_df["Goal scored"].sum()),
            "goals_conceded": int(away_df["Goal conceded"].sum()),
            "clean_sheets": int(away_df["is_clean_sheet"].sum()),
            "avg_possession": round(away_df["possession_pct"].mean(), 1) if len(away_df) > 0 else 0,
        },
    }


def get_form(df: pd.DataFrame, last_n: int = 5) -> dict:
    """Get recent form for last N games.

    Args:
        df: DataFrame sorted by date (most recent last)
        last_n: Number of recent games to analyze

    Returns:
        Dictionary with form statistics
    """
    recent = df.tail(last_n)

    # Create form string (W/D/L)
    form_list = []
    for _, row in recent.iterrows():
        if row["is_win"] == 1:
            form_list.append("W")
        elif row["is_draw"] == 1:
            form_list.append("D")
        else:
            form_list.append("L")

    return {
        "form_string": "".join(form_list),
        "form_list": form_list,
        "points": int(recent["points"].sum()),
        "max_points": last_n * 3,
        "goals_scored": int(recent["Goal scored"].sum()),
        "goals_conceded": int(recent["Goal conceded"].sum()),
        "wins": int(recent["is_win"].sum()),
        "draws": int(recent["is_draw"].sum()),
        "losses": int(recent["is_loss"].sum()),
    }


def calculate_league_position(df: pd.DataFrame, season: str = None) -> pd.DataFrame:
    """Calculate league table/positions.

    Args:
        df: Full DataFrame
        season: Optional season filter

    Returns:
        DataFrame with league standings
    """
    if season:
        df = df[df["season"] == season]

    # Aggregate by team
    standings = df.groupby("Team").agg({
        "points": "sum",
        "Goal scored": "sum",
        "Goal conceded": "sum",
        "is_win": "sum",
        "is_draw": "sum",
        "is_loss": "sum",
    }).reset_index()

    standings.columns = ["Team", "Points", "GF", "GA", "W", "D", "L"]
    standings["GD"] = standings["GF"] - standings["GA"]
    standings["P"] = standings["W"] + standings["D"] + standings["L"]

    # Sort by points, then goal difference, then goals scored
    standings = standings.sort_values(
        ["Points", "GD", "GF"],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    standings["Position"] = standings.index + 1

    # Ensure all columns have correct data types
    result = standings[["Position", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Points"]].copy()

    # Convert numeric columns to int to avoid mixed types
    for col in ["Position", "P", "W", "D", "L", "GF", "GA", "GD", "Points"]:
        result[col] = result[col].astype(int)

    # Ensure Team column is string type
    result["Team"] = result["Team"].astype(str)

    return result
