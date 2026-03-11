
# load packages
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# this script holds the code for the charts in the what-to-watch section
# a lot of this code was AI generated (at least to start) with modification as needed to accerlate learning curve/code dev

def lollipop_chart_plotly(ff_chart_df, matchup_dict, selected_side, x_min=0.5, x_max=30.5):

    # --- Ordinal helper ---
    def ordinal(n):
        n = int(n)
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"

    # Copy to avoid modifying original
    df = ff_chart_df.copy()

    # Build names
    selected_team = selected_side + " Offense"
    opponent = matchup_dict[selected_side] + " Defense"
    chart_title = selected_team + " vs. " + opponent

    # Rename columns
    df = df.rename(columns={"off": selected_team, "def": opponent})

    # Order for y-axis
    measure_order = [
        "Offensive Rating",
        "Effective Field Goal %",
        "Turnover %",
        "Offensive Rebounding %",
        "Free Throw Rate",
    ]

    df["measure"] = pd.Categorical(df["measure"], categories=measure_order, ordered=True)
    df = df.sort_values("measure")

    # Colors
    offense_color = '#FF8C00'
    defense_color = '#6e6e6e'

    fig = go.Figure()

    # --- Stems (horizontal lines) ---
    for _, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[x_min, x_max],
            y=[row["measure"], row["measure"]],
            mode="lines",
            line=dict(color="lightgray", width=2),
            showlegend=False
        ))

    # --- Offense points ---
    fig.add_trace(go.Scatter(
        x=df[selected_team],
        y=df["measure"],
        mode="markers+text",
        marker=dict(size=18, color=offense_color),
        text=[ordinal(v) for v in df[selected_team]],
        textposition="top center",
        name=selected_team,
        hovertemplate = selected_team + ": %{text} %{y}<extra></extra>"

    ))


    # --- Defense points ---
    fig.add_trace(go.Scatter(
        x=df[opponent],
        y=df["measure"],
        mode="markers+text",
        marker=dict(size=18, color=defense_color),
        text=[ordinal(v) for v in df[opponent]],        # <-- UPDATED
        textposition="top center",
        name=opponent,
        hovertemplate = opponent + ": %{text} %{y}<extra></extra>"
    ))

    # Layout
    fig.update_layout(
        title=dict(text=chart_title, font=dict(size=22)),
        xaxis=dict(range=[x_min, x_max], showgrid=False, showticklabels=False, title=""),
        yaxis=dict(showgrid=False, title=""),
        height=480,
        margin=dict(l=120, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            x=-0.01,
            y=-0.15,
            xanchor="left",
            yanchor="bottom",
            font=dict(size=18)
        )
    )

    fig.update_xaxes(tickfont=dict(size=18))
    fig.update_yaxes(
        tickfont=dict(size=18),
        categoryorder="array",
        categoryarray=measure_order[::-1],   # reverse the order
    )

    fig.update_traces(textfont=dict(size=18))

    return fig


def pt_scatter_plotly(pt_chart_df):

    df = pd.DataFrame(pt_chart_df)

    # this helps the tooltip show relative frequency/efficiency in the desired format
    df["freq_delta"] = ((df["rel_poss_pct"] - 1) * 100).round(0)   # e.g. 1.20 -> +20
    df["eff_delta"]  = ((df["rel_ppp"]      - 1) * 100).round(0)   # e.g. 0.85 -> -15
    customdata = df[["freq_delta", "eff_delta"]].to_numpy()


    title_var = (
        st.session_state.selected_side
        + " Offense: Relative Frequency and Efficiency of Play Types, Compared to League Average"
    )

    # Colors
    point_color = "#FF8C00"
    line_color = "#D3D3D3"

    fig = go.Figure()

    # --- Horizontal reference line at y = 1 ---
    fig.add_shape(
        type="line",
        x0=-0.5, x1=2.5,
        y0=1, y1=1,
        line=dict(color=line_color, width=1),
        layer="below"
    )

    # --- Vertical reference line at x = 1 ---
    fig.add_shape(
        type="line",
        x0=1, x1=1,
        y0=0.5, y1=1.5,
        line=dict(color=line_color, width=1),
        layer="below"
    )

    # --- Scatter points with labels ---
    fig.add_trace(go.Scatter(
        x=df["rel_poss_pct"],
        y=df["rel_ppp"],
        mode="markers+text",
        marker=dict(size=14, color=point_color),
        text=df["play_type"],
        textposition="top center",
        name="Play Type",
        customdata=customdata,
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Frequency: %{customdata[0]:+.0f}%<br>"
            "Efficiency: %{customdata[1]:+.0f}%<extra></extra>"
        )


        ))

    # --- Axes formatting ---
    fig.update_xaxes(
        title="Relative Frequency (%)",
        range=[-0.5, 2.5],
        tickmode="array",
        tickvals=[-0.5, 0, 0.5, 1, 1.5, 2, 2.5],
        ticktext=[f"{round((v - 1) * 100)}%" for v in [-0.5, 0, 0.5, 1, 1.5, 2, 2.5]],
        showgrid=False,
        zeroline=False
    )

    fig.update_yaxes(
        title="Relative Efficiency (%)",
        range=[0.5, 1.5],
        tickmode="array",
        tickvals=[0.5, 0.75, 1, 1.25, 1.5],
        ticktext=[f"{round((v - 1) * 100)}%" for v in [0.5, 0.75, 1, 1.25, 1.5]],
        showgrid=False,
        zeroline=False
    )

    # --- Layout ---
    fig.update_layout(
        title=dict(text=title_var, font=dict(size=20)),
        height=450,
        margin=dict(l=60, r=40, t=60, b=60),
        showlegend=False
    )

    fig.update_xaxes(tickfont=dict(size=18), titlefont=dict(size=18))
    fig.update_yaxes(tickfont=dict(size=18), titlefont=dict(size=18))
    fig.update_traces(textfont=dict(size=18))

    return fig


def style_scatter_plotly(style_df, selected_side, selected_id, name_dict):
    df = pd.DataFrame(style_df)

    # --- Ordinal helper (same as lollipop chart) ---
    def ordinal(n):
        n = int(n)
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"

    # Colors
    base_color = "#6e6e6e"
    highlight_color = "#FF8C00"

    # --- Compute rank within each Category (1 = highest Value) ---
    df["Rank"] = (
        df.groupby("Category")["Value"]
          .rank(ascending=False, method="dense")
          .astype(int)
    )

    df['Name'] = df['Team'].apply(lambda x: name_dict[x])

    # Split data
    df_all = df
    df_selected = df[df["Team"] == selected_id]

    fig = go.Figure()

    # --- All teams (gray) ---
    fig.add_trace(go.Scatter(
        x=df_all["Category"],
        y=df_all["Value"],
        mode="markers",
        marker=dict(size=14, color=base_color),
        text=[ordinal(r) for r in df_all["Rank"]],   # ordinal rank
        customdata=df_all['Name'],
        hovertemplate=(
            "%{customdata}: %{text}<extra></extra>"
        )
    ))

    # --- Selected team (orange) with ordinal rank labels ---
    fig.add_trace(go.Scatter(
        x=df_selected["Category"],
        y=df_selected["Value"],
        mode="markers+text",
        marker=dict(size=16, color=highlight_color),
        text=[ordinal(r) for r in df_selected["Rank"]],   # ordinal rank
        textposition="middle right",
        name=selected_side,
        hovertemplate=(
            selected_side +
            ": %{text}<extra></extra>"
        )
    ))

    # --- Layout ---
    fig.update_layout(
        title=dict(
            text=selected_side+": Team Style Overview",
            font=dict(size=22)
        ),
        height=450,
        margin=dict(l=80, r=40, t=60, b=60),
        font=dict(size=18),
        showlegend=False
    )

    # --- Axes ---
    fig.update_xaxes(
        tickfont=dict(size=18),
        titlefont=dict(size=18),
        showgrid=False
    )

    fig.update_yaxes(
        showticklabels=False,
        title=None,
        showgrid=False,
        zeroline=False
    )

    return fig

def shot_bar_plotly(off_df, def_df, matchup_dict, team_dict, selected_side, freq=True):

        # --- Ordinal helper ---
    def ordinal(n):
        n = int(n)
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"

    # establish teams
    offense_name = selected_side
    defense_name = matchup_dict[selected_side]
    offense_id = team_dict[selected_side]
    defense_id = team_dict[defense_name] # this needs to be the other team

    chart_title = (
        "Shot Distribution by Location" if freq else "Field Goal Percentage by Location"
    )

    off_df['off_rank_text'] = off_df.groupby('Measure')['Offense'].rank(ascending=False) # 1st means you get the most
    off_df['off_rank_bar'] = off_df.groupby('Measure')['Offense'].rank(ascending=True)
    def_df['def_rank_text'] = def_df.groupby('Measure')['Defense'].rank(ascending=True) # 1st means you give up the least
    def_df['def_rank_bar'] = def_df.groupby('Measure')['Defense'].rank(ascending=False)

    # create chart dataframes
    off_df_team = off_df[off_df['team_id'] == offense_id]
    def_df_team = def_df[def_df['team_id'] == defense_id]
    df = off_df_team.merge(def_df_team[['Measure', 'def_rank_text','def_rank_bar']], on='Measure')

    fig = go.Figure()

    # --- Offense bar ---
    fig.add_trace(go.Bar(
        x=df["Measure"],
        y=df["off_rank_bar"],
        name=offense_name + " Offense",
        marker_color="#FF8C00",
        # text=[f"{v:.0%}" for v in df["Offense"]],
        text = [ordinal(v) for v in df['off_rank_text']],
        textposition="outside",
        textfont=dict(color="#FF8C00", size=18),
        width=0.35,   # <-- narrower bar
        hovertemplate = offense_name + " Offense: %{text} Highest %{x}<extra></extra>"
    ))

    # --- Defense bar ---
    fig.add_trace(go.Bar(
        x=df["Measure"],
        y=df["def_rank_bar"],
        name=defense_name + " Defense",
        marker_color="#6e6e6e",
        # text=[f"{v:.0%}" for v in df["Defense"]],
        text = [ordinal(v) for v in df['def_rank_text']],
        textposition="outside",
        textfont=dict(color="#6e6e6e", size=18),
        width=0.35,  # <-- narrower bar
        hovertemplate = defense_name + " Defense: %{text} Lowest %{x}<extra></extra>"
    ))

    # Layout
    fig.update_layout(
        barmode="group",
        bargap=0.25,        # space between categories
        bargroupgap=0.1,   # space between orange & gray
        title=dict(text=chart_title,font=dict(size=22)),
        font=dict(size=16),
        height=580,
        margin=dict(l=60, r=40, t=60, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,      # pushes legend below chart
            xanchor="center",
            x=0.5,
            font=dict(size=18)
        )

    )

    # Remove y-axis labels + gridlines
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False
    )

    fig.update_xaxes(tickfont=dict(size=18))

    return fig