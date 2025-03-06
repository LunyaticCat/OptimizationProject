from mip import Model, xsum, minimize, maximize, BINARY, INTEGER, OptimizationStatus

def KP ():
    n=4
    items = ['A', 'B', 'C', 'D']
    weights = [5, 7, 4, 6]
    values = [10, 13, 8, 11]
    capacity = 15

    model = Model("knapsack")
    take = [model.add_var(var_type=BINARY) for _ in range(n)]
    model.objective = maximize(xsum(values[i] * take[i] for i in range(n)))
    model += xsum(weights[i] * take[i] for i in range(n)) <= capacity

    status = model.optimize(max_seconds=2)

    print("Status: ", OptimizationStatus(status))
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print("Total value = ", model.objective_value)
        for i in range(len(items)):
            if take[i].x == 1:
                print(items[i], ": Taken")

KP()

def solve_assignment_problem(cost_matrix):
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

cost_matrix = [
    [8, 5, 6, 7],
    [7, 6, 4, 9],
    [9, 8, 7, 5],
    [6, 9, 5, 8]
]

solve_assignment_problem(cost_matrix)

def solve_bin_packing():
    bin_capacity = 10
    item_sizes = [3, 5, 2, 7, 4, 6, 1, 8]
    num_bins = len(item_sizes)

    model = Model("bin_packing")

    # x[i][j] = 1 if item i is placed in bin j, 0 otherwise.
    item_in_bin_list = [[model.add_var(var_type=BINARY) for _ in range(num_bins)] for _ in range(len(item_sizes))]
    # y[j] = 1 if bin j is used, 0 otherwise.
    bins_used = [model.add_var(var_type=BINARY) for _ in range(num_bins)]

    model.objective = minimize(xsum(bins_used[bin_] for bin_ in range(num_bins)))

    # For each item, ensure that it is placed in exactly one bin by forcing the sum
    # of its assignment variables (across all bins) to equal 1.
    for item_index in range(len(item_sizes)):
        model += xsum(item_in_bin_list[item_index][bin_] for bin_ in range(num_bins)) == 1

    # For each bin, ensure that the total size of items assigned to that bin does not exceed the bin's capacity.
    # This constraint multiplies the bin capacity by the binary variable indicating if the bin is used.
    # If a bin is not used (bins_used[bin_] == 0), then no items can be assigned (total size must be 0).
    # If a bin is used (bins_used[bin_] == 1), then the sum of item sizes in that bin must be less than or equal to its capacity.
    for bin_ in range(num_bins):
        model += xsum(item_sizes[item] * item_in_bin_list[item][bin_] for item in range(len(item_sizes))) <= bin_capacity * bins_used[bin_]

    status = model.optimize()
    if status == OptimizationStatus.OPTIMAL:
        print("Optimal solution found!")
        print("Total Cost: ", model.objective_value)
        for bin_ in range(num_bins):
            for item in range(len(item_in_bin_list)):
                if item_in_bin_list[item][bin_].x == 1:
                    print(f"Item {item+1} (size = {item_sizes[item]}) assigned to Bin {bin_+1}")

    else:
        print("No optimal solution found.")

solve_bin_packing()