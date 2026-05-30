# database.py
import sqlite3
from datetime import datetime
from pathlib import Path

DB_FILE = "database.db"


# ==========================================
# CONNECTION
# ==========================================
def get_connection():
    conn = sqlite3.connect(
        DB_FILE,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# ==========================================
# DATABASE INIT
# ==========================================
def init_database():

    conn = get_connection()

    cursor = conn.cursor()

    # MATCHES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        team_a TEXT NOT NULL,

        team_b TEXT NOT NULL,

        overs INTEGER NOT NULL,

        status TEXT DEFAULT 'LIVE',

        winner TEXT,

        created_at TEXT
    )
    """)

    # INNINGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS innings (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        match_id INTEGER,

        innings_no INTEGER,

        batting_team TEXT,

        bowling_team TEXT,

        runs INTEGER DEFAULT 0,

        wickets INTEGER DEFAULT 0,

        balls INTEGER DEFAULT 0,

        extras INTEGER DEFAULT 0,

        FOREIGN KEY(match_id)
        REFERENCES matches(id)
    )
    """)

    # PLAYERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        match_id INTEGER,

        innings_no INTEGER,

        name TEXT,

        role TEXT,

        runs INTEGER DEFAULT 0,

        balls INTEGER DEFAULT 0,

        fours INTEGER DEFAULT 0,

        sixes INTEGER DEFAULT 0,

        wickets INTEGER DEFAULT 0,

        runs_conceded INTEGER DEFAULT 0,

        overs_bowled REAL DEFAULT 0,

        FOREIGN KEY(match_id)
        REFERENCES matches(id)
    )
    """)

    # BALL EVENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ball_events (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        match_id INTEGER,

        innings_no INTEGER,

        over_no INTEGER,

        ball_no INTEGER,

        batter TEXT,

        bowler TEXT,

        runs INTEGER,

        extra_type TEXT,

        wicket INTEGER DEFAULT 0,

        description TEXT,

        created_at TEXT,

        FOREIGN KEY(match_id)
        REFERENCES matches(id)
    )
    """)

    conn.commit()
    conn.close()


# ==========================================
# CREATE MATCH
# ==========================================
def create_match(
    match_name,
    team_a,
    team_b,
    overs
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO matches (
        name,
        team_a,
        team_b,
        overs,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        match_name,
        team_a,
        team_b,
        overs,
        datetime.now().isoformat()
    ))

    match_id = cursor.lastrowid

    # Create Innings 1
    cursor.execute("""
    INSERT INTO innings (
        match_id,
        innings_no,
        batting_team,
        bowling_team
    )
    VALUES (?, ?, ?, ?)
    """, (
        match_id,
        1,
        team_a,
        team_b
    ))

    # Create Innings 2
    cursor.execute("""
    INSERT INTO innings (
        match_id,
        innings_no,
        batting_team,
        bowling_team
    )
    VALUES (?, ?, ?, ?)
    """, (
        match_id,
        2,
        team_b,
        team_a
    ))

    conn.commit()
    conn.close()

    return match_id


# ==========================================
# GET ALL MATCHES
# ==========================================
def get_matches():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM matches
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ==========================================
# GET SINGLE MATCH
# ==========================================
def get_match(match_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM matches
    WHERE id=?
    """, (match_id,))

    match = cursor.fetchone()

    if not match:
        conn.close()
        return None

    match = dict(match)

    # Load innings
    cursor.execute("""
    SELECT *
    FROM innings
    WHERE match_id=?
    ORDER BY innings_no
    """, (match_id,))

    innings = [
        dict(row)
        for row in cursor.fetchall()
    ]

    match["innings"] = innings

    conn.close()

    return match


# ==========================================
# UPDATE INNINGS
# ==========================================
def update_innings(
    innings_id,
    runs,
    wickets,
    balls,
    extras
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE innings
    SET
        runs=?,
        wickets=?,
        balls=?,
        extras=?
    WHERE id=?
    """, (
        runs,
        wickets,
        balls,
        extras,
        innings_id
    ))

    conn.commit()
    conn.close()


# ==========================================
# BALL EVENT
# ==========================================
def add_ball_event(
    match_id,
    innings_no,
    over_no,
    ball_no,
    batter,
    bowler,
    runs,
    extra_type="",
    wicket=0,
    description=""
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO ball_events (

        match_id,
        innings_no,
        over_no,
        ball_no,
        batter,
        bowler,
        runs,
        extra_type,
        wicket,
        description,
        created_at

    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        match_id,
        innings_no,
        over_no,
        ball_no,
        batter,
        bowler,
        runs,
        extra_type,
        wicket,
        description,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


# ==========================================
# GET BALL EVENTS
# ==========================================
def get_ball_events(
    match_id,
    innings_no
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM ball_events
    WHERE match_id=?
    AND innings_no=?
    ORDER BY id
    """, (
        match_id,
        innings_no
    ))

    events = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return events


# ==========================================
# PLAYER MANAGEMENT
# ==========================================
def add_player(
    match_id,
    innings_no,
    player_name,
    role
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO players (
        match_id,
        innings_no,
        name,
        role
    )
    VALUES (?, ?, ?, ?)
    """, (
        match_id,
        innings_no,
        player_name,
        role
    ))

    conn.commit()
    conn.close()


def get_players(
    match_id,
    innings_no
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM players
    WHERE match_id=?
    AND innings_no=?
    """, (
        match_id,
        innings_no
    ))

    players = [
        dict(row)
        for row in cursor.fetchall()
    ]

    conn.close()

    return players


# ==========================================
# COMPLETE MATCH
# ==========================================
def finish_match(
    match_id,
    winner
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE matches
    SET
        status='COMPLETED',
        winner=?
    WHERE id=?
    """, (
        winner,
        match_id
    ))

    conn.commit()
    conn.close()


# ==========================================
# DELETE MATCH
# ==========================================
def delete_match(
    match_id
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM ball_events WHERE match_id=?",
        (match_id,)
    )

    cursor.execute(
        "DELETE FROM players WHERE match_id=?",
        (match_id,)
    )

    cursor.execute(
        "DELETE FROM innings WHERE match_id=?",
        (match_id,)
    )

    cursor.execute(
        "DELETE FROM matches WHERE id=?",
        (match_id,)
    )

    conn.commit()
    conn.close()
