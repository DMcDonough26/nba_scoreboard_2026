
import pandas as pd
import streamlit as st


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
        STOP # eventually replace this with better exception handling

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
def get_ratings(x, var_means, var_stds):

    level_dictionary = {'High':3,'Medium':2,'Low':1,'None':0}
    game_state_total = level_dictionary[st.session_state.var1] + level_dictionary[st.session_state.var2] + level_dictionary[st.session_state.var3]
    exp_qual_total = level_dictionary[st.session_state.var4] + level_dictionary[st.session_state.var5] + level_dictionary[st.session_state.var6] +\
                     level_dictionary[st.session_state.var7] + level_dictionary[st.session_state.var8]
    matchup_total =  level_dictionary[st.session_state.var9] + level_dictionary[st.session_state.var10] + level_dictionary[st.session_state.var11] +\
                     level_dictionary[st.session_state.var12]
    style_total = level_dictionary[st.session_state.var13] + level_dictionary[st.session_state.var14] + level_dictionary[st.session_state.var15] +\
                     level_dictionary[st.session_state.var16] + level_dictionary[st.session_state.var17] + level_dictionary[st.session_state.var18]+\
                     level_dictionary[st.session_state.var19]
    # weights
    weight_dict = {
        'point_diff':st.session_state.cat1/100 * level_dictionary[st.session_state.var1] / game_state_total,
        'time_remaining':st.session_state.cat1/100 * level_dictionary[st.session_state.var2] / game_state_total,
        'game_flow':st.session_state.cat1/100 * level_dictionary[st.session_state.var3] / game_state_total,
        'team_strength':st.session_state.cat2/100 * level_dictionary[st.session_state.var4] / exp_qual_total,
        'player_avail':st.session_state.cat2/100 * level_dictionary[st.session_state.var5] / exp_qual_total,
        'rest':st.session_state.cat2/100 * level_dictionary[st.session_state.var6] / exp_qual_total,
        'off_rating':st.session_state.cat2/100 * level_dictionary[st.session_state.var7] / exp_qual_total,
        'def_rating':st.session_state.cat2/100 * level_dictionary[st.session_state.var8] / exp_qual_total,
        'rivalry':st.session_state.cat3/100 * level_dictionary[st.session_state.var9] / matchup_total,
        'contrast':st.session_state.cat3/100 * level_dictionary[st.session_state.var10] / matchup_total,
        'star':st.session_state.cat3/100 * level_dictionary[st.session_state.var11] / matchup_total,
        'national':st.session_state.cat3/100 * level_dictionary[st.session_state.var12] / matchup_total,
        'ringer':st.session_state.cat4/100 * level_dictionary[st.session_state.var13] / style_total,
        'fouls':st.session_state.cat4/100 * level_dictionary[st.session_state.var14] / style_total,
        'pace':st.session_state.cat4/100 * level_dictionary[st.session_state.var15] / style_total,
        'player':st.session_state.cat4/100 * level_dictionary[st.session_state.var16] / style_total,
        'ball':st.session_state.cat4/100 * level_dictionary[st.session_state.var17] / style_total,
        'fg_con':st.session_state.cat4/100 * level_dictionary[st.session_state.var18] / style_total,
        'play_div':st.session_state.cat4/100 * level_dictionary[st.session_state.var19] / style_total
        }

    mean_dict = {
        'point_diff':12.7480, # from 2025 season
        'time_remaining':1440.5, # from uniform distribution of seconds
        'game_flow':0.8711, # from 2025 season
        'team_strength':40.8837, # from ?2025 season
        'player_avail':var_means['injured'], # from current injuries
        'rest':1.1225, # from 2025 season
        'off_rating':var_means['off_rating'], # from current season
        'def_rating':var_means['def_rating'], # from current season
        'rivalry':0.08, # from distribution of 870 matchups and 66 being rivalries
        'contrast':0.2460, # from distribution of 870 matchups with 10 stats each
        'star': 1.1, # from team distribution in 2026
        'national':0.2008, # from 2026 schedule
        'ringer':15.5, # calc distribution
        'fouls':var_means['fouls'], # from current season
        'pace':var_means['pace'], # from current season
        'play_div':var_means['play_div'] # from current season
    }

    std_dict = {
        'point_diff':9.6114, # from 2025 season
        'time_remaining':831.5287, # from uniform distribution of seconds
        'game_flow':1.0868, # from 2025 season
        'team_strength':10.7595, # from 2025 season
        'player_avail':var_stds['injured'], # from current injuries
        'rest':0.8783, # from 2025 season
        'off_rating':var_stds['off_rating'], # from current season
        'def_rating':var_stds['def_rating'], # from current season
        'rivalry':0.26, # from distribution of 870 matchups and 66 being rivalries
        'contrast':0.4309, # from distribution of 870 matchups with 10 stats each
        'star': 0.8449, # from team distribution in 2026
        'national':0.4008, # from 2026 schedule
        'ringer':6.0173, # calc distribution
        'fouls':var_stds['fouls'], # from current season
        'pace':var_stds['pace'], # from current season
        'play_div':var_stds['play_div'] # from current season
    }

    point_diff_val = weight_dict['point_diff'] * ((abs(point_diff(x)) - mean_dict['point_diff'])/std_dict['point_diff'])*-1
    time_remaining_val = weight_dict['time_remaining'] * ((time_remaining(x) - mean_dict['time_remaining'])/std_dict['time_remaining'])*-1
    if x['gameStatus'] != 1:
        game_flow_val = weight_dict['game_flow'] * (game_flow(x) - mean_dict['game_flow'])/std_dict['game_flow']
    else:
        game_flow_val = 0
    team_strength_val = weight_dict['team_strength'] * (team_strength(x) - mean_dict['team_strength'])/std_dict['team_strength']
    player_avail_val = weight_dict['player_avail'] * (((x['injured_vorp_home2']+x['injured_vorp_away2'])/2 - mean_dict['player_avail'])/std_dict['player_avail'])*-1
    rest_val = weight_dict['rest'] * (((x['rest_away']+x['rest_home'])/2) - mean_dict['rest'])/std_dict['rest']
    off_rating_val = weight_dict['off_rating'] * ((x['off_rating_home3']+x['off_rating_away3'])/2 - mean_dict['off_rating']) /std_dict['off_rating']
    def_rating_val = weight_dict['def_rating'] * (((x['def_rating_home3']+x['def_rating_away3'])/2 - mean_dict['def_rating']) /std_dict['def_rating'])*-1
    rivalry_val = weight_dict['rivalry'] * (x['rivalry'] - mean_dict['rivalry'])/ std_dict['rivalry']
    contrast_val = weight_dict['contrast'] * (x['contrast'] - mean_dict['contrast'])/std_dict['contrast']
    star_val = weight_dict['star'] * ((x['star_ind_home4'] + x['star_ind_away4'])/2 - mean_dict['star'])/std_dict['star']
    national_val = weight_dict['national'] * ((0 if x['broadcastDisplay']=='League Pass' else 1) - mean_dict['national'])/std_dict['national']
    ringer_val = weight_dict['ringer'] * ((x['ring_avg'] - mean_dict['ringer'])/std_dict['ringer'])*-1
    foul_val = weight_dict['fouls'] * (((x['total_fouls_home5'] + x['total_fouls_away5'])/2 - mean_dict['fouls'])/std_dict['fouls'])*-1
    pace_val = weight_dict['pace'] * (((x['pace_home3'] + x['pace_away3'])/2 - mean_dict['pace'])/std_dict['pace'])
    player_val = weight_dict['player'] * (x['Player Movement_home6'] + x['Player Movement_away6'])/2
    ball_val = weight_dict['ball'] * (x['Ball Movement_home6'] + x['Ball Movement_away6'])/2
    fg_con_val = weight_dict['fg_con'] * (x['Field Goal Concentration_home6'] + x['Field Goal Concentration_away6'])/2
    play_div_val = weight_dict['play_div'] * (((x['play_var_home7'] + x['play_var_away7'])/2 - mean_dict['play_div'])/std_dict['play_div'])

    rating = point_diff_val + time_remaining_val + game_flow_val +\
             team_strength_val + player_avail_val + rest_val + off_rating_val + def_rating_val +\
             rivalry_val + contrast_val + star_val + national_val +\
             ringer_val + foul_val + pace_val + player_val + ball_val + fg_con_val + play_div_val

    # apply normalization to 0-10 scale
    # this may just need to be observed/tweaked over time rather than estimated

    rating = (rating - -0.5) / (1 - -0.5)

    return round(rating*10,1)