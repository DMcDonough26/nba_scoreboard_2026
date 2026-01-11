
# load packages
import streamlit as st
from datetime import datetime
import pandas as pd
from nba_api.live.nba.endpoints import boxscore, odds, playbyplay, scoreboard
# initially built with live endpoint, but new stats endpoint has broadcaster, could refactor to just one endpoint
from nba_api.stats.endpoints import scoreboardv3, leaguegamefinder
from ui.web_page import *
from data.scoreboard_data import *
from data.chart_data import *
from util.helper import *

@st.cache_data()
def get_team_adv():
    adv_df = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Advanced').get_data_frames()[0]
    adv_df.columns = lower_all(adv_df)
    return

@st.cache_data()
def get_team_four():
    four_df = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Four Factors').get_data_frames()[0]
    four_df.columns = lower_all(four_df)
    return four_df

def build_one_side_df(i,sb_df,team_stats_df,home=True, offense=True):

    measure_dict = {'off_rating_rank':'Rating','efg_pct_rank':'EFG','fta_rate_rank':'FTA','tm_tov_pct_rank':'TOV','oreb_pct_rank':'ORB',
                'def_rating_rank':'Rating','opp_efg_pct_rank':'EFG','opp_fta_rate_rank':'FTA','opp_tov_pct_rank':'TOV','opp_oreb_pct_rank':'ORB'}

    if home == True:
        team = sb_df['homeTeam.teamId'][i]
    else:
        team = sb_df['awayTeam.teamId'][i]
    if offense == True:
        temp_df = team_stats_df[team_stats_df['team_id']==team][['off_rating_rank','efg_pct_rank','fta_rate_rank','tm_tov_pct_rank','oreb_pct_rank']]
    else:
        temp_df = team_stats_df[team_stats_df['team_id']==team][['def_rating_rank','opp_efg_pct_rank','opp_fta_rate_rank','opp_tov_pct_rank','opp_oreb_pct_rank']]
    temp_df.columns = [measure_dict[x] for x in temp_df.columns]
    temp_df = temp_df.transpose().reset_index()
    if offense == True:
        temp_df.columns = ['measure','off']
    else:
        temp_df.columns = ['measure','def']
    return temp_df

@st.cache_data()
def get_ff_chart_data(sb_df):
    
    # make API calls
    adv_df = get_team_adv()
    four_df = get_team_four()

    # select columnns
    adv_red_df = adv_df[['team_id','off_rating','def_rating','off_rating_rank','def_rating_rank']]
    four_red_df = four_df[['team_id','efg_pct','fta_rate','tm_tov_pct','oreb_pct',
                        'opp_efg_pct', 'opp_fta_rate','opp_tov_pct', 'opp_oreb_pct',
                        'efg_pct_rank', 'fta_rate_rank', 'tm_tov_pct_rank', 'oreb_pct_rank',
                        'opp_efg_pct_rank', 'opp_fta_rate_rank', 'opp_tov_pct_rank', 'opp_oreb_pct_rank']]

    # merge
    team_stats_df = adv_red_df.merge(four_red_df,how='left',on='team_id')

    # wrangle for each of today's games
    for i in range(len(sb_df)):

        # home side on offense
        off_df = build_one_side_df(i,sb_df,team_stats_df,home=True,offense=True)
        def_df = build_one_side_df(i,sb_df,team_stats_df,home=False,offense=False)
        game_df1 = off_df.merge(def_df,on='measure')
        game_df1['game_name'] = sb_df['game_name'][i]
        game_df1['offense'] = sb_df['homeTeam.teamId'][i]
        
        # away side on offense
        off_df = build_one_side_df(i,sb_df,team_stats_df,home=False,offense=True)
        def_df = build_one_side_df(i,sb_df,team_stats_df,home=True,offense=False)
        game_df2 = off_df.merge(def_df,on='measure')
        game_df2['game_name'] = sb_df['game_name'][i]
        game_df2['offense'] = sb_df['awayTeam.teamId'][i]
        
        # combine to single game _df
        game_df = pd.concat([game_df1,game_df2],axis=0)
        
        # build cumulative df across games
        if i == 0:
            running_df = game_df.copy()
        else:
            running_df = pd.concat([running_df,game_df],axis=0)

    return running_df