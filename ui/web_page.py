

# load packages
import streamlit as st
from datetime import datetime
import pandas as pd
from nba_api.live.nba.endpoints import boxscore, odds, playbyplay, scoreboard
# initially built with live endpoint, but new stats endpoint has broadcaster, could refactor to just one endpoint
from nba_api.stats.endpoints import scoreboardv3, leaguegamefinder
from data.scoreboard_data import *
from data.chart_data import *
from util.helper import *




# creating the page first, so that I can then start catching functions
def create_page():
    st.set_page_config(layout="wide")

# set up page
def launch_page(today, live_df, upcoming_df, finished_df, scoreboard_raw_df):
    st.title("NBA Scoreboard:"+" "+today.strftime("%m/%d/%Y"))
    st.write("Scores as of: ", today.strftime('%#I:%M:%p'))
    if st.button("Refresh"):
        get_today.clear()
        get_scoreboard.clear()
        get_injuries.clear()
        st.rerun()
    st.write("Importance for game ratings")

    with st.expander("Select categories for game ratings",expanded=True):
        # omitted contest percent, ball movement, player movement since not available for live games
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            cat1 = st.slider(label = "Point Differential", min_value = 0, max_value = 10, value = 10, step = 1, key='cat1')
        with col2:
            cat2 = st.slider(label = "Time Remaining", min_value = 0, max_value = 10, value = 10, step = 1, key='cat2')
        with col3:
            cat3 = st.slider(label = "Player Availability", min_value = 0, max_value = 10, value = 9, step = 1, key='cat3')
        with col4:
            cat4 = st.slider(label = "Team Quality", min_value = 0, max_value = 10, value = 9, step = 1, key='cat4')
        with col5:
            cat5 = st.slider(label = "Style Contrasts", min_value = 0, max_value = 10, value = 8, step = 1, key='cat5')
        with col6:
            cat6 = st.slider(label = "Zach Lowe Rankings", min_value = 0, max_value = 10, value = 8, step = 1, key='cat6')
        with col7:
            cat7 = st.slider(label = "Offensive Rating", min_value = 0, max_value = 10, value = 7, step = 1, key='cat7')
        
        col8, col9, col10, col11, col12, col13, col14 = st.columns(7)
        with col8:
            cat8 = st.slider(label = "Game Flow", min_value = 0, max_value = 10, value = 7, step = 1, key='cat8')
        with col9:
            cat9 = st.slider(label = "Foul Rate", min_value = 0, max_value = 10, value = 7, step = 1, key='cat9')
        with col10:
            cat10 = st.slider(label = "Assist Percent", min_value = 0, max_value = 10, value = 6, step = 1, key='cat10')
        with col11:
            cat11 = st.slider(label = "Egalitarian Offense", min_value = 0, max_value = 10, value = 6, step = 1, key='cat11')
        with col12:
            cat12 = st.slider(label = "Heroic Performance", min_value = 0, max_value = 10, value = 6, step = 1, key='cat12')
        with col13:
            cat13 = st.slider(label = "Pace", min_value = 0, max_value = 10, value = 6, step = 1, key='cat13')
        with col14:
            cat14 = st.slider(label = "National Broadcast", min_value = 0, max_value = 10, value = 6, step = 1, key='cat14')
    
    # Create the tabs
    tab1, tab2, tab3 = st.tabs(['Live Games', 'Upcoming', 'Finished Games'])

    # st.write('Live Games')
    with tab1:
        st.dataframe(
            live_df,
            column_config={
                "Away Logo": st.column_config.ImageColumn("Away Logo"),
                "Home Logo": st.column_config.ImageColumn("Home Logo")
            },
            hide_index=True,
            row_height=60)
    # st.write('Upcoming Games')
    with tab2:
        st.dataframe(
            upcoming_df,
                column_config={
                "Away Logo": st.column_config.ImageColumn("Away Logo"),
                "Home Logo": st.column_config.ImageColumn("Home Logo")
            },
            hide_index=True,
            row_height=60)
    # st.write('Finished Games')
    with tab3:
        st.dataframe(
            finished_df,
                column_config={
                "Away Logo": st.column_config.ImageColumn("Away Logo"),
                "Home Logo": st.column_config.ImageColumn("Home Logo")
            },
            hide_index=True,
            row_height=60)

        # option1 = st.selectbox(
    #     "Select a game",
    #     scoreboard_raw_df['game_name'],
    # )

    # # maybe make this a radial button

    # option2 = st.selectbox(
    #     "Choose a side of the ball",
    #     scoreboard_raw_df['game_name'],
    # )

    # # maybe make this three tabs

    # option3 = st.selectbox(
    #     "Choose a category",
    #     scoreboard_raw_df['game_name'],
    # )

    # box 1 - four factors
    # maybe a lollipop chart
    # maybe scale axes to min/max for league and use actual values OR use ranks

    # box 2 - shot selection
    # 

    # box 3 - style and play types
    # maybe start with radar charts
    # also consider a scatter plot which plots frequency/efficiency with dots for the team and league average

    # st.write("What to watch:")