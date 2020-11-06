#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
import pytest
import numpy as np
import os, sys
current_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current_directory)
grandparent_directory = os.path.dirname(parent_directory)
sys.path.append(grandparent_directory)
from src.calculations import inner_goals_regression

def test_dimension_mismatch_error():
    b = np.array([[1, 6, 7, 8]]).T
    A = np.array([[2, 5, 4],
                  [6, 9, 4],
                  [9, 7, 3]])
    with pytest.raises(ValueError):
        inner_goals_regression.least_squares(A, b)

def test_singular_matrix_error():
    b = np.array([[1, 6, 7, 8]]).T
    A = np.array([[2, 5, 4],
                  [6, 9, 4],
                  [0, 0, 0],
                  [0, 0, 0]])
    with pytest.raises(ValueError):
        inner_goals_regression.least_squares(A, b)

def test_no_cap():
    b = np.array([[0, 1, 2]]).T
    A = np.array([[0, 0],
                  [1, 0],
                  [1, -1]])
    expected_result = np.array([[1], [-1]])
    assert (expected_result == inner_goals_regression.least_squares(A, b)).all()

def test_capped():
    b = np.array([[0, 1, 2]]).T
    A = np.array([[0, 0],
                  [1, 0],
                  [1, -1]])
    actual_result = inner_goals_regression.least_squares(A, b, cap_0_to_1=True)
    expected_result = np.array([[1], [0]])
    assert (abs(actual_result - expected_result) < .01).all()

def test_monte_carlo_accuracy():
    b = np.array([[16, 78, 10]]).T
    A = np.array([[5, 1],
                  [25, 3],
                  [3, 1.001]])
    actual_result = inner_goals_regression.least_squares(A, b, cap_0_to_1=True)
    expected_result = np.array([[1], [1]])
    assert (abs(actual_result - expected_result) < .01).all()
