import pandas as pd
import numpy as np


def average_possession(df: pd.DataFrame) -> float:
    """Calculate average possession percentage."""
    if len(df) == 0:
        return 0.0
    return df["possession_pct"].mean()


def passes_per_game(df: pd.DataFrame) -> float:
    """Calculate average passes per game."""
    if len(df) == 0:
        return 0.0
    return df["Passes"].sum() / len(df)


def pass_accuracy(df: pd.DataFrame) -> float:
    """Calculate average pass accuracy percentage."""
    if len(df) == 0 or "Accurate passes_pct" not in df.columns:
        return 0.0
    return df["Accurate passes_pct"].mean() * 100


def opposition_half_passes_per_game(df: pd.DataFrame) -> float:
    """Calculate average passes in opposition half per game."""
    if len(df) == 0:
        return 0.0
    return df["Opposition half"].sum() / len(df)


def own_half_passes_per_game(df: pd.DataFrame) -> float:
    """Calculate average passes in own half per game."""
    if len(df) == 0:
        return 0.0
    return df["Own half"].sum() / len(df)


def long_ball_accuracy(df: pd.DataFrame) -> float:
    """Calculate average long ball accuracy percentage."""
    if len(df) == 0 or "Accurate long balls_pct" not in df.columns:
        return 0.0
    return df["Accurate long balls_pct"].mean() * 100


def cross_accuracy(df: pd.DataFrame) -> float:
    """Calculate average cross accuracy percentage."""
    if len(df) == 0 or "Accurate crosses_pct" not in df.columns:
        return 0.0
    return df["Accurate crosses_pct"].mean() * 100


def touches_in_box_per_game(df: pd.DataFrame) -> float:
    """Calculate average touches in opposition box per game."""
    if len(df) == 0:
        return 0.0
    return df["Touches in opposition box"].sum() / len(df)


def corners_per_game(df: pd.DataFrame) -> float:
    """Calculate average corners per game."""
    if len(df) == 0:
        return 0.0
    return df["Corners"].sum() / len(df)


def successful_dribbles_per_game(df: pd.DataFrame) -> float:
    """Calculate average successful dribbles per game."""
    if len(df) == 0 or "Successful dribbles_count" not in df.columns:
        return 0.0
    return df["Successful dribbles_count"].sum() / len(df)


def get_possession_metrics(df: pd.DataFrame) -> dict:
    """Get all possession and passing metrics for a team.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary of possession metrics
    """
    return {
        "matches": len(df),
        "avg_possession": round(average_possession(df), 1),
        "passes_per_game": round(passes_per_game(df), 0),
        "pass_accuracy_pct": round(pass_accuracy(df), 1),
        "opp_half_passes_per_game": round(opposition_half_passes_per_game(df), 0),
        "own_half_passes_per_game": round(own_half_passes_per_game(df), 0),
        "long_ball_accuracy_pct": round(long_ball_accuracy(df), 1),
        "cross_accuracy_pct": round(cross_accuracy(df), 1),
        "touches_in_box_per_game": round(touches_in_box_per_game(df), 1),
        "corners_per_game": round(corners_per_game(df), 1),
        "successful_dribbles_per_game": round(successful_dribbles_per_game(df), 1),
        "total_passes": int(df["Passes"].sum()),
        "total_corners": int(df["Corners"].sum()),
    }


def get_possession_comparison(df: pd.DataFrame, teams: list) -> pd.DataFrame:
    """Get possession metrics comparison for multiple teams.

    Args:
        df: Full DataFrame
        teams: List of team names

    Returns:
        DataFrame with metrics as rows and teams as columns
    """
    results = {}
    for team in teams:
        team_df = df[df["Team"] == team]
        results[team] = get_possession_metrics(team_df)

    return pd.DataFrame(results)


# ===========================================
# POSSESSION EFFECTIVENESS METRICS
# ===========================================

def get_possession_effectiveness(df: pd.DataFrame) -> dict:
    """Analyze how effectively possession translates to results.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary of possession effectiveness metrics
    """
    if len(df) == 0:
        return {}

    # Possession categories
    high_poss = df[df["possession_pct"] >= 55]
    medium_poss = df[(df["possession_pct"] >= 45) & (df["possession_pct"] < 55)]
    low_poss = df[df["possession_pct"] < 45]

    # Points per game by possession level
    high_poss_ppg = high_poss["points"].sum() / len(high_poss) if len(high_poss) > 0 else 0
    medium_poss_ppg = medium_poss["points"].sum() / len(medium_poss) if len(medium_poss) > 0 else 0
    low_poss_ppg = low_poss["points"].sum() / len(low_poss) if len(low_poss) > 0 else 0

    # Win rates by possession level
    high_poss_win_rate = (high_poss["is_win"].sum() / len(high_poss)) * 100 if len(high_poss) > 0 else 0
    low_poss_win_rate = (low_poss["is_win"].sum() / len(low_poss)) * 100 if len(low_poss) > 0 else 0

    # xG efficiency per possession point
    total_xg = df["Expected goals (xG)"].sum()
    avg_possession = df["possession_pct"].mean()
    xg_per_possession_pct = total_xg / (avg_possession * len(df)) if avg_possession > 0 else 0

    # Touches to xG efficiency
    total_touches = df["Touches in opposition box"].sum()
    touches_per_xg = total_touches / total_xg if total_xg > 0 else 0

    return {
        "high_possession_games": len(high_poss),
        "high_possession_ppg": round(high_poss_ppg, 2),
        "high_possession_win_rate": round(high_poss_win_rate, 1),
        "medium_possession_games": len(medium_poss),
        "medium_possession_ppg": round(medium_poss_ppg, 2),
        "low_possession_games": len(low_poss),
        "low_possession_ppg": round(low_poss_ppg, 2),
        "low_possession_win_rate": round(low_poss_win_rate, 1),
        "xg_per_possession_pct": round(xg_per_possession_pct, 3),
        "touches_per_xg": round(touches_per_xg, 1),
        "better_with_possession": high_poss_ppg > low_poss_ppg,
        "possession_differential": round(high_poss_ppg - low_poss_ppg, 2),
    }


def get_possession_vs_results(df: pd.DataFrame) -> pd.DataFrame:
    """Get detailed possession vs results data for visualization.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        DataFrame with possession category stats
    """
    if len(df) == 0:
        return pd.DataFrame()

    results = []

    # Define possession brackets
    brackets = [
        ("Very Low (<40%)", 0, 40),
        ("Low (40-45%)", 40, 45),
        ("Medium (45-55%)", 45, 55),
        ("High (55-60%)", 55, 60),
        ("Very High (>60%)", 60, 100),
    ]

    for label, low, high in brackets:
        bracket_df = df[(df["possession_pct"] >= low) & (df["possession_pct"] < high)]
        if len(bracket_df) > 0:
            results.append({
                "Possession Range": label,
                "Games": len(bracket_df),
                "Wins": int(bracket_df["is_win"].sum()),
                "Draws": int(bracket_df["is_draw"].sum()),
                "Losses": int(bracket_df["is_loss"].sum()),
                "Win %": round((bracket_df["is_win"].sum() / len(bracket_df)) * 100, 1),
                "PPG": round(bracket_df["points"].sum() / len(bracket_df), 2),
                "Avg xG": round(bracket_df["Expected goals (xG)"].mean(), 2),
                "Avg Goals": round(bracket_df["Goal scored"].mean(), 2),
            })

    return pd.DataFrame(results)


def get_possession_tactical_insights(team_df: pd.DataFrame, comparison_df: pd.DataFrame, team_name: str, comparison_name: str) -> list:
    """Generate actionable insights about possession effectiveness.

    Args:
        team_df: DataFrame for the main team
        comparison_df: DataFrame for the comparison team
        team_name: Name of the main team
        comparison_name: Name of the comparison team

    Returns:
        List of insight dictionaries
    """
    insights = []

    team_eff = get_possession_effectiveness(team_df)
    comp_eff = get_possession_effectiveness(comparison_df)

    # Counter-attack vs possession-based effectiveness
    if not team_eff.get("better_with_possession", True):
        insights.append({
            "title": "Counter-Attack Style More Effective",
            "finding": f"{team_name} earns {team_eff['low_possession_ppg']} PPG with low possession vs {team_eff['high_possession_ppg']} PPG with high possession",
            "action": "Consider tactical shift towards counter-attacking style",
            "severity": "high",
        })

    # Possession efficiency gap
    team_xg_eff = team_eff.get("xg_per_possession_pct", 0)
    comp_xg_eff = comp_eff.get("xg_per_possession_pct", 0)
    if team_xg_eff < comp_xg_eff * 0.8:
        insights.append({
            "title": "Possession Efficiency Gap",
            "finding": f"{team_name}: {team_xg_eff:.3f} xG per possession % vs {comparison_name}: {comp_xg_eff:.3f}",
            "action": "Possession is not translating to chances - work on final third penetration",
            "severity": "medium",
        })

    # High possession underperformance
    if team_eff.get("high_possession_win_rate", 0) < 50 and team_eff.get("high_possession_games", 0) >= 5:
        insights.append({
            "title": "High Possession Not Converting to Wins",
            "finding": f"{team_name} wins only {team_eff['high_possession_win_rate']}% when dominating possession (>55%)",
            "action": "Add more directness and urgency when in control of possession",
            "severity": "high",
        })

    return insights
