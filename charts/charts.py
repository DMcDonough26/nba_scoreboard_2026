

# load packages
import streamlit as st
from datetime import datetime
import pandas as pd
from nba_api.live.nba.endpoints import boxscore, odds, playbyplay, scoreboard
# initially built with live endpoint, but new stats endpoint has broadcaster, could refactor to just one endpoint
from nba_api.stats.endpoints import scoreboardv3, leaguegamefinder

# four factors

# style

# shots