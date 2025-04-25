from mip import Model, xsum, BINARY, CONTINUOUS, minimize, OptimizationStatus
from aircraft import AircraftLanding
from data_fetcher import fetch_aircraft_data

def time_window_constraint(model: Model, aircraft_landing: AircraftLanding):
    landing_times_decision = [model.add_var(var_type=CONTINUOUS, name=f"landing_time_{i}")
                              for i in range(aircraft_landing.n_aircraft)]

    for i, landing_time_window in enumerate(aircraft_landing.landing_times):
        model += landing_time_window.earliest <= landing_times_decision[i]
        model += landing_times_decision[i] <= landing_time_window.latest

    return model

def separation_constraint(model: Model, aircraft_landing: AircraftLanding):
    runway_assignment = [[model.add_var(var_type=BINARY, name=f"runway_{i}_{r}")
                          for r in range(aircraft_landing.n_runways)]
                         for i in range(aircraft_landing.n_aircraft)]

    landing_order = [[model.add_var(var_type=BINARY, name=f"order_{i}_{j}")
                      for j in range(aircraft_landing.n_aircraft)]
                     for i in range(aircraft_landing.n_aircraft)]

    big_m = 1000

    # Each aircraft is assigned to exactly one runway
    for i in range(aircraft_landing.n_aircraft):
        model += xsum(runway_assignment[i][r] for r in range(aircraft_landing.n_runways)) == 1

    ## TODO Separation constraint
    return model

def problem_1(aircraft_landing: AircraftLanding):
    model = Model("Minimize Weighted Deviation from Target Landing Times")

    landing_times_decision = [model.add_var(var_type=CONTINUOUS, name=f"landing_time_{i}")
        for i in range(aircraft_landing.n_aircraft)]

    early_penalty = [model.add_var(var_type=CONTINUOUS, name=f"early_penalty_{i}")
        for i in range(aircraft_landing.n_aircraft)]
    late_penalty = [model.add_var(var_type=CONTINUOUS, name=f"late_penalty_{i}")
        for i in range(aircraft_landing.n_aircraft)]

    for landing_time_index, landing_time in enumerate(aircraft_landing.landing_times):
        model += landing_times_decision[landing_time_index] >= landing_time.earliest
        model += landing_times_decision[landing_time_index] <= landing_time.latest

        model += early_penalty[landing_time_index] >= landing_time.target - landing_times_decision[landing_time_index]
        model += late_penalty[landing_time_index] >= landing_times_decision[landing_time_index] - landing_time.target

        model += early_penalty[landing_time_index] >= 0
        model += late_penalty[landing_time_index] >= 0

    model = separation_constraint(model, aircraft_landing)
    model = time_window_constraint(model, aircraft_landing)

    model.objective = minimize(xsum(
        lt.penalty_cost_before_target * early_penalty[i] +
        lt.penalty_cost_after_target * late_penalty[i]
        for i, lt in enumerate(aircraft_landing.landing_times)
    ))

    return model.optimize(max_seconds=2)


def problem_2(aircraft_landing: AircraftLanding):
    model = Model("Minimizing Makespan")

    landing_times = [
        model.add_var(var_type=CONTINUOUS, name=f"landing_time_{i}")
        for i in range(aircraft_landing.n_aircraft)
    ]

    makespan = model.add_var(var_type=CONTINUOUS, name="makespan")

    for i, lt in enumerate(aircraft_landing.landing_times):
        model += landing_times[i] >= lt.earliest
        model += landing_times[i] <= lt.latest

        model += makespan >= landing_times[i]

    model = separation_constraint(model, aircraft_landing)
    model = time_window_constraint(model, aircraft_landing)

    model.objective = minimize(makespan)

    return model.optimize(max_seconds=2)


def problem_3(aircraft_landing: AircraftLanding):
    model = Model("Minimizing Total Lateness with Runway Assignment")

    ## TODO Solve problem 3

    return model.optimize(max_seconds=2)


data = fetch_aircraft_data()[0]
data.n_runways = 1
print(OptimizationStatus(problem_2(data)))