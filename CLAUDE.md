# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Premier League football analytics dashboard built with Streamlit. Analyze any team's performance and compare teams using match-level statistics from FotMob.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

## Project Architecture

```
pl_team_analysis/
├── app.py                    # Main Streamlit entry point
├── config.py                 # Configuration (paths, defaults, season files)
├── datasets/                 # CSV data files from fotmob-scraper
├── src/
│   ├── data/
│   │   ├── loader.py         # Data loading with @st.cache_data
│   │   └── preprocessor.py   # Data cleaning, parsing, calculated fields
│   ├── metrics/
│   │   ├── attacking.py      # Goals, xG, shots, big chances metrics
│   │   ├── defensive.py      # Tackles, clean sheets, defensive actions
│   │   ├── possession.py     # Possession, passing, crosses metrics
│   │   └── aggregators.py    # Season summaries, home/away splits, form
│   ├── visualizations/
│   │   ├── charts.py         # Plotly charts (bar, line, radar, cumulative)
│   │   └── theme.py          # Team colors (TEAM_COLORS dict)
│   └── utils/
│       └── constants.py      # TEAMS list (20 Premier League teams)
└── pages/                    # Streamlit multi-page app
    ├── 1_Season_Overview.py
    ├── 2_Attacking_Analysis.py
    ├── 3_Defensive_Analysis.py
    ├── 4_Possession_Passing.py
    └── 5_Match_Explorer.py
```

## Key Functions

| Module | Function | Purpose |
|--------|----------|---------|
| `loader.py` | `load_all_seasons()` | Load and combine all season CSVs |
| `preprocessor.py` | `preprocess_data(df)` | Parse columns, add calculated fields |
| `preprocessor.py` | `filter_by_season(df, season)` | Filter data by season string |
| `aggregators.py` | `get_season_summary(df)` | Full season stats for a team |
| `aggregators.py` | `get_home_away_split(df)` | Home vs away performance |
| `aggregators.py` | `get_form(df, last_n)` | Recent form (W/D/L) |
| `aggregators.py` | `calculate_league_position(df, season)` | League table standings |

## Adding New Seasons

1. Add CSV to `datasets/` folder
2. Update `SEASON_FILES` dict in `config.py`
3. Optionally update `DEFAULT_SEASON`

## Data Format

CSV files from [fotmob-scraper](https://github.com/ZeeetOne/fotmob-scraper):
- Each match = 2 rows (one per team)
- Percentage columns: "408 (85%)" format - parsed by `parse_percentage_string()`
- Possession: "55%" format - parsed by `parse_possession()`

### Key Columns

| Category | Columns |
|----------|---------|
| Match Info | `Date`, `Match`, `Team`, `Opponent`, `Side`, `Round`, `Score` |
| Goals | `Goal scored`, `Goal conceded`, `points` |
| xG | `Expected goals (xG)`, `xG open play`, `xG set play`, `xG on target (xGOT)` |
| Shots | `Total shots`, `Shots on target`, `Big chances`, `Shots inside box` |
| Passing | `Accurate passes`, `Passes`, `Opposition half`, `Accurate crosses` |
| Defensive | `Tackles`, `Interceptions`, `Blocks`, `Clearances`, `Keeper saves` |
| Possession | `Ball possession`, `Duels won`, `Successful dribbles` |
