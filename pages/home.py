import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DEFAULT_TEAM, DEFAULT_COMPARISON_TEAM, DEFAULT_SEASON, SEASON_FILES
from src.data.loader import load_all_seasons, get_available_teams
from src.data.preprocessor import preprocess_data, filter_by_season
from src.metrics.aggregators import get_season_summary, get_form, calculate_league_position


@st.cache_data
def load_and_preprocess_data():
    """Load and preprocess all data."""
    df = load_all_seasons()
    df = preprocess_data(df)
    return df


def show():
    # Load data
    df = load_and_preprocess_data()
    teams = get_available_teams(df)

    # Sidebar
    st.sidebar.title("⚽ Analysis Settings")

    # Season selector
    season_options = list(SEASON_FILES.keys())
    selected_season = st.sidebar.selectbox(
        "Select Season",
        season_options,
        index=season_options.index(DEFAULT_SEASON) if DEFAULT_SEASON in season_options else 0,
        key="home_season",
    )

    # Team selector
    selected_team = st.sidebar.selectbox(
        "Select Team",
        teams,
        index=teams.index(DEFAULT_TEAM) if DEFAULT_TEAM in teams else 0,
        key="home_team",
    )

    # Comparison team selector (multiselect, max 3 teams)
    available_comparison_teams = [t for t in teams if t != selected_team]
    default_comparison = (
        [DEFAULT_COMPARISON_TEAM]
        if DEFAULT_COMPARISON_TEAM in available_comparison_teams
        else []
    )
    comparison_teams = st.sidebar.multiselect(
        "Compare With (max 3)",
        options=available_comparison_teams,
        default=default_comparison,
        max_selections=3,
        key="home_comparison",
    )

    # Filter data by season
    filtered_df = filter_by_season(df, selected_season)

    # Store in session state for pages
    st.session_state["df"] = filtered_df
    st.session_state["selected_team"] = selected_team
    st.session_state["comparison_teams"] = comparison_teams
    st.session_state["selected_season"] = selected_season

    # Main content - Home page
    st.markdown(f'<p class="main-header">Premier League Team Analysis Dashboard</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Premier League Performance Analysis (2023-24 & 2024-25 Seasons)</p>', unsafe_allow_html=True)

    # Get team data
    team_df = filtered_df[filtered_df["Team"] == selected_team]

    if len(team_df) == 0:
        st.warning(f"No data available for {selected_team} in the selected season.")
        return

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

    # League position
    standings = calculate_league_position(filtered_df, selected_season)
    team_position = standings[standings["Team"] == selected_team]["Position"].values[0] if len(standings[standings["Team"] == selected_team]) > 0 else "N/A"

    # KPI Row
    st.subheader(f"📊 {selected_team} Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Position", f"#{team_position}")

    with col2:
        st.metric("Points", team_summary.get("total_points", 0))

    with col3:
        st.metric("Matches", team_summary.get("matches_played", 0))

    with col4:
        st.metric("Goals For", team_summary.get("goals_scored", 0))

    with col5:
        st.metric("Goals Against", team_summary.get("goals_conceded", 0))

    st.markdown("---")

    # Quick comparison
    if comparison_teams:
        comparison_label = " vs ".join([selected_team] + comparison_teams)
        st.subheader(f"⚔️ Quick Comparison: {comparison_label}")

        # Create columns: 1 for selected team + 1 for each comparison team
        num_cols = 1 + len(comparison_teams)
        cols = st.columns(num_cols)

        with cols[0]:
            st.markdown(f"### {selected_team}")
            st.markdown(f"**Position:** #{team_position}")
            st.markdown(f"**Record:** {team_summary.get('wins', 0)}W - {team_summary.get('draws', 0)}D - {team_summary.get('losses', 0)}L")
            st.markdown(f"**Points:** {team_summary.get('total_points', 0)}")
            st.markdown(f"**Goal Difference:** {team_summary.get('goal_difference', 0):+d}")
            st.markdown(f"**xG Overperformance:** {team_summary.get('xg_overperformance', 0):+.2f}")

        for i, comp_team in enumerate(comparison_teams):
            if comp_team in comparison_data:
                comp_summary = comparison_data[comp_team]["summary"]
                comp_position = standings[standings["Team"] == comp_team]["Position"].values[0] if len(standings[standings["Team"] == comp_team]) > 0 else "N/A"
                with cols[i + 1]:
                    st.markdown(f"### {comp_team}")
                    st.markdown(f"**Position:** #{comp_position}")
                    st.markdown(f"**Record:** {comp_summary.get('wins', 0)}W - {comp_summary.get('draws', 0)}D - {comp_summary.get('losses', 0)}L")
                    st.markdown(f"**Points:** {comp_summary.get('total_points', 0)}")
                    st.markdown(f"**Goal Difference:** {comp_summary.get('goal_difference', 0):+d}")
                    st.markdown(f"**xG Overperformance:** {comp_summary.get('xg_overperformance', 0):+.2f}")

        st.markdown("---")

    # Recent form
    st.subheader("📈 Recent Form (Last 5 Matches)")

    team_form = get_form(team_df, last_n=5)

    if comparison_teams:
        num_cols = 1 + len(comparison_teams)
        cols = st.columns(num_cols)

        with cols[0]:
            st.markdown(f"**{selected_team}:** {team_form['form_string']}")
            st.markdown(f"Points: {team_form['points']}/15 | GF: {team_form['goals_scored']} | GA: {team_form['goals_conceded']}")

        for i, comp_team in enumerate(comparison_teams):
            if comp_team in comparison_data:
                comp_form = get_form(comparison_data[comp_team]["df"], last_n=5)
                with cols[i + 1]:
                    st.markdown(f"**{comp_team}:** {comp_form['form_string']}")
                    st.markdown(f"Points: {comp_form['points']}/15 | GF: {comp_form['goals_scored']} | GA: {comp_form['goals_conceded']}")
    else:
        st.markdown(f"**{selected_team}:** {team_form['form_string']}")
        st.markdown(f"Points: {team_form['points']}/15 | GF: {team_form['goals_scored']} | GA: {team_form['goals_conceded']}")

    st.markdown("---")

    # League Table
    st.subheader("📋 League Standings")

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

    # Footer
    st.markdown("---")
    st.markdown("*Navigate to other pages using the sidebar for detailed analysis.*")


# Run the page
show()
