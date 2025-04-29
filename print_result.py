from mip import OptimizationStatus


def print_solution_info(status, model_variables):
    print(f"\nOptimization status: {status.name}\n")

    if status != OptimizationStatus.OPTIMAL and status != OptimizationStatus.FEASIBLE:
        print("No feasible or optimal solution found.")
        return

    landing_times = model_variables.get("landing_times_decision", [])
    early_penalty = model_variables.get("early_penalty", [])
    late_penalty = model_variables.get("late_penalty", [])
    makespan = model_variables.get("makespan", None)
    runway_assignment = model_variables.get("runway_assignment", [])
    landing_order = model_variables.get("landing_order", [])

    print("Landing Times:")
    for i, var in enumerate(landing_times):
        print(f"  Aircraft {i}: {var.x:.2f}")

    if early_penalty and late_penalty:
        print("\nPenalties:")
        for i in range(len(early_penalty)):
            print(f"  Aircraft {i}: Early = {early_penalty[i].x:.2f}, Late = {late_penalty[i].x:.2f}")

    if makespan:
        print(f"\nMakespan: {makespan.x:.2f}")

    if runway_assignment:
        print("\nRunway Assignments:")
        for i, assignments in enumerate(runway_assignment):
            assigned = [r for r, var in enumerate(assignments) if var.x >= 0.99]
            print(f"  Aircraft {i}: Runway {assigned[0] if assigned else 'Unassigned'}")

    if landing_order:
        print("\nLanding Order Matrix:")
        for i, row in enumerate(landing_order):
            row_values = [int(var.x + 0.5) for var in row]
            print(f"  {i}: {row_values}")
