def test_generate_random_value():
    from calculations import generate_random_value

    # test if function returns correct type
    assert isinstance(generate_random_value.generate_random_value("str"), str)
    assert isinstance(generate_random_value.generate_random_value("int"), int)
    assert isinstance(generate_random_value.generate_random_value("float"), float)
    assert isinstance(generate_random_value.generate_random_value("bool"), bool)

    # test all strings
    assert generate_random_value.generate_random_value("str", seed=254) == "xxxxxxxxxx"
    assert generate_random_value.generate_random_value("str", "team_number", seed=254) == "5846"
    assert (
        generate_random_value.generate_random_value("str", "lfm_max_auto_charge_level", seed=254)
        == "DOCK"
    )
    assert (
        generate_random_value.generate_random_value("str", "preloaded_gamepiece", seed=254)
        == "CONE"
    )

    # test int, float, bool
    assert generate_random_value.generate_random_value("int", seed=254) == 47

    assert generate_random_value.generate_random_value("float", seed=10) == 57.1403

    assert generate_random_value.generate_random_value("bool", seed=10) == False

    # test all lists
    assert generate_random_value.generate_random_value("list", seed=254) == []
    assert generate_random_value.generate_random_value(
        "list", "auto_pieces_start_position", seed=254
    ) == [1, 1, 1, 1]
    assert generate_random_value.generate_random_value(
        "list", "lfm_mode_start_position", seed=254
    ) == ["THREE", "TWO"]
    assert generate_random_value.generate_random_value(
        "list", "lfm_mode_preloaded_gamepiece", seed=254
    ) == ["CONE", "CUBE"]
    assert generate_random_value.generate_random_value(
        "list", "lfm_mode_charge_level", seed=254
    ) == ["ENGAGE", "DOCK"]

    # test enum[int] and all enum[str]
    assert generate_random_value.generate_random_value("enum[int]", "drivetrain", seed=254) == 1
    assert (
        generate_random_value.generate_random_value("enum[str]", "auto_charge_level", seed=254)
        == "DOCK"
    )
    assert (
        generate_random_value.generate_random_value("enum[str]", "tele_charge_level", seed=254)
        == "DOCK"
    )
    assert (
        generate_random_value.generate_random_value("enum[str]", "start_position", seed=254)
        == "TWO"
    )
    assert (
        generate_random_value.generate_random_value("enum[str]", "preloaded_gamepiece", seed=254)
        == "CONE"
    )
