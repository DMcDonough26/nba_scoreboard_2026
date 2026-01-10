# Notes:
# add to the inputs: rest, ball movement, player movement, contests, maybe four factors
# highlight games in crunch time, as well as rivalries
# finish game rating method
# confirm how refresh functionality works, since it is automatically refreshing now
# Tasting notes
# Format better, including background image or header
# Real time remaining model
# Win prob model or scrape


# load packages
import streamlit as st
from datetime import datetime
import pandas as pd
from nba_api.live.nba.endpoints import boxscore, odds, playbyplay, scoreboard
# initially built with live endpoint, but new stats endpoint has broadcaster, could refactor to just one endpoint
from nba_api.stats.endpoints import scoreboardv3, leaguegamefinder
from ui.web_page import *
from data.get_data import *
from util.helper import *


def main():
    # define today
    today = datetime.today()

    # get ingredients
    live_df, upcoming_df, finished_df, scoreboard_raw_df = combine_data(today)

    # start page
    launch_page(today, live_df, upcoming_df, finished_df, scoreboard_raw_df)

    # update page

main()