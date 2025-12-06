import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loader import load_all_seasons
from src.data.preprocessor import preprocess_data, filter_by_season
from src.metrics.defensive import get_defensive_metrics, get_defensive_comparison
from src.metrics.aggregators import get_home_away_split
from src.visualizations.charts import (
    create_bar_chart,
    create_radar_chart,
    create_line_chart,
    create_home_away_comparison,
)
from config import DEFAULT_TEAM, DEFAULT_COMPARISON_TEAM, SEASON_FILES, DEFAULT_SEASON

st.title("🛡️ Defensive Analysis")


@st.cache_data
def load_data():
    df = load_all_seasons()
    return preprocess_data(df)


# Load data
df = load_data()

# Get settings from session state or use defaults
selected_team = st.session_state.get("selected_team", DEFAULT_TEAM)
comparison_teams_default = st.session_state.get("comparison_teams", [DEFAULT_COMPARISON_TEAM])
selected_season = st.session_state.get("selected_season", DEFAULT_SEASON)

# Sidebar
st.sidebar.title("Defensive Analysis Settings")
teams = sorted(df["Team"].unique().tolist())

selected_team = st.sidebar.selectbox(
    "Select Team",
    teams,
    index=teams.index(selected_team) if selected_team in teams else 0,
    key="defensive_team",
)

# Comparison team selector (multiselect, max 3 teams)
available_comparison_teams = [t for t in teams if t != selected_team]
default_comparison = [t for t in comparison_teams_default if t in available_comparison_teams]
comparison_teams = st.sidebar.multiselect(
    "Compare With (max 3)",
    options=available_comparison_teams,
    default=default_comparison,
    max_selections=3,
    key="defensive_comparison",
)

season_options = list(SEASON_FILES.keys())
selected_season = st.sidebar.selectbox(
    "Season",
    season_options,
    index=season_options.index(selected_season) if selected_season in season_options else 0,
    key="defensive_season",
)

# Sync selections back to session state for cross-page persistence
st.session_state["selected_team"] = selected_team
st.session_state["comparison_teams"] = comparison_teams
st.session_state["selected_season"] = selected_season

# Filter data
filtered_df = filter_by_season(df, selected_season)
team_df = filtered_df[filtered_df["Team"] == selected_team]

if len(team_df) == 0:
    st.warning(f"No data available for {selected_team}")
    st.stop()

# Get defensive metrics for selected team
team_metrics = get_defensive_metrics(team_df)

# Get comparison data for all selected comparison teams
comparison_data = {}
for comp_team in comparison_teams:
    comp_df = filtered_df[filtered_df["Team"] == comp_team]
    if len(comp_df) > 0:
        comparison_data[comp_team] = {
            "df": comp_df,
            "metrics": get_defensive_metrics(comp_df),
        }

# Get first comparison team's metrics for delta calculations (if any)
first_comparison_metrics = comparison_data[comparison_teams[0]]["metrics"] if comparison_teams else team_metrics

# KPI Section
st.subheader(f"Defensive Statistics: {selected_team}")

col1, col2, col3, col4, col5 = st.columns(5)

# Use first comparison team for deltas if available
comp_label = comparison_teams[0][:3] if comparison_teams else ""

with col1:
    delta = first_comparison_metrics["goals_conceded_per_game"] - team_metrics["goals_conceded_per_game"]
    st.metric(
        "Goals Conceded/Game",
        team_metrics["goals_conceded_per_game"],
        delta=f"{delta:+.2f}" if comparison_teams else None,
        delta_color="normal",  # Lower is better, but delta shows difference
    )

with col2:
    delta = team_metrics["clean_sheets"] - first_comparison_metrics["clean_sheets"]
    st.metric(
        "Clean Sheets",
        team_metrics["clean_sheets"],
        delta=f"{delta:+d} vs {comp_label}" if comparison_teams else None,
    )

with col3:
    st.metric(
        "Clean Sheet %",
        f"{team_metrics['clean_sheet_pct']}%",
    )

with col4:
    delta = team_metrics["tackles_per_game"] - first_comparison_metrics["tackles_per_game"]
    st.metric(
        "Tackles/Game",
        team_metrics["tackles_per_game"],
        delta=f"{delta:+.1f}" if comparison_teams else None,
    )

with col5:
    delta = team_metrics["interceptions_per_game"] - first_comparison_metrics["interceptions_per_game"]
    st.metric(
        "Interceptions/Game",
        team_metrics["interceptions_per_game"],
        delta=f"{delta:+.1f}" if comparison_teams else None,
    )

st.markdown("---")

# Goals Conceded Trend
st.subheader("Goals Conceded Trend")

# Create columns for selected team + comparison teams
num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    trend_df = team_df.sort_values("Round").copy()
    trend_df["conceded_rolling"] = trend_df["Goal conceded"].rolling(window=5, min_periods=1).mean()

    fig = create_line_chart(
        trend_df,
        x_col="Round",
        y_col="conceded_rolling",
        title=f"{selected_team} - Goals Conceded (5-game rolling avg)",
        x_title="Matchweek",
        y_title="Goals Conceded",
    )
    st.plotly_chart(fig, width='stretch')

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        with cols[i + 1]:
            trend_df = comparison_data[comp_team]["df"].sort_values("Round").copy()
            trend_df["conceded_rolling"] = trend_df["Goal conceded"].rolling(window=5, min_periods=1).mean()

            fig = create_line_chart(
                trend_df,
                x_col="Round",
                y_col="conceded_rolling",
                title=f"{comp_team} - Goals Conceded (5-game rolling avg)",
                x_title="Matchweek",
                y_title="Goals Conceded",
            )
            st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Defensive Actions Breakdown
st.subheader("Defensive Actions Breakdown")

col1, col2 = st.columns(2)

with col1:
    actions_data = {selected_team: team_metrics["defensive_actions_per_game"]}
    for comp_team in comparison_teams:
        if comp_team in comparison_data:
            actions_data[comp_team] = comparison_data[comp_team]["metrics"]["defensive_actions_per_game"]
    fig = create_bar_chart(
        actions_data,
        title="Total Defensive Actions/Game",
        y_title="Actions",
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    # Breakdown by type
    st.markdown("### Defensive Actions Breakdown (per game)")

    breakdown_data = {
        "Metric": ["Tackles", "Interceptions", "Blocks", "Clearances"],
        selected_team: [
            team_metrics["tackles_per_game"],
            team_metrics["interceptions_per_game"],
            team_metrics["blocks_per_game"],
            team_metrics["clearances_per_game"],
        ],
    }
    for comp_team in comparison_teams:
        if comp_team in comparison_data:
            comp_metrics = comparison_data[comp_team]["metrics"]
            breakdown_data[comp_team] = [
                comp_metrics["tackles_per_game"],
                comp_metrics["interceptions_per_game"],
                comp_metrics["blocks_per_game"],
                comp_metrics["clearances_per_game"],
            ]

    st.dataframe(pd.DataFrame(breakdown_data).set_index("Metric"), width='stretch')

st.markdown("---")

# Clean Sheets Analysis
st.subheader("Clean Sheets Analysis")

team_split = get_home_away_split(team_df)

# Create columns for selected team + comparison teams
num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    st.markdown(f"### {selected_team}")
    st.markdown(f"**Total Clean Sheets:** {team_metrics['clean_sheets']} ({team_metrics['clean_sheet_pct']}%)")
    st.markdown(f"- Home: {team_split['home']['clean_sheets']}")
    st.markdown(f"- Away: {team_split['away']['clean_sheets']}")

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        comp_metrics = comparison_data[comp_team]["metrics"]
        comparison_split = get_home_away_split(comparison_data[comp_team]["df"])
        with cols[i + 1]:
            st.markdown(f"### {comp_team}")
            st.markdown(f"**Total Clean Sheets:** {comp_metrics['clean_sheets']} ({comp_metrics['clean_sheet_pct']}%)")
            st.markdown(f"- Home: {comparison_split['home']['clean_sheets']}")
            st.markdown(f"- Away: {comparison_split['away']['clean_sheets']}")

# Clean sheets comparison chart
cs_data = {selected_team: team_metrics["clean_sheet_pct"]}
for comp_team in comparison_teams:
    if comp_team in comparison_data:
        cs_data[comp_team] = comparison_data[comp_team]["metrics"]["clean_sheet_pct"]
fig = create_bar_chart(cs_data, title="Clean Sheet Percentage", y_title="%")
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Defensive Radar Chart
st.subheader("Defensive Profile Comparison")

# Normalize metrics for radar chart
all_teams_metrics = get_defensive_comparison(filtered_df, teams)

# For defensive metrics, lower is often better for conceded, higher for actions
radar_metrics = [
    "goals_conceded_per_game", "clean_sheet_pct", "tackles_per_game",
    "interceptions_per_game", "blocks_per_game", "clearances_per_game",
]

# Get max/min values
max_values = {m: all_teams_metrics.loc[m].max() for m in radar_metrics}
min_conceded = all_teams_metrics.loc["goals_conceded_per_game"].min()
max_conceded = all_teams_metrics.loc["goals_conceded_per_game"].max()

teams_for_radar = [selected_team] + comparison_teams
normalized_metrics = {}
for team in teams_for_radar:
    metrics = get_defensive_metrics(filtered_df[filtered_df["Team"] == team])

    # For goals conceded, invert (lower is better)
    conceded_norm = 100 - ((metrics["goals_conceded_per_game"] - min_conceded) / (max_conceded - min_conceded) * 100) if max_conceded > min_conceded else 50

    normalized_metrics[team] = {
        "Defensive Solidity": conceded_norm,
        "Clean Sheet %": metrics["clean_sheet_pct"],
        "Tackles/Game": (metrics["tackles_per_game"] / max_values["tackles_per_game"]) * 100 if max_values["tackles_per_game"] > 0 else 0,
        "Interceptions": (metrics["interceptions_per_game"] / max_values["interceptions_per_game"]) * 100 if max_values["interceptions_per_game"] > 0 else 0,
        "Blocks": (metrics["blocks_per_game"] / max_values["blocks_per_game"]) * 100 if max_values["blocks_per_game"] > 0 else 0,
        "Clearances": (metrics["clearances_per_game"] / max_values["clearances_per_game"]) * 100 if max_values["clearances_per_game"] > 0 else 0,
    }

fig = create_radar_chart(
    normalized_metrics,
    teams_for_radar,
    title="Defensive Profile (Normalized to League Best = 100)",
)
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Detailed Metrics Table
st.subheader("Detailed Defensive Metrics")

# Build metrics display with selected team and all comparison teams
metric_names = [
    "Total Goals Conceded", "Goals Conceded/Game", "Clean Sheets", "Clean Sheet %",
    "Tackles/Game", "Interceptions/Game", "Blocks/Game", "Clearances/Game",
    "Defensive Actions/Game", "Saves/Game",
]
metric_keys = [
    "total_goals_conceded", "goals_conceded_per_game", "clean_sheets", "clean_sheet_pct",
    "tackles_per_game", "interceptions_per_game", "blocks_per_game", "clearances_per_game",
    "defensive_actions_per_game", "saves_per_game",
]

metrics_display = {name: [team_metrics[key]] for name, key in zip(metric_names, metric_keys)}
team_index = [selected_team]

for comp_team in comparison_teams:
    if comp_team in comparison_data:
        comp_metrics = comparison_data[comp_team]["metrics"]
        team_index.append(comp_team)
        for name, key in zip(metric_names, metric_keys):
            metrics_display[name].append(comp_metrics[key])

metrics_df = pd.DataFrame(metrics_display, index=team_index).T
# Ensure all values are numeric for Arrow compatibility
for col in metrics_df.columns:
    metrics_df[col] = metrics_df[col].astype(float)
st.dataframe(metrics_df, width='stretch')
