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
from data.chart_data import get_ff_chart_data, get_style_chart_data, get_team_play_type, get_shot_data
from util.helper import get_today

def main():
    # create page first, so you can cache functions
    create_page()

    # define today - this is cached
    today = get_today()

    # get ingredients
    live_df, upcoming_df, finished_df, scoreboard_raw_df = combine_data(today)

    # get chart dfs
    ff_df = get_ff_chart_data(scoreboard_raw_df)
    style_df = get_style_chart_data()
    pt_df = get_team_play_type()
    shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long = get_shot_data()

    # launch page
    launch_page(today, live_df, upcoming_df, finished_df, scoreboard_raw_df,
                ff_df, style_df, pt_df,
                shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long)
    

main()