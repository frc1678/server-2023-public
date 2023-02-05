from cc import cc


def test_cc():
    data = [
        {"parties": ["A", "B"], "value": 10.0},
        {"parties": ["A", "C"], "value": 5.0},
        {"parties": ["B", "C"], "value": 7.5},
    ]
    result = cc(data)
    expected_result = {"A": 3.75, "B": 6.25, "C": 1.25}
    for key in result.keys():
        assert result[key] == expected_result[key]


def test_cc_precision():
    data = [
        {"parties": ["A", "B"], "value": 10.0},
        {"parties": ["A", "C"], "value": 5.0},
        {"parties": ["B", "C"], "value": 7.5},
    ]
    result = cc(data, precision=0)
    expected_result = {"A": 4.0, "B": 6.0, "C": 1.0}
    for key in result.keys():
        assert result[key] == expected_result[key]


def test_cc_empty_input():
    data = []
    result = cc(data)
    expected_result = {}
    assert result == expected_result
