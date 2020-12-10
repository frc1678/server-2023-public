import pytest


def test_avg():
    from calculations.base_calculations import BaseCalculations

    # Test if there is no input
    assert 0 == BaseCalculations.avg('')
    # Test average with no weights
    assert 2 == BaseCalculations.avg([1, 2, 3])
    # Test error if there are a different amount of weights than numbers
    with pytest.raises(ValueError) as num_error:
        BaseCalculations.avg([1, 2], [3, 4, 5])
    assert 'Weighted average expects one weight for each number.' in str(num_error)
    # Test average with weights
    assert 1 == BaseCalculations.avg([1, 3], [2.0, 0.0])
