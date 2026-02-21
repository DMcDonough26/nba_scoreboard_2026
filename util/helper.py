
# load packages
import streamlit as st
from datetime import datetime
import pandas as pd
import base64
import requests

# get today
@st.cache_data()
def get_today():
    today = datetime.today()
    return today

# format time (passing as apply function this way because row by row formatting differs)
def format_time(x):
    return pd.to_datetime(x).strftime('%#I:%M:%p')

def lower_all(df):
    return [x.lower() for x in df.columns]

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

# version 2
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

# note: if this is just binary, it could probably be rewritten as a one-line lambda function
@st.cache_data()
def days_rest(x):
    # if x == 0:
        # return 'B2B'
    if x == 1:
        return '1 day'
    else:
        return str(x) + ' days'

# check contrast
@st.cache_data()
def get_contrast(x):
    if ((x['off'] <= 5) & (x['def'] <=5)):
        return 1
    else:
        return 0

# star function
@st.cache_data()
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