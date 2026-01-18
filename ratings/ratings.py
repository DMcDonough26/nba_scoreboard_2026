
import pandas as pd
import streamlit as st


# upcoming, live, finished


# get point diff
def point_diff(x):
    if x['gameStatus']==1:
        return x['spread']
    else:
        return x['diff']

# get time remaining
def time_remaining(x):
    if x['gameStatus']==1:
        return 48*60
    if x['gameStatus']==2:
        if x['gameStatusText'] == 'Half':
            return 24*60
        else:
            if x['gameStatusText'].split(' ')[0] == 'END':
                qtr = int(x['gameStatusText'].split(' ')[1][1])
                qtr_val = (4-qtr)*12*60
                min_val = 0
                sec_val = 0
            else:
                qtr = int(x['gameStatusText'].split(' ')[0][1])
                time = x['gameStatusText'].split(' ')[1]
                qtr_val = (4-qtr)*12*60
                if time.split(":")[0] == '':
                    min_val = 0
                else:
                    min_val = int(time.split(":")[0])*60
                sec_val = round(float(time.split(":")[1]))
            return qtr_val + min_val + sec_val
    if x['gameStatus']==3:
        return 0
    else:
        STOP

# get game flow
def game_flow(x):

    # need to adjust count for time remaining
    time_left = time_remaining(x)
    if x['gameStatus']==3:
        time_adj_factor = 1
    else:
        time_adj_factor = 2880/(2880-time_left)

    if ((x['lead_changes'] + x['times_tied']) * time_adj_factor)> 21: # this would be around top 15% of games
        return 3
    elif x['biggest_lead'] > 15 and x['diff'] < 7: # don't call it a comeback, around 10% of games
        return 2
    elif x['biggest_lead'] < 16: # around 20% of games
        return 1
    else:
        return 0 # around 50% of games

# get team strength
def team_strength(x):
    return (x['away_w82'] + x['home_w82'])/2



# ratings
@st.cache_data()
def get_ratings(x):
    # weights
    # if the vars are not in the session state
    initial_weight_dict = {
        'point_diff':0.15,
        'time_remaining':0.15,
        'game_flow':0.1,
        'team_strength':0.075
        }

    mean_dict = {
        'point_diff':12.7480, # from 2025 season
        'time_remaining':1440.5, # from uniform distribution of seconds
        'game_flow':0.8711,
        'team_strength':40.8837 # from 2025 season
    }

    std_dict = {
        'point_diff':9.6114, # from 2025 season
        'time_remaining':831.5287, # from uniform distribution of seconds
        'game_flow':1.0868,
        'team_strength':10.7595 # from 2025 season
    }

    # point_diff_val = initial_weight_dict['point_diff'] * (abs(point_diff(x)) - mean_dict['point_diff'])/std_dict['point_diff']
    # time_remaining_val = initial_weight_dict['time_remaining'] * (time_remaining(x) - mean_dict['time_remaining'])/std_dict['time_remaining']
    # if x['gameStatus'] != 1:
    #     game_flow_val = initial_weight_dict['game_flow'] * (game_flow(x) - mean_dict['game_flow'])/std_dict['game_flow']
    # else:
    #     game_flow_val = 0
    team_strength_val = initial_weight_dict['team_strength'] * (team_strength(x) - mean_dict['team_strength'])/std_dict['team_strength']

    # rating = point_diff_val + time_remaining_val
    rating = team_strength_val

    # apply normalization to 0-10 scale
    pass

    return round(rating,1)