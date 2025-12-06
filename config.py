from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
DATASETS_DIR = PROJECT_ROOT / "datasets"

# Data files
SEASON_FILES = {
    "2023-2024": DATASETS_DIR / "fotmob_season_2023-2024_stats.csv",
    "2024-2025": DATASETS_DIR / "fotmob_season_2024-2025_stats.csv",
}

# Default selections
DEFAULT_TEAM = "Manchester United"
DEFAULT_COMPARISON_TEAM = "Manchester City"
DEFAULT_SEASON = "2024-2025"

# League winners by season
LEAGUE_WINNERS = {
    "2023-2024": "Manchester City",
    "2024-2025": "Liverpool",
}

# Chart settings
ROLLING_WINDOW = 5
CHART_HEIGHT = 400
