
# load packages
from ui.web_page import create_page, launch_page
from data.wrangle_data import combine_data

def main():
    # create page first, so you can cache functions
    create_page()

    # get ingredients
    today, live_df, upcoming_df, finished_df, scoreboard_raw_df,\
    ff_chart_df, style_df, pt_df, shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long = combine_data()

    # launch page
    launch_page(today, live_df, upcoming_df, finished_df, scoreboard_raw_df,
                ff_chart_df, style_df, pt_df,
                shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long)
    

main()