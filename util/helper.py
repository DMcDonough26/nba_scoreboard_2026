
# load packages
import streamlit as st
from datetime import datetime
import pandas as pd
import base64
import requests
import pytz
import re

# get today
@st.cache_data(ttl=300)
def get_today():
    eastern = pytz.timezone("America/New_York")
    return datetime.now(eastern)


# format time (passing as apply function this way because row by row formatting differs)
def format_time(x):
    return pd.to_datetime(x).strftime('%#I:%M:%p')

# lower case the field names
def lower_all(df):
    return [x.lower() for x in df.columns]

# map team names and abbreviations
def get_team_abbreviations():
    team_abbreviations = {
        "Atlanta Hawks": "ATL",
        "Boston Celtics": "BOS",
        "Brooklyn Nets": "BKN",
        "Charlotte Hornets": "CHA",
        "Chicago Bulls": "CHI",
        "Cleveland Cavaliers": "CLE",
        "Dallas Mavericks": "DAL",
        "Denver Nuggets": "DEN",
        "Detroit Pistons": "DET",
        "Golden State Warriors": "GSW",
        "Houston Rockets": "HOU",
        "Indiana Pacers": "IND",
        "Los Angeles Clippers": "LAC",
        "Los Angeles Lakers": "LAL",
        "Memphis Grizzlies": "MEM",
        "Miami Heat": "MIA",
        "Milwaukee Bucks": "MIL",
        "Minnesota Timberwolves": "MIN",
        "New Orleans Pelicans": "NOP",
        "New York Knicks": "NYK",
        "Oklahoma City Thunder": "OKC",
        "Orlando Magic": "ORL",
        "Philadelphia 76ers": "PHI",
        "Phoenix Suns": "PHX",
        "Portland Trail Blazers": "POR",
        "Sacramento Kings": "SAC",
        "San Antonio Spurs": "SAS",
        "Toronto Raptors": "TOR",
        "Utah Jazz": "UTA",
        "Washington Wizards": "WAS"
    }
    return team_abbreviations

# map abbreviations across sources
def get_team_abbreviations2():
    team_abbreviations2 = {
        "ATL": "ATL",
        "BOS": "BOS",
        "BRK": "BKN",
        "CHO": "CHA",
        "CHI": "CHI",
        "CLE": "CLE",
        "DAL": "DAL",
        "DEN": "DEN",
        "DET": "DET",
        "GSW": "GSW",
        "HOU": "HOU",
        "IND": "IND",
        "LAC": "LAC",
        "LAL": "LAL",
        "MEM": "MEM",
        "MIA": "MIA",
        "MIL": "MIL",
        "MIN": "MIN",
        "NOP": "NOP",
        "NYK": "NYK",
        "OKC": "OKC",
        "ORL": "ORL",
        "PHI": "PHI",
        "PHO": "PHX",
        "POR": "POR",
        "SAC": "SAC",
        "SAS": "SAS",
        "TOR": "TOR",
        "UTA": "UTA",
        "WAS": "WAS"
        } 
    
    return team_abbreviations2

# check contrast in four factors for ratings
def get_contrast(x):
    if ((x['off'] <= 5) & (x['def'] <=5)):
        return 1
    else:
        return 0

# use NBA's definition of star for injury rating
def define_star(x):
    response = 0
    if pd.isna(x):
        return response
    else:
        vals = x.split(',')
    for i in range(len(vals)):
        if vals[i] in ['AS','NBA1','NBA2','NBA3']:
            response = 1
    return response

# alter URL for logos
def url_to_data_url(url: str) -> str:
        r = requests.get(url)
        b64 = base64.b64encode(r.content).decode("utf-8")
        return f"data:image/png;base64,{b64}"


class APIFailure(Exception):
    pass


# additional code to handle change in gamestatustext from API
def _clock_to_seconds(clock):
    """Convert an ISO-style clock like 'PT08M30.00S' to whole seconds (None if unparseable)."""
    if not isinstance(clock, str) or not clock.strip():
        return None
    m = re.fullmatch(r'PT(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?', clock.strip())
    if not m:
        return None
    minutes = int(m.group(1)) if m.group(1) else 0
    seconds = float(m.group(2)) if m.group(2) else 0.0
    return minutes * 60 + int(round(seconds))


def format_game_clock(x):
    """Display string for a scoreboard row, e.g. 'Q3 8:30', 'END Q2', 'Half', 'Final'."""

    status = x['gameStatus']
    status_text = str(x['gameStatusText']).strip()

    # upcoming games: the feed already gives the tip-off time (e.g. '9:00 pm ET')
    if status == 1:
        return status_text

    # finished games
    if status == 3:
        return status_text or 'Final'

    # live games
    if status == 2:
        if status_text.upper().startswith('HALF'):
            return 'Half'

        period = int(x['period'])
        if period > 4:
            ot = period - 4
            label = 'OT' if ot == 1 else f'OT{ot}'
        else:
            label = f'Q{period}'

        total = _clock_to_seconds(x['gameClock'])
        if total is None:
            return label
        if total == 0:
            return f'END {label}'

        mins, secs = divmod(total, 60)
        return f'{label} {mins}:{secs:02d}'

    return status_text