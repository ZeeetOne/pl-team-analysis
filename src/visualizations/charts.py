import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from .theme import TEAM_COLORS, CHART_TEMPLATE, DEFAULT_LAYOUT, get_team_color


def create_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str = None,
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    height: int = 400,
) -> go.Figure:
    """Create a line chart for trends.

    Args:
        df: DataFrame with data
        x_col: Column for x-axis
        y_col: Column for y-axis
        color_col: Column for color grouping (e.g., team)
        title: Chart title
        x_title: X-axis title
        y_title: Y-axis title
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    if color_col:
        for team in df[color_col].unique():
            team_df = df[df[color_col] == team]
            fig.add_trace(go.Scatter(
                x=team_df[x_col],
                y=team_df[y_col],
                mode="lines+markers",
                name=team,
                line=dict(color=get_team_color(team), width=2),
                marker=dict(size=6),
            ))
    else:
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            line=dict(width=2),
            marker=dict(size=6),
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        template=CHART_TEMPLATE,
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
    )

    return fig


def create_bar_chart(
    data: dict,
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    height: int = 400,
    horizontal: bool = False,
) -> go.Figure:
    """Create a bar chart for comparisons.

    Args:
        data: Dictionary with team names as keys and values
        title: Chart title
        x_title: X-axis title
        y_title: Y-axis title
        height: Chart height
        horizontal: If True, create horizontal bar chart

    Returns:
        Plotly figure
    """
    teams = list(data.keys())
    values = list(data.values())
    colors = [get_team_color(team) for team in teams]

    fig = go.Figure()

    if horizontal:
        fig.add_trace(go.Bar(
            y=teams,
            x=values,
            orientation="h",
            marker_color=colors,
            text=values,
            textposition="auto",
        ))
    else:
        fig.add_trace(go.Bar(
            x=teams,
            y=values,
            marker_color=colors,
            text=values,
            textposition="auto",
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_title if not horizontal else y_title,
        yaxis_title=y_title if not horizontal else x_title,
        template=CHART_TEMPLATE,
        height=height,
        showlegend=False,
    )

    return fig


def create_radar_chart(
    metrics: dict,
    teams: list,
    title: str = "",
    height: int = 500,
) -> go.Figure:
    """Create a radar/spider chart for multi-metric comparison.

    Args:
        metrics: Dict with structure {team: {metric: value}}
        teams: List of team names to include
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Get all metric names from first team
    categories = list(metrics[teams[0]].keys())

    for team in teams:
        values = [metrics[team].get(cat, 0) for cat in categories]
        # Close the radar chart
        values.append(values[0])
        cats = categories + [categories[0]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=cats,
            fill="toself",
            name=team,
            line_color=get_team_color(team),
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
            )
        ),
        title=title,
        template=CHART_TEMPLATE,
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
    )

    return fig


def create_cumulative_points_chart(
    df: pd.DataFrame,
    teams: list,
    title: str = "Cumulative Points",
    height: int = 400,
) -> go.Figure:
    """Create cumulative points chart for season comparison.

    Args:
        df: DataFrame with match data including 'Round' and 'points'
        teams: List of team names to compare
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    for team in teams:
        team_df = df[df["Team"] == team].sort_values("Round").copy()
        team_df["cumulative_points"] = team_df["points"].cumsum()

        fig.add_trace(go.Scatter(
            x=team_df["Round"],
            y=team_df["cumulative_points"],
            mode="lines+markers",
            name=team,
            line=dict(color=get_team_color(team), width=2),
            marker=dict(size=5),
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Matchweek",
        yaxis_title="Cumulative Points",
        template=CHART_TEMPLATE,
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
    )

    return fig


def create_xg_vs_goals_chart(
    df: pd.DataFrame,
    team: str,
    rolling_window: int = 5,
    title: str = "",
    height: int = 400,
) -> go.Figure:
    """Create xG vs Actual Goals trend chart.

    Args:
        df: DataFrame filtered to team
        team: Team name for coloring
        rolling_window: Rolling average window
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    df = df.sort_values("Round").copy()
    df["goals_rolling"] = df["Goal scored"].rolling(window=rolling_window, min_periods=1).mean()
    df["xg_rolling"] = df["Expected goals (xG)"].rolling(window=rolling_window, min_periods=1).mean()

    fig = go.Figure()

    # Actual goals rolling
    fig.add_trace(go.Scatter(
        x=df["Round"],
        y=df["goals_rolling"],
        mode="lines",
        name=f"Goals ({rolling_window}-game avg)",
        line=dict(color=get_team_color(team), width=2),
    ))

    # xG rolling
    fig.add_trace(go.Scatter(
        x=df["Round"],
        y=df["xg_rolling"],
        mode="lines",
        name=f"xG ({rolling_window}-game avg)",
        line=dict(color=get_team_color(team), width=2, dash="dash"),
    ))

    # Individual match xG
    fig.add_trace(go.Scatter(
        x=df["Round"],
        y=df["Expected goals (xG)"],
        mode="markers",
        name="Match xG",
        marker=dict(color=get_team_color(team), size=6, opacity=0.3),
    ))

    fig.update_layout(
        title=title or f"{team} - Goals vs xG Trend",
        xaxis_title="Matchweek",
        yaxis_title="Goals / xG",
        template=CHART_TEMPLATE,
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
    )

    return fig


def create_home_away_comparison(
    home_data: dict,
    away_data: dict,
    metrics: list,
    title: str = "",
    height: int = 400,
) -> go.Figure:
    """Create home vs away comparison chart.

    Args:
        home_data: Dictionary of home metrics
        away_data: Dictionary of away metrics
        metrics: List of metric keys to compare
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Home",
        x=metrics,
        y=[home_data.get(m, 0) for m in metrics],
        marker_color="#28a745",
    ))

    fig.add_trace(go.Bar(
        name="Away",
        x=metrics,
        y=[away_data.get(m, 0) for m in metrics],
        marker_color="#6c757d",
    ))

    fig.update_layout(
        title=title,
        barmode="group",
        template=CHART_TEMPLATE,
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
    )

    return fig
