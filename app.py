import streamlit as st

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Premier League Team Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS - Theme compatible (works with both light and dark modes)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #DA291C;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: inherit;
        opacity: 0.7;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: transparent;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    /* Theme-aware metric styling using semi-transparent background */
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Define pages with grouping
home_page = st.Page("pages/home.py", title="Home", icon="🏠")
season_overview = st.Page("pages/1_Season_Overview.py", title="Season Overview", icon="📅")
attacking = st.Page("pages/2_Attacking_Analysis.py", title="Attacking", icon="⚽")
defensive = st.Page("pages/3_Defensive_Analysis.py", title="Defensive", icon="🛡️")
possession = st.Page("pages/4_Possession_Passing.py", title="Possession & Passing", icon="🎯")
match_explorer = st.Page("pages/5_Match_Explorer.py", title="Match Explorer", icon="🔍")

# Create navigation with groups
pg = st.navigation({
    "Overview": [home_page, season_overview],
    "Statistic Analysis": [attacking, defensive, possession],
    "Tools": [match_explorer],
})

# Run the selected page
pg.run()
