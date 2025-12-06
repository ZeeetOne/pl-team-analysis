import pandas as pd
import numpy as np
import re
from datetime import datetime


def parse_percentage_string(value: str) -> tuple:
    """Parse strings like '408 (85%)' into (count, percentage).

    Args:
        value: String in format 'N (P%)'

    Returns:
        Tuple of (count, percentage as decimal)
    """
    if pd.isna(value) or value == "" or value is None:
        return (0, 0.0)

    value_str = str(value).strip()

    # Pattern for "408 (85%)"
    match = re.match(r"(\d+)\s*\((\d+)%\)", value_str)
    if match:
        count = int(match.group(1))
        percentage = float(match.group(2)) / 100
        return (count, percentage)

    # If just a number
    try:
        return (int(float(value_str)), 0.0)
    except (ValueError, TypeError):
        return (0, 0.0)


def parse_possession(value: str) -> float:
    """Parse possession string like '55%' to float.

    Args:
        value: String in format 'N%'

    Returns:
        Float value (e.g., 55.0)
    """
    if pd.isna(value) or value == "" or value is None:
        return 0.0

    value_str = str(value).strip()

    # Remove % sign and convert
    match = re.match(r"(\d+(?:\.\d+)?)\s*%?", value_str)
    if match:
        return float(match.group(1))

    return 0.0


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object.

    Args:
        date_str: Date string like 'Saturday, August 12, 2023'

    Returns:
        datetime object
    """
    if pd.isna(date_str):
        return None

    try:
        # Format: "Saturday, August 12, 2023"
        return datetime.strptime(date_str.strip(), "%A, %B %d, %Y")
    except ValueError:
        return None


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all preprocessing steps to the raw data.

    Args:
        df: Raw DataFrame from CSV

    Returns:
        Preprocessed DataFrame with parsed columns and calculated fields
    """
    df = df.copy()

    # Parse date column
    df["date_parsed"] = df["Date"].apply(parse_date)

    # Parse possession
    df["possession_pct"] = df["Ball possession"].apply(parse_possession)

    # Parse percentage columns (count and percentage)
    percentage_columns = [
        "Accurate passes",
        "Accurate long balls",
        "Accurate crosses",
        "Duels won",
        "Ground duels won",
        "Aerial duels won",
        "Successful dribbles",
    ]

    for col in percentage_columns:
        if col in df.columns:
            parsed = df[col].apply(parse_percentage_string)
            df[f"{col}_count"] = parsed.apply(lambda x: x[0])
            df[f"{col}_pct"] = parsed.apply(lambda x: x[1])

    # Convert numeric columns
    numeric_cols = [
        "Goal scored", "Goal conceded", "points", "Round",
        "Expected goals (xG)", "Total shots", "Shots on target",
        "Big chances", "Big chances missed", "Fouls committed",
        "Corners", "xG open play", "xG set play", "Non-penalty xG",
        "xG on target (xGOT)", "Shots off target", "Blocked shots",
        "Hit woodwork", "Shots inside box", "Shots outside box",
        "Passes", "Own half", "Opposition half", "Throws",
        "Touches in opposition box", "Offsides", "Yellow cards",
        "Red cards", "Tackles", "Interceptions", "Blocks",
        "Clearances", "Keeper saves",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Add calculated columns
    df = add_calculated_columns(df)

    # Sort by date and round
    df = df.sort_values(["season", "Round", "date_parsed"]).reset_index(drop=True)

    return df


def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived metrics to the DataFrame.

    Args:
        df: DataFrame with parsed columns

    Returns:
        DataFrame with additional calculated columns
    """
    # xG-based metrics
    df["xg_difference"] = df["Goal scored"] - df["Expected goals (xG)"]

    # Shot metrics
    df["shot_conversion_pct"] = np.where(
        df["Total shots"] > 0,
        (df["Goal scored"] / df["Total shots"]) * 100,
        0
    )

    df["shots_on_target_pct"] = np.where(
        df["Total shots"] > 0,
        (df["Shots on target"] / df["Total shots"]) * 100,
        0
    )

    df["big_chance_conversion_pct"] = np.where(
        df["Big chances"] > 0,
        ((df["Big chances"] - df["Big chances missed"]) / df["Big chances"]) * 100,
        0
    )

    df["shots_inside_box_pct"] = np.where(
        df["Total shots"] > 0,
        (df["Shots inside box"] / df["Total shots"]) * 100,
        0
    )

    # Result flags
    df["is_win"] = (df["points"] == 3).astype(int)
    df["is_draw"] = (df["points"] == 1).astype(int)
    df["is_loss"] = (df["points"] == 0).astype(int)
    df["is_clean_sheet"] = (df["Goal conceded"] == 0).astype(int)

    # Goal difference
    df["goal_difference"] = df["Goal scored"] - df["Goal conceded"]

    # Defensive actions
    df["defensive_actions"] = (
        df["Tackles"] + df["Interceptions"] +
        df["Blocks"] + df["Clearances"]
    )

    # Passing in opposition half percentage
    df["opp_half_passes_pct"] = np.where(
        df["Passes"] > 0,
        (df["Opposition half"] / df["Passes"]) * 100,
        0
    )

    # ===========================================
    # TACTICAL METRICS - Set Piece & Shot Quality
    # ===========================================

    # Set piece analysis - xG breakdown by source
    df["xg_open_play_ratio"] = np.where(
        df["Expected goals (xG)"] > 0,
        df["xG open play"] / df["Expected goals (xG)"],
        0
    )
    df["xg_set_play_ratio"] = np.where(
        df["Expected goals (xG)"] > 0,
        df["xG set play"] / df["Expected goals (xG)"],
        0
    )

    # Shot quality metrics
    df["xg_per_shot"] = np.where(
        df["Total shots"] > 0,
        df["Expected goals (xG)"] / df["Total shots"],
        0
    )

    df["woodwork_rate"] = np.where(
        df["Total shots"] > 0,
        (df["Hit woodwork"] / df["Total shots"]) * 100,
        0
    )

    df["blocked_shot_rate"] = np.where(
        df["Total shots"] > 0,
        (df["Blocked shots"] / df["Total shots"]) * 100,
        0
    )

    df["shots_off_target_rate"] = np.where(
        df["Total shots"] > 0,
        (df["Shots off target"] / df["Total shots"]) * 100,
        0
    )

    # Possession category for effectiveness analysis
    df["possession_category"] = pd.cut(
        df["possession_pct"],
        bins=[0, 45, 55, 100],
        labels=["Low (<45%)", "Medium (45-55%)", "High (>55%)"]
    )

    return df


def filter_by_season(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Filter data by season.

    Args:
        df: DataFrame with season column
        season: Season to filter for

    Returns:
        Filtered DataFrame
    """
    return df[df["season"] == season].copy()
