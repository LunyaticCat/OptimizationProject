from mip import Model, xsum, minimize, BINARY, OptimizationStatus

def solve_assignment(cost_matrix: list[list[int]]):
    num_workers = len(cost_matrix)
    num_tasks = len(cost_matrix[0])

    if num_workers != num_tasks:
        raise ValueError("Number of workers does not match number of tasks")

    model = Model("assignment")
    #decision variables x[i][j] = 1 if worker i is assigned to task j, 0 otherwise
    x = [[model.add_var(var_type=BINARY) for _ in range(num_tasks)] for _ in range(num_workers)]


    #Objective minimize the total cost
    model.objective = minimize(xsum(cost_matrix[i][j] * x[i][j] for i in range(num_workers) for j in range(num_tasks)))

    for i in range(num_workers):
        model += xsum(x[i][j] for j in range(num_tasks)) == 1

    for j in range(num_tasks):
        model += xsum(x[i][j] for i in range(num_workers)) == 1

    status = model.optimize()

    if status == OptimizationStatus.OPTIMAL:
        print("Optimal solution found!")
        print("Total Cost: ", model.objective_value)
        for i in range(num_workers):
            for j in range(num_tasks):
                if x[i][j].x == 1:
                    print(f"Worker {i+1} assigned to Task {j+1}")
    else:
        print("No optimal solution found.")

matrix = [
    [8, 5, 6, 7],
    [7, 6, 4, 9],
    [9, 8, 7, 5],
    [6, 9, 5, 8]
]

solve_assignment(matrix)