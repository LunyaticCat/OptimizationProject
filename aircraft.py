from typing import List
from mip import Model, xsum, BINARY, CONTINUOUS, minimize, OptimizationStatus


class LandingTime:
    """
    Represents the landing time window for an aircraft.

    Attributes:
        earliest (int): Earliest allowable landing time.
        latest (int): Latest allowable landing time.
    """

    def __init__(self, earliest: int, latest: int):
        if earliest > latest:
            raise ValueError("Earliest landing time cannot be later than latest")
        self.earliest = earliest
        self.latest = latest


class AircraftLanding:
    """
    Represents an aircraft landing problem.

    Args:
        n_aircraft (int): Number of aircraft.
        n_runways (int): Number of runways.
        landing_times (List[LandingTime]): A list of LandingTime objects, one per aircraft.
        separation_times (List[List[int]]): A matrix representing separation times between aircraft.
    """

    def __init__(self,
                 n_aircraft: int,
                 n_runways: int,
                 landing_times: List[LandingTime],
                 separation_times: List[List[int]]):
        if n_aircraft != len(landing_times):
            raise ValueError("There must be a landing time for each aircraft.")
        self.n_aircraft = n_aircraft
        self.n_runways = n_runways
        self.landing_times = landing_times
        self.separation_times = separation_times


def solver(aircraft_landing: AircraftLanding):
    model = Model("Aircraft Landing")

    # Decision variables
    x = [model.add_var(var_type=CONTINUOUS, name=f"x_{i}")
         for i in range(aircraft_landing.n_aircraft)]

    # Time Window Constraints
    for i, lt in enumerate(aircraft_landing.landing_times):
        model += lt.earliest <= x[i]
        model += x[i] <= lt.latest

    # TODO add other constraints

    status = model.optimize(max_seconds=2)
    print("Status: ", OptimizationStatus(status))
    if status in (OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE):
        for i in range(aircraft_landing.n_aircraft):
            print(f"Aircraft {i + 1} lands at time {x[i].x:.2f}")



n = 5
m = 2
landing_times = [LandingTime(earliest, latest)
                 for earliest, latest in zip([10, 15, 20, 30, 35],
                                             [30, 40, 50, 60, 70])]
s = [
    [0, 3, 4, 5, 6],
    [3, 0, 2, 4, 5],
    [4, 2, 0, 3, 4],
    [5, 4, 3, 0, 2],
    [6, 5, 4, 2, 0]
]

aircraft_landing = AircraftLanding(n_aircraft=n, n_runways=m, landing_times=landing_times, separation_times=s)
solver(aircraft_landing)
