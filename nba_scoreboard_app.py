# Notes:
# add to the inputs: rest, ball movement, player movement, contests, maybe four factors
# highlight games in crunch time, as well as rivalries
# finish game rating method
# Tasting notes
# Format better, including background image or header
# Real time remaining model
# Win prob model or scrape


# load packages
from ui.web_page import create_page, launch_page
from data.scoreboard_data import combine_data
from data.chart_data import get_ff_chart_data, get_team_play_type
from util.helper import get_today


# on a non-refresh rerun:
# create page
# launch page

# on refresh, these are also unlocked:
# today (for timestamp)
# scoreboard (latest scores)
# injuries (could be late scratches on upcoming games)

def main():
    # create page first, so you can cache functions
    create_page()

    # define today - this is cached
    today = get_today()

    # get ingredients
    live_df, upcoming_df, finished_df, scoreboard_raw_df = combine_data(today)
    ff_df = get_ff_chart_data(scoreboard_raw_df)
    pt_df = get_team_play_type()

    # start page
    launch_page(today, live_df, upcoming_df, finished_df, scoreboard_raw_df, ff_df, pt_df)
    

main()