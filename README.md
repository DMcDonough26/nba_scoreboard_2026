# nba\_scoreboard\_2026

## Overview

The purpose of this project is to create a data product that serves as a companion to watching NBA league pass.
This streamlit web app has:
- a scoreboard that directs the user to the best game currently on TV
- charts that provide context and let the user analyze matchups

The app can be found: [nbawatch.streamlit.app](https://nbawatch.streamlit.app) <br>
And the writeup here: [nba_scoreboard_2026](https://dmcdonough26.github.io/nba-scoreboard/)

## Requirements

All packages can be found in requirements.txt

lmxl is just needed for cloud deployment and was left unpinned to let streamlit cloud use the latest compatible version

## App

This file is the main driver of the web app and manages control flow. The key steps are:

-- The top of the page is rendered first since streamlit needs to be run before caching can begin
-- All data is then returned from wrangle_data.py
-- Data is passed to web_page.py to render the rest of the page
-- App.py also handles autorefresh and some exeception handling for days without games and breakages in data pipeline

## Get data

The file contains all of the functions to pull data for the app. Most of the data comes from the NBA API, but there is some scraping of basketball reference, sourcing of team logos, and a few static files.

Everything here is cached - either for the remainder of the day or for five minutes depending on the data element.

## Wrangle data

This file calls all of the data pull functions. No new data pull functions are defined, this script purely wrangles the data.

## Ratings

This file handles the game ratings, which are a linear combination of the variables in the ratings UI.

The "weights" come from the UI rating variables. This script handles properly translating the user inputs into percentages for each of the variables.

The "X" variables come from the wrangle data script. They are normalized to be put on the same scale, which is also handled here.

The final combination of weights and normalized variables is put into a final score, which goes through a min/max normalization to be put on a 0-10 scale and passed to the scoreboard dataframe on the app.

## Web page

This file handles rendering everything in the web app:
-- UI to assign weights to rating variables
-- the scoreboard dataframe
-- UI to let the user select the game and a side of the ball
-- the what-to-watch charts
-- a refresh button which will clear the cache on the scoreboard API, injury report, odds, and live box score

## Charts

This file contains code for the four charts, built via plotly

## Helper

This file has miscellaneous helper code including translation dictionaries across data sources

