import json
from mip import OptimizationStatus
import re


def export_solution_info_json(aircraft_landing_problem, status, model_variables, filename):
    """
    Export solution and problem information to a JSON file, including status messages when infeasible.

    Args:
        aircraft_landing_problem (AircraftLanding): Problem instance containing input data.
        status (OptimizationStatus): The solver status.
        model_variables (dict): Dictionary containing variable lists:
            - landing_times_decision
            - early_penalty
            - late_penalty
            - makespan
            - runway_assignment
            - landing_order
        filename (str): Output file path (without extension).
    """
    data = {
        'status': status.name,
        'landing_times': [],
        'penalties': [],
        'makespan': None,
        'runway_assignments': [],
        'landing_order': []
    }

    aircraft = []
    for lt in aircraft_landing_problem.landing_times:
        aircraft.append({
            'appearance_time': lt.appearance_time,
            'earliest': lt.earliest,
            'target': lt.target,
            'latest': lt.latest,
            'penalty_cost_before_target': lt.penalty_cost_before_target,
            'penalty_cost_after_target': lt.penalty_cost_after_target
        })
    data['aircraft_data'] = {
        'n_aircraft': aircraft_landing_problem.n_aircraft,
        'n_runways': aircraft_landing_problem.n_runways,
        'freeze_time': aircraft_landing_problem.freeze_time,
        'landing_times': aircraft,
        'separation_times': aircraft_landing_problem.separation_times,
        't_ir': aircraft_landing_problem.t_ir
    }

    if status in (OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE):
        for var in model_variables.get('landing_times_decision', []):
            data['landing_times'].append(round(var.x, 2))

        early = model_variables.get('early_penalty', [])
        late = model_variables.get('late_penalty', [])
        if early and late:
            for e, l in zip(early, late):
                data['penalties'].append({'early': round(e.x, 2), 'late': round(l.x, 2)})

        makespan_var = model_variables.get('makespan')
        if makespan_var is not None:
            data['makespan'] = round(makespan_var.x, 2)

        for assignments in model_variables.get('runway_assignment', []):
            assigned = [i for i, var in enumerate(assignments) if var.x >= 0.99]
            data['runway_assignments'].append(assigned[0] if assigned else None)

        for row in model_variables.get('landing_order', []):
            data['landing_order'].append([int(var.x + 0.5) for var in row])
    else:
        data['message'] = 'No feasible or optimal solution found.'

    # Generate JSON string with indent
    json_str = json.dumps(data, indent=4)

    # Collapse numeric lists onto one line
    # Matches any list of numbers or simple values
    pattern = re.compile(r"\[\s*([-?\d+\., \n]+?)\s*\]")
    def inline_lists(match):
        items = match.group(1)
        # split on commas or whitespace
        parts = re.split(r',\s*', items.replace('\n', ' '))
        compact = ', '.join(p.strip() for p in parts if p)
        return f"[{compact}]"

    json_str = pattern.sub(inline_lists, json_str)

    # Write to JSON file
    out_path = f"results/{filename}.json"
    with open(out_path, 'w') as f:
        f.write(json_str)
    print(f"Solution export completed: {out_path}")
