
# load packages
import streamlit as st
import pandas as pd
from nba_api.live.nba.endpoints import scoreboard, odds, boxscore
from nba_api.stats.endpoints import scoreboardv3, leaguegamefinder, leaguedashteamstats, synergyplaytypes, leaguedashptstats, leaguedashplayerstats, leaguedashteamshotlocations
from util.helper import get_team_abbreviations, format_time, lower_all, get_team_abbreviations2, define_star
import time


# pull scoreboard from API
@st.cache_data()
def get_scoreboard():
    # define columns to keep
    sb_keep_col = ['gameId', 'gameStatus', 'gameStatusText', 'gameEt',
       'homeTeam.teamId', 'homeTeam.teamTricode', 'homeTeam.teamName', 'homeTeam.wins', 'homeTeam.losses',
       'homeTeam.score', 'homeTeam.inBonus', 'homeTeam.timeoutsRemaining',
       'awayTeam.teamId','awayTeam.teamTricode', 'awayTeam.teamName', 'awayTeam.wins', 'awayTeam.losses',
       'awayTeam.score', 'awayTeam.inBonus','awayTeam.timeoutsRemaining']
    scoreboard_raw_df = pd.json_normalize(scoreboard.ScoreBoard().get_dict()['scoreboard']['games'])[sb_keep_col]

    # calculate fields
    scoreboard_raw_df['diff'] = (scoreboard_raw_df['homeTeam.score'] - scoreboard_raw_df['awayTeam.score']).abs()
    scoreboard_raw_df['away_w82'] = (scoreboard_raw_df['awayTeam.wins']/(scoreboard_raw_df['awayTeam.wins']+scoreboard_raw_df['awayTeam.losses'])*82).round().astype(int)
    scoreboard_raw_df['home_w82'] = (scoreboard_raw_df['homeTeam.wins']/(scoreboard_raw_df['homeTeam.wins']+scoreboard_raw_df['homeTeam.losses'])*82).round().astype(int)
    scoreboard_raw_df['game_name'] = scoreboard_raw_df['awayTeam.teamName'].str.cat(scoreboard_raw_df['homeTeam.teamName'], sep = ' vs. ')
    scoreboard_raw_df['team_combo'] = scoreboard_raw_df['homeTeam.teamId'].astype(str) + scoreboard_raw_df['awayTeam.teamId'].astype(str)
    scoreboard_raw_df['tipoff'] = scoreboard_raw_df['gameEt'].apply(format_time)

    return scoreboard_raw_df

# rivalries from reddit survey
# maybe just make this a dictionary to remove dependency to workbook?
@st.cache_data()
def get_rivalries():
    rival_df = pd.read_excel('data\\Rivalries.xlsx',sheet_name=1)
    return rival_df

# league pass rankings
# maybe just make this a dictionary to remove dependency to workbook?
@st.cache_data()
def get_lp_rankings():
    lp_df = pd.read_excel('data\\League Pass Rankings.xlsx',sheet_name=0)
    return lp_df

# network
@st.cache_data()
def get_network(today):
    bd_df = scoreboardv3.ScoreboardV3(today.strftime('%Y-%m-%d')).get_data_frames()[5]
    nat_df = bd_df[bd_df['broadcasterType']=='nationalTv'].groupby('gameId')['broadcastDisplay'].unique().reset_index()
    nat_df['broadcastDisplay'] = nat_df['broadcastDisplay'].apply(lambda x: ', '.join(x))
    return nat_df


# logo dictionary
@st.cache_data()
def get_logos():
    # https://www.sportslogos.net/teams/list_by_league/6/National-Basketball-Association-Logos/NBA-Logos/

    logo_links = {
    'ATL':'https://content.sportslogos.net/logos/6/220/full/kqhjtzl2ik3gnxsnwsn8yf002.gif',
    'BKN':'https://content.sportslogos.net/logos/6/215/full/hvkhsaffs9x9zre7gku4vmnte.gif', # https://content.sportslogos.net/logos/6/215/full/2hh70mg3h40yl41tzfpn3gha2.gif, https://content.sportslogos.net/logos/6/3786/full/brooklyn_nets_logo_alternate_20138452.png
    'BOS':'https://content.sportslogos.net/logos/6/213/full/boston_celtics_logo_primary_19977628.png',
    'CHA':'https://content.sportslogos.net/logos/6/256/full/charlotte_hornets_logo_primary_19896932.png',
    'CHI':'https://content.sportslogos.net/logos/6/221/full/zdrycpc7mh5teihl10gko8sgf.png',
    'CLE':'https://content.sportslogos.net/logos/6/222/full/cleveland_cavaliers_logo_primary_19955963.png',
    'DAL':'https://content.sportslogos.net/logos/6/228/full/aa65jz06hggyuale7xmkeefka.png',
    'DEN':'https://content.sportslogos.net/logos/6/229/full/denver_nuggets_logo_primary_19828731.png', # https://content.sportslogos.net/logos/6/229/full/gs5fgn4fn5pd6gmfs0re4lvcx.gif
    'DET':'https://content.sportslogos.net/logos/6/223/full/detroit_pistons_logo_primary_19976102.png',
    'GSW':'https://content.sportslogos.net/logos/6/235/full/1bhcqs6l5t44lw04y1tygdsce.png',
    'HOU':'https://content.sportslogos.net/logos/6/230/full/eigv3ra8cjkojrywrgcvy6z29.gif',
    'IND':'https://content.sportslogos.net/logos/6/224/full/indiana-pacers-logo-primary-1991-2451.png',
    'LAC':'https://content.sportslogos.net/logos/6/236/full/los_angeles_clippers_logo_primary_20117648.png',
    'LAL':'https://content.sportslogos.net/logos/6/237/full/los_angeles_lakers_logo_primary_20007265.png',
    'MEM':'https://content.sportslogos.net/logos/6/231/full/qaksk2s6vp8gszbc10202tjzt.png', # https://content.sportslogos.net/logos/6/231/full/795.png
    'MIA':'https://content.sportslogos.net/logos/6/214/full/burm5gh2wvjti3xhei5h16k8e.gif',
    'MIL':'https://content.sportslogos.net/logos/6/225/full/milwaukee_bucks_logo_primary_19946491.png',
    'MIN':'https://content.sportslogos.net/logos/6/232/full/t5mgc3aeqfofhslwi8yzua6ro.gif',
    'NOP':'https://content.sportslogos.net/logos/6/4962/full/2681_new_orleans_pelicans-primary-2014.png',
    'NYK':'https://content.sportslogos.net/logos/6/216/full/new_york_knicks_logo_primary_19962276.png',
    'OKC':'https://content.sportslogos.net/logos/6/2687/full/oklahoma-city-thunder-logo-primary-2009-9699.png',
    'ORL':'https://content.sportslogos.net/logos/6/217/full/orlando_magic_logo_primary_20117178.png',
    'PHI':'https://content.sportslogos.net/logos/6/218/full/fge4lf9ridpgum631fb0gg9tt.gif',
    'PHX':'https://content.sportslogos.net/logos/6/238/full/phoenix_suns_logo_primary_19931753.png',
    'POR':'https://content.sportslogos.net/logos/6/239/full/portland_trail_blazers_logo_primary_19918704.png',
    'SAC':'https://content.sportslogos.net/logos/6/240/full/832.png',
    'SAS':'https://content.sportslogos.net/logos/6/233/full/e04ylwkfdofkr2ctlerjov26s.png',
    'TOR':'https://content.sportslogos.net/logos/6/227/full/toronto_raptors_logo_primary_19961665.png',
    'UTA':'https://content.sportslogos.net/logos/6/234/full/utah_jazz_logo_primary_19973688.png',
    'WAS':'https://content.sportslogos.net/logos/6/219/full/x2ulyduse08rm42lmtu9ugych.png'
    }
    return logo_links


# spread
@st.cache_data()
def get_spreads():
    odds_df = pd.json_normalize(odds.Odds().get_dict()['games'])
    return odds_df

# rest
@st.cache_data()
def get_rest():
    games_df = leaguegamefinder.LeagueGameFinder(season_nullable='2025-26', season_type_nullable='Regular Season',league_id_nullable='00').get_data_frames()[0]
    games_df.columns = lower_all(games_df)
    games_df['game_date'] =  pd.to_datetime(games_df['game_date'])
    today_norm = pd.Timestamp('today').normalize()
    prior_games = games_df[games_df['game_date'] < today_norm]
    latest_games = prior_games.groupby('team_abbreviation')['game_date'].max().reset_index()
    latest_games['rest'] = (today_norm - latest_games['game_date']).dt.days - 1
    # latest_games['rest'] = latest_games['rest'].apply(days_rest) # removing for now 
    return latest_games


# injuries
@st.cache_data()
def get_injuries():
    team_abbreviations = get_team_abbreviations()
    inury_url = "https://www.basketball-reference.com/friv/injuries.fcgi"
    injury_df = pd.read_html(inury_url)[0]
    injury_df['design'] = injury_df['Description'].apply(lambda x: x.split(' (')[0])
    injury_df['teamtricode'] = injury_df['Team'].apply(lambda x: team_abbreviations[x])
    injury_df = injury_df[(injury_df['design'] == 'Out')|(injury_df['design'] == 'Out For Season')]
    agg_df = injury_df.groupby(['teamtricode'])['Player'].unique().reset_index()
    agg_df['injuries'] = agg_df['Player'].apply(lambda x: ', '.join(x))
    return agg_df, injury_df

# get live box score
@st.cache_data()
def get_live_box_score(x):
    game_id_list = []
    biggest_lead_list = []
    lead_changes_list = []
    times_tied_list = []

    for i, game_id in enumerate(x['gameId']):
        if x['gameStatus'][i] == 1:
            continue
        else:
            game_id_list.append(game_id)
            game_box = boxscore_obj = boxscore.BoxScore(game_id)
            biggest_lead_list.append(max(game_box.get_dict()['game']['homeTeam']['statistics']['biggestLead'],
                                            game_box.get_dict()['game']['awayTeam']['statistics']['biggestLead']))
            lead_changes_list.append(game_box.get_dict()['game']['homeTeam']['statistics']['leadChanges'])
            times_tied_list.append(game_box.get_dict()['game']['homeTeam']['statistics']['timesTied'])
            time.sleep(1)

    live_box_df = pd.DataFrame({'gameId':game_id_list,'biggest_lead':biggest_lead_list,'lead_changes':lead_changes_list,'times_tied':times_tied_list})

    return live_box_df

# get vorp
@st.cache_data()
def get_vorp(stat_year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(stat_year) + "_advanced.html"
    df = pd.read_html(url)[0]
    df_agg = df.groupby('Player').agg({'VORP':'mean'}).reset_index()
    return df_agg


# get award function:
@st.cache_data()
def get_award_data(year, current=False):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_advanced.html"
    player_df = pd.read_html(url)[0]
    if current == False:
        player_df['star_ind'] = player_df['Awards'].apply(define_star)
        return player_df.groupby('Player')['star_ind'].mean().reset_index()
    else:
        return player_df[(player_df['Team']!='2TM')&(player_df['Team']!='3TM')&(player_df['Player']!='League Average')]


# get stars
@st.cache_data()
def get_stars():
    # get team abbreviations
    team_abbreviations2 = get_team_abbreviations2()


    # get last three years of data
    df23 = get_award_data(2023)
    df24 = get_award_data(2024)
    df25 = get_award_data(2025)
    combined_df = pd.concat([df23,df24,df25],axis=0)

    # make a unique list of stars
    star_set = set(combined_df[combined_df['star_ind']==1]['Player'])

    # get 26 players
    df26 = get_award_data(2026, current=True)

    # bring in team tri code
    df26['teamtricode'] = df26['Team'].apply(lambda x: team_abbreviations2[x])

    # join in the awards
    df26['star_ind'] = df26['Player'].apply(lambda x: 1 if x in star_set else 0)

    # remove anyone who is injured
    injury_df = pd.read_html("https://www.basketball-reference.com/friv/injuries.fcgi")[0]
    injury_df['design'] = injury_df['Description'].apply(lambda x: x.split(' (')[0])
    injury_df = injury_df[(injury_df['design'] == 'Out')|(injury_df['design'] == 'Out For Season')]
    df26_non_injured = df26[~df26["Player"].isin(injury_df["Player"])]

    # aggregate to the tri code
    return df26_non_injured.groupby('teamtricode')['star_ind'].sum().reset_index()

# get fouls
@st.cache_data()
def get_fouls():
    foul_df = leaguedashteamstats.LeagueDashTeamStats(per_mode_detailed='PerGame').get_data_frames()[0]
    opp_df = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Opponent',per_mode_detailed='PerGame').get_data_frames()[0]
    combined_df = foul_df[['TEAM_ID','PF']].merge(opp_df[['TEAM_ID','OPP_PF']],how='left',on='TEAM_ID')
    combined_df['total_fouls'] = combined_df['PF'] + combined_df['OPP_PF']
    combined_df.columns = lower_all(combined_df)
    return combined_df

# advanced team stats
@st.cache_data()
def get_team_adv():
    adv_df = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Advanced').get_data_frames()[0]
    adv_df.columns = lower_all(adv_df)
    return adv_df

# four factor team stats
@st.cache_data()
def get_team_four():
    four_df = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Four Factors').get_data_frames()[0]
    four_df.columns = lower_all(four_df)
    return four_df


# build FF data
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

# FF chart data
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

# play type data
@st.cache_data()
def get_team_play_type():
    # api response
    iso = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Isolation',type_grouping_nullable='Offensive')
    time.sleep(1)
    trans = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Transition',type_grouping_nullable='Offensive')
    time.sleep(1)
    pnrb = synergyplaytypes.SynergyPlayTypes(play_type_nullable='PRBallHandler',type_grouping_nullable='Offensive')
    time.sleep(1)
    pnrr = synergyplaytypes.SynergyPlayTypes(play_type_nullable='PRRollMan',type_grouping_nullable='Offensive')
    time.sleep(1)
    post = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Postup',type_grouping_nullable='Offensive')
    time.sleep(1)
    spot = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Spotup',type_grouping_nullable='Offensive')
    time.sleep(1)
    hand = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Handoff',type_grouping_nullable='Offensive')
    time.sleep(1)
    cut = synergyplaytypes.SynergyPlayTypes(play_type_nullable='Cut',type_grouping_nullable='Offensive')
    time.sleep(1)
    os = synergyplaytypes.SynergyPlayTypes(play_type_nullable='OffScreen',type_grouping_nullable='Offensive')
    time.sleep(1)
    put = synergyplaytypes.SynergyPlayTypes(play_type_nullable='OffRebound',type_grouping_nullable='Offensive')
    time.sleep(1)
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

# player tracking distance
@st.cache_data()
def get_team_pt_dist():
    pm_df = leaguedashptstats.LeagueDashPtStats().get_data_frames()[0]
    pm_df.columns = lower_all(pm_df)
    return pm_df

# player tracking passes
@st.cache_data()
def get_team_pt_pass():
    pass_df = leaguedashptstats.LeagueDashPtStats(pt_measure_type='Passing').get_data_frames()[0]
    pass_df.columns = lower_all(pass_df)
    return pass_df

# FG concentration
@st.cache_data()
def get_team_fg_con_df():
    player_df = leaguedashplayerstats.LeagueDashPlayerStats().get_data_frames()[0]
    player_df.columns = lower_all(player_df)
    fg_con_df = player_df.groupby('team_id').agg({'fga':['max','sum']}).reset_index()
    fg_con_df.columns = ['team_id','max','sum']
    fg_con_df['fg_con_pct'] = fg_con_df['max']/fg_con_df['sum']
    return fg_con_df

# Build style chart data
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

# shot chart data
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