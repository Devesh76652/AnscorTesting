# scoring.py
from copy import deepcopy
from modules.models import (
    Batter,
    Bowler,
    BallEvent,
    FallOfWicket
)

# =====================================================
# SCORING ENGINE
# =====================================================

class ScoringEngine:

    def __init__(self, innings):

        self.innings = innings

        self.undo_stack = []

        self.striker = None
        self.non_striker = None

        self.current_bowler = None

    # =================================================
    # SET PLAYERS
    # =================================================

    def set_batters(
        self,
        striker: Batter,
        non_striker: Batter
    ):

        striker.strike = True
        non_striker.strike = False

        self.striker = striker
        self.non_striker = non_striker

    def set_bowler(
        self,
        bowler: Bowler
    ):

        self.current_bowler = bowler

    # =================================================
    # UNDO
    # =================================================

    def save_state(self):

        self.undo_stack.append(
            deepcopy(self.innings)
        )

        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def undo(self):

        if not self.undo_stack:
            return None

        self.innings = self.undo_stack.pop()

        return self.innings

    # =================================================
    # HELPERS
    # =================================================

    def rotate_strike(self):

        self.striker.strike = False
        self.non_striker.strike = True

        self.striker, self.non_striker = (
            self.non_striker,
            self.striker
        )

    def current_over(self):

        return (
            self.innings.balls // 6,
            self.innings.balls % 6
        )

    # =================================================
    # BALL EVENT
    # =================================================

    def add_ball_event(
        self,
        runs=0,
        extra_type="",
        wicket=False,
        description=""
    ):

        over_no = self.innings.balls // 6

        ball_no = (self.innings.balls % 6) + 1

        event = BallEvent(
            innings_no=self.innings.innings_no,
            over_no=over_no,
            ball_no=ball_no,
            batter=self.striker.name,
            bowler=self.current_bowler.name,
            runs=runs,
            extra_type=extra_type,
            wicket=wicket,
            description=description
        )

        return event

    # =================================================
    # NORMAL RUNS
    # =================================================

    def score_runs(
        self,
        runs
    ):

        self.save_state()

        self.innings.runs += runs
        self.innings.balls += 1

        self.striker.runs += runs
        self.striker.balls += 1

        self.current_bowler.runs_conceded += runs
        self.current_bowler.balls += 1

        if runs == 4:
            self.striker.fours += 1

        if runs == 6:
            self.striker.sixes += 1

        self.innings.current_over.append(
            str(runs)
        )

        if runs % 2 == 1:
            self.rotate_strike()

        self._complete_over_check()

        return self.add_ball_event(
            runs=runs
        )

    # =================================================
    # DOT BALL
    # =================================================

    def dot_ball(self):

        self.save_state()

        self.innings.balls += 1

        self.striker.balls += 1

        self.current_bowler.balls += 1

        self.innings.current_over.append("•")

        self._complete_over_check()

        return self.add_ball_event(
            runs=0
        )

    # =================================================
    # WIDE
    # =================================================

    def wide(
        self,
        runs=1
    ):

        self.save_state()

        self.innings.runs += runs
        self.innings.extras += runs

        self.current_bowler.runs_conceded += runs

        self.innings.current_over.append(
            f"WD{runs}"
        )

        return self.add_ball_event(
            runs=runs,
            extra_type="WD"
        )

    # =================================================
    # NO BALL
    # =================================================

    def no_ball(
        self,
        bat_runs=0
    ):

        self.save_state()

        total = 1 + bat_runs

        self.innings.runs += total
        self.innings.extras += 1

        self.current_bowler.runs_conceded += total

        self.striker.runs += bat_runs

        if bat_runs == 4:
            self.striker.fours += 1

        if bat_runs == 6:
            self.striker.sixes += 1

        self.innings.current_over.append(
            f"NB+{bat_runs}"
        )

        return self.add_ball_event(
            runs=total,
            extra_type="NB"
        )

    # =================================================
    # BYE
    # =================================================

    def bye(
        self,
        runs
    ):

        self.save_state()

        self.innings.runs += runs
        self.innings.extras += runs

        self.innings.balls += 1

        self.current_bowler.balls += 1

        self.striker.balls += 1

        self.innings.current_over.append(
            f"B{runs}"
        )

        if runs % 2 == 1:
            self.rotate_strike()

        self._complete_over_check()

        return self.add_ball_event(
            runs=runs,
            extra_type="BYE"
        )

    # =================================================
    # LEG BYE
    # =================================================

    def leg_bye(
        self,
        runs
    ):

        self.save_state()

        self.innings.runs += runs
        self.innings.extras += runs

        self.innings.balls += 1

        self.current_bowler.balls += 1

        self.striker.balls += 1

        self.innings.current_over.append(
            f"LB{runs}"
        )

        if runs % 2 == 1:
            self.rotate_strike()

        self._complete_over_check()

        return self.add_ball_event(
            runs=runs,
            extra_type="LB"
        )

    # =================================================
    # WICKET
    # =================================================

    def wicket(
        self,
        dismissal="Bowled"
    ):

        self.save_state()

        self.innings.wickets += 1

        self.innings.balls += 1

        self.striker.balls += 1

        self.current_bowler.balls += 1
        self.current_bowler.wickets += 1

        self.striker.dismissal = dismissal

        self.innings.current_over.append("W")

        fow = FallOfWicket(
            wicket_no=self.innings.wickets,
            score=f"{self.innings.runs}/{self.innings.wickets}",
            batter=self.striker.name,
            over=self.innings.overs()
        )

        self.innings.fall_of_wickets.append(
            fow.to_dict()
        )

        self._complete_over_check()

        return self.add_ball_event(
            wicket=True,
            description=dismissal
        )

    # =================================================
    # RETIRED OUT
    # =================================================

    def retired_out(self):

        self.striker.dismissal = "Retired Out"

        self.innings.wickets += 1

    # =================================================
    # COMPLETE OVER
    # =================================================

    def _complete_over_check(self):

        if self.innings.balls % 6 == 0:

            over_text = " ".join(
                self.innings.current_over
            )

            self.innings.over_history.append({

                "over":
                    len(
                        self.innings.over_history
                    ) + 1,

                "score":
                    f"{self.innings.runs}/"
                    f"{self.innings.wickets}",

                "timeline":
                    over_text
            })

            self.innings.current_over = []

            self.rotate_strike()

    # =================================================
    # TARGET CHECK
    # =================================================

    @staticmethod
    def chase_completed(
        innings,
        target
    ):

        return innings.runs >= target

    # =================================================
    # INNINGS COMPLETE
    # =================================================

    @staticmethod
    def innings_completed(
        innings,
        max_overs
    ):

        all_out = innings.wickets >= 10

        overs_done = (
            innings.balls >=
            (max_overs * 6)
        )

        return all_out or overs_done

    # =================================================
    # RESULT ENGINE
    # =================================================

    @staticmethod
    def calculate_result(
        first_innings,
        second_innings,
        team_a,
        team_b
    ):

        target = first_innings.runs + 1

        if second_innings.runs >= target:

            wickets_left = (
                10 - second_innings.wickets
            )

            return (
                f"{team_b} won by "
                f"{wickets_left} wickets"
            )

        margin = (
            first_innings.runs -
            second_innings.runs
        )

        if margin > 0:

            return (
                f"{team_a} won by "
                f"{margin} runs"
            )

        return "Match Tied"

    # =================================================
    # RUN RATE
    # =================================================

    @staticmethod
    def run_rate(
        runs,
        balls
    ):

        if balls == 0:
            return 0.0

        return round(
            runs / (balls / 6),
            2
        )

    # =================================================
    # REQUIRED RUN RATE
    # =================================================

    @staticmethod
    def required_run_rate(
        target,
        current_runs,
        balls_remaining
    ):

        if balls_remaining <= 0:
            return 0.0

        runs_needed = (
            target - current_runs
        )

        return round(
            runs_needed /
            (balls_remaining / 6),
            2
        )
