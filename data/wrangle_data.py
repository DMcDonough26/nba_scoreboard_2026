
# load packages
import streamlit as st
from util.helper import get_today, get_contrast, url_to_data_url
from data.get_data import get_scoreboard, get_rivalries, get_lp_rankings, get_network, get_logos, get_spreads, get_rest, get_injuries,\
                          get_live_box_score, get_vorp, get_team_adv, get_ff_chart_data, get_stars, get_fouls, get_style_chart_data,\
                          get_team_play_type, get_shot_data
from ratings.ratings import get_ratings


# bring it all together
@st.cache_data()
def combine_data():
    today = get_today()
    scoreboard_raw_df = get_scoreboard()
    rival_df = get_rivalries()
    lp_df = get_lp_rankings()
    nat_df = get_network(today)
    logo_links = get_logos()
    odds_df = get_spreads()
    latest_games = get_rest()
    injury_agg_df, injury_full_df = get_injuries()
    live_box_df = get_live_box_score(scoreboard_raw_df)
    vorp_df_25 = get_vorp(2025)
    adv_df = get_team_adv()
    ff_chart_df = get_ff_chart_data(scoreboard_raw_df)
    star_df = get_stars()
    foul_df = get_fouls()
    style_df = get_style_chart_data()
    pt_df = get_team_play_type()
    shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long = get_shot_data()

    # merge rival
    scoreboard_raw_df['rivalry'] = scoreboard_raw_df['team_combo'].apply(lambda x: 1 if int(x) in list(rival_df['key'].values) else 0)

    # merge lp
    scoreboard_raw_df = scoreboard_raw_df.merge(lp_df,how='left',left_on='homeTeam.teamTricode',right_on='Team')
    scoreboard_raw_df = scoreboard_raw_df.merge(lp_df,how='left',left_on='awayTeam.teamTricode',right_on='Team',suffixes=('_home','_away'))
    scoreboard_raw_df['ring_avg'] = ((scoreboard_raw_df['Ringer_home'] + scoreboard_raw_df['Ringer_away'])/2).round()
    scoreboard_raw_df['rob_avg'] = ((scoreboard_raw_df['Rob Perez_home'] + scoreboard_raw_df['Rob Perez_away'])/2).round()

    # merge network
    scoreboard_raw_df = scoreboard_raw_df.merge(nat_df,how='left',on='gameId')
    scoreboard_raw_df['broadcastDisplay'].fillna('League Pass',inplace=True)

    # merge logos
    scoreboard_raw_df['home_logo'] = scoreboard_raw_df['homeTeam.teamTricode'].apply(lambda x: logo_links[x])
    scoreboard_raw_df['away_logo'] = scoreboard_raw_df['awayTeam.teamTricode'].apply(lambda x: logo_links[x])
    scoreboard_raw_df["home_logo"] = scoreboard_raw_df["home_logo"].apply(url_to_data_url)
    scoreboard_raw_df["away_logo"] = scoreboard_raw_df["away_logo"].apply(url_to_data_url)

    # merge odds
    odds_today_df = odds_df.merge(scoreboard_raw_df['gameId'], how='inner',on='gameId')
    odds_today_df['spread'] = odds_today_df['markets'].apply(lambda x: float(x[1]['books'][0]['outcomes'][0]['spread']))
    scoreboard_raw_df = scoreboard_raw_df.merge(odds_today_df[['gameId','spread']],how='left',on='gameId')

    # merge rest
    scoreboard_raw_df = scoreboard_raw_df.merge(latest_games[['team_abbreviation','rest']],how='left',left_on='homeTeam.teamTricode',right_on='team_abbreviation')
    scoreboard_raw_df = scoreboard_raw_df.merge(latest_games[['team_abbreviation','rest']],how='left',left_on='awayTeam.teamTricode',right_on='team_abbreviation',\
                                                suffixes=('_home','_away'))

    # merge injuries (list verison for dashboard display)
    scoreboard_raw_df = scoreboard_raw_df.merge(injury_agg_df[['teamtricode','injuries']],how='left',left_on='homeTeam.teamTricode',right_on='teamtricode')
    scoreboard_raw_df = scoreboard_raw_df.merge(injury_agg_df[['teamtricode','injuries']],how='left',left_on='awayTeam.teamTricode',right_on='teamtricode',\
                                                suffixes=('_home','_away'))

    # merge live box
    scoreboard_raw_df = scoreboard_raw_df.merge(live_box_df,how='left',on='gameId')

    # merge injury and vorp
    injured_vorp_full_df = injury_full_df.merge(vorp_df_25[['Player','VORP']],how='left',on='Player')
    injured_vorp_team_df = injured_vorp_full_df[['teamtricode','Player','VORP']].dropna().groupby('teamtricode')['VORP'].sum().reset_index()
    injured_vorp_team_df.columns = ['teamtricode','injured_vorp']
    scoreboard_raw_df = scoreboard_raw_df.merge(injured_vorp_team_df[['teamtricode','injured_vorp']],how='left',left_on='homeTeam.teamTricode',right_on='teamtricode')
    scoreboard_raw_df = scoreboard_raw_df.merge(injured_vorp_team_df[['teamtricode','injured_vorp']],how='left',left_on='awayTeam.teamTricode',right_on='teamtricode',\
                                                suffixes=('_home2','_away2'))

    scoreboard_raw_df['injured_vorp_home2'].fillna(0,inplace=True)
    scoreboard_raw_df['injured_vorp_away2'].fillna(0,inplace=True)

    # get off/def ratings

    scoreboard_raw_df = scoreboard_raw_df.merge(adv_df[['team_id','off_rating','def_rating','pace']],how='left',left_on='homeTeam.teamId',right_on='team_id')
    scoreboard_raw_df = scoreboard_raw_df.merge(adv_df[['team_id','off_rating','def_rating','pace']],how='left',left_on='awayTeam.teamId',right_on='team_id',\
                                                suffixes=('_home3','_away3'))

    # style contrasts

    ff_chart_df['contrast'] = ff_chart_df.apply(get_contrast,axis=1)
    ff_chart_agg = ff_chart_df.groupby('game_name')['contrast'].max().reset_index()
    
    scoreboard_raw_df = scoreboard_raw_df.merge(ff_chart_agg,how='left',on='game_name')

    # star power
    scoreboard_raw_df = scoreboard_raw_df.merge(star_df,how='left',left_on='homeTeam.teamTricode',right_on='teamtricode')
    scoreboard_raw_df = scoreboard_raw_df.merge(star_df,how='left',left_on='awayTeam.teamTricode',right_on='teamtricode',\
                                                suffixes=('_home4','_away4'))

    # get fouls
    scoreboard_raw_df = scoreboard_raw_df.merge(foul_df[['team_id','total_fouls']],how='left',left_on='homeTeam.teamId',right_on='team_id')
    scoreboard_raw_df = scoreboard_raw_df.merge(foul_df[['team_id','total_fouls']],how='left',left_on='awayTeam.teamId',right_on='team_id',\
                                                suffixes=('_home5','_away5'))
    
    var_means = {'injured':injured_vorp_team_df['injured_vorp'].mean(), 'off_rating':adv_df['off_rating'].mean(), 'def_rating':adv_df['def_rating'].mean(),
                 'fouls':foul_df['total_fouls'].mean(), 'pace':adv_df['pace'].mean()}
    var_stds = {'injured':injured_vorp_team_df['injured_vorp'].std(),'off_rating':adv_df['off_rating'].std(), 'def_rating':adv_df['def_rating'].std(),
                'fouls':foul_df['total_fouls'].std(), 'pace':adv_df['pace'].std()}

    # get rating
    scoreboard_raw_df['game_rating'] = scoreboard_raw_df.apply(get_ratings,axis=1, var_means=var_means,
                                                                var_stds=var_stds)
    # scoreboard_raw_df['game_rating'] = 'TBD' # to be updated with formula and user inputs

    # placeholder fields
    scoreboard_raw_df['win_prob'] = 'TBD' # to be updated (calculate live, pull ML from somewhere in advance)
    scoreboard_raw_df['real_time'] = 'TBD' # to be updated with model
    scoreboard_raw_df['end_time'] = 'TBD' # add real time remaining to current/tipoff time

    # split into sections
    upcoming_raw_df = scoreboard_raw_df[scoreboard_raw_df['gameStatus']==1].copy()
    # upcoming_raw_df['tipoff'] = pd.to_datetime(upcoming_raw_df['gameEt']).dt.time.apply(lambda x: x.strftime('%#I:%M:%p')) # differing formats requires repeating this code for each df

    live_raw_df = scoreboard_raw_df[scoreboard_raw_df['gameStatus']==2].copy()
    # live_raw_df['tipoff'] = pd.to_datetime(live_raw_df['gameEt']).dt.time.apply(lambda x: x.strftime('%#I:%M:%p'))

    finished_raw_df = scoreboard_raw_df[scoreboard_raw_df['gameStatus']==3].copy()
    # finished_raw_df['tipoff'] = pd.to_datetime(finished_raw_df['gameEt']).dt.time.apply(lambda x: x.strftime('%#I:%M:%p'))

    # create final dataframes
    live_df = live_raw_df[['tipoff','broadcastDisplay','away_logo','home_logo','away_w82','home_w82','rivalry','awayTeam.score','homeTeam.score',\
                            'diff','gameStatusText','win_prob','real_time',
                            # temporary test fields
                            'biggest_lead','lead_changes','times_tied', 'injured_vorp_home2', 'injured_vorp_away2','off_rating_home3','off_rating_away3',
                            'def_rating_home3','def_rating_away3', 'contrast', 'star_ind_home4', 'star_ind_away4', 'total_fouls_home5', 'total_fouls_away5',
                            'pace_home3','pace_away3',
                            #
                            'game_rating','rest_away','rest_home','injuries_away','injuries_home',\
                            'ring_avg','rob_avg']].copy()

    live_df.columns = ['Tipoff (ET)','Network','Away Logo','Home Logo','Away W82', 'Home W82','Rivalry','Away Score','Home Score','"The Diff"','Game Time Remaining',\
                    'Win Probability','Est. Real Time Remaining',
                    # temporary test fields
                            'biggest_lead','lead_changes','times_tied', 'injured_vorp_home2', 'injured_vorp_away2','off_rating_home3','off_rating_away3',
                            'def_rating_home3','def_rating_away3', 'contrast', 'star_ind_home4', 'star_ind_away4', 'total_fouls_home5', 'total_fouls_away5',
                            'pace_home3','pace_away3',
                    #
                    'Game Rating','Rest Away','Rest Home','Injuries Away','Injuries Home',\
                    'Zach Lowe Rank',' Rob Perez Rank']

    upcoming_df = upcoming_raw_df[['tipoff','broadcastDisplay','away_logo','home_logo','away_w82','home_w82','rivalry','spread','win_prob',\
                                    'end_time',
                                    # temporary test fields
                            'biggest_lead','lead_changes','times_tied', 'injured_vorp_home2', 'injured_vorp_away2','off_rating_home3','off_rating_away3',
                            'def_rating_home3','def_rating_away3', 'contrast', 'star_ind_home4', 'star_ind_away4', 'total_fouls_home5', 'total_fouls_away5',
                            'pace_home3','pace_away3',
                                    #
                                    'game_rating','rest_away','rest_home','injuries_away','injuries_home','ring_avg','rob_avg']].copy()

    upcoming_df.columns = ['Tipoff (ET)','Network','Away Logo','Home Logo','Away W82', 'Home W82','Rivalry','Spread','Win Probability','Projected End Time',
                            # temporary test fields
                            'biggest_lead','lead_changes','times_tied', 'injured_vorp_home2', 'injured_vorp_away2','off_rating_home3','off_rating_away3',
                            'def_rating_home3','def_rating_away3', 'contrast', 'star_ind_home4', 'star_ind_away4', 'total_fouls_home5', 'total_fouls_away5',
                            'pace_home3','pace_away3',
                            #
    'Game Rating',\
                            'Rest Away','Rest Home','Injuries Away','Injuries Home','Zach Lowe Rank',' Rob Perez Rank']

    finished_df = finished_raw_df[['tipoff','broadcastDisplay','away_logo','home_logo','away_w82','home_w82','rivalry','awayTeam.score',\
                                    'homeTeam.score','diff',
                                    # temporary test fields
                            'biggest_lead','lead_changes','times_tied', 'injured_vorp_home2', 'injured_vorp_away2','off_rating_home3','off_rating_away3',
                            'def_rating_home3','def_rating_away3', 'contrast', 'star_ind_home4', 'star_ind_away4', 'total_fouls_home5', 'total_fouls_away5',
                            'pace_home3','pace_away3',
                                    #
                                    'game_rating','rest_away','rest_home','injuries_away','injuries_home','ring_avg','rob_avg']].copy()

    finished_df.columns = ['Tipoff (ET)','Network','Away Logo','Home Logo','Away W82', 'Home W82','Rivalry','Away Score','Home Score','"The Diff"',
                            # temporary test fields
                            'biggest_lead','lead_changes','times_tied', 'injured_vorp_home2', 'injured_vorp_away2','off_rating_home3','off_rating_away3',
                            'def_rating_home3','def_rating_away3', 'contrast', 'star_ind_home4', 'star_ind_away4', 'total_fouls_home5', 'total_fouls_away5',
                            'pace_home3','pace_away3',
                            #
    'Game Rating',\
                            'Rest Away','Rest Home','Injuries Away','Injuries Home','Zach Lowe Rank',' Rob Perez Rank']

    return today, live_df, upcoming_df, finished_df, scoreboard_raw_df,\
           ff_chart_df, style_df, pt_df, shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long