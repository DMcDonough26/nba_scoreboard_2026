
# enable traceback
import sys
import traceback

def show_traceback():
    st.error("An error occurred. See details below.")
    st.code(traceback.format_exc())


# load packages
from ui.web_page import create_page, launch_page
from data.wrangle_data import combine_data
import streamlit as st
from streamlit_autorefresh import st_autorefresh


def main():
    # create the page first, so you can start caching functions
    create_page()

    # exception handling is added for days when there are no NBA games
    try:
        # fetch all of the data needed for the app
        data = combine_data()

        # if no games today, provide a message
        if data.get("no_games"):
            st.info("There are no NBA games scheduled today.")
            return

        # while games are live, auto refresh the dashboard every five minutes
        if not data['live_df'].empty:
            st_autorefresh(interval=300000, key="live_refresh")

        # remove the no games flag before passing to launch page
        data.pop("no_games", None) 

        # render the rest of the page
        launch_page(**data)

    # if an issue exists (beyond no games that day) provide feedback to the user
    except Exception as e:
        st.error("The app is temporarily unavailable due to missing data.")
        st.caption(f"Technical detail: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        show_traceback()



