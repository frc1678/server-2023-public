def test_generate_random_value():
    from calculations import generate_random_value

    assert isinstance(generate_random_value.generate_random_value("str"), str)
    assert isinstance(generate_random_value.generate_random_value("int"), int)
    assert isinstance(generate_random_value.generate_random_value("float"), float)
    assert isinstance(generate_random_value.generate_random_value("bool"), bool)

    assert generate_random_value.generate_random_value("str", seed=254) == "xxxxxxxxxxxxxxxxxxxxx"
    assert generate_random_value.generate_random_value("int", seed=254) == 47
    assert generate_random_value.generate_random_value("float", seed=10) == 57.1403
    assert generate_random_value.generate_random_value("bool", seed=10) == False

