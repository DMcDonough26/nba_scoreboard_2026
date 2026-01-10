
# load packages
import streamlit as st
from datetime import datetime
import pandas as pd
from nba_api.live.nba.endpoints import boxscore, odds, playbyplay, scoreboard
# initially built with live endpoint, but new stats endpoint has broadcaster, could refactor to just one endpoint
from nba_api.stats.endpoints import scoreboardv3, leaguegamefinder
from ui.web_page import *
from util.helper import *


# pull scoreboard from API
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
def get_rivalries():
    rival_df = pd.read_excel('data\\Rivalries.xlsx',sheet_name=1)
    return rival_df

# league pass rankings
def get_lp_rankings():
    lp_df = pd.read_excel('data\\League Pass Rankings.xlsx',sheet_name=0)
    return lp_df

# network
def get_network(today):
    bd_df = scoreboardv3.ScoreboardV3(today.strftime('%Y-%m-%d')).get_data_frames()[5]
    nat_df = bd_df[bd_df['broadcasterType']=='nationalTv'].groupby('gameId')['broadcastDisplay'].unique().reset_index()
    nat_df['broadcastDisplay'] = nat_df['broadcastDisplay'].apply(lambda x: ', '.join(x))
    return nat_df


# logo dictionary
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
def get_spreads():
    odds_df = pd.json_normalize(odds.Odds().get_dict()['games'])
    return odds_df

# note: if this is just binary, it could probably be rewritten as a one-line lambda function
def days_rest(x):
    # if x == 0:
        # return 'B2B'
    if x == 1:
        return '1 day'
    else:
        return str(x) + ' days'

# rest
def get_rest():
    games_df = leaguegamefinder.LeagueGameFinder(season_nullable='2025-26', season_type_nullable='Regular Season',league_id_nullable='00').get_data_frames()[0]
    games_df.columns = lower_all(games_df)
    games_df['game_date'] =  pd.to_datetime(games_df['game_date'])
    today_norm = pd.Timestamp('today').normalize()
    prior_games = games_df[games_df['game_date'] < today_norm]
    latest_games = prior_games.groupby('team_abbreviation')['game_date'].max().reset_index()
    latest_games['rest'] = (today_norm - latest_games['game_date']).dt.days - 1
    latest_games['rest'] = latest_games['rest'].apply(days_rest)
    return latest_games


# injuries
def get_injuries():
    inury_url = "https://www.basketball-reference.com/friv/injuries.fcgi"
    injury_df = pd.read_html(inury_url)[0]
    injury_df['design'] = injury_df['Description'].apply(lambda x: x.split(' (')[0])
    injury_df['teamtricode'] = injury_df['Team'].apply(lambda x: team_abbreviations[x])
    injury_df = injury_df[(injury_df['design'] == 'Out')|(injury_df['design'] == 'Out For Season')]
    agg_df = injury_df.groupby(['teamtricode'])['Player'].unique().reset_index()
    agg_df['injuries'] = agg_df['Player'].apply(lambda x: ', '.join(x))
    return agg_df



# bring it all together
def combine_data(today):
    scoreboard_raw_df = get_scoreboard()
    rival_df = get_rivalries()
    lp_df = get_lp_rankings()
    nat_df = get_network(today)
    logo_links = get_logos()
    odds_df = get_spreads()
    latest_games = get_rest()
    agg_df = get_injuries()

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

    # merge odds
    odds_today_df = odds_df.merge(scoreboard_raw_df['gameId'], how='inner',on='gameId')
    odds_today_df['spread'] = odds_today_df['markets'].apply(lambda x: float(x[1]['books'][0]['outcomes'][0]['spread']))
    scoreboard_raw_df = scoreboard_raw_df.merge(odds_today_df[['gameId','spread']],how='left',on='gameId')

    # merge rest
    scoreboard_raw_df = scoreboard_raw_df.merge(latest_games[['team_abbreviation','rest']],how='left',left_on='homeTeam.teamTricode',right_on='team_abbreviation')
    scoreboard_raw_df = scoreboard_raw_df.merge(latest_games[['team_abbreviation','rest']],how='left',left_on='awayTeam.teamTricode',right_on='team_abbreviation',\
                                                suffixes=('_home','_away'))

    # merge injuries

    scoreboard_raw_df = scoreboard_raw_df.merge(agg_df[['teamtricode','injuries']],how='left',left_on='homeTeam.teamTricode',right_on='teamtricode')
    scoreboard_raw_df = scoreboard_raw_df.merge(agg_df[['teamtricode','injuries']],how='left',left_on='awayTeam.teamTricode',right_on='teamtricode',\
                                                suffixes=('_home','_away'))


    # placeholder fields
    scoreboard_raw_df['win_prob'] = 'TBD' # to be updated (calculate live, pull ML from somewhere in advance)
    scoreboard_raw_df['real_time'] = 'TBD' # to be updated with model
    scoreboard_raw_df['game_rating'] = 'TBD' # to be updated with formula and user inputs
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
                            'diff','gameStatusText','win_prob','real_time','game_rating','rest_away','rest_home','injuries_away','injuries_home',\
                            'ring_avg','rob_avg']].copy()

    live_df.columns = ['Tipoff (ET)','Network','Away Logo','Home Logo','Away W82', 'Home W82','Rivalry','Away Score','Home Score','"The Diff"','Game Time Remaining',\
                    'Win Probability','Est. Real Time Remaining','Game Rating','Rest Away','Rest Home','Injuries Away','Injuries Home',\
                    'Zach Lowe Rank',' Rob Perez Rank']

    upcoming_df = upcoming_raw_df[['tipoff','broadcastDisplay','away_logo','home_logo','away_w82','home_w82','rivalry','spread','win_prob',\
                                    'end_time','game_rating','rest_away','rest_home','injuries_away','injuries_home','ring_avg','rob_avg']].copy()

    upcoming_df.columns = ['Tipoff (ET)','Network','Away Logo','Home Logo','Away W82', 'Home W82','Rivalry','Spread','Win Probability','Projected End Time','Game Rating',\
                            'Rest Away','Rest Home','Injuries Away','Injuries Home','Zach Lowe Rank',' Rob Perez Rank']

    finished_df = finished_raw_df[['tipoff','broadcastDisplay','away_logo','home_logo','away_w82','home_w82','rivalry','awayTeam.score',\
                                    'homeTeam.score','diff','game_rating','rest_away','rest_home','injuries_away','injuries_home','ring_avg','rob_avg']].copy()

    finished_df.columns = ['Tipoff (ET)','Network','Away Logo','Home Logo','Away W82', 'Home W82','Rivalry','Away Score','Home Score','"The Diff"','Game Rating',\
                            'Rest Away','Rest Home','Injuries Away','Injuries Home','Zach Lowe Rank',' Rob Perez Rank']

    return live_df, upcoming_df, finished_df, scoreboard_raw_df
