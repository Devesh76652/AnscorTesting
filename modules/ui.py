import streamlit as st


def render_header():
    st.title("🏏 ANSCOR APL 2026")


def render_match_selector(matches):
    if not matches:
        return None

    ids = [m["id"] for m in matches]

    return st.selectbox(
        "Select Match",
        ids
    )


def render_scoreboard(match):
    st.subheader(
        f'{match["team_a"]} vs {match["team_b"]}'
    )


def render_batting_card(match):
    st.info("Batting card coming soon")


def render_bowling_card(match):
    st.info("Bowling card coming soon")


def render_scoring_panel(match):
    st.info("Scoring panel coming soon")
