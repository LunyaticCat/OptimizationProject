import csv
import glob
import json
import os

from mip import OptimizationStatus
import re
from tabulate import tabulate


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
            - lateness
            - total_penalty
            - runway_assignment
            - landing_order
        filename (str): Output file path (without extension).
    """
    data = {
        'status': status.name,
        'landing_times': [],
        'penalties': [],
        'makespan': None,
        'lateness': None,
        'total_penalty': None,
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

        lateness_var = model_variables.get('lateness')
        if lateness_var is not None:
            data['lateness'] = round(lateness_var.x, 2)

        total_penalty_var = model_variables.get('total_penalty')
        if total_penalty_var is not None:
            data['total_penalty'] = round(total_penalty_var.x, 2)

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


import os
import json
import glob
import csv

def summarize_all_results_to_csv(result_folder='results', problems=(1, 2, 3), output_file='summary.csv'):
    """
    Summarize structured solution results from multiple files in each problem folder and write to a CSV file.
    The output can be copied to Google Sheets. Results are sorted by result number and problem number.

    Args:
        result_folder (str): Base folder containing problem subdirectories.
        problems (tuple): Problem indices to scan and summarize.
        output_file (str): Path to output the summary CSV file (default is 'summary.csv').
    """
    summary = []
    headers = ['File', 'Problem', 'Status', 'Landing Times']

    for i in problems:
        problem_dir = os.path.join(result_folder, f'problem{i}')
        pattern = os.path.join(problem_dir, f'result_*.json')
        matches = glob.glob(pattern)

        if not matches:
            summary.append([f"result_{i+1}", f"Problem {i}", 'No result file found', '-'])
            continue

        # Process all result files for this problem
        for file_path in matches:
            file_name = os.path.basename(file_path)

            with open(file_path) as f:
                data = json.load(f)

            status = data.get('status', 'UNKNOWN')
            landing_times = data.get('landing_times', [])

            lt_str = ', '.join(map(str, landing_times)) if landing_times else '-'

            # Add the result to the summary
            result_num = int(file_name.split('_')[1])  # Extract result number from filename
            summary.append([file_name, f"Problem {i}", status, lt_str, result_num, i])

    summary.sort(key=lambda x: (x[4], x[5]))

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)  # Write the header
        for row in summary:
            writer.writerow(row[:4])

    print(f"Summary written to {output_file}")
