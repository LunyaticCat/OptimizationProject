import random
from typing import List

class LandingTime:
    """
    Represents the landing time window for an aircraft.

    Attributes:
        appearance_time (int)
        earliest (int): Earliest allowable landing time.
        target (int): Target time for the aircraft.
        latest (int): Latest allowable landing time.
        penalty_cost_before_target (int): penalty cost per unit of time for landing before target.
        penalty_cost_after_target (int): penalty cost per unit of time for landing after target.
    """

    def __init__(self, appearance_time: int, earliest: int, target:int, latest: int, penalty_cost_before_target: int = 0, penalty_cost_after_target: int = 0):
        if not earliest <= target <= latest:
            raise ValueError(f"Earliest landing time cannot be later than latest, got {earliest} {target} {latest}")
        self.appearance_time = appearance_time
        self.earliest = earliest
        self.target = target
        self.latest = latest
        self.penalty_cost_before_target = penalty_cost_before_target
        self.penalty_cost_after_target = penalty_cost_after_target

    def __str__(self):
        return (f"LandingTime(appearance_time={self.appearance_time}, "
                f"earliest={self.earliest}, target={self.target}, latest={self.latest}, "
                f"penalty_cost_before_target={self.penalty_cost_before_target}, "
                f"penalty_cost_after_target={self.penalty_cost_after_target})")

    def __repr__(self):
        return (f"LandingTime(appearance_time={self.appearance_time!r}, "
                f"earliest={self.earliest!r}, target={self.target!r}, latest={self.latest!r}, "
                f"penalty_cost_before_target={self.penalty_cost_before_target!r}, "
                f"penalty_cost_after_target={self.penalty_cost_after_target!r})")


import random
from typing import List
from aircraft import LandingTime  # assuming this is defined elsewhere

class AircraftLanding:
    """
    Represents an aircraft landing problem.

    Args:
        n_aircraft (int): Number of aircraft.
        n_runways (int): Number of runways.
        freeze_time (int): Time period during which no changes can be made.
        landing_times (List[LandingTime]): A list of LandingTime objects, one per aircraft.
        separation_times (List[List[int]]): A matrix representing separation times between aircraft.
        seed (int, optional): A random seed to ensure reproducibility of generated parameters.
    """

    def __init__(self,
                 n_aircraft: int,
                 n_runways: int,
                 freeze_time: int,
                 landing_times: List[LandingTime],
                 separation_times: List[List[int]],
                 seed: int = None):
        if n_aircraft != len(landing_times):
            raise ValueError(
                f"There must be a landing time for each aircraft. Got {len(landing_times)} instead of {n_aircraft}")

        self.n_aircraft = n_aircraft
        self.n_runways = n_runways
        self.freeze_time = freeze_time
        self.landing_times = landing_times
        self.separation_times = separation_times
        self.seed = seed

    @property
    def t_ir(self):
        """
        Dynamic property of a matrix where t_ir[i][r] is the time for aircraft i
        to reach parking after landing on runway r. Values are generated
        deterministically using the provided seed.
        """
        rng = random.Random(self.seed)
        t_ir_matrix = []
        for landing_time in self.landing_times:
            t_i = landing_time.target
            e_i = landing_time.earliest
            max_travel = max(1, t_i - e_i)
            t_ir_i = [rng.randint(1, max_travel) for _ in range(self.n_runways)]
            t_ir_matrix.append(t_ir_i)
        return t_ir_matrix

    def __str__(self):
        return (f"AircraftLanding(n_aircraft={self.n_aircraft}, n_runways={self.n_runways}, "
                f"freeze_time={self.freeze_time}, "
                f"landing_times={self.landing_times}, "
                f"separation_times={self.separation_times}, "
                f"t_ir={self.t_ir})")

    def __repr__(self):
        return (f"AircraftLanding(n_aircraft={self.n_aircraft!r}, n_runways={self.n_runways!r}, "
                f"freeze_time={self.freeze_time!r}, "
                f"landing_times={self.landing_times!r}, "
                f"separation_times={self.separation_times!r}, "
                f"t_ir={self.t_ir!r})")
