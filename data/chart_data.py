
# load packages
import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats, synergyplaytypes, leaguedashptstats, leaguedashplayerstats, leaguedashteamshotlocations
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
    
@st.cache_data()
def get_team_pt_dist():
    pm_df = leaguedashptstats.LeagueDashPtStats().get_data_frames()[0]
    pm_df.columns = lower_all(pm_df)
    return pm_df

@st.cache_data()
def get_team_pt_pass():
    pass_df = leaguedashptstats.LeagueDashPtStats(pt_measure_type='Passing').get_data_frames()[0]
    pass_df.columns = lower_all(pass_df)
    return pass_df

@st.cache_data()
def get_team_fg_con_df():
    player_df = leaguedashplayerstats.LeagueDashPlayerStats().get_data_frames()[0]
    player_df.columns = lower_all(player_df)
    fg_con_df = player_df.groupby('team_id').agg({'fga':['max','sum']}).reset_index()
    fg_con_df.columns = ['team_id','max','sum']
    fg_con_df['fg_con_pct'] = fg_con_df['max']/fg_con_df['sum']
    return fg_con_df

@st.cache_data()
def get_style_chart_data():
    adv_df = get_team_adv()
    pm_df = get_team_pt_dist()
    pass_df = get_team_pt_pass()
    fg_con_df = get_team_fg_con_df()

    combined_df = adv_df[['team_id','pace','ast_pct']].merge(pm_df[['team_id','dist_miles']], on='team_id')
    combined_df = combined_df.merge(pass_df[['team_id','passes_made']],on='team_id')
    combined_df = combined_df.merge(fg_con_df[['team_id','fg_con_pct']],on='team_id')

    combined_df['dist_adj'] = combined_df['dist_miles'] / combined_df['pace']
    combined_df['passes_adj'] = combined_df['passes_made'] / combined_df['pace']

    chart_df = combined_df[['team_id','pace','dist_adj','passes_adj','fg_con_pct','ast_pct']].copy()
    chart_df.columns = ['Team','Pace','Player Movement','Ball Movement','Field Goal Concentration','Assist Percent']


    for column in chart_df.columns[1:]:
        mean = chart_df[column].mean()
        std = chart_df[column].std()
        chart_df[column] = (chart_df[column] - mean) / std

    chart_df_long = chart_df.melt(id_vars=['Team'], value_vars=chart_df.columns[1:], var_name='Category', value_name='Value')

    return chart_df_long


@st.cache_data()
def get_shot_data():
    # get data
    shot_df = leaguedashteamshotlocations.LeagueDashTeamShotLocations().get_data_frames()[0]
    opp_shot_df = leaguedashteamshotlocations.LeagueDashTeamShotLocations(measure_type_simple='Opponent').get_data_frames()[0]

    # flatten column index
    shot_df.columns = ['_'.join(col) for col in shot_df.columns.values]
    opp_shot_df.columns = ['_'.join(col) for col in opp_shot_df.columns.values]

    # create dataframes
    shot_freq_df = shot_df[['_TEAM_ID','Restricted Area_FGA','In The Paint (Non-RA)_FGA','Mid-Range_FGA','Above the Break 3_FGA','Corner 3_FGA']]
    shot_pct_df = shot_df[['_TEAM_ID', 'Restricted Area_FG_PCT','In The Paint (Non-RA)_FG_PCT','Mid-Range_FG_PCT','Above the Break 3_FG_PCT','Corner 3_FG_PCT']]
    opp_freq_df = opp_shot_df[['_TEAM_ID', 'Restricted Area_OPP_FGA','In The Paint (Non-RA)_OPP_FGA','Mid-Range_OPP_FGA','Above the Break 3_OPP_FGA','Corner 3_OPP_FGA']]
    opp_pct_df = opp_shot_df[['_TEAM_ID','Restricted Area_OPP_FG_PCT','In The Paint (Non-RA)_OPP_FG_PCT','Mid-Range_OPP_FG_PCT','Above the Break 3_OPP_FG_PCT','Corner 3_OPP_FG_PCT']]

    # rename columns
    shot_freq_df.columns = ['team_id','rim_fga','paint_fga','mid_fga','break_fga','corner_fga']
    shot_pct_df.columns = ['team_id','Rim','Paint','Mid Range','Above the Break 3','Corner 3']
    opp_freq_df.columns = ['team_id','rim_fga','paint_fga','mid_fga','break_fga','corner_fga']
    opp_pct_df.columns = ['team_id','Rim','Paint','Mid Range','Above the Break 3','Corner 3']

    # add total fga
    shot_freq_df['tot_fga'] = shot_freq_df['rim_fga'] + shot_freq_df['paint_fga'] + shot_freq_df['mid_fga'] + shot_freq_df['break_fga'] + shot_freq_df['corner_fga']
    opp_freq_df['tot_fga'] = opp_freq_df['rim_fga'] + opp_freq_df['paint_fga'] + opp_freq_df['mid_fga'] + opp_freq_df['break_fga'] + opp_freq_df['corner_fga']

    # calculate frequency percents
    shot_freq_df['Rim'] = shot_freq_df['rim_fga']/shot_freq_df['tot_fga']
    shot_freq_df['Paint'] = shot_freq_df['paint_fga']/shot_freq_df['tot_fga']
    shot_freq_df['Mid Range'] = shot_freq_df['mid_fga']/shot_freq_df['tot_fga']
    shot_freq_df['Above the Break 3'] = shot_freq_df['break_fga']/shot_freq_df['tot_fga']
    shot_freq_df['Corner 3'] = shot_freq_df['corner_fga']/shot_freq_df['tot_fga']

    opp_freq_df['Rim'] = opp_freq_df['rim_fga']/opp_freq_df['tot_fga']
    opp_freq_df['Paint'] = opp_freq_df['paint_fga']/opp_freq_df['tot_fga']
    opp_freq_df['Mid Range'] = opp_freq_df['mid_fga']/opp_freq_df['tot_fga']
    opp_freq_df['Above the Break 3'] = opp_freq_df['break_fga']/opp_freq_df['tot_fga']
    opp_freq_df['Corner 3'] = opp_freq_df['corner_fga']/opp_freq_df['tot_fga']

    # melt the dataframes
    shot_freq_df_long = shot_freq_df.melt(
        id_vars=['team_id'],
        value_vars=['Rim','Paint','Mid Range','Above the Break 3','Corner 3'],
        var_name='Measure', value_name='Offense')

    shot_pct_df_long = shot_pct_df.melt(
        id_vars=['team_id'],
        value_vars=['Rim','Paint','Mid Range','Above the Break 3','Corner 3'],
        var_name='Measure', value_name='Offense')

    opp_freq_df_long = opp_freq_df.melt(
        id_vars=['team_id'],
        value_vars=['Rim','Paint','Mid Range','Above the Break 3','Corner 3'],
        var_name='Measure', value_name='Defense')

    opp_pct_df_long = opp_pct_df.melt(
        id_vars=['team_id'],
        value_vars=['Rim','Paint','Mid Range','Above the Break 3','Corner 3'],
        var_name='Measure', value_name='Defense')

    return shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long