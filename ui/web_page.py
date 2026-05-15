
# load packages
import streamlit as st
from util.helper import get_today
from data.get_data import get_scoreboard, get_injuries, get_live_box_score, get_spreads
from ratings.calculate_ratings import get_ratings
from charts.charts import lollipop_chart_plotly, pt_scatter_plotly, style_scatter_plotly, shot_bar_plotly
# import seaborn as sns
import matplotlib.colors as mcolors
from datetime import datetime, timedelta
import pytz


# creating the page first, so that I can then start catching functions
# moved the weights up to this function to help with caching later on
def create_page():
    st.set_page_config(layout="wide")

    # time stamp
    today = get_today()
    st.title("NBA Scoreboard:"+" "+today.strftime("%m/%d/%Y"))
    st.write("Scores as of: ", today.strftime('%#I:%M:%p'), " ET")


    with st.expander("ℹ️ How This Dashboard Works", expanded=False):
        st.markdown("""
        **🔄 Auto‑Refresh:**  
        Live data updates automatically every **5 minutes** during active games.

        **🔁 Manual Refresh:**  
        Use the **Refresh** button to pull the latest scoreboard, injuries, odds, and live box scores.  
        Refreshes are limited to **once every 30 seconds** to avoid API throttling.

        **⭐ Game Ratings:**  
        Each matchup receives a **0–10 score** based on four categories:  
        **Game State, Matchup Quality, Narrative Context, and Style of Play.**

        - Use the **sliders** to set how important each category is.  
        - Use the **High / Medium / Low / None** controls to fine‑tune the variables inside each category.  
        - Your selections are converted into percentages and combined with normalized stats to produce the final rating.

        Adjust anything — the ratings update instantly.

        **🔍 Learn more:**  
        Read the full architecture deep dive [on GitHub.](https://dmcdonough26.github.io/nba-scoreboard/)
        """)

    # set guardrail to avoid users spamming refresh button
    eastern = pytz.timezone("America/New_York")
    now = datetime.now(eastern)
    COOLDOWN = timedelta(seconds=30)

    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.min.replace(tzinfo=eastern)

    # create refresh button
    if st.button("Refresh"):
        if (now - st.session_state.last_refresh) < COOLDOWN:
            st.warning("*In my most Johnny Tran voice* Too soon, Junior 🙅‍♂️. Please allow ~30 seconds in between refreshes.")
        
        # clear cache on the live data elements (time stamp, scoreboard, injuries, live box score, odds)
        else:
            st.session_state.refresh_warning = False
            st.session_state.last_refresh = now
            get_today.clear()
            get_scoreboard.clear()
            get_injuries.clear()
            get_live_box_score.clear()
            get_spreads.clear()
            st.rerun()

    # four major categories for game ratings, with default weights adding to 100%
    st.write("Select weights for game rating categories:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cat1 = st.slider(
            label="Game State",
            min_value=0,
            max_value=100,
            value=40,
            step=1,
            format="%.0f%%",
            key='cat1'
        )

    with col2:
        cat2 = st.slider(
            label="Matchup Quality",
            min_value=0,
            max_value=100,
            value=35,
            step=1,
            format="%.0f%%",
            key='cat2'
        )

    with col3:
        cat3 = st.slider(
            label="Narrative Context",
            min_value=0,
            max_value=100,
            value=10,
            step=1,
            format="%.0f%%",
            key='cat3'
        )
            
    with col4:
        cat4 = st.slider(
            label="Style of Play",
            min_value=0,
            max_value=100,
            value=15,
            step=1,
            format="%.0f%%",
            key='cat4'
        )

    # variables underneath each category which allocate the category weights further
    st.write("Select weights for variables:")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        with st.expander("Game State Variables:",expanded=False):
            var1 = st.segmented_control(label = "Point Differential", options = ['High','Medium','Low','None'], key='var1', default='High')
            var2 = st.segmented_control(label = "Time Remaining", options = ['High','Medium','Low','None'], key='var2', default='Medium')
            var3 = st.segmented_control(label = "Game Flow", options = ['High','Medium','Low','None'], key='var3', default='None')

    with col6:
        with st.expander("Matchup Quality Variables:",expanded=False):
            var4 = st.segmented_control(label = "Team Strength", options = ['High','Medium','Low','None'], key='var4', default='High')
            var5 = st.segmented_control(label = "Player Availability", options = ['High','Medium','Low','None'], key='var5', default='High')
            var6 = st.segmented_control(label = "Rest", options = ['High','Medium','Low','None'], key='var6', default='Low')
            var7 = st.segmented_control(label = "Offensive Rating", options = ['High','Medium','Low','None'], key='var7', default='None')
            var8 = st.segmented_control(label = "Defensive Rating", options = ['High','Medium','Low','None'], key='var8', default='None')
    
    with col7:
        with st.expander("Narrative Context Variables:",expanded=False):
            val9 = st.segmented_control(label = "Rivalry", options = ['High','Medium','Low','None'], key='var9', default='Medium')
            var10 = st.segmented_control(label = "Style Contrasts", options = ['High','Medium','Low','None'], key='var10', default='Medium')
            var11 = st.segmented_control(label = "Star Power", options = ['High','Medium','Low','None'], key='var11', default='None')    
            var12 = st.segmented_control(label = "National Broadcast", options = ['High','Medium','Low','None'], key='var12', default='None')
            # I moved this variable up later on and didn't want to renumber all of the others so it remains 19
            var19 = st.segmented_control(label = "Zach Lowe Rankings", options = ['High','Medium','Low','None'], key='var19', default='None')

    with col8:
        with st.expander("Style Variables:",expanded=False):
            var13 = st.segmented_control(label = "Diversity of Play Types", options = ['High','Medium','Low','None'], key='var13', default='Medium')
            var14 = st.segmented_control(label = "Foul Rate", options = ['High','Medium','Low','None'], key='var14', default='Medium')
            var15 = st.segmented_control(label = "Pace", options = ['High','Medium','Low','None'], key='var15', default='Medium')
            var16 = st.segmented_control(label = "Ball Movement", options = ['High','Medium','Low','None'], key='var16', default='Medium')
            var17 = st.segmented_control(label = "Player Movement", options = ['High','Medium','Low','None'], key='var17', default='Medium')
            # var18 = st.segmented_control(label = "Assist Percent", options = ['High','Medium','Low','None'], key='var18', default='Medium')
            var18 = st.segmented_control(label = "Egalitarian Offense", options = ['High','Medium','Low','None'], key='var18', default='Medium')    


# launch the scoreboard dataframes and the what to watch charts
def launch_page(today, live_df, upcoming_df, finished_df, scoreboard_raw_df,
                ff_df, style_df, pt_df,
                shot_freq_df_long, shot_pct_df_long, opp_freq_df_long, opp_pct_df_long, name_dict):

    # choose color for game rating
    # color_choice = "#00B2A9"

    # One‑color lighter teal gradient
    # cmap = sns.light_palette(color_choice, as_cmap=True)

    color1 = "#EF426F" # low value
    color2 = "#00B2A9" # high value
    mid = "#ffffff"   # white neutral
    cmap = mcolors.LinearSegmentedColormap.from_list(
    "custom_div", [color1, mid, color2]
    )
    
    # Round rating to one decimal (numeric)
    live_df["Game Rating"] = live_df["Game Rating"].astype(float).round(1)
    upcoming_df["Game Rating"] = upcoming_df["Game Rating"].astype(float).round(1)
    finished_df["Game Rating"] = finished_df["Game Rating"].astype(float).round(1)

    # Style dataframes
    live_styled = (
        live_df.style
            .set_properties(subset=["Rivalry"], **{"font-size": "22px"})
            .format({"Game Rating": "{:.1f}"}) 
            .background_gradient(cmap=cmap, subset=["Game Rating"],vmin=0,vmax=10)
    )

    upcoming_styled = (
        upcoming_df.style
            .format({"Game Rating": "{:.1f}","Point Spread": "{:.1f}"})
            .background_gradient(cmap=cmap, subset=["Game Rating"],vmin=0,vmax=10)
    )

    finished_styled = (
        finished_df.style
            .format({"Game Rating": "{:.1f}"})
            .background_gradient(cmap=cmap, subset=["Game Rating"],vmin=0,vmax=10)
    )

    st.caption('''The table below shows all games on today's schedule, separated by game status.  \n"Win pace" shows how many games each team is on-pace to win in an 82‑game season.  \nInjuries are only shown for players that are confirmed out (players listed as doubtful/questionable are not included below).  \nPoint spreads are from the perspective of the home team.''')

    # Create the tabs for the scoreboards
    tab1, tab2, tab3 = st.tabs(['Live Games', 'Upcoming', 'Finished Games'])

    with tab1:
        st.dataframe(
            live_styled,
            column_config={
                "Away": st.column_config.ImageColumn("Away", width=100),
                "Home": st.column_config.ImageColumn("Home", width=100)
            },
            hide_index=True,
            row_height=60)
    
    with tab2:
        st.dataframe(
            upcoming_styled,
                column_config={
                "Away": st.column_config.ImageColumn("Away", width=100),
                "Home": st.column_config.ImageColumn("Home", width=100)
            },
            hide_index=True,
            row_height=60)
    
    with tab3:
        st.dataframe(          
            finished_styled,
                column_config={
                "Away": st.column_config.ImageColumn("Away", width=100),
                "Home": st.column_config.ImageColumn("Home", width=100)
            },
            hide_index=True,
            row_height=60)

    # have user choose a game for the what-to-watch charts
    # consider making this a select column instead in the dataframe?
    selected_game = st.selectbox(
        "Select a game",
        scoreboard_raw_df['game_name'],
        key = 'selected_game'
    )

    selected_teams = scoreboard_raw_df[scoreboard_raw_df['game_name']==st.session_state.selected_game][['awayTeam.teamName','homeTeam.teamName']].iloc[0].values

    # have user choose a side of the ball
    selected_side = st.radio(
        "Choose a side of the ball",
        selected_teams,
        key = 'selected_side',
        horizontal=True
    )

    # dictionaries team names/ids/matchups for the charts
    team_dict = dict(zip(
        list(scoreboard_raw_df['homeTeam.teamName'])+list(scoreboard_raw_df['awayTeam.teamName']),
        list(scoreboard_raw_df['homeTeam.teamId'])+list(scoreboard_raw_df['awayTeam.teamId'])
    ))

    matchup_dict = dict(zip(
        list(scoreboard_raw_df['homeTeam.teamName'])+list(scoreboard_raw_df['awayTeam.teamName']),
        list(scoreboard_raw_df['awayTeam.teamName'])+list(scoreboard_raw_df['homeTeam.teamName']),
    ))

    # create the tabs for the what-to-watch charts
    tab4, tab5, tab6, tab7 = st.tabs(['Four Factors', 'Style', 'Play Types', 'Shot Chart'])    

    with tab4:
        st.caption("The lollipop chart below shows where each team ranks on each of the four factors compared to the rest of the league.  \nOrange points compare the selected team's offense against the other 29 offenses. Gray points compare the opponent's defense against the other 29 defenses.  \nFor both offense and defense, 1st is best and 30th is worst.")
        ff_chart_df = ff_df[(ff_df['game_name']==selected_game)&(ff_df['offense']==team_dict[selected_side])]
        fig = lollipop_chart_plotly(ff_chart_df, matchup_dict, selected_side)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📘 Glossary", expanded=False):
            st.caption("Each metric is defined for the offense/defense respectively.  \nOffensive Rating: The number of points scored/allowed per 100 possessions.  \nEffective Field Goal %: Field goal percentage shot/allowed having converted three pointers onto the same scale as two-point shots.  \nTurnover %: The percentage of possessions that resulted in a turnover committed/forced.  \nOffensive Rebounding %: The percentage of rebounds that were grabbed by/given up to the offensive team.  \nFree Throw Rate: This dashboard uses the NBA's defintion, which is free throw attempts ÷ field goal attempts (Dean Oliver's original formula used free throws made ÷ field goal attempts).")

    with tab5:
        st.caption("The scatter plot below shows how the selected team's offense compares to the rest of the league. The tooltip shows the team name and rank for each data point. All six categories are standardized to be put on the same scale.")
        fig = style_scatter_plotly(style_df, selected_side, team_dict[selected_side], name_dict)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📘 Glossary", expanded=False):
            st.caption("Pace: The number of possessions per game.  \nPlayer Movement: The total distance ran ÷ the number of posessions.  \nBall Movement: The total number of passes made ÷ the number of possessions.  \nField Goal Concentration: The percentage of the team's field goal attempts taken by the player with the most field goal attempts (1st is the team with the heaviest concentration).  \nAssist Percent: The percentage of the team's made field goals that were assisted.  \nPlay Diversity: The sum of the squared differences of a team’s frequency of running each play type vs. the league average frequency for that play type.")
        

    with tab6:
        st.caption("The scatter plot below shows both the frequency and efficiency of each play type relative to league average. You can highlight a section of the chart to zoom.")
        pt_chart_df = pt_df[pt_df['team_id']==team_dict[st.session_state.selected_side]].reset_index(drop=True)
        fig = pt_scatter_plotly(pt_chart_df)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📘 Glossary", expanded=False):
            st.caption("The play type data from the NBA API works backwards to say where shots came from, as opposed to working forwards to say what actions a team typically runs (which would be preferred).  \nPutbacks and Miscellaneous were ommited because they do not help answer the question of what the team is trying to run.  \nPick and Roll Ballhandler and Pick and Roll Screener were combined to generally describe the action of Pick and Roll.  \nRelative Frequency: The selected team's percentage of plays from that play type ÷ the league average frequency.  \nRelative Efficiency: The selected team's points per possession from that play type ÷ the league average efficiency.")

    with tab7:

        st.caption("The bar charts below show data by shot location.  \nThe chart on the left shows where each team ranks in frequency and the chart on the right shows where they rank on efficiency.  \nOn offense, 1st means the selected team has the highest frequency/efficiency from that location.  \nOn Defense, 1st means the opponent allows the lowest frequency/efficiency from that location.")

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
