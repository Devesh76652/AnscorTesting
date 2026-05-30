from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime


# ==================================================
# BATTER MODEL
# ==================================================

@dataclass
class Batter:

    name: str

    runs: int = 0
    balls: int = 0

    fours: int = 0
    sixes: int = 0

    strike: bool = False

    dismissal: str = "Not Out"

    def strike_rate(self) -> float:

        if self.balls == 0:
            return 0.0

        return round(
            (self.runs / self.balls) * 100,
            2
        )

    def to_dict(self):

        return asdict(self)


# ==================================================
# BOWLER MODEL
# ==================================================

@dataclass
class Bowler:

    name: str

    balls: int = 0

    runs_conceded: int = 0

    wickets: int = 0

    maidens: int = 0

    def overs(self) -> str:

        return f"{self.balls // 6}.{self.balls % 6}"

    def economy(self) -> float:

        if self.balls == 0:
            return 0.0

        overs_float = self.balls / 6

        return round(
            self.runs_conceded / overs_float,
            2
        )

    def to_dict(self):

        return asdict(self)


# ==================================================
# PARTNERSHIP MODEL
# ==================================================

@dataclass
class Partnership:

    batter_one: str
    batter_two: str

    runs: int = 0

    balls: int = 0

    def to_dict(self):

        return asdict(self)


# ==================================================
# FALL OF WICKET MODEL
# ==================================================

@dataclass
class FallOfWicket:

    wicket_no: int

    score: str

    batter: str

    over: str

    def to_dict(self):

        return asdict(self)


# ==================================================
# BALL EVENT MODEL
# ==================================================

@dataclass
class BallEvent:

    innings_no: int

    over_no: int

    ball_no: int

    batter: str

    bowler: str

    runs: int

    extra_type: str = ""

    wicket: bool = False

    description: str = ""

    timestamp: str = field(
        default_factory=lambda:
        datetime.now().isoformat()
    )

    def to_dict(self):

        return asdict(self)


# ==================================================
# INNINGS MODEL
# ==================================================

@dataclass
class Innings:

    innings_no: int

    batting_team: str

    bowling_team: str

    runs: int = 0

    wickets: int = 0

    balls: int = 0

    extras: int = 0

    current_over: List[str] = field(
        default_factory=list
    )

    over_history: List[dict] = field(
        default_factory=list
    )

    partnerships: List[dict] = field(
        default_factory=list
    )

    fall_of_wickets: List[dict] = field(
        default_factory=list
    )

    batting_card: List[dict] = field(
        default_factory=list
    )

    bowling_card: List[dict] = field(
        default_factory=list
    )

    def overs(self) -> str:

        return f"{self.balls // 6}.{self.balls % 6}"

    def run_rate(self) -> float:

        if self.balls == 0:
            return 0.0

        overs_float = self.balls / 6

        return round(
            self.runs / overs_float,
            2
        )

    def to_dict(self):

        return asdict(self)


# ==================================================
# MATCH MODEL
# ==================================================

@dataclass
class Match:

    match_id: Optional[int]

    name: str

    team_a: str

    team_b: str

    overs_limit: int

    status: str = "LIVE"

    winner: str = ""

    toss_winner: str = ""

    toss_decision: str = ""

    current_innings: int = 1

    innings_one: Optional[Innings] = None

    innings_two: Optional[Innings] = None

    created_at: str = field(
        default_factory=lambda:
        datetime.now().isoformat()
    )

    def target(self):

        if self.innings_one:

            return self.innings_one.runs + 1

        return None

    def to_dict(self):

        data = asdict(self)

        return data


# ==================================================
# TOURNAMENT TEAM MODEL
# ==================================================

@dataclass
class Team:

    name: str

    played: int = 0

    won: int = 0

    lost: int = 0

    tied: int = 0

    points: int = 0

    net_run_rate: float = 0.0

    players: List[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(self)


# ==================================================
# TOURNAMENT STANDINGS MODEL
# ==================================================

@dataclass
class PointsTable:

    teams: List[Team] = field(
        default_factory=list
    )

    def sorted_table(self):

        return sorted(
            self.teams,
            key=lambda x: (
                x.points,
                x.net_run_rate
            ),
            reverse=True
        )

    def to_dict(self):

        return [
            team.to_dict()
            for team in self.sorted_table()
        ]
