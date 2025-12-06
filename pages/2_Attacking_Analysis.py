import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loader import load_all_seasons
from src.data.preprocessor import preprocess_data, filter_by_season
from src.metrics.attacking import (
    get_attacking_metrics,
    get_attacking_comparison,
    get_set_piece_metrics,
    get_shot_quality_metrics,
    get_shot_outcome_breakdown,
    get_tactical_insights,
)
from src.visualizations.charts import (
    create_bar_chart,
    create_radar_chart,
    create_xg_vs_goals_chart,
)
from src.visualizations.theme import get_team_color
from config import DEFAULT_TEAM, DEFAULT_COMPARISON_TEAM, SEASON_FILES, DEFAULT_SEASON

st.title("⚽ Attacking Analysis")


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
st.sidebar.title("Attacking Analysis Settings")
teams = sorted(df["Team"].unique().tolist())

selected_team = st.sidebar.selectbox(
    "Select Team",
    teams,
    index=teams.index(selected_team) if selected_team in teams else 0,
    key="attacking_team",
)

# Comparison team selector (multiselect, max 3 teams)
available_comparison_teams = [t for t in teams if t != selected_team]
default_comparison = [t for t in comparison_teams_default if t in available_comparison_teams]
comparison_teams = st.sidebar.multiselect(
    "Compare With (max 3)",
    options=available_comparison_teams,
    default=default_comparison,
    max_selections=3,
    key="attacking_comparison",
)

season_options = list(SEASON_FILES.keys())
selected_season = st.sidebar.selectbox(
    "Season",
    season_options,
    index=season_options.index(selected_season) if selected_season in season_options else 0,
    key="attacking_season",
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

# Get attacking metrics for selected team
team_metrics = get_attacking_metrics(team_df)

# Get comparison data for all selected comparison teams
comparison_data = {}
for comp_team in comparison_teams:
    comp_df = filtered_df[filtered_df["Team"] == comp_team]
    if len(comp_df) > 0:
        comparison_data[comp_team] = {
            "df": comp_df,
            "metrics": get_attacking_metrics(comp_df),
        }

# Get first comparison team's metrics for delta calculations (if any)
first_comparison_metrics = comparison_data[comparison_teams[0]]["metrics"] if comparison_teams else team_metrics

# KPI Section
st.subheader(f"Attacking Statistics: {selected_team}")

col1, col2, col3, col4, col5 = st.columns(5)

# Use first comparison team for deltas if available
comp_label = comparison_teams[0][:3] if comparison_teams else ""

with col1:
    delta = team_metrics["goals_per_game"] - first_comparison_metrics["goals_per_game"]
    st.metric(
        "Goals/Game",
        team_metrics["goals_per_game"],
        delta=f"{delta:+.2f} vs {comp_label}" if comparison_teams else None,
    )

with col2:
    delta = team_metrics["xg_per_game"] - first_comparison_metrics["xg_per_game"]
    st.metric(
        "xG/Game",
        team_metrics["xg_per_game"],
        delta=f"{delta:+.2f}" if comparison_teams else None,
    )

with col3:
    st.metric(
        "xG Over/Under",
        f"{team_metrics['xg_overperformance']:+.2f}",
        help="Goals - xG (positive = overperforming)",
    )

with col4:
    delta = team_metrics["shot_conversion_pct"] - first_comparison_metrics["shot_conversion_pct"]
    st.metric(
        "Shot Conversion %",
        f"{team_metrics['shot_conversion_pct']}%",
        delta=f"{delta:+.1f}%" if comparison_teams else None,
    )

with col5:
    delta = team_metrics["big_chance_conversion_pct"] - first_comparison_metrics["big_chance_conversion_pct"]
    st.metric(
        "Big Chance Conv. %",
        f"{team_metrics['big_chance_conversion_pct']}%",
        delta=f"{delta:+.1f}%" if comparison_teams else None,
    )

st.markdown("---")

# xG vs Goals Trend
st.subheader("Goals vs Expected Goals (xG) Trend")

# Create columns for selected team + comparison teams
num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    fig = create_xg_vs_goals_chart(
        team_df,
        selected_team,
        rolling_window=5,
        title=f"{selected_team} - Goals vs xG",
    )
    st.plotly_chart(fig, width='stretch')

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        with cols[i + 1]:
            fig = create_xg_vs_goals_chart(
                comparison_data[comp_team]["df"],
                comp_team,
                rolling_window=5,
                title=f"{comp_team} - Goals vs xG",
            )
            st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Shot Analysis
st.subheader("Shot Analysis")

col1, col2 = st.columns(2)

with col1:
    # Shots per game comparison
    shot_data = {selected_team: team_metrics["shots_per_game"]}
    for comp_team in comparison_teams:
        if comp_team in comparison_data:
            shot_data[comp_team] = comparison_data[comp_team]["metrics"]["shots_per_game"]
    fig = create_bar_chart(
        shot_data,
        title="Shots per Game",
        y_title="Shots",
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    # Shots on target percentage
    sot_data = {selected_team: team_metrics["shots_on_target_pct"]}
    for comp_team in comparison_teams:
        if comp_team in comparison_data:
            sot_data[comp_team] = comparison_data[comp_team]["metrics"]["shots_on_target_pct"]
    fig = create_bar_chart(
        sot_data,
        title="Shots on Target %",
        y_title="Percentage",
    )
    st.plotly_chart(fig, width='stretch')

# Shot location
num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    st.markdown(f"### {selected_team} Shot Location")
    inside_box = team_metrics["shots_inside_box_pct"]
    outside_box = 100 - inside_box
    st.markdown(f"- Inside Box: **{inside_box:.1f}%**")
    st.markdown(f"- Outside Box: **{outside_box:.1f}%**")

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        with cols[i + 1]:
            st.markdown(f"### {comp_team} Shot Location")
            inside_box = comparison_data[comp_team]["metrics"]["shots_inside_box_pct"]
            outside_box = 100 - inside_box
            st.markdown(f"- Inside Box: **{inside_box:.1f}%**")
            st.markdown(f"- Outside Box: **{outside_box:.1f}%**")

st.markdown("---")

# Big Chances Analysis
st.subheader("Big Chances Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    bc_data = {selected_team: team_metrics["big_chances_per_game"]}
    for comp_team in comparison_teams:
        if comp_team in comparison_data:
            bc_data[comp_team] = comparison_data[comp_team]["metrics"]["big_chances_per_game"]
    fig = create_bar_chart(bc_data, title="Big Chances Created/Game")
    st.plotly_chart(fig, width='stretch')

with col2:
    bc_conv = {selected_team: team_metrics["big_chance_conversion_pct"]}
    for comp_team in comparison_teams:
        if comp_team in comparison_data:
            bc_conv[comp_team] = comparison_data[comp_team]["metrics"]["big_chance_conversion_pct"]
    fig = create_bar_chart(bc_conv, title="Big Chance Conversion %")
    st.plotly_chart(fig, width='stretch')

with col3:
    st.markdown("### Big Chances Summary")
    st.markdown(f"**{selected_team}:**")
    st.markdown(f"- Total: {team_metrics['total_big_chances']}")
    st.markdown(f"- Missed: {team_metrics['total_big_chances_missed']}")
    st.markdown(f"- Scored: {team_metrics['total_big_chances'] - team_metrics['total_big_chances_missed']}")

    for comp_team in comparison_teams:
        if comp_team in comparison_data:
            comp_metrics = comparison_data[comp_team]["metrics"]
            st.markdown(f"**{comp_team}:**")
            st.markdown(f"- Total: {comp_metrics['total_big_chances']}")
            st.markdown(f"- Missed: {comp_metrics['total_big_chances_missed']}")
            st.markdown(f"- Scored: {comp_metrics['total_big_chances'] - comp_metrics['total_big_chances_missed']}")

st.markdown("---")

# Attacking Radar Chart
st.subheader("Attacking Profile Comparison")

# Normalize metrics for radar chart (0-100 scale based on max values)
all_teams_metrics = get_attacking_comparison(filtered_df, teams)

# Get max values for normalization
radar_metrics = [
    "goals_per_game", "xg_per_game", "shots_per_game",
    "shots_on_target_pct", "big_chances_per_game", "shot_conversion_pct",
]

max_values = {m: all_teams_metrics.loc[m].max() for m in radar_metrics}

teams_for_radar = [selected_team] + comparison_teams
normalized_metrics = {}
for team in teams_for_radar:
    metrics = get_attacking_metrics(filtered_df[filtered_df["Team"] == team])
    normalized_metrics[team] = {
        "Goals/Game": (metrics["goals_per_game"] / max_values["goals_per_game"]) * 100 if max_values["goals_per_game"] > 0 else 0,
        "xG/Game": (metrics["xg_per_game"] / max_values["xg_per_game"]) * 100 if max_values["xg_per_game"] > 0 else 0,
        "Shots/Game": (metrics["shots_per_game"] / max_values["shots_per_game"]) * 100 if max_values["shots_per_game"] > 0 else 0,
        "SOT %": metrics["shots_on_target_pct"],  # Already percentage
        "Big Chances": (metrics["big_chances_per_game"] / max_values["big_chances_per_game"]) * 100 if max_values["big_chances_per_game"] > 0 else 0,
        "Conversion %": metrics["shot_conversion_pct"] * 5,  # Scale up for visibility
    }

fig = create_radar_chart(
    normalized_metrics,
    teams_for_radar,
    title="Attacking Profile (Normalized to League Best = 100)",
)
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Detailed Metrics Table
st.subheader("Detailed Attacking Metrics")

# Build metrics display with selected team and all comparison teams
metric_names = [
    "Total Goals", "Total xG", "Goals per Game", "xG per Game", "xG Overperformance",
    "Shots per Game", "Shots on Target per Game", "Shot Conversion %", "Shots on Target %",
    "Shots Inside Box %", "Big Chances per Game", "Big Chance Conversion %", "xGOT per Game",
]
metric_keys = [
    "total_goals", "total_xg", "goals_per_game", "xg_per_game", "xg_overperformance",
    "shots_per_game", "shots_on_target_per_game", "shot_conversion_pct", "shots_on_target_pct",
    "shots_inside_box_pct", "big_chances_per_game", "big_chance_conversion_pct", "xgot_per_game",
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

st.markdown("---")

# ===========================================
# TACTICAL INSIGHTS SECTION
# ===========================================

st.header("🎯 Tactical Insights")

# Get tactical metrics for selected team
team_sp = get_set_piece_metrics(team_df)
team_sq = get_shot_quality_metrics(team_df)

# Get tactical metrics for comparison teams
comparison_tactical_data = {}
for comp_team in comparison_teams:
    if comp_team in comparison_data:
        comparison_tactical_data[comp_team] = {
            "sp": get_set_piece_metrics(comparison_data[comp_team]["df"]),
            "sq": get_shot_quality_metrics(comparison_data[comp_team]["df"]),
        }

# Get first comparison team's metrics for delta calculations
first_comp_sp = comparison_tactical_data[comparison_teams[0]]["sp"] if comparison_teams else team_sp
first_comp_sq = comparison_tactical_data[comparison_teams[0]]["sq"] if comparison_teams else team_sq

# Set Piece Analysis
st.subheader("Set Piece vs Open Play Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    delta_val = team_sp.get('open_play_xg_pct', 0) - first_comp_sp.get('open_play_xg_pct', 0) if comparison_teams else None
    st.metric(
        "Open Play xG %",
        f"{team_sp.get('open_play_xg_pct', 0)}%",
        delta=f"{delta_val:+.1f}% vs {comparison_teams[0][:3]}" if comparison_teams else None,
    )

with col2:
    delta_val = team_sp.get('set_piece_xg_pct', 0) - first_comp_sp.get('set_piece_xg_pct', 0) if comparison_teams else None
    st.metric(
        "Set Piece xG %",
        f"{team_sp.get('set_piece_xg_pct', 0)}%",
        delta=f"{delta_val:+.1f}%" if comparison_teams else None,
    )

with col3:
    delta_val = team_sp.get('xg_per_corner', 0) - first_comp_sp.get('xg_per_corner', 0) if comparison_teams else None
    st.metric(
        "xG per Corner",
        f"{team_sp.get('xg_per_corner', 0):.3f}",
        delta=f"{delta_val:+.3f}" if comparison_teams else None,
    )

# xG Source Comparison Chart
col1, col2 = st.columns(2)

with col1:
    x_teams = [selected_team] + comparison_teams
    open_play_vals = [team_sp.get('xg_from_open_play', 0)]
    set_piece_vals = [team_sp.get('xg_from_set_pieces', 0)]
    for comp_team in comparison_teams:
        if comp_team in comparison_tactical_data:
            open_play_vals.append(comparison_tactical_data[comp_team]["sp"].get('xg_from_open_play', 0))
            set_piece_vals.append(comparison_tactical_data[comp_team]["sp"].get('xg_from_set_pieces', 0))

    fig = go.Figure(data=[
        go.Bar(name="Open Play", x=x_teams, y=open_play_vals, marker_color="#28a745"),
        go.Bar(name="Set Pieces", x=x_teams, y=set_piece_vals, marker_color="#ffc107"),
    ])
    fig.update_layout(
        title="xG by Source",
        barmode="stack",
        template="none",
        height=350,
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("### xG Source Breakdown")
    st.markdown(f"**{selected_team}:**")
    st.markdown(f"- Open Play: {team_sp.get('open_play_xg_pct', 0)}% ({team_sp.get('xg_from_open_play', 0)} xG)")
    st.markdown(f"- Set Pieces: {team_sp.get('set_piece_xg_pct', 0)}% ({team_sp.get('xg_from_set_pieces', 0)} xG)")
    st.markdown(f"- Corners: {team_sp.get('corners_total', 0)} ({team_sp.get('corners_per_game', 0)}/game)")

    for comp_team in comparison_teams:
        if comp_team in comparison_tactical_data:
            comp_sp = comparison_tactical_data[comp_team]["sp"]
            st.markdown(f"**{comp_team}:**")
            st.markdown(f"- Open Play: {comp_sp.get('open_play_xg_pct', 0)}% ({comp_sp.get('xg_from_open_play', 0)} xG)")
            st.markdown(f"- Set Pieces: {comp_sp.get('set_piece_xg_pct', 0)}% ({comp_sp.get('xg_from_set_pieces', 0)} xG)")

st.markdown("---")

# Shot Quality Analysis
st.subheader("Shot Quality Breakdown")

col1, col2, col3 = st.columns(3)

with col1:
    delta_val = team_sq.get('avg_xg_per_shot', 0) - first_comp_sq.get('avg_xg_per_shot', 0) if comparison_teams else None
    st.metric(
        "xG per Shot",
        f"{team_sq.get('avg_xg_per_shot', 0):.3f}",
        delta=f"{delta_val:+.3f} vs {comparison_teams[0][:3]}" if comparison_teams else None,
        help="Higher = better quality chances",
    )

with col2:
    st.metric(
        "Woodwork Hits",
        team_sq.get('woodwork_total', 0),
        delta=f"~{team_sq.get('potential_woodwork_goals', 0)} unlucky goals",
        delta_color="off",
    )

with col3:
    delta_val = team_sq.get('blocked_rate_pct', 0) - first_comp_sq.get('blocked_rate_pct', 0) if comparison_teams else None
    st.metric(
        "Blocked Shot %",
        f"{team_sq.get('blocked_rate_pct', 0)}%",
        delta=f"{delta_val:+.1f}%" if comparison_teams else None,
        delta_color="inverse",  # Lower is better
    )

# Shot Outcome Breakdown
team_outcomes = get_shot_outcome_breakdown(team_df)
colors = ["#28a745", "#17a2b8", "#6c757d", "#dc3545", "#ffc107"]

num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    if team_outcomes:
        labels = list(team_outcomes.keys())
        values = [team_outcomes[k]["count"] for k in labels]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.4,
        )])
        fig.update_layout(
            title=f"{selected_team} - Shot Outcomes",
            template="none",
            height=350,
        )
        st.plotly_chart(fig, width='stretch')

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        comparison_outcomes = get_shot_outcome_breakdown(comparison_data[comp_team]["df"])
        with cols[i + 1]:
            if comparison_outcomes:
                labels = list(comparison_outcomes.keys())
                values = [comparison_outcomes[k]["count"] for k in labels]

                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    marker_colors=colors,
                    hole=0.4,
                )])
                fig.update_layout(
                    title=f"{comp_team} - Shot Outcomes",
                    template="none",
                    height=350,
                )
                st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Actionable Tactical Insights
st.subheader("🎯 Actionable Tactical Gaps")

# Get insights comparing to first comparison team (if any)
if comparison_teams and comparison_teams[0] in comparison_data:
    first_comp_df = comparison_data[comparison_teams[0]]["df"]
    insights = get_tactical_insights(team_df, first_comp_df, selected_team, comparison_teams[0])

    if insights:
        for insight in insights:
            severity = insight.get("severity", "medium")
            if severity == "high":
                icon = "🔴"
                color = "#dc3545"
            elif severity == "medium":
                icon = "🟡"
                color = "#ffc107"
            else:
                icon = "🟢"
                color = "#28a745"

            st.markdown(f"""
            <div style="background-color: rgba(128, 128, 128, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid {color};">
                <h4 style="margin: 0;">{icon} {insight['title']}</h4>
                <p style="margin: 5px 0;"><strong>Finding:</strong> {insight['finding']}</p>
                <p style="margin: 5px 0; color: {color};"><strong>Action:</strong> {insight['action']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(f"No significant tactical gaps identified compared to {comparison_teams[0]}. Keep up the good work!")
else:
    st.info("Select comparison team(s) to see tactical insights.")

# Summary Table
st.markdown("---")
st.subheader("Tactical Metrics Summary")

tactical_summary = {
    "Metric": [
        "Open Play xG %", "Set Piece xG %", "xG per Shot", "xG per Corner",
        "Blocked Shot %", "Woodwork Hits", "Off Target %"
    ],
    selected_team: [
        f"{team_sp.get('open_play_xg_pct', 0)}%",
        f"{team_sp.get('set_piece_xg_pct', 0)}%",
        f"{team_sq.get('avg_xg_per_shot', 0):.3f}",
        f"{team_sp.get('xg_per_corner', 0):.3f}",
        f"{team_sq.get('blocked_rate_pct', 0)}%",
        str(team_sq.get('woodwork_total', 0)),
        f"{team_sq.get('off_target_rate_pct', 0)}%",
    ],
}

# Add comparison teams to tactical summary
for comp_team in comparison_teams:
    if comp_team in comparison_tactical_data:
        comp_sp = comparison_tactical_data[comp_team]["sp"]
        comp_sq = comparison_tactical_data[comp_team]["sq"]
        tactical_summary[comp_team] = [
            f"{comp_sp.get('open_play_xg_pct', 0)}%",
            f"{comp_sp.get('set_piece_xg_pct', 0)}%",
            f"{comp_sq.get('avg_xg_per_shot', 0):.3f}",
            f"{comp_sp.get('xg_per_corner', 0):.3f}",
            f"{comp_sq.get('blocked_rate_pct', 0)}%",
            str(comp_sq.get('woodwork_total', 0)),
            f"{comp_sq.get('off_target_rate_pct', 0)}%",
        ]

st.dataframe(pd.DataFrame(tactical_summary).set_index("Metric"), width='stretch')
