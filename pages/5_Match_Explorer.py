import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loader import load_all_seasons
from src.data.preprocessor import preprocess_data, filter_by_season
from src.visualizations.theme import get_team_color, FORM_COLORS
from config import DEFAULT_TEAM, SEASON_FILES, DEFAULT_SEASON

st.title("🔍 Match Explorer")


@st.cache_data
def load_data():
    df = load_all_seasons()
    return preprocess_data(df)


# Load data
df = load_data()

# Get settings from session state or use defaults
selected_team = st.session_state.get("selected_team", DEFAULT_TEAM)
selected_season = st.session_state.get("selected_season", DEFAULT_SEASON)

# Sidebar
st.sidebar.title("Match Explorer Settings")
teams = sorted(df["Team"].unique().tolist())

selected_team = st.sidebar.selectbox(
    "Select Team",
    teams,
    index=teams.index(selected_team) if selected_team in teams else 0,
    key="explorer_team",
)

season_options = list(SEASON_FILES.keys())
selected_season = st.sidebar.selectbox(
    "Season",
    season_options,
    index=season_options.index(selected_season) if selected_season in season_options else 0,
    key="explorer_season",
)

# Sync selections back to session state for cross-page persistence
st.session_state["selected_team"] = selected_team
st.session_state["selected_season"] = selected_season

# Filter data
filtered_df = filter_by_season(df, selected_season)
team_df = filtered_df[filtered_df["Team"] == selected_team].sort_values(["season", "Round"])

if len(team_df) == 0:
    st.warning(f"No data available for {selected_team}")
    st.stop()

# Create match selector
team_df["match_label"] = team_df.apply(
    lambda x: f"R{int(x['Round'])} ({x['season']}) - {x['Match']} ({x['Score']})",
    axis=1
)

match_options = team_df["match_label"].tolist()
selected_match = st.selectbox("Select Match", match_options)

# Get selected match data
match_row = team_df[team_df["match_label"] == selected_match].iloc[0]

# Get opponent's data for the same match
opponent = match_row["Opponent"]
opponent_row = filtered_df[
    (filtered_df["Team"] == opponent) &
    (filtered_df["Opponent"] == selected_team) &
    (filtered_df["Round"] == match_row["Round"]) &
    (filtered_df["season"] == match_row["season"])
]

if len(opponent_row) > 0:
    opponent_row = opponent_row.iloc[0]
else:
    opponent_row = None

st.markdown("---")

# Match Summary
st.subheader("Match Summary")

col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    st.markdown(f"### {selected_team}")
    if match_row["Side"] == "Home":
        st.markdown("🏠 **HOME**")
    else:
        st.markdown("✈️ **AWAY**")

with col2:
    # Score display
    score = match_row["Score"]
    st.markdown(f"## {score}")

    # Result
    if match_row["is_win"] == 1:
        st.markdown(f"**{selected_team} WIN** ✅")
    elif match_row["is_draw"] == 1:
        st.markdown("**DRAW** 🟡")
    else:
        st.markdown(f"**{selected_team} LOSS** ❌")

with col3:
    st.markdown(f"### {opponent}")
    if match_row["Side"] == "Home":
        st.markdown("✈️ **AWAY**")
    else:
        st.markdown("🏠 **HOME**")

st.markdown(f"**Date:** {match_row['Date']}")
st.markdown(f"**Round:** {int(match_row['Round'])} | **Season:** {match_row['season']}")

st.markdown("---")

# Key Stats Comparison
st.subheader("Key Statistics Comparison")

if opponent_row is not None:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"### {selected_team}")

    with col2:
        st.markdown("### Metric")

    with col3:
        st.markdown(f"### {opponent}")

    # Stats to compare
    key_stats = [
        ("Goals", "Goal scored"),
        ("xG", "Expected goals (xG)"),
        ("Possession %", "possession_pct"),
        ("Total Shots", "Total shots"),
        ("Shots on Target", "Shots on target"),
        ("Big Chances", "Big chances"),
        ("Passes", "Passes"),
        ("Tackles", "Tackles"),
        ("Corners", "Corners"),
    ]

    # Define which stats should be integers vs floats
    float_stats = ["xG", "Possession %"]

    for stat_name, col_name in key_stats:
        col1, col2, col3 = st.columns(3)

        team_val = match_row[col_name] if col_name in match_row.index else "N/A"
        opp_val = opponent_row[col_name] if col_name in opponent_row.index else "N/A"

        # Format values based on stat type
        if isinstance(team_val, (int, float)) and team_val != "N/A":
            if stat_name == "Possession %":
                team_val = f"{int(team_val)}%"
            elif stat_name in float_stats:
                team_val = f"{team_val:.2f}"
            else:
                team_val = f"{int(team_val)}"

        if isinstance(opp_val, (int, float)) and opp_val != "N/A":
            if stat_name == "Possession %":
                opp_val = f"{int(opp_val)}%"
            elif stat_name in float_stats:
                opp_val = f"{opp_val:.2f}"
            else:
                opp_val = f"{int(opp_val)}"

        with col1:
            st.markdown(f"**{team_val}**")
        with col2:
            st.markdown(f"{stat_name}")
        with col3:
            st.markdown(f"**{opp_val}**")

    st.markdown("---")

    # Visual comparison bar chart
    st.subheader("Visual Comparison")

    comparison_metrics = [
        ("xG", "Expected goals (xG)"),
        ("Possession", "possession_pct"),
        ("Shots", "Total shots"),
        ("Shots on Target", "Shots on target"),
        ("Passes", "Passes"),
        ("Tackles", "Tackles"),
    ]

    team_values = []
    opp_values = []
    metric_names = []

    for name, col in comparison_metrics:
        if col in match_row.index and col in opponent_row.index:
            team_values.append(match_row[col])
            opp_values.append(opponent_row[col])
            metric_names.append(name)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name=selected_team,
        x=metric_names,
        y=team_values,
        marker_color=get_team_color(selected_team),
    ))

    fig.add_trace(go.Bar(
        name=opponent,
        x=metric_names,
        y=opp_values,
        marker_color=get_team_color(opponent),
    ))

    fig.update_layout(
        barmode="group",
        title="Match Statistics Comparison",
        template="none",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
    )

    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Full Match Stats Table
st.subheader("Full Match Statistics")

# Select columns to display
display_columns = [
    "Team", "Side", "Score", "Goal scored", "Goal conceded",
    "Expected goals (xG)", "xG on target (xGOT)", "possession_pct",
    "Total shots", "Shots on target", "Shots inside box", "Shots outside box",
    "Big chances", "Big chances missed",
    "Passes", "Accurate passes_count", "Accurate passes_pct",
    "Opposition half", "Own half",
    "Tackles", "Interceptions", "Blocks", "Clearances",
    "Corners", "Offsides", "Fouls committed",
    "Yellow cards", "Red cards",
]

# Filter columns that exist
existing_cols = [c for c in display_columns if c in match_row.index]

# Create display dataframe
if opponent_row is not None:
    stats_df = pd.DataFrame({
        "Metric": existing_cols,
        selected_team: [match_row[c] for c in existing_cols],
        opponent: [opponent_row[c] for c in existing_cols],
    })
else:
    stats_df = pd.DataFrame({
        "Metric": existing_cols,
        selected_team: [match_row[c] for c in existing_cols],
    })

# Format numeric values properly before converting to strings for Arrow compatibility
# Integer columns (no decimals)
int_cols = ["Goal scored", "Goal conceded", "Total shots", "Shots on target",
            "Shots inside box", "Shots outside box", "Big chances", "Big chances missed",
            "Passes", "Accurate passes_count", "Opposition half", "Own half",
            "Tackles", "Interceptions", "Blocks", "Clearances",
            "Corners", "Offsides", "Fouls committed", "Yellow cards", "Red cards"]

# Float columns with 2 decimals
float_cols = ["Expected goals (xG)", "xG on target (xGOT)", "possession_pct", "Accurate passes_pct"]

team_cols = [selected_team] + ([opponent] if opponent_row is not None else [])

for col in team_cols:
    formatted_values = []
    for i, metric in enumerate(stats_df["Metric"]):
        val = stats_df.loc[i, col]
        if pd.isna(val) or val == "N/A":
            formatted_values.append("N/A")
        elif metric == "possession_pct":
            formatted_values.append(f"{int(float(val))}%")
        elif metric in int_cols:
            formatted_values.append(str(int(float(val))))
        elif metric in float_cols:
            formatted_values.append(f"{float(val):.2f}")
        else:
            formatted_values.append(str(val))
    stats_df[col] = formatted_values

# Clean up metric names for display
stats_df["Metric"] = stats_df["Metric"].replace({
    "possession_pct": "Possession %",
    "Accurate passes_count": "Accurate Passes",
    "Accurate passes_pct": "Pass Accuracy %",
    "Goal scored": "Goals Scored",
    "Goal conceded": "Goals Conceded",
    "Expected goals (xG)": "xG",
    "xG on target (xGOT)": "xGOT",
    "Total shots": "Total Shots",
    "Shots on target": "Shots on Target",
    "Shots inside box": "Shots Inside Box",
    "Shots outside box": "Shots Outside Box",
    "Big chances": "Big Chances",
    "Big chances missed": "Big Chances Missed",
    "Opposition half": "Opp. Half Passes",
    "Own half": "Own Half Passes",
    "Fouls committed": "Fouls",
    "Yellow cards": "Yellow Cards",
    "Red cards": "Red Cards",
})

st.dataframe(stats_df.set_index("Metric"), width='stretch')

st.markdown("---")

# Match Context
st.subheader("Match Context")

# Get matches around this one
match_idx = team_df.index.get_loc(team_df[team_df["match_label"] == selected_match].index[0])
context_start = max(0, match_idx - 2)
context_end = min(len(team_df), match_idx + 3)

context_matches = team_df.iloc[context_start:context_end][
    ["Round", "Date", "Opponent", "Side", "Score", "points", "Goal scored", "Goal conceded"]
].copy()

context_matches["Result"] = context_matches["points"].map({3: "W", 1: "D", 0: "L"})

# Ensure all columns have consistent types for Arrow compatibility
# Convert numeric columns that should be integers to int
int_columns = ["Round", "points", "Goal scored", "Goal conceded"]
for col in int_columns:
    if col in context_matches.columns:
        context_matches[col] = context_matches[col].astype(int)

# Convert remaining object columns to string
for col in context_matches.columns:
    if context_matches[col].dtype == 'object':
        context_matches[col] = context_matches[col].astype(str)

# Highlight current match
def highlight_current(row):
    if row.name == team_df[team_df["match_label"] == selected_match].index[0]:
        return ["background-color: #DA291C; color: white"] * len(row)
    return [""] * len(row)

st.markdown("**Surrounding Matches:**")
st.dataframe(
    context_matches.style.apply(highlight_current, axis=1),
    width='stretch',
    hide_index=True,
)
