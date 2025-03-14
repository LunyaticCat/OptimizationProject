from mip import Model, xsum, minimize, BINARY, OptimizationStatus

def solve_bin_packing(bin_capacity, item_sizes):
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
            for item_index in range(len(item_in_bin_list)):
                if item_in_bin_list[item_index][bin_].x == 1:
                    print(f"Item {item_index+1} (size = {item_sizes[item_index]}) assigned to Bin {bin_+1}")

    else:
        print("No optimal solution found.")

solve_bin_packing(10, [3, 5, 2, 7, 4, 6, 1, 8])