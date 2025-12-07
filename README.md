# Premier League Team Analysis Dashboard

A Streamlit dashboard for analyzing Premier League team performance with match-level statistics from FotMob.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Season Overview**: Points, wins, draws, losses, cumulative points chart, home/away splits, recent form
- **Attacking Analysis**: Goals, xG, shots, big chances, shot quality metrics, tactical insights
- **Defensive Analysis**: Goals conceded, tackles, interceptions, clean sheets, defensive actions
- **Possession & Passing**: Ball possession, pass accuracy, long balls, crosses, touches in box
- **Match Explorer**: Browse individual match statistics

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pl_team_analysis.git
cd pl_team_analysis

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

## Project Structure

```
pl_team_analysis/
├── app.py                    # Main Streamlit entry point
├── config.py                 # Configuration (paths, defaults)
├── requirements.txt          # Python dependencies
├── datasets/                 # CSV data files
│   ├── fotmob_season_2023-2024_stats.csv
│   └── fotmob_season_2024-2025_stats.csv
├── src/
│   ├── data/
│   │   ├── loader.py         # Data loading with caching
│   │   └── preprocessor.py   # Data cleaning & transformation
│   ├── metrics/
│   │   ├── attacking.py      # Goals, xG, shots metrics
│   │   ├── defensive.py      # Tackles, clean sheets metrics
│   │   ├── possession.py     # Possession, passing metrics
│   │   └── aggregators.py    # Season summaries, form
│   ├── visualizations/
│   │   ├── charts.py         # Plotly chart functions
│   │   └── theme.py          # Team colors, styling
│   └── utils/
│       └── constants.py      # Team names
└── pages/                    # Streamlit multi-page app
    ├── 1_Season_Overview.py
    ├── 2_Attacking_Analysis.py
    ├── 3_Defensive_Analysis.py
    ├── 4_Possession_Passing.py
    └── 5_Match_Explorer.py
```

## Data Source

Match statistics scraped from [FotMob](https://www.fotmob.com/) using my [fotmob-scraper](https://github.com/ZeeetOne/fotmob-scraper).

**Included seasons:**
- 2023-2024 Premier League season
- 2024-2025 Premier League season

### Adding Your Own Dataset

You can add more seasons or leagues by following these steps:

1. **Scrape data** using [fotmob-scraper](https://github.com/ZeeetOne/fotmob-scraper)

2. **Add CSV file** to the `datasets/` folder:
   ```
   datasets/
   ├── fotmob_season_2023-2024_stats.csv
   ├── fotmob_season_2024-2025_stats.csv
   └── fotmob_season_2025-2026_stats.csv  # Your new file
   ```

3. **Update `config.py`** to include the new season:
   ```python
   SEASON_FILES = {
       "2023-2024": DATASETS_DIR / "fotmob_season_2023-2024_stats.csv",
       "2024-2025": DATASETS_DIR / "fotmob_season_2024-2025_stats.csv",
       "2025-2026": DATASETS_DIR / "fotmob_season_2025-2026_stats.csv",  # Add this
   }

   # Optionally update default season
   DEFAULT_SEASON = "2025-2026"
   ```

4. **Restart the app** and the new season will appear in the dropdown

## Key Metrics

| Category | Metrics |
|----------|---------|
| Attacking | Goals, xG, xGOT, shots, big chances, shot conversion |
| Defensive | Goals conceded, tackles, interceptions, blocks, clean sheets |
| Possession | Ball possession %, passes, pass accuracy, crosses, long balls |

## Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly

## License

MIT License - feel free to use this project for your own analysis.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
