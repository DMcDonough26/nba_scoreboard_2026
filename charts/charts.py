import altair as alt
import pandas as pd
import streamlit as st

def lollipop_chart(df, matchup_dict, x_min=1, x_max=30):
    """
    Render a lollipop chart using Altair inside Streamlit.

    df must contain:
      - measure
      - off
      - def
    """
    # Copy to avoid modifying original
    df = df.copy()

    # Update names
    selected_team = st.session_state.selected_side + " Offense"
    opponent = matchup_dict[st.session_state.selected_side] + " Defense"
    chart_title = selected_team + " vs. " + opponent

    # Rename Off/Def to Offense/Defense for legend clarity
    df = df.rename(columns={"off": selected_team, "def": opponent})

    # Add stem endpoints
    df["min_x"] = x_min
    df["max_x"] = x_max

    # Melt into long format for legend + points
    long_df = df.melt(
        id_vars=["measure", "min_x", "max_x"],
        value_vars=[selected_team, opponent],
        var_name="Metric",
        value_name="Value"
    )

    # Desired y-axis order
    measure_order = [
        "Offensive Rating",
        "Effective Field Goal %",
        "Turnover %",
        "Offensive Rebounding %",
        "Free Throw Rate",
    ]

    # Horizontal stems
    stems = alt.Chart(df).mark_rule(
        color="lightgray",
        strokeWidth=2
    ).encode(
        y=alt.Y("measure:N", sort=measure_order),
        x="min_x:Q",
        x2="max_x:Q"
    )

    offense_color = '#FF8C00' 
    defense_color = '#6e6e6e'

    # Lollipop points
    points = alt.Chart(long_df).mark_circle(
        size=300,
        strokeWidth=2,
        opacity=1.0
    ).encode(
        x=alt.X(
            "Value:Q",
            scale=alt.Scale(domain=[x_min, x_max]),
            axis=alt.Axis(
                labels=False,   # hides the numbers
                ticks=False,    # hides tick marks
                title=None
            )
        ),
        y=alt.Y("measure:N", sort=measure_order, axis=alt.Axis(labelAlign="left")),
        fill=alt.Fill(
            "Metric:N",
            scale=alt.Scale(
                domain=[selected_team, opponent],
                range=[offense_color, defense_color]   # Offense fill = orange, Defense fill = white
            ),
            legend=alt.Legend(
                title=None,
                orient="bottom",
                direction="horizontal",
                symbolSize=300,
                labelFontSize=16
            )
        ),
        stroke=alt.Stroke(
            "Metric:N",
            scale=alt.Scale(
                domain=[selected_team, opponent],
                range=[offense_color, defense_color]   # pick any two colors you want
            ),
            legend=None
        )

    )

    # Labels
    labels = alt.Chart(long_df).mark_text(
        dy=-20,
        color="black",
        fontSize=16
    ).encode(
        x="Value:Q",
        y=alt.Y("measure:N", sort=measure_order),
        text="Value:Q"
    )

    # Combine layers
    chart = (
        stems + points + labels
    ).properties(
        width=600,
        height=400,
        title=alt.TitleParams(
            chart_title,
            fontSize=22
        )
    ).configure_axis(
        grid=False,
        labelFontSize=16,
        labelPadding=150,
        labelLimit=200,
        title=None   # removes axis titles
    )

    st.altair_chart(chart, use_container_width=True)