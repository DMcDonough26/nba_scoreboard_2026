
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
    st.write("Select weights for game rating categories:")

    # with st.expander("Select importance for game rating categories:",expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cat1 = st.slider(
            label="Current Game State",
            min_value=0,
            max_value=100,
            value=40,
            step=1,
            format="%.0f%%",
            key='cat1'
        )

        with st.expander("Game State Variables:",expanded=True):
                var1 = st.segmented_control(label = "Point Differential", options = ['High','Medium','Low','None'], key='var1')
                var2 = st.segmented_control(label = "Time Remaining", options = ['High','Medium','Low','None'], key='var2')
                var3 = st.segmented_control(label = "Game Flow", options = ['High','Medium','Low','None'], key='var3')

    with col2:
        cat2 = st.slider(
            label="Expected Quality of Play",
            min_value=0,
            max_value=100,
            value=30,
            step=1,
            format="%.0f%%",
            key='cat2'
        )

        with st.expander("Expected Quality Variables:",expanded=True):
            var4 = st.segmented_control(label = "Team Strength", options = ['High','Medium','Low','None'], key='var4')
            var5 = st.segmented_control(label = "Player Availability", options = ['High','Medium','Low','None'], key='var5')
            var6 = st.segmented_control(label = "Rest", options = ['High','Medium','Low','None'], key='var6')
            var7 = st.segmented_control(label = "Offensive Rating", options = ['High','Medium','Low','None'], key='var7')
            var8 = st.segmented_control(label = "Defensive Rating", options = ['High','Medium','Low','None'], key='var8')

    with col3:
        cat3 = st.slider(
            label="Matchup",
            min_value=0,
            max_value=100,
            value=20,
            step=1,
            format="%.0f%%",
            key='cat3'
        )

        with st.expander("Matchup Variables:",expanded=True):
            val9 = st.segmented_control(label = "Rivalry", options = ['High','Medium','Low','None'], key='var9')
            var10 = st.segmented_control(label = "Style Contrasts", options = ['High','Medium','Low','None'], key='var10')
            var11 = st.segmented_control(label = "Star Power", options = ['High','Medium','Low','None'], key='var11')    
            var12 = st.segmented_control(label = "National Broadcast", options = ['High','Medium','Low','None'], key='var12')
            
    with col4:
        cat4 = st.slider(
            label="Style of Play",
            min_value=0,
            max_value=100,
            value=10,
            step=1,
            format="%.0f%%",
            key='cat4'
        )

        with st.expander("Style Variables:",expanded=True):
            var13 = st.segmented_control(label = "Zach Lowe Rankings", options = ['High','Medium','Low','None'], key='var13')
            var14 = st.segmented_control(label = "Foul Rate", options = ['High','Medium','Low','None'], key='var14')
            var15 = st.segmented_control(label = "Pace", options = ['High','Medium','Low','None'], key='var15')
            var16 = st.segmented_control(label = "Ball Movement", options = ['High','Medium','Low','None'], key='var16')
            var17 = st.segmented_control(label = "Player Movement", options = ['High','Medium','Low','None'], key='var17')
            # var18 = st.segmented_control(label = "Assist Percent", options = ['High','Medium','Low','None'], key='var18')
            var19 = st.segmented_control(label = "Egalitarian Offense", options = ['High','Medium','Low','None'], key='var19')    
            var20 = st.segmented_control(label = "Diversity of Play Types", options = ['High','Medium','Low','None'], key='var20')

    
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
