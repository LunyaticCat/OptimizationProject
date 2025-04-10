from mip import Model, xsum, BINARY, CONTINUOUS, minimize, OptimizationStatus
from aircraft import AircraftLanding, LandingTime
from data_fetcher import fetch_aircraft_data

def solver(aircraft_landing: AircraftLanding, additional_constraints: Model = None):
    if additional_constraints is None:
        model = Model("Aircraft Landing")
    else:
        model = additional_constraints

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

def problem_1(aircraft_landing: AircraftLanding):
    model = Model("Minimizing Weighted Delay with Target Landing Times")

    # Decision variables
    landing_times_decision = [model.add_var(var_type=CONTINUOUS, name=f"landing_time_{i}")
                               for i in range(aircraft_landing.n_aircraft)]
    early_penalty = [model.add_var(var_type=CONTINUOUS, name=f"early_penalty_{i}")
                     for i in range(aircraft_landing.n_aircraft)]
    late_penalty = [model.add_var(var_type=CONTINUOUS, name=f"late_penalty_{i}")
                    for i in range(aircraft_landing.n_aircraft)]

    target_times = [(lt.earliest + lt.latest) // 2 for lt in aircraft_landing.landing_times]
    early_landing_weight = [1] * aircraft_landing.n_aircraft  # Weight for early landing
    late_landing_weight = [1] * aircraft_landing.n_aircraft   # Weight for late landing

    # Penalty Constraints
    for i in range(aircraft_landing.n_aircraft):
        model += early_penalty[i] >= target_times[i] - landing_times_decision[i]
        model += late_penalty[i] >= landing_times_decision[i] - target_times[i]
        model += early_penalty[i] >= 0
        model += late_penalty[i] >= 0

    model.objective = minimize(xsum(early_landing_weight[i] * early_penalty[i] + late_landing_weight[i] * late_penalty[i]
                                    for i in range(aircraft_landing.n_aircraft)))

    solver(aircraft_landing, model)

def problem_2(aircraft_landing: AircraftLanding):
    model = Model("Minimizing Makespan")

    # Decision variables

    ## TODO Solve problem 2

    solver(aircraft_landing, model)

def problem_3(aircraft_landing: AircraftLanding):
    model = Model("Minimizing Total Lateness with Runway Assignment")

    # Decision variables

    ## TODO Solve problem 3

    solver(aircraft_landing, model)

data = fetch_aircraft_data()[0]

solver(data)