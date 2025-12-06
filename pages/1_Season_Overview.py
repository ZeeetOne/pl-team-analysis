import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loader import load_all_seasons
from src.data.preprocessor import preprocess_data, filter_by_season
from src.metrics.aggregators import (
    get_season_summary,
    get_home_away_split,
    get_form,
    calculate_league_position,
)
from src.visualizations.charts import (
    create_cumulative_points_chart,
    create_bar_chart,
    create_home_away_comparison,
)
from config import DEFAULT_TEAM, DEFAULT_COMPARISON_TEAM, SEASON_FILES, DEFAULT_SEASON

st.title("📊 Season Overview")


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

# Sidebar for this page
st.sidebar.title("Season Overview Settings")
teams = sorted(df["Team"].unique().tolist())

selected_team = st.sidebar.selectbox(
    "Select Team",
    teams,
    index=teams.index(selected_team) if selected_team in teams else 0,
    key="overview_team",
)

# Comparison team selector (multiselect, max 3 teams)
available_comparison_teams = [t for t in teams if t != selected_team]
default_comparison = [t for t in comparison_teams_default if t in available_comparison_teams]
comparison_teams = st.sidebar.multiselect(
    "Compare With (max 3)",
    options=available_comparison_teams,
    default=default_comparison,
    max_selections=3,
    key="overview_comparison",
)

season_options = list(SEASON_FILES.keys())
selected_season = st.sidebar.selectbox(
    "Season",
    season_options,
    index=season_options.index(selected_season) if selected_season in season_options else 0,
    key="overview_season",
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

# Get summaries
team_summary = get_season_summary(team_df)

# Get comparison data for all selected comparison teams
comparison_data = {}
for comp_team in comparison_teams:
    comp_df = filtered_df[filtered_df["Team"] == comp_team]
    if len(comp_df) > 0:
        comparison_data[comp_team] = {
            "df": comp_df,
            "summary": get_season_summary(comp_df),
        }

# KPI Section
st.subheader(f"Key Statistics: {selected_team}")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Matches", team_summary.get("matches_played", 0))

with col2:
    st.metric("Points", team_summary.get("total_points", 0))

with col3:
    st.metric("Wins", team_summary.get("wins", 0))

with col4:
    st.metric("Draws", team_summary.get("draws", 0))

with col5:
    st.metric("Losses", team_summary.get("losses", 0))

with col6:
    st.metric("PPG", team_summary.get("points_per_game", 0))

st.markdown("---")

# Cumulative Points Chart
st.subheader("Cumulative Points Comparison")

# Build list of teams to compare
teams_to_compare = [selected_team] + comparison_teams

fig = create_cumulative_points_chart(
    filtered_df,
    teams_to_compare,
    title=f"Cumulative Points - {selected_season}",
)
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Home vs Away Performance
st.subheader("Home vs Away Performance")

team_split = get_home_away_split(team_df)

# Create columns: 1 for selected team + 1 for each comparison team
num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    st.markdown(f"### {selected_team}")

    ha_col1, ha_col2 = st.columns(2)

    with ha_col1:
        st.markdown("**Home**")
        st.markdown(f"Record: {team_split['home']['wins']}W-{team_split['home']['draws']}D-{team_split['home']['losses']}L")
        st.markdown(f"Points: {team_split['home']['points']}")
        st.markdown(f"PPG: {team_split['home']['points_per_game']}")
        st.markdown(f"GF: {team_split['home']['goals_scored']} | GA: {team_split['home']['goals_conceded']}")

    with ha_col2:
        st.markdown("**Away**")
        st.markdown(f"Record: {team_split['away']['wins']}W-{team_split['away']['draws']}D-{team_split['away']['losses']}L")
        st.markdown(f"Points: {team_split['away']['points']}")
        st.markdown(f"PPG: {team_split['away']['points_per_game']}")
        st.markdown(f"GF: {team_split['away']['goals_scored']} | GA: {team_split['away']['goals_conceded']}")

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        comparison_split = get_home_away_split(comparison_data[comp_team]["df"])
        with cols[i + 1]:
            st.markdown(f"### {comp_team}")

            ha_col1, ha_col2 = st.columns(2)

            with ha_col1:
                st.markdown("**Home**")
                st.markdown(f"Record: {comparison_split['home']['wins']}W-{comparison_split['home']['draws']}D-{comparison_split['home']['losses']}L")
                st.markdown(f"Points: {comparison_split['home']['points']}")
                st.markdown(f"PPG: {comparison_split['home']['points_per_game']}")
                st.markdown(f"GF: {comparison_split['home']['goals_scored']} | GA: {comparison_split['home']['goals_conceded']}")

            with ha_col2:
                st.markdown("**Away**")
                st.markdown(f"Record: {comparison_split['away']['wins']}W-{comparison_split['away']['draws']}D-{comparison_split['away']['losses']}L")
                st.markdown(f"Points: {comparison_split['away']['points']}")
                st.markdown(f"PPG: {comparison_split['away']['points_per_game']}")
                st.markdown(f"GF: {comparison_split['away']['goals_scored']} | GA: {comparison_split['away']['goals_conceded']}")

# Home/Away comparison chart
metrics = ["points", "goals_scored", "goals_conceded", "clean_sheets"]
fig = create_home_away_comparison(
    team_split["home"],
    team_split["away"],
    metrics,
    title=f"{selected_team} - Home vs Away",
)
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Recent Form
st.subheader("Recent Form (Last 5 Matches)")

team_form = get_form(team_df, last_n=5)

# Create columns: 1 for selected team + 1 for each comparison team
num_cols = 1 + len(comparison_teams) if comparison_teams else 1
cols = st.columns(num_cols)

with cols[0]:
    st.markdown(f"### {selected_team}")
    st.markdown(f"**Form:** {team_form['form_string']}")
    st.markdown(f"**Points:** {team_form['points']}/15")
    st.markdown(f"**Goals:** {team_form['goals_scored']} scored, {team_form['goals_conceded']} conceded")

for i, comp_team in enumerate(comparison_teams):
    if comp_team in comparison_data:
        comparison_form = get_form(comparison_data[comp_team]["df"], last_n=5)
        with cols[i + 1]:
            st.markdown(f"### {comp_team}")
            st.markdown(f"**Form:** {comparison_form['form_string']}")
            st.markdown(f"**Points:** {comparison_form['points']}/15")
            st.markdown(f"**Goals:** {comparison_form['goals_scored']} scored, {comparison_form['goals_conceded']} conceded")

st.markdown("---")

# League Table
st.subheader("League Standings")
standings = calculate_league_position(filtered_df, selected_season)

def highlight_teams(row):
    if row['Team'] == selected_team:
        return ['background-color: #DA291C; color: white'] * len(row)
    elif row['Team'] in comparison_teams:
        return ['background-color: #6CABDD; color: white'] * len(row)
    return [''] * len(row)

st.dataframe(
    standings.style.apply(highlight_teams, axis=1),
    width='stretch',
    hide_index=True,
)
