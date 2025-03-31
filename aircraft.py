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


from mip import Constr

def solver(aircraft_landing: AircraftLanding):
    model = Model("Aircraft Landing")

    # Decision variables
    landing_times_decision = [model.add_var(var_type=CONTINUOUS, name=f"landing_time_{i}")
                               for i in range(aircraft_landing.n_aircraft)]

    runway_assignment = [[model.add_var(var_type=BINARY, name=f"runway_{i}_{r}")
                          for r in range(aircraft_landing.n_runways)]
                         for i in range(aircraft_landing.n_aircraft)]

    landing_order = [[model.add_var(var_type=BINARY, name=f"order_{i}_{j}")
                      for j in range(aircraft_landing.n_aircraft)]
                     for i in range(aircraft_landing.n_aircraft)]

    big_number_variable = 1000

    # Time Window Constraints
    for i, landing_time_window in enumerate(aircraft_landing.landing_times):
        model += landing_time_window.earliest <= landing_times_decision[i]
        model += landing_times_decision[i] <= landing_time_window.latest

    # Each aircraft is assigned to exactly one runway
    for i in range(aircraft_landing.n_aircraft):
        model += xsum(runway_assignment[i][r] for r in range(aircraft_landing.n_runways)) == 1

    # Separation Constraints: If aircraft i and j land on the same runway, enforce separation
    for i in range(aircraft_landing.n_aircraft):
        for j in range(i + 1, aircraft_landing.n_aircraft):
            for r in range(aircraft_landing.n_runways):
                if aircraft_landing.separation_times[i][j] > 0:
                    model += landing_times_decision[i] + aircraft_landing.separation_times[i][j] <= landing_times_decision[j] + \
                             (1 - landing_order[i][j]) * big_number_variable
                    model += landing_times_decision[j] + aircraft_landing.separation_times[j][i] <= landing_times_decision[i] + \
                             landing_order[i][j] * big_number_variable
                    model += runway_assignment[i][r] + runway_assignment[j][r] <= 1 + landing_order[i][j]

    status = model.optimize(max_seconds=2)
    print("Status: ", OptimizationStatus(status))
    if status in (OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE):
        for i in range(aircraft_landing.n_aircraft):
            assigned_runway = next(r for r in range(aircraft_landing.n_runways) if runway_assignment[i][r].x >= 1)
            print(f"Aircraft {i + 1} lands at time {landing_times_decision[i].x:.2f} on runway {assigned_runway + 1}")


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
