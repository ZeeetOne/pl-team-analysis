# Team colors for Premier League teams
TEAM_COLORS = {
    "Manchester United": "#DA291C",
    "Manchester City": "#6CABDD",
    "Arsenal": "#EF0107",
    "Liverpool": "#C8102E",
    "Chelsea": "#034694",
    "Tottenham Hotspur": "#132257",
    "Newcastle United": "#241F20",
    "Aston Villa": "#670E36",
    "Brighton & Hove Albion": "#0057B8",
    "West Ham United": "#7A263A",
    "Brentford": "#E30613",
    "Fulham": "#000000",
    "Crystal Palace": "#1B458F",
    "Wolverhampton Wanderers": "#FDB913",
    "AFC Bournemouth": "#DA291C",
    "Nottingham Forest": "#DD0000",
    "Everton": "#003399",
    "Leicester City": "#003090",
    "Southampton": "#D71920",
    "Ipswich Town": "#0033A0",
    "Luton Town": "#F78F1E",
    "Burnley": "#6C1D45",
    "Sheffield United": "#EE2737",
}

# Chart template settings
CHART_TEMPLATE = "none"  # Use none for theme-agnostic transparent backgrounds

# Default layout settings
DEFAULT_LAYOUT = {
    "font_family": "Arial, sans-serif",
    "title_font_size": 18,
    "legend_orientation": "h",
    "legend_yanchor": "bottom",
    "legend_y": -0.2,
    "legend_xanchor": "center",
    "legend_x": 0.5,
    "margin": {"l": 50, "r": 50, "t": 60, "b": 50},
}

# Color palette for general use
COLORS = {
    "primary": "#DA291C",  # Man Utd Red
    "secondary": "#6CABDD",  # Man City Blue
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40",
}

# Form colors (Win/Draw/Loss)
FORM_COLORS = {
    "W": "#28a745",  # Green
    "D": "#ffc107",  # Yellow
    "L": "#dc3545",  # Red
}


def get_team_color(team: str) -> str:
    """Get color for a specific team.

    Args:
        team: Team name

    Returns:
        Hex color code
    """
    return TEAM_COLORS.get(team, "#666666")
