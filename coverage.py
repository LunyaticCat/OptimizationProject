import pytest
from mip import OptimizationStatus
from class_example import knap_sack, solve_assignment_problem, solve_bin_packing  # Adjust the import

def test_knapsack():
    knap_sack()  # Run function
    assert True  # Basic test to ensure it runs without errors

def test_assignment_problem():
    cost_matrix = [
        [8, 5, 6, 7],
        [7, 6, 4, 9],
        [9, 8, 7, 5],
        [6, 9, 5, 8]
    ]
    solve_assignment_problem(cost_matrix)  # Run function
    assert True  # Check execution

def test_bin_packing():
    solve_bin_packing()  # Run function
    assert True  # Check execution
