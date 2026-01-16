
# load packages
import streamlit as st
from data.scoreboard_data import get_scoreboard, get_injuries
from util.helper import get_today
from charts.charts import lollipop_chart_plotly, pt_scatter_plotly, style_scatter_plotly, shot_bar_plotly


# creating the page first, so that I can then start catching functions
def create_page():
    st.set_page_config(layout="wide")



# set up page - saved copy of my code
def launch_page(today, live_df, upcoming_df, finished_df, scoreboard_raw_df,
                ff_df, style_df, pt_df,
                shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long):

    st.title("NBA Scoreboard:"+" "+today.strftime("%m/%d/%Y"))
    st.write("Scores as of: ", today.strftime('%#I:%M:%p'))
    if st.button("Refresh"):
        get_today.clear()
        get_scoreboard.clear()
        get_injuries.clear()
        st.rerun()
    st.write("Importance for game ratings")

    with st.expander("Select categories for game ratings",expanded=True):
        # omitted contest percent, ball movement, player movement since not available for live games
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            cat1 = st.slider(label = "Point Differential", min_value = 0, max_value = 10, value = 10, step = 1, key='cat1')
        with col2:
            cat2 = st.slider(label = "Time Remaining", min_value = 0, max_value = 10, value = 10, step = 1, key='cat2')
        with col3:
            cat3 = st.slider(label = "Player Availability", min_value = 0, max_value = 10, value = 9, step = 1, key='cat3')
        with col4:
            cat4 = st.slider(label = "Team Quality", min_value = 0, max_value = 10, value = 9, step = 1, key='cat4')
        with col5:
            cat5 = st.slider(label = "Style Contrasts", min_value = 0, max_value = 10, value = 8, step = 1, key='cat5')
        with col6:
            cat6 = st.slider(label = "Zach Lowe Rankings", min_value = 0, max_value = 10, value = 8, step = 1, key='cat6')
        with col7:
            cat7 = st.slider(label = "Offensive Rating", min_value = 0, max_value = 10, value = 7, step = 1, key='cat7')
        
        col8, col9, col10, col11, col12, col13, col14 = st.columns(7)
        with col8:
            cat8 = st.slider(label = "Game Flow", min_value = 0, max_value = 10, value = 7, step = 1, key='cat8')
        with col9:
            cat9 = st.slider(label = "Foul Rate", min_value = 0, max_value = 10, value = 7, step = 1, key='cat9')
        with col10:
            cat10 = st.slider(label = "Assist Percent", min_value = 0, max_value = 10, value = 6, step = 1, key='cat10')
        with col11:
            cat11 = st.slider(label = "Egalitarian Offense", min_value = 0, max_value = 10, value = 6, step = 1, key='cat11')
        with col12:
            cat12 = st.slider(label = "Heroic Performance", min_value = 0, max_value = 10, value = 6, step = 1, key='cat12')
        with col13:
            cat13 = st.slider(label = "Pace", min_value = 0, max_value = 10, value = 6, step = 1, key='cat13')
        with col14:
            cat14 = st.slider(label = "National Broadcast", min_value = 0, max_value = 10, value = 6, step = 1, key='cat14')
    
    # Create the tabs
    tab1, tab2, tab3 = st.tabs(['Live Games', 'Upcoming', 'Finished Games'])

    # st.write('Live Games')
    with tab1:
        st.dataframe(
            live_df,
            column_config={
                "Away Logo": st.column_config.ImageColumn("Away Logo"),
                "Home Logo": st.column_config.ImageColumn("Home Logo")
            },
            hide_index=True,
            row_height=60)
    # st.write('Upcoming Games')
    with tab2:
        st.dataframe(
            upcoming_df,
                column_config={
                "Away Logo": st.column_config.ImageColumn("Away Logo"),
                "Home Logo": st.column_config.ImageColumn("Home Logo")
            },
            hide_index=True,
            row_height=60)
    # st.write('Finished Games')
    with tab3:
        st.dataframe(
            finished_df,
                column_config={
                "Away Logo": st.column_config.ImageColumn("Away Logo"),
                "Home Logo": st.column_config.ImageColumn("Home Logo")
            },
            hide_index=True,
            row_height=60)

    # consider making this a select column instead in the dataframe?
    selected_game = st.selectbox(
        "Select a game",
        scoreboard_raw_df['game_name'],
        key = 'selected_game'
    )

    selected_teams = scoreboard_raw_df[scoreboard_raw_df['game_name']==st.session_state.selected_game][['awayTeam.teamName','homeTeam.teamName']].iloc[0].values

    selected_side = st.radio(
        "Choose a side of the ball",
        selected_teams,
        key = 'selected_side',
        horizontal=True
    )

    team_dict = dict(zip(
        list(scoreboard_raw_df['homeTeam.teamName'])+list(scoreboard_raw_df['awayTeam.teamName']),
        list(scoreboard_raw_df['homeTeam.teamId'])+list(scoreboard_raw_df['awayTeam.teamId'])
    ))

    matchup_dict = dict(zip(
        list(scoreboard_raw_df['homeTeam.teamName'])+list(scoreboard_raw_df['awayTeam.teamName']),
        list(scoreboard_raw_df['awayTeam.teamName'])+list(scoreboard_raw_df['homeTeam.teamName']),
    ))

    tab4, tab5, tab6, tab7 = st.tabs(['Four Factors', 'Style', 'Play Types', 'Shot Chart'])    


    with tab4:
        ff_chart_df = ff_df[(ff_df['game_name']==selected_game)&(ff_df['offense']==team_dict[selected_side])]
        fig = lollipop_chart_plotly(ff_chart_df, matchup_dict, selected_side)
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        fig = style_scatter_plotly(style_df, selected_side, team_dict[selected_side])
        st.plotly_chart(fig, use_container_width=True)

    with tab6:
        pt_chart_df = pt_df[pt_df['team_id']==team_dict[st.session_state.selected_side]].reset_index(drop=True)
        fig = pt_scatter_plotly(pt_chart_df)
        st.plotly_chart(fig, use_container_width=True)

    # with tab7:
    #     # supply the dataframes, the matchup dict, the team dict, selected side
    #     fig1 = shot_bar_plotly(shot_freq_df_long, opp_freq_df_long, matchup_dict, team_dict, selected_side, freq=True)
    #     st.plotly_chart(fig1, use_container_width=True)

    #     fig2 = shot_bar_plotly(shot_pct_df_long, opp_pct_df_long, matchup_dict, team_dict, selected_side, freq=False)
    #     st.plotly_chart(fig2, use_container_width=True)

    with tab7:

        col1, col2 = st.columns(2)

        with col1:
            fig1 = shot_bar_plotly(
                shot_freq_df_long,
                opp_freq_df_long,
                matchup_dict,
                team_dict,
                selected_side,
                freq=True
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = shot_bar_plotly(
                shot_pct_df_long,
                opp_pct_df_long,
                matchup_dict,
                team_dict,
                selected_side,
                freq=False
            )
            st.plotly_chart(fig2, use_container_width=True)
