import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loader import load_all_seasons
from src.data.preprocessor import preprocess_data, filter_by_season
from src.metrics.possession import (
    get_possession_metrics,
    get_possession_comparison,
    get_possession_effectiveness,
    get_possession_vs_results,
    get_possession_tactical_insights,
)
from src.visualizations.charts import (
    create_bar_chart,
    create_radar_chart,
    create_line_chart,
)
from src.visualizations.theme import get_team_color
from config import DEFAULT_TEAM, DEFAULT_COMPARISON_TEAM, SEASON_FILES, DEFAULT_SEASON

st.title("🎯 Possession & Passing Analysis")


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
st.sidebar.title("Possession Analysis Settings")
teams = sorted(df["Team"].unique().tolist())

selected_team = st.sidebar.selectbox(
    "Select Team",
    teams,
    index=teams.index(selected_team) if selected_team in teams else 0,
    key="possession_team",
)

# Comparison team selector (multiselect, max 3 teams)
available_comparison_teams = [t for t in teams if t != selected_team]
default_comparison = [t for t in comparison_teams_default if t in available_comparison_teams]
comparison_teams = st.sidebar.multiselect(
    "Compare With (max 3)",
    options=available_comparison_teams,
    default=default_comparison,
    max_selections=3,
    key="possession_comparison",
)

season_options = list(SEASON_FILES.keys())
selected_season = st.sidebar.selectbox(
    "Season",
    season_options,
    index=season_options.index(selected_season) if selected_season in season_options else 0,
    key="possession_season",
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

# Get possession metrics for selected team
team_metrics = get_possession_metrics(team_df)

# Get comparison data for all selected comparison teams
comparison_data = {}
for comp_team in comparison_teams:
    comp_df = filtered_df[filtered_df["Team"] == comp_team]
    if len(comp_df) > 0:
        comparison_data[comp_team] = {
            "df": comp_df,
            "metrics": get_possession_metrics(comp_df),
        }

# Get first comparison team's metrics for delta calculations (if any)
first_comparison_metrics = comparison_data[comparison_teams[0]]["metrics"] if comparison_teams else team_metrics

# KPI Section
st.subheader(f"Possession Statistics: {selected_team}")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta = team_metrics["avg_possession"] - first_comparison_metrics["avg_possession"]
    st.metric(
        "Avg Possession",
        f"{team_metrics['avg_possession']}%",
        delta=f"{delta:+.1f}%" if comparison_teams else None,
    )

with col2:
    delta = team_metrics["pass_accuracy_pct"] - first_comparison_metrics["pass_accuracy_pct"]
    st.metric(
        "Pass Accuracy",
        f"{team_metrics['pass_accuracy_pct']}%",
        delta=f"{delta:+.1f}%" if comparison_teams else None,
    )

with col3:
    delta = team_metrics["passes_per_game"] - first_comparison_metrics["passes_per_game"]
    st.metric(
        "Passes/Game",
        int(team_metrics["passes_per_game"]),
        delta=f"{delta:+.0f}" if comparison_teams else None,
    )

with col4:
    delta = team_metrics["opp_half_passes_per_game"] - first_comparison_metrics["opp_half_passes_per_game"]
    st.metric(
        "Opp. Half Passes",
        int(team_metrics["opp_half_passes_per_game"]),
        delta=f"{delta:+.0f}" if comparison_teams else None,
    )

with col5:
    delta = team_metrics["touches_in_box_per_game"] - first_comparison_metrics["touches_in_box_per_game"]
    st.metric(
        "Touches in Box",
        team_metrics["touches_in_box_per_game"],
        delta=f"{delta:+.1f}" if comparison_teams else None,
    )

st.markdown("---")

# Possession Trend
st.subheader("Possession Trend")

# Create columns for selected team + comparison teams
num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    trend_df = team_df.sort_values("Round").copy()
    trend_df["possession_rolling"] = trend_df["possession_pct"].rolling(window=5, min_periods=1).mean()

    fig = create_line_chart(
        trend_df,
        x_col="Round",
        y_col="possession_rolling",
        title=f"{selected_team} - Possession % (5-game rolling avg)",
        x_title="Matchweek",
        y_title="Possession %",
    )
    st.plotly_chart(fig, width='stretch')

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        with cols[i + 1]:
            trend_df = comparison_data[comp_team]["df"].sort_values("Round").copy()
            trend_df["possession_rolling"] = trend_df["possession_pct"].rolling(window=5, min_periods=1).mean()

            fig = create_line_chart(
                trend_df,
                x_col="Round",
                y_col="possession_rolling",
                title=f"{comp_team} - Possession % (5-game rolling avg)",
                x_title="Matchweek",
                y_title="Possession %",
            )
            st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Passing Distribution
st.subheader("Passing Distribution")

num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    # Passes by location
    pass_location = {
        "Own Half": team_metrics["own_half_passes_per_game"],
        "Opposition Half": team_metrics["opp_half_passes_per_game"],
    }
    fig = create_bar_chart(
        pass_location,
        title=f"{selected_team} - Passing Distribution/Game",
        y_title="Passes",
    )
    st.plotly_chart(fig, width='stretch')

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        comp_metrics = comparison_data[comp_team]["metrics"]
        with cols[i + 1]:
            pass_location = {
                "Own Half": comp_metrics["own_half_passes_per_game"],
                "Opposition Half": comp_metrics["opp_half_passes_per_game"],
            }
            fig = create_bar_chart(
                pass_location,
                title=f"{comp_team} - Passing Distribution/Game",
                y_title="Passes",
            )
            st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Pass Accuracy Breakdown
st.subheader("Pass Accuracy Breakdown")

num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    st.markdown(f"### {selected_team}")
    st.markdown(f"**Overall Pass Accuracy:** {team_metrics['pass_accuracy_pct']}%")
    st.markdown(f"**Long Ball Accuracy:** {team_metrics['long_ball_accuracy_pct']}%")
    st.markdown(f"**Cross Accuracy:** {team_metrics['cross_accuracy_pct']}%")

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        comp_metrics = comparison_data[comp_team]["metrics"]
        with cols[i + 1]:
            st.markdown(f"### {comp_team}")
            st.markdown(f"**Overall Pass Accuracy:** {comp_metrics['pass_accuracy_pct']}%")
            st.markdown(f"**Long Ball Accuracy:** {comp_metrics['long_ball_accuracy_pct']}%")
            st.markdown(f"**Cross Accuracy:** {comp_metrics['cross_accuracy_pct']}%")

# Accuracy comparison chart
accuracy_data = {
    "Pass Type": ["Overall", "Long Balls", "Crosses"],
    selected_team: [team_metrics["pass_accuracy_pct"], team_metrics["long_ball_accuracy_pct"], team_metrics["cross_accuracy_pct"]],
}
color_map = {selected_team: get_team_color(selected_team)}

for comp_team in comparison_teams:
    if comp_team in comparison_data:
        comp_metrics = comparison_data[comp_team]["metrics"]
        accuracy_data[comp_team] = [comp_metrics["pass_accuracy_pct"], comp_metrics["long_ball_accuracy_pct"], comp_metrics["cross_accuracy_pct"]]
        color_map[comp_team] = get_team_color(comp_team)

accuracy_df = pd.DataFrame(accuracy_data)

fig = px.bar(
    accuracy_df.melt(id_vars="Pass Type", var_name="Team", value_name="Accuracy %"),
    x="Pass Type",
    y="Accuracy %",
    color="Team",
    barmode="group",
    title="Pass Accuracy Comparison",
    color_discrete_map=color_map,
)
fig.update_layout(template="none")
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Possession Effectiveness Analysis
st.subheader("Possession Effectiveness")

team_effectiveness = get_possession_effectiveness(team_df)

# Get first comparison effectiveness for deltas
first_comp_effectiveness = None
if comparison_teams and comparison_teams[0] in comparison_data:
    first_comp_effectiveness = get_possession_effectiveness(comparison_data[comparison_teams[0]]["df"])

if team_effectiveness:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta = None
        if first_comp_effectiveness:
            delta = team_effectiveness["high_possession_ppg"] - first_comp_effectiveness["high_possession_ppg"]
        st.metric(
            "High Poss. PPG (≥55%)",
            f"{team_effectiveness['high_possession_ppg']}",
            delta=f"{delta:+.2f}" if delta is not None else None,
        )
        st.caption(f"{team_effectiveness['high_possession_games']} games")

    with col2:
        delta = None
        if first_comp_effectiveness:
            delta = team_effectiveness["low_possession_ppg"] - first_comp_effectiveness["low_possession_ppg"]
        st.metric(
            "Low Poss. PPG (<45%)",
            f"{team_effectiveness['low_possession_ppg']}",
            delta=f"{delta:+.2f}" if delta is not None else None,
        )
        st.caption(f"{team_effectiveness['low_possession_games']} games")

    with col3:
        delta = None
        if first_comp_effectiveness:
            delta = team_effectiveness["high_possession_win_rate"] - first_comp_effectiveness["high_possession_win_rate"]
        st.metric(
            "High Poss. Win %",
            f"{team_effectiveness['high_possession_win_rate']}%",
            delta=f"{delta:+.1f}%" if delta is not None else None,
        )

    with col4:
        delta = None
        if first_comp_effectiveness:
            delta = team_effectiveness["xg_per_possession_pct"] - first_comp_effectiveness["xg_per_possession_pct"]
        st.metric(
            "xG per Poss. %",
            f"{team_effectiveness['xg_per_possession_pct']:.3f}",
            delta=f"{delta:+.3f}" if delta is not None else None,
        )

    # Possession effectiveness indicator
    if team_effectiveness.get("better_with_possession"):
        st.success(f"✅ {selected_team} performs better with high possession (+{team_effectiveness['possession_differential']:.2f} PPG)")
    else:
        st.warning(f"⚠️ {selected_team} performs better with low possession (counter-attacking style more effective)")

st.markdown("---")

# Possession vs Results Breakdown
st.subheader("Possession vs Results Breakdown")

num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    st.markdown(f"### {selected_team}")
    poss_results = get_possession_vs_results(team_df)
    if len(poss_results) > 0:
        st.dataframe(poss_results, width='stretch', hide_index=True)
    else:
        st.info("Not enough data for breakdown")

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        with cols[i + 1]:
            st.markdown(f"### {comp_team}")
            poss_results_comp = get_possession_vs_results(comparison_data[comp_team]["df"])
            if len(poss_results_comp) > 0:
                st.dataframe(poss_results_comp, width='stretch', hide_index=True)
            else:
                st.info("Not enough data for breakdown")

st.markdown("---")

# Tactical Insights
st.subheader("🎯 Possession Tactical Insights")

if comparison_teams and comparison_teams[0] in comparison_data:
    first_comp_team = comparison_teams[0]
    first_comp_df = comparison_data[first_comp_team]["df"]
    tactical_insights = get_possession_tactical_insights(team_df, first_comp_df, selected_team, first_comp_team)

    if tactical_insights:
        for insight in tactical_insights:
            severity = insight.get("severity", "info")
            if severity == "high":
                st.error(f"**{insight['title']}**\n\n{insight['finding']}\n\n→ *{insight['action']}*")
            elif severity == "medium":
                st.warning(f"**{insight['title']}**\n\n{insight['finding']}\n\n→ *{insight['action']}*")
            else:
                st.info(f"**{insight['title']}**\n\n{insight['finding']}\n\n→ *{insight['action']}*")
    else:
        st.success(f"✅ No significant possession-related tactical gaps identified vs {first_comp_team}")
else:
    st.info("Select a comparison team to see tactical insights.")

st.markdown("---")

# Possession vs Results Analysis
st.subheader("Possession vs Results Scatter")

num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    # Create scatter plot for selected team
    fig = px.scatter(
        team_df,
        x="possession_pct",
        y="points",
        color="Side",
        title=f"{selected_team} - Possession vs Points",
        labels={"possession_pct": "Possession %", "points": "Points"},
        hover_data=["Opponent", "Score"],
    )
    fig.update_layout(template="none")
    st.plotly_chart(fig, width='stretch')

    # Stats
    high_poss = team_df[team_df["possession_pct"] >= 55]
    low_poss = team_df[team_df["possession_pct"] < 45]

    st.markdown("**Win Rate by Possession:**")
    if len(high_poss) > 0:
        st.markdown(f"- High (≥55%): {high_poss['is_win'].mean()*100:.1f}% wins ({len(high_poss)} games)")
    if len(low_poss) > 0:
        st.markdown(f"- Low (<45%): {low_poss['is_win'].mean()*100:.1f}% wins ({len(low_poss)} games)")

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        comp_df = comparison_data[comp_team]["df"]
        with cols[i + 1]:
            fig = px.scatter(
                comp_df,
                x="possession_pct",
                y="points",
                color="Side",
                title=f"{comp_team} - Possession vs Points",
                labels={"possession_pct": "Possession %", "points": "Points"},
                hover_data=["Opponent", "Score"],
            )
            fig.update_layout(template="none")
            st.plotly_chart(fig, width='stretch')

            high_poss = comp_df[comp_df["possession_pct"] >= 55]
            low_poss = comp_df[comp_df["possession_pct"] < 45]

            st.markdown("**Win Rate by Possession:**")
            if len(high_poss) > 0:
                st.markdown(f"- High (≥55%): {high_poss['is_win'].mean()*100:.1f}% wins ({len(high_poss)} games)")
            if len(low_poss) > 0:
                st.markdown(f"- Low (<45%): {low_poss['is_win'].mean()*100:.1f}% wins ({len(low_poss)} games)")

st.markdown("---")

# Possession Radar Chart
st.subheader("Possession & Passing Profile")

# Normalize metrics for radar chart
all_teams_metrics = get_possession_comparison(filtered_df, teams)

radar_metrics = [
    "avg_possession", "pass_accuracy_pct", "passes_per_game",
    "opp_half_passes_per_game", "touches_in_box_per_game",
]

max_values = {m: all_teams_metrics.loc[m].max() for m in radar_metrics}

teams_for_radar = [selected_team] + comparison_teams
normalized_metrics = {}
for team in teams_for_radar:
    metrics = get_possession_metrics(filtered_df[filtered_df["Team"] == team])
    normalized_metrics[team] = {
        "Possession": metrics["avg_possession"],  # Already percentage
        "Pass Accuracy": metrics["pass_accuracy_pct"],  # Already percentage
        "Passes/Game": (metrics["passes_per_game"] / max_values["passes_per_game"]) * 100 if max_values["passes_per_game"] > 0 else 0,
        "Opp. Half Passes": (metrics["opp_half_passes_per_game"] / max_values["opp_half_passes_per_game"]) * 100 if max_values["opp_half_passes_per_game"] > 0 else 0,
        "Touches in Box": (metrics["touches_in_box_per_game"] / max_values["touches_in_box_per_game"]) * 100 if max_values["touches_in_box_per_game"] > 0 else 0,
    }

fig = create_radar_chart(
    normalized_metrics,
    teams_for_radar,
    title="Possession Profile (Normalized)",
)
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Detailed Metrics Table
st.subheader("Detailed Possession Metrics")

metric_names = [
    "Average Possession %", "Passes per Game", "Pass Accuracy %",
    "Opposition Half Passes/Game", "Own Half Passes/Game",
    "Long Ball Accuracy %", "Cross Accuracy %", "Touches in Box/Game",
    "Corners/Game", "Successful Dribbles/Game",
]
metric_keys = [
    "avg_possession", "passes_per_game", "pass_accuracy_pct",
    "opp_half_passes_per_game", "own_half_passes_per_game",
    "long_ball_accuracy_pct", "cross_accuracy_pct", "touches_in_box_per_game",
    "corners_per_game", "successful_dribbles_per_game",
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
