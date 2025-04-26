from mip import Model, xsum, BINARY, CONTINUOUS, minimize, OptimizationStatus
from aircraft import AircraftLanding
from data_fetcher import fetch_aircraft_data
from print_info import print_solution_info

def time_window_constraint(model: Model, aircraft_landing: AircraftLanding, model_variables):
    for i, landing_time_window in enumerate(aircraft_landing.landing_times):
        model += landing_time_window.earliest <= model_variables["landing_times_decision"][i]
        model += model_variables["landing_times_decision"][i] <= landing_time_window.latest

    return model

def separation_constraint(model: Model, aircraft_landing: AircraftLanding, model_variables):
    runway_assignment = [[model.add_var(var_type=BINARY, name=f"runway_{i}_{r}")
                          for r in range(aircraft_landing.n_runways)]
                         for i in range(aircraft_landing.n_aircraft)]

    landing_order = [[model.add_var(var_type=BINARY, name=f"order_{i}_{j}")
                      for j in range(aircraft_landing.n_aircraft)]
                     for i in range(aircraft_landing.n_aircraft)]

    big_m = 1000
    n_aircraft = aircraft_landing.n_aircraft
    n_runways = aircraft_landing.n_runways
    landing_times_decision = model_variables["landing_times_decision"]

    for i in range(n_aircraft):
        model += xsum(runway_assignment[i][r] for r in range(n_runways)) == 1
    for i in range(n_aircraft):
        for j in range(n_aircraft):
            if i == j:
                model += landing_order[i][j] == 0
            else:
                model += landing_order[i][j] + landing_order[j][i] == 1
    for i in range(n_aircraft):
        for j in range(n_aircraft):
            if i == j:
                continue
            s_ij = aircraft_landing.separation_times[i][j]
            for r in range(n_runways):
                model += (
                    landing_times_decision[j] >= landing_times_decision[i] + s_ij
                    - big_m * (3 - runway_assignment[i][r]
                               - runway_assignment[j][r]
                               - landing_order[i][j])
                )

    return model, runway_assignment, landing_order

def problem_1(aircraft_landing: AircraftLanding):
    model = Model("Minimize Weighted Deviation from Target Landing Times")

    landing_times_decision = [model.add_var(var_type=CONTINUOUS, name=f"landing_time_{i}")
        for i in range(aircraft_landing.n_aircraft)]

    early_penalty = [model.add_var(var_type=CONTINUOUS, name=f"early_penalty_{i}")
        for i in range(aircraft_landing.n_aircraft)]
    late_penalty = [model.add_var(var_type=CONTINUOUS, name=f"late_penalty_{i}")
        for i in range(aircraft_landing.n_aircraft)]

    for landing_time_index, landing_time in enumerate(aircraft_landing.landing_times):
        model += early_penalty[landing_time_index] >= landing_time.target - landing_times_decision[landing_time_index]
        model += late_penalty[landing_time_index] >= landing_times_decision[landing_time_index] - landing_time.target

        model += early_penalty[landing_time_index] >= 0
        model += late_penalty[landing_time_index] >= 0

    model_variables = {"landing_times_decision": landing_times_decision}

    model, runway_assignment, landing_order = separation_constraint(
        model, aircraft_landing, model_variables
    )

    model = time_window_constraint(model, aircraft_landing, model_variables)

    model.objective = minimize(xsum(
        lt.penalty_cost_before_target * early_penalty[i] +
        lt.penalty_cost_after_target * late_penalty[i]
        for i, lt in enumerate(aircraft_landing.landing_times)
    ))

    status =  model.optimize(max_seconds=2)

    model_variables = {"landing_times_decision": landing_times_decision, "early_penalty": early_penalty,
                       "late_penalty": late_penalty, "runway_assignment": runway_assignment, "landing_order": landing_order}
    return status, model_variables


def problem_2(aircraft_landing: AircraftLanding):
    model = Model("Minimizing Makespan")

    landing_times_decision = [model.add_var(var_type=CONTINUOUS, name=f"landing_time_{i}")
                              for i in range(aircraft_landing.n_aircraft)]

    makespan = model.add_var(var_type=CONTINUOUS, name="makespan")

    for i, lt in enumerate(aircraft_landing.landing_times):
        model += makespan >= landing_times_decision[i]

    model_variables = {"landing_times_decision": landing_times_decision}

    model, runway_assignment, landing_order = separation_constraint(
        model, aircraft_landing, model_variables
    )

    model = time_window_constraint(model, aircraft_landing, model_variables)

    model.objective = minimize(makespan)

    status = model.optimize(max_seconds=2)

    model_variables = {"landing_times_decision": landing_times_decision, "makespan": makespan,
                       "runway_assignment": runway_assignment, "landing_order": landing_order}
    return status, model_variables


def problem_3(aircraft_landing: AircraftLanding):
    model = Model("Minimizing Total Lateness with Runway Assignment")

    ## TODO Solve problem 3

    return model.optimize(max_seconds=2)


data = fetch_aircraft_data()[0]
data.n_runways = 1

status, model_vars = problem_1(data)
print_solution_info(status, model_vars)