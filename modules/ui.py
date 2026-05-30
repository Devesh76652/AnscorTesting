# modules/ui.py

import streamlit as st
import pandas as pd


def render_live_match(match):

    st.subheader(
        f"{match['team_a']} vs {match['team_b']}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Score",
            f"{match['runs']}/{match['wickets']}"
        )

    with col2:
        st.metric(
            "Overs",
            f"{match['overs']}.{match['balls']}"
        )

    with col3:
        crr = 0

        total_balls = (
            match['overs'] * 6 +
            match['balls']
        )

        if total_balls > 0:
            crr = round(
                match['runs'] /
                (total_balls / 6),
                2
            )

        st.metric("CRR", crr)

    st.divider()

    batting_col, bowling_col = st.columns([2, 1])

    with batting_col:

        st.markdown("### Batting")

        batting = pd.DataFrame(
            match.get("batters", [])
        )

        if not batting.empty:
            st.dataframe(
                batting,
                use_container_width=True
            )
        else:
            st.info("No batters yet")

    with bowling_col:

        st.markdown("### Bowling")

        bowling = pd.DataFrame(
            match.get("bowlers", [])
        )

        if not bowling.empty:
            st.dataframe(
                bowling,
                use_container_width=True
            )
        else:
            st.info("No bowlers yet")

    st.divider()

    st.markdown("## Scoring Panel")

    run_cols = st.columns(7)

    if run_cols[0].button("0"):
        add_runs(match, 0)

    if run_cols[1].button("1"):
        add_runs(match, 1)

    if run_cols[2].button("2"):
        add_runs(match, 2)

    if run_cols[3].button("3"):
        add_runs(match, 3)

    if run_cols[4].button("4"):
        add_runs(match, 4)

    if run_cols[5].button("6"):
        add_runs(match, 6)

    if run_cols[6].button("W"):
        wicket(match)

    st.write("")

    extra_cols = st.columns(4)

    if extra_cols[0].button("Wide"):
        extra(match, "WD")

    if extra_cols[1].button("No Ball"):
        extra(match, "NB")

    if extra_cols[2].button("Bye"):
        extra(match, "B")

    if extra_cols[3].button("Leg Bye"):
        extra(match, "LB")

    st.write("")

    action_cols = st.columns(3)

    if action_cols[0].button("Undo"):
        undo_last_ball(match)

    if action_cols[1].button("End Over"):
        end_over(match)

    if action_cols[2].button("End Innings"):
        end_innings(match)


def add_runs(match, runs):

    match["runs"] += runs

    match["balls"] += 1

    if match["balls"] == 6:
        match["overs"] += 1
        match["balls"] = 0

    st.success(f"{runs} Run(s) Added")

    st.rerun()


def wicket(match):

    match["wickets"] += 1

    match["balls"] += 1

    if match["balls"] == 6:
        match["overs"] += 1
        match["balls"] = 0

    st.error("Wicket!")

    st.rerun()


def extra(match, kind):

    match["runs"] += 1

    st.info(f"{kind} Added")

    st.rerun()


def undo_last_ball(match):

    st.warning(
        "Undo logic to be connected to database"
    )


def end_over(match):

    match["overs"] += 1
    match["balls"] = 0

    st.success("Over Completed")

    st.rerun()


def end_innings(match):

    st.success("Innings Finished")

    st.rerun()


def render_create_match():

    st.subheader("Create Match")

    name = st.text_input("Match Name")

    team_a = st.text_input("Team A")

    team_b = st.text_input("Team B")

    overs = st.number_input(
        "Overs",
        min_value=1,
        value=10
    )

    if st.button("Create Match"):

        st.success(
            f"{name} created successfully"
        )


def render_archive(matches):

    st.subheader("Match Archive")

    if len(matches) == 0:
        st.info("No matches found")
        return

    st.dataframe(
        pd.DataFrame(matches),
        use_container_width=True
    )


def render_tournament():

    st.subheader("Tournament Dashboard")

    st.info(
        "Points Table, NRR, Rankings and Awards"
    )
