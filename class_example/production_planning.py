from mip import Model, xsum, maximize, INTEGER

class Product:
    def __init__(self, labor, material, profit):
        self.labor = labor
        self.material = material
        self.profit = profit

def solve_production_planning(products: list[Product], available_labor: int, available_materials: int):
    num_products = len(products)

    model = Model("production_planning")

    # Variables
    produced_unit = [model.add_var(var_type=INTEGER, lb=0) for _ in range(num_products)]

    # Objective
    model.objective = maximize(xsum(products[product_index].profit * produced_unit[product_index] for product_index in range(num_products)))

    # Constraints
    model += xsum(products[product_index].labor * produced_unit[product_index] for product_index in range(num_products)) <= available_labor
    model += xsum(products[product_index].material * produced_unit[product_index] for product_index in range(num_products)) <= available_materials

    model.optimize()

    # Print results
    for product_index in range(num_products):
        print(f"Product {product_index}: Produced {produced_unit[product_index].x}")

product_list = [Product(2, 3, 5), Product(3, 2, 4)]
solve_production_planning(product_list,24,18)