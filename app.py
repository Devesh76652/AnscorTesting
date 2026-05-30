import streamlit as st
import pandas as pd
from datetime import datetime

from modules.database import (
    init_database,
    get_matches,
    create_match,
    get_match
)

from modules.ui import (
    render_header,
    render_scoreboard,
    render_batting_card,
    render_bowling_card,
    render_scoring_panel,
    render_match_selector
)

from modules.analytics import (
    render_runrate_graph,
    render_worm_graph
)

from modules.pdf_export import (
    generate_scorecard_pdf
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="ANSCOR APL",
    page_icon="🏏",
    layout="wide"
)

# =====================================
# INIT DATABASE
# =====================================

init_database()

# =====================================
# THEME
# =====================================

st.markdown("""
<style>

.main {
    background-color: #020617;
}

.block-container {
    padding-top: 1rem;
}

.metric-container {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# SESSION STATE
# =====================================

if "selected_match" not in st.session_state:
    st.session_state.selected_match = None

# =====================================
# HEADER
# =====================================

render_header()

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("🏏 ANSCOR")

    page = st.radio(
        "Navigation",
        [
            "Live Match",
            "Create Match",
            "Archive",
            "Tournament"
        ]
    )

# =====================================
# CREATE MATCH PAGE
# =====================================

if page == "Create Match":

    st.subheader("Create New Match")

    with st.form("create_match"):

        match_name = st.text_input("Match Name")

        team_a = st.text_input("Team A")

        team_b = st.text_input("Team B")

        overs = st.number_input(
            "Overs",
            min_value=1,
            max_value=50,
            value=10
        )

        submitted = st.form_submit_button("Create Match")

        if submitted:

            match_id = create_match(
                match_name,
                team_a,
                team_b,
                overs
            )

            st.success(
                f"Match Created Successfully ({match_id})"
            )

# =====================================
# LIVE MATCH PAGE
# =====================================

elif page == "Live Match":

    matches = get_matches()

    if not matches:

        st.info("No Matches Available")

        st.stop()

    selected = render_match_selector(matches)

    if selected is None:

        st.stop()

    match = get_match(selected)

    st.session_state.selected_match = selected

    render_scoreboard(match)

    col1, col2 = st.columns([2, 1])

    with col1:

        st.subheader("Batting")

        render_batting_card(match)

    with col2:

        st.subheader("Bowling")

        render_bowling_card(match)

    st.divider()

    render_scoring_panel(match)

    st.divider()

    st.subheader("Analytics")

    render_runrate_graph(match)

    render_worm_graph(match)

    st.divider()

    pdf_bytes = generate_scorecard_pdf(match)

    st.download_button(
        "📥 Download Scorecard",
        data=pdf_bytes,
        file_name=f"{match['name']}.pdf",
        mime="application/pdf"
    )

# =====================================
# ARCHIVE PAGE
# =====================================

elif page == "Archive":

    st.subheader("Match Archive")

    matches = get_matches()

    if matches:

        archive_df = pd.DataFrame(matches)

        st.dataframe(
            archive_df,
            use_container_width=True
        )

    else:

        st.info("No Archived Matches")

# =====================================
# TOURNAMENT PAGE
# =====================================

elif page == "Tournament":

    st.subheader("Tournament Dashboard")

    st.info(
        "Points Table, Rankings and Stats "
        "will appear here."
    )

# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    f"ANSCOR APL Platform • {datetime.now().year}"
)
