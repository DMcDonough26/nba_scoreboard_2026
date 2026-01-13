
# load packages
import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats, synergyplaytypes
from util.helper import lower_all

@st.cache_data()
def get_team_adv():
    adv_df = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Advanced').get_data_frames()[0]
    adv_df.columns = lower_all(adv_df)
    return adv_df

@st.cache_data()
def get_team_four():
    four_df = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Four Factors').get_data_frames()[0]
    four_df.columns = lower_all(four_df)
    return four_df

@st.cache_data()
def build_one_side_df(i,sb_df,team_stats_df,home=True, offense=True):

    measure_dict = {'off_rating_rank':'Offensive Rating','efg_pct_rank':'Effective Field Goal %','fta_rate_rank':'Free Throw Rate',
                    'tm_tov_pct_rank':'Turnover %','oreb_pct_rank':'Offensive Rebounding %',
                'def_rating_rank':'Offensive Rating','opp_efg_pct_rank':'Effective Field Goal %','opp_fta_rate_rank':'Free Throw Rate',
                'opp_tov_pct_rank':'Turnover %','opp_oreb_pct_rank':'Offensive Rebounding %'}

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

@st.cache_data()
def get_team_play_type():
    # api response
    iso = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Isolation',type_grouping_nullable='Offensive')
    trans = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Transition',type_grouping_nullable='Offensive')
    pnrb = synergyplaytypes.SynergyPlayTypes(play_type_nullable='PRBallHandler',type_grouping_nullable='Offensive')
    pnrr = synergyplaytypes.SynergyPlayTypes(play_type_nullable='PRRollMan',type_grouping_nullable='Offensive')
    post = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Postup',type_grouping_nullable='Offensive')
    spot = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Spotup',type_grouping_nullable='Offensive')
    hand = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Handoff',type_grouping_nullable='Offensive')
    cut = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Cut',type_grouping_nullable='Offensive')
    os = synergyplaytypes.SynergyPlayTypes(play_type_nullable='OffScreen',type_grouping_nullable='Offensive')
    put = synergyplaytypes.SynergyPlayTypes(play_type_nullable='OffRebound',type_grouping_nullable='Offensive')
    misc = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Misc',type_grouping_nullable='Offensive')

    # dataframes
    iso_df = iso.get_data_frames()[0]
    trans_df = trans.get_data_frames()[0]
    pnrb_df = pnrb.get_data_frames()[0]
    pnrr_df = pnrr.get_data_frames()[0]
    post_df = post.get_data_frames()[0]
    spot_df = spot.get_data_frames()[0]
    hand_df = hand.get_data_frames()[0]
    cut_df = cut.get_data_frames()[0]
    os_df = os.get_data_frames()[0]
    put_df = put.get_data_frames()[0]
    misc_df = misc.get_data_frames()[0]

    # transform the data
    play_type_df = pd.concat([iso_df,trans_df,pnrb_df,pnrr_df,post_df,spot_df,hand_df,cut_df,os_df,put_df,misc_df],axis=0).reset_index(drop=True)
    play_type_df['avg_poss_pct'] = play_type_df.groupby('PLAY_TYPE')['POSS_PCT'].transform('mean')
    play_type_df['avg_ppp'] = play_type_df.groupby('PLAY_TYPE')['PPP'].transform('mean')
    play_type_df['rel_poss_pct'] = play_type_df['POSS_PCT'] / play_type_df['avg_poss_pct']
    play_type_df['rel_ppp'] = play_type_df['PPP'] / play_type_df['avg_ppp']

    play_type_df.columns = lower_all(play_type_df)

    return play_type_df
    