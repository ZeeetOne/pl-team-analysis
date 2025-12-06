import pandas as pd
import numpy as np


def goals_per_game(df: pd.DataFrame) -> float:
    """Calculate average goals scored per game."""
    if len(df) == 0:
        return 0.0
    return df["Goal scored"].sum() / len(df)


def xg_per_game(df: pd.DataFrame) -> float:
    """Calculate average xG per game."""
    if len(df) == 0:
        return 0.0
    return df["Expected goals (xG)"].sum() / len(df)


def xg_overperformance(df: pd.DataFrame) -> float:
    """Calculate total goals minus total xG (positive = overperforming)."""
    return df["Goal scored"].sum() - df["Expected goals (xG)"].sum()


def xg_overperformance_per_game(df: pd.DataFrame) -> float:
    """Calculate average xG overperformance per game."""
    if len(df) == 0:
        return 0.0
    return xg_overperformance(df) / len(df)


def shot_conversion_rate(df: pd.DataFrame) -> float:
    """Calculate overall shot conversion percentage."""
    total_shots = df["Total shots"].sum()
    if total_shots == 0:
        return 0.0
    return (df["Goal scored"].sum() / total_shots) * 100


def shots_on_target_rate(df: pd.DataFrame) -> float:
    """Calculate shots on target percentage."""
    total_shots = df["Total shots"].sum()
    if total_shots == 0:
        return 0.0
    return (df["Shots on target"].sum() / total_shots) * 100


def big_chance_conversion_rate(df: pd.DataFrame) -> float:
    """Calculate big chance conversion percentage."""
    big_chances = df["Big chances"].sum()
    if big_chances == 0:
        return 0.0
    scored = big_chances - df["Big chances missed"].sum()
    return (scored / big_chances) * 100


def shots_per_game(df: pd.DataFrame) -> float:
    """Calculate average total shots per game."""
    if len(df) == 0:
        return 0.0
    return df["Total shots"].sum() / len(df)


def shots_on_target_per_game(df: pd.DataFrame) -> float:
    """Calculate average shots on target per game."""
    if len(df) == 0:
        return 0.0
    return df["Shots on target"].sum() / len(df)


def big_chances_per_game(df: pd.DataFrame) -> float:
    """Calculate average big chances created per game."""
    if len(df) == 0:
        return 0.0
    return df["Big chances"].sum() / len(df)


def xgot_per_game(df: pd.DataFrame) -> float:
    """Calculate average xG on target per game."""
    if len(df) == 0:
        return 0.0
    return df["xG on target (xGOT)"].sum() / len(df)


def shots_inside_box_rate(df: pd.DataFrame) -> float:
    """Calculate percentage of shots from inside the box."""
    total_shots = df["Total shots"].sum()
    if total_shots == 0:
        return 0.0
    return (df["Shots inside box"].sum() / total_shots) * 100


def get_attacking_metrics(df: pd.DataFrame) -> dict:
    """Get all attacking metrics for a team.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary of attacking metrics
    """
    return {
        "matches": len(df),
        "total_goals": int(df["Goal scored"].sum()),
        "total_xg": round(df["Expected goals (xG)"].sum(), 2),
        "goals_per_game": round(goals_per_game(df), 2),
        "xg_per_game": round(xg_per_game(df), 2),
        "xg_overperformance": round(xg_overperformance(df), 2),
        "xg_overperformance_per_game": round(xg_overperformance_per_game(df), 2),
        "shot_conversion_pct": round(shot_conversion_rate(df), 1),
        "shots_on_target_pct": round(shots_on_target_rate(df), 1),
        "big_chance_conversion_pct": round(big_chance_conversion_rate(df), 1),
        "shots_per_game": round(shots_per_game(df), 1),
        "shots_on_target_per_game": round(shots_on_target_per_game(df), 1),
        "big_chances_per_game": round(big_chances_per_game(df), 2),
        "xgot_per_game": round(xgot_per_game(df), 2),
        "shots_inside_box_pct": round(shots_inside_box_rate(df), 1),
        "total_big_chances": int(df["Big chances"].sum()),
        "total_big_chances_missed": int(df["Big chances missed"].sum()),
    }


def get_attacking_comparison(df: pd.DataFrame, teams: list) -> pd.DataFrame:
    """Get attacking metrics comparison for multiple teams.

    Args:
        df: Full DataFrame
        teams: List of team names

    Returns:
        DataFrame with metrics as rows and teams as columns
    """
    results = {}
    for team in teams:
        team_df = df[df["Team"] == team]
        results[team] = get_attacking_metrics(team_df)

    return pd.DataFrame(results)


# ===========================================
# TACTICAL METRICS - Set Piece & Shot Quality
# ===========================================

def get_set_piece_metrics(df: pd.DataFrame) -> dict:
    """Get set piece analysis metrics for a team.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary of set piece metrics
    """
    if len(df) == 0:
        return {}

    total_xg = df["Expected goals (xG)"].sum()
    xg_set_play = df["xG set play"].sum()
    xg_open_play = df["xG open play"].sum()
    corners = df["Corners"].sum()

    return {
        "xg_from_set_pieces": round(xg_set_play, 2),
        "xg_from_open_play": round(xg_open_play, 2),
        "set_piece_xg_pct": round((xg_set_play / total_xg) * 100, 1) if total_xg > 0 else 0,
        "open_play_xg_pct": round((xg_open_play / total_xg) * 100, 1) if total_xg > 0 else 0,
        "corners_total": int(corners),
        "corners_per_game": round(corners / len(df), 1),
        "xg_per_corner": round(xg_set_play / corners, 3) if corners > 0 else 0,
        "set_piece_xg_per_game": round(xg_set_play / len(df), 2),
        "open_play_xg_per_game": round(xg_open_play / len(df), 2),
    }


def get_shot_quality_metrics(df: pd.DataFrame) -> dict:
    """Get shot quality breakdown metrics for a team.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary of shot quality metrics
    """
    if len(df) == 0:
        return {}

    total_shots = df["Total shots"].sum()
    total_xg = df["Expected goals (xG)"].sum()
    woodwork = df["Hit woodwork"].sum()
    blocked = df["Blocked shots"].sum()
    off_target = df["Shots off target"].sum()
    on_target = df["Shots on target"].sum()
    goals = df["Goal scored"].sum()

    return {
        "avg_xg_per_shot": round(total_xg / total_shots, 3) if total_shots > 0 else 0,
        "total_shots": int(total_shots),
        "woodwork_total": int(woodwork),
        "woodwork_rate_pct": round((woodwork / total_shots) * 100, 1) if total_shots > 0 else 0,
        "blocked_shots_total": int(blocked),
        "blocked_rate_pct": round((blocked / total_shots) * 100, 1) if total_shots > 0 else 0,
        "off_target_total": int(off_target),
        "off_target_rate_pct": round((off_target / total_shots) * 100, 1) if total_shots > 0 else 0,
        "on_target_total": int(on_target),
        "on_target_rate_pct": round((on_target / total_shots) * 100, 1) if total_shots > 0 else 0,
        "goals_total": int(goals),
        "goal_rate_pct": round((goals / total_shots) * 100, 1) if total_shots > 0 else 0,
        # Estimated unlucky goals (woodwork * avg xG per woodwork hit ~0.5)
        "potential_woodwork_goals": round(woodwork * 0.5, 1),
    }


def get_shot_outcome_breakdown(df: pd.DataFrame) -> dict:
    """Get shot outcome breakdown for visualization.

    Args:
        df: DataFrame filtered to a specific team

    Returns:
        Dictionary with shot outcome counts and percentages
    """
    if len(df) == 0:
        return {}

    total_shots = df["Total shots"].sum()
    goals = df["Goal scored"].sum()
    saved = df["Shots on target"].sum() - goals  # On target but not goals = saved
    blocked = df["Blocked shots"].sum()
    off_target = df["Shots off target"].sum()
    woodwork = df["Hit woodwork"].sum()

    return {
        "Goals": {"count": int(goals), "pct": round((goals / total_shots) * 100, 1) if total_shots > 0 else 0},
        "Saved": {"count": int(saved), "pct": round((saved / total_shots) * 100, 1) if total_shots > 0 else 0},
        "Blocked": {"count": int(blocked), "pct": round((blocked / total_shots) * 100, 1) if total_shots > 0 else 0},
        "Off Target": {"count": int(off_target), "pct": round((off_target / total_shots) * 100, 1) if total_shots > 0 else 0},
        "Woodwork": {"count": int(woodwork), "pct": round((woodwork / total_shots) * 100, 1) if total_shots > 0 else 0},
    }


def get_tactical_insights(team_df: pd.DataFrame, comparison_df: pd.DataFrame, team_name: str, comparison_name: str) -> list:
    """Generate actionable tactical insights comparing two teams.

    Args:
        team_df: DataFrame for the main team
        comparison_df: DataFrame for the comparison team
        team_name: Name of the main team
        comparison_name: Name of the comparison team

    Returns:
        List of insight dictionaries with title, finding, and action
    """
    insights = []

    team_sp = get_set_piece_metrics(team_df)
    comp_sp = get_set_piece_metrics(comparison_df)
    team_sq = get_shot_quality_metrics(team_df)
    comp_sq = get_shot_quality_metrics(comparison_df)

    # Set piece dependency insight
    if team_sp.get("set_piece_xg_pct", 0) > comp_sp.get("set_piece_xg_pct", 0) + 5:
        insights.append({
            "title": "Set Piece Dependency",
            "finding": f"{team_name}: {team_sp['set_piece_xg_pct']}% of xG from set pieces vs {comparison_name}: {comp_sp['set_piece_xg_pct']}%",
            "action": "Improve open play build-up patterns and create more chances from possession",
            "severity": "high" if team_sp['set_piece_xg_pct'] > 35 else "medium",
        })

    # Shot quality insight
    xg_per_shot_diff = team_sq.get("avg_xg_per_shot", 0) - comp_sq.get("avg_xg_per_shot", 0)
    if xg_per_shot_diff < -0.02:
        insights.append({
            "title": "Shot Quality Gap",
            "finding": f"{team_name}: {team_sq['avg_xg_per_shot']:.3f} xG/shot vs {comparison_name}: {comp_sq['avg_xg_per_shot']:.3f} xG/shot",
            "action": "Focus on creating higher quality chances rather than volume of shots",
            "severity": "high" if xg_per_shot_diff < -0.03 else "medium",
        })

    # Blocked shots insight
    blocked_diff = team_sq.get("blocked_rate_pct", 0) - comp_sq.get("blocked_rate_pct", 0)
    if blocked_diff > 5:
        insights.append({
            "title": "Shots Being Blocked",
            "finding": f"{team_name}: {team_sq['blocked_rate_pct']}% blocked vs {comparison_name}: {comp_sq['blocked_rate_pct']}%",
            "action": "Work on quicker shooting and less telegraphed attempts",
            "severity": "medium",
        })

    # Woodwork/unlucky insight
    if team_sq.get("woodwork_total", 0) > 5:
        insights.append({
            "title": "Finishing Luck",
            "finding": f"{team_name} hit woodwork {team_sq['woodwork_total']} times (est. {team_sq['potential_woodwork_goals']} unlucky goals)",
            "action": "Finishing execution is good - variance should correct over time",
            "severity": "info",
        })

    # Open play efficiency
    if team_sp.get("open_play_xg_per_game", 0) < comp_sp.get("open_play_xg_per_game", 0) - 0.3:
        insights.append({
            "title": "Open Play Creation",
            "finding": f"{team_name}: {team_sp['open_play_xg_per_game']} open play xG/game vs {comparison_name}: {comp_sp['open_play_xg_per_game']}",
            "action": "Tactical focus needed on build-up play and creating chances from possession",
            "severity": "high",
        })

    return insights
