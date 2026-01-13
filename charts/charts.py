# import altair as alt
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# def lollipop_chart_plotly(ff_chart_df, matchup_dict, selected_side, x_min=1, x_max=30):
#     # Copy to avoid modifying original
#     df = ff_chart_df.copy()

#     # Build names
#     selected_team = selected_side + " Offense"
#     opponent = matchup_dict[selected_side] + " Defense"
#     chart_title = selected_team + " vs. " + opponent

#     # Rename columns
#     df = df.rename(columns={"off": selected_team, "def": opponent})

#     # Order for y-axis
#     measure_order = [
#         "Offensive Rating",
#         "Effective Field Goal %",
#         "Turnover %",
#         "Offensive Rebounding %",
#         "Free Throw Rate",
#     ]

#     df["measure"] = pd.Categorical(df["measure"], categories=measure_order, ordered=True)
#     df = df.sort_values("measure")

#     # Colors
#     offense_color = '#FF8C00'
#     defense_color = '#6e6e6e'

#     fig = go.Figure()

#     # --- Stems (horizontal lines) ---
#     for _, row in df.iterrows():
#         fig.add_trace(go.Scatter(
#             x=[x_min, x_max],
#             y=[row["measure"], row["measure"]],
#             mode="lines",
#             line=dict(color="lightgray", width=2),
#             showlegend=False
#         ))

#     # --- Offense points ---
#     fig.add_trace(go.Scatter(
#         x=df[selected_team],
#         y=df["measure"],
#         mode="markers+text",
#         marker=dict(size=18, color=offense_color),
#         text=[f"{v:.1f}" for v in df[selected_team]],
#         textposition="top center",
#         name=selected_team
#     ))

#     # --- Defense points ---
#     fig.add_trace(go.Scatter(
#         x=df[opponent],
#         y=df["measure"],
#         mode="markers+text",
#         marker=dict(size=18, color=defense_color),
#         text=[f"{v:.1f}" for v in df[opponent]],
#         textposition="top center",
#         name=opponent
#     ))

#     # Layout
#     fig.update_layout(
#         title=dict(text=chart_title, font=dict(size=22)),
#         xaxis=dict(range=[x_min, x_max], showgrid=False, showticklabels=False, title=""),
#         yaxis=dict(showgrid=False, title=""),
#         height=420,
#         margin=dict(l=120, r=40, t=60, b=40),
#         legend=dict(
#             orientation="h",
#             x=-0.01,
#             y=-0.15,
#             xanchor="left",
#             yanchor="bottom",
#             font=dict(size=18)
#         )

#     )

#     fig.update_xaxes(tickfont=dict(size=18))
#     fig.update_yaxes(tickfont=dict(size=18))
#     fig.update_traces(textfont=dict(size=18))

#     return fig

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
        text=[ordinal(v) for v in df[selected_team]],   # <-- UPDATED
        textposition="top center",
        name=selected_team
    ))

    # --- Defense points ---
    fig.add_trace(go.Scatter(
        x=df[opponent],
        y=df["measure"],
        mode="markers+text",
        marker=dict(size=18, color=defense_color),
        text=[ordinal(v) for v in df[opponent]],        # <-- UPDATED
        textposition="top center",
        name=opponent
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
    fig.update_yaxes(tickfont=dict(size=18))
    fig.update_traces(textfont=dict(size=18))

    return fig


def pt_scatter_plotly(pt_chart_df):

    df = pd.DataFrame(pt_chart_df)

    title_var = (
        st.session_state.selected_side
        + " Offense: Relative Frequency and Efficiency of Play Types, Compared to Leage Average"
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
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Rel Frequency (raw): %{x:.2f}<br>" +
            "Rel Efficiency (raw): %{y:.2f}<extra></extra>"
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

