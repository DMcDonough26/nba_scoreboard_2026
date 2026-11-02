# diag.py - temporary Streamlit page: can this environment reach stats.nba.com,
# and does what comes back look the same as locally?
import sys
import time
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import certifi
import nba_api
import pandas as pd
import requests
import streamlit as st
import urllib3
from nba_api.stats.endpoints import scoreboardv3
from nba_api.stats.library.http import NBAStatsHTTP

FALLBACK_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "Accept": "application/json, text/plain, */*",
}

st.title("Deployment diagnostics")

eastern_now = datetime.now(ZoneInfo("America/New_York"))
st.write({
    "python": sys.version.split()[0],
    "nba_api": getattr(nba_api, "__version__", "unknown"),
    "pandas": pd.__version__,
    "requests": requests.__version__,
    "urllib3": urllib3.__version__,
    "certifi": certifi.__version__,
})

date_str = st.text_input("Game date (YYYY-MM-DD)", eastern_now.strftime("%Y-%m-%d"))

if st.button("Run tests"):

    # Test 1: raw HTTP request, bypassing nba_api's parsing
    st.subheader("1. Raw request to stats.nba.com")
    lib_headers = getattr(NBAStatsHTTP, "headers", None)
    headers = dict(lib_headers) if lib_headers else FALLBACK_HEADERS
    st.caption(f"Headers used: {'nba_api defaults' if lib_headers else 'fallback browser-style set'}")

    start = time.time()
    try:
        r = requests.get(
            "https://stats.nba.com/stats/scoreboardv3",
            params={"GameDate": date_str, "LeagueID": "00"},
            headers=headers,
            timeout=30,
        )
        st.write({
            "status": r.status_code,
            "content-type": r.headers.get("content-type"),
            "seconds": round(time.time() - start, 1),
            "bytes": len(r.content),
        })
        try:
            j = r.json()
            sb = j.get("scoreboard", {})
            st.write("Top-level keys:", list(j.keys()))
            st.write("scoreboard keys:", list(sb.keys()), "| games:", len(sb.get("games", [])))
        except ValueError:
            st.error("Response was not JSON. First 300 characters:")
            st.code(r.text[:300])
    except Exception as e:
        st.error(f"Request failed after {round(time.time() - start, 1)}s: {type(e).__name__}: {e}")

    # Test 2: the same call through nba_api
    st.subheader("2. Through nba_api")
    try:
        frames = scoreboardv3.ScoreboardV3(game_date=date_str, timeout=60).get_data_frames()
        st.success(f"OK: {len(frames)} frames")
        for i, df in enumerate(frames):
            st.write(i, df.shape, list(df.columns)[:6])
    except Exception as e:
        st.error(f"{type(e).__name__}: {e}")
        st.code(traceback.format_exc())