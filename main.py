import argparse

from mip import Model, xsum, BINARY, CONTINUOUS, minimize
from aircraft import AircraftLanding
from data_fetcher import fetch_aircraft_data
from export_result import export_solution_info_json

def time_window_constraint(model: Model, aircraft_landing: AircraftLanding, model_variables):
    """
    Adds time window constraints for each aircraft's landing.

    Args:
        model (Model): The optimization model.
        aircraft_landing (AircraftLanding): The problem instance.
        model_variables (dict): Dictionary containing decision variables.

    Returns:
        Model: The updated model with time window constraints added.
    """
    for i, landing_time_window in enumerate(aircraft_landing.landing_times):
        model += landing_time_window.earliest <= model_variables["landing_times_decision"][i]
        model += model_variables["landing_times_decision"][i] <= landing_time_window.latest

    return model

def separation_constraint(model: Model, aircraft_landing: AircraftLanding, model_variables):
    """
    Adds runway separation and ordering constraints between aircraft.

    Args:
        model (Model): The optimization model.
        aircraft_landing (AircraftLanding): The problem instance.
        model_variables (dict): Dictionary containing decision variables.

    Returns:
        Tuple[Model, List[List[Var]], List[List[Var]]]: The updated model,
            runway assignment variables, and landing order variables.
    """
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
    """
    Solves Problem 1: Minimize weighted deviation from target landing times.

    Args:
        aircraft_landing (AircraftLanding): The problem instance.

    Returns:
        Tuple[str, dict]: The solver status and model variables.
    """
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
    """
    Solves Problem 2: Minimize the makespan (latest landing time).

    Args:
        aircraft_landing (AircraftLanding): The problem instance.

    Returns:
        Tuple[str, dict]: The solver status and model variables.
    """
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
    """
    Solves Problem 3: Minimize total lateness including parking delays.

    Args:
        aircraft_landing (AircraftLanding): The problem instance.

    Returns:
        Tuple[str, dict]: The solver status and model variables.
    """
    model = Model("Minimizing Total Lateness with Runway Assignment")

    landing_times_decision = [model.add_var(var_type=CONTINUOUS, name=f"landing_time_{i}")
                              for i in range(aircraft_landing.n_aircraft)]

    lateness = [model.add_var(var_type=CONTINUOUS, name=f"lateness_{i}")
                for i in range(aircraft_landing.n_aircraft)]

    model_variables = {"landing_times_decision": landing_times_decision}

    model, runway_assignment, landing_order = separation_constraint(
        model, aircraft_landing, model_variables
    )

    model = time_window_constraint(model, aircraft_landing, model_variables)

    n_aircraft = aircraft_landing.n_aircraft
    n_runways = aircraft_landing.n_runways
    t_ir = aircraft_landing.t_ir
    a_i = [lt.target for lt in aircraft_landing.landing_times]

    for i in range(n_aircraft):
        model += lateness[i] >= xsum(
            landing_times_decision[i] + t_ir[i][r] * runway_assignment[i][r]
            for r in range(n_runways)
        ) - a_i[i]

    model.objective = minimize(xsum(lateness))

    status = model.optimize(max_seconds=2)

    model_variables = {"landing_times_decision": landing_times_decision, "lateness": lateness,
                       "runway_assignment": runway_assignment, "landing_order": landing_order}
    return status, model_variables

data = fetch_aircraft_data()

def main():
    """
    Main entry point for solving aircraft landing problem optimization and exporting results.

    Command-line arguments:
    - seed: A random seed integer to initialize the datasets.
    - n_runways: The number of runways to be used in the optimization problem.
    - n_files (optional): The number of files to check (default is 12, mainly use for fast unit testing).
    """

    parser = argparse.ArgumentParser(description="Run aircraft landing problem optimization and export results.")
    parser.add_argument("seed", type=int, help="Random seed for the datasets.")
    parser.add_argument("n_runways", type=int, help="Number of runways for the optimization.")
    parser.add_argument("--n_files", type=int, default=12, help="Number of files to check (default is 12).")
    args = parser.parse_args()

    for i in range(min(args.n_files, 12)):
        data[i].seed = args.seed
        data[i].n_runways = args.n_runways
        data_status, model_vars = problem_1(data[i])
        export_solution_info_json(data[i], data_status, model_vars, f"problem1/result_{i + 1}_{args.seed}_{args.n_runways}")
        data_status, model_vars = problem_2(data[i])
        export_solution_info_json(data[i], data_status, model_vars, f"problem2/result_{i + 1}_{args.seed}_{args.n_runways}")
        data_status, model_vars = problem_3(data[i])
        export_solution_info_json(data[i], data_status, model_vars, f"problem3/result_{i + 1}_{args.seed}_{args.n_runways}")


if __name__ == "__main__":
    main()