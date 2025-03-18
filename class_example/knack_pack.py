from mip import Model, xsum, maximize, BINARY, OptimizationStatus

class Item:
    def __init__(self, name, weight, value):
        self.name = name
        self.weight = weight
        self.value = value

def solve_knap_sack(items: list[Item], capacity: int):
    model = Model("knapsack")
    take = [model.add_var(var_type=BINARY) for _ in range(len(items))]
    model.objective = maximize(xsum(items[i].value * take[i] for i in range(len(items))))
    model += xsum(items[i].weight * take[i] for i in range(len(items))) <= capacity

    status = model.optimize(max_seconds=2)

    print("Status: ", OptimizationStatus(status))
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print("Total value = ", model.objective_value)
        for i in range(len(items)):
            if take[i].x == 1:
                print(items[i].name, ": Taken")

item_list = [Item("A", 5, 10), Item("B", 7, 13), Item("C", 4, 8), Item("D", 6, 11)]
item_list_2 = [Item("x1", 5, 17), Item("x2", 3, 10), Item("x3", 8, 23), Item("x4", 7, 17)]
solve_knap_sack(item_list, 15)
solve_knap_sack(item_list_2, 12) # solution to the exercise 5 problem (branch and bound method)