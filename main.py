import argparse

from mip import Model, xsum, BINARY, CONTINUOUS, minimize
from aircraft import AircraftLanding
from data_fetcher import fetch_aircraft_data
from export_result import export_solution_info_json, summarize_all_results_to_csv


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

    n_aircraft = aircraft_landing.n_aircraft
    n_runways = aircraft_landing.n_runways
    separation_times = aircraft_landing.separation_times
    landing_time_decision = model_variables["landing_times_decision"]
    earliest = min(t.earliest for t in aircraft_landing.landing_times)
    latest = max(t.latest for t in aircraft_landing.landing_times)
    max_sep = max(separation_times[i][j] for i in range(n_aircraft)
                  for j in range(n_aircraft) if i != j)
    big_m = (latest - earliest) + max_sep

    runway_assignment = model.add_var_tensor((n_aircraft, n_runways),
                                             var_type=BINARY,
                                             name="runway")

    landing_order = model.add_var_tensor((n_aircraft, n_aircraft),
                                  var_type=BINARY,
                                  name="order")

    for i in range(n_aircraft):
        model.add_constr(
            xsum([landing_order[i, i]]) == 0,
            name=f"no_self_order_{i}"
        )
        for j in range(i + 1, n_aircraft):
            model.add_constr(
                xsum([landing_order[i, j], landing_order[j, i]]) == 1,
                name=f"order_xor_{i}_{j}"
            )

    for i in range(n_aircraft):
        model.add_constr(
            xsum(runway_assignment[i, r] for r in range(n_runways)) == 1,
            name=f"assign_runway_{i}"
        )

    for i in range(n_aircraft):
        for j in range(n_aircraft):
            if i == j:
                continue
            sep_ij = separation_times[i][j]
            for r in range(n_runways):
                model.add_constr(
                    landing_time_decision[j]
                    >= landing_time_decision[i] + sep_ij
                    - big_m * (3
                               - runway_assignment[i, r]
                               - runway_assignment[j, r]
                               - landing_order[i, j]),
                    name=f"sep_{i}_{j}_runway{r}"
                )

    return model, runway_assignment, landing_order

def problem_1(aircraft_landing: AircraftLanding, max_problem_time):
    """
    Solves Problem 1: Minimize weighted deviation from target landing times.

    Args:
        aircraft_landing (AircraftLanding): The problem instance.
        max_problem_time (int): The maximum time to spend on each problem in seconds.

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

    status =  model.optimize(max_seconds=max_problem_time)

    model_variables = {"landing_times_decision": landing_times_decision, "early_penalty": early_penalty,
                       "late_penalty": late_penalty, "runway_assignment": runway_assignment, "landing_order": landing_order}
    return status, model_variables

def problem_2(aircraft_landing: AircraftLanding, max_problem_time):
    """
    Solves Problem 2: Minimize the makespan (latest landing time).

    Args:
        aircraft_landing (AircraftLanding): The problem instance.
        max_problem_time (int): The maximum time to spend on each problem in seconds.

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

    status = model.optimize(max_seconds=max_problem_time)

    model_variables = {"landing_times_decision": landing_times_decision, "makespan": makespan,
                       "runway_assignment": runway_assignment, "landing_order": landing_order}
    return status, model_variables

def problem_3(aircraft_landing: AircraftLanding, max_problem_time):
    """
    Solves Problem 3: Minimize total lateness including parking delays.

    Args:
        aircraft_landing (AircraftLanding): The problem instance.
        max_problem_time (int): The maximum time to spend on each problem in seconds.

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

    status = model.optimize(max_seconds=max_problem_time)

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
    - max_time (optional): The maximum time to spend on each problem in seconds (default is 60).
    """

    parser = argparse.ArgumentParser(description="Run aircraft landing problem optimization and export results.")
    parser.add_argument("seed", type=int, help="Random seed for the datasets.")
    parser.add_argument("n_runways", type=int, help="Number of runways for the optimization.")
    parser.add_argument("--n_files", type=int, default=12, help="Number of files to check (default is 12).")
    parser.add_argument("--max_time", type=int, default=60, help="Maximum time to spend on each problem in seconds (default is 60).")
    args = parser.parse_args()

    for i in range(min(args.n_files, 12)):
        data[i].seed = args.seed
        data[i].n_runways = args.n_runways
        max_time = args.max_time
        data_status, model_vars = problem_1(data[i], max_time)
        export_solution_info_json(data[i], data_status, model_vars, f"problem1/result_{i + 1}_{args.seed}_{args.n_runways}")
        data_status, model_vars = problem_2(data[i], max_time)
        export_solution_info_json(data[i], data_status, model_vars, f"problem2/result_{i + 1}_{args.seed}_{args.n_runways}")
        data_status, model_vars = problem_3(data[i], max_time)
        export_solution_info_json(data[i], data_status, model_vars, f"problem3/result_{i + 1}_{args.seed}_{args.n_runways}")

if __name__ == "__main__":
    main()