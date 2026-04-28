from collatz_exp.mixed import (
    classify_cycle_word,
    explore_mixed_automaton,
    forced_valuation,
    initial_states,
    transition_state,
)


def test_forced_valuation_needs_enough_binary_precision():
    assert forced_valuation(1, 1) is None
    assert forced_valuation(3, 2) == 1
    assert forced_valuation(3, 3) == 1


def test_cycle_classifier_has_known_anchors():
    one = classify_cycle_word((2,))
    assert one.kind == "positive_integer_cycle"
    assert one.value == 1

    minus_one = classify_cycle_word((1,))
    assert minus_one.kind == "negative_integer_cycle"
    assert minus_one.value == -1


def test_initial_mixed_states_cover_odd_binary_and_mod3_classes():
    states = initial_states(mod2_power=3, mod3_power=1, bucket_scale=100)
    assert len(states) == 12
    assert {state.residue2 for state in states} == {1, 3, 5, 7}
    assert {state.residue3 for state in states} == {0, 1, 2}


def test_transition_grows_3adic_precision_and_decays_binary_precision():
    state = initial_states(mod2_power=3, mod3_power=1, bucket_scale=100)[0]
    next_state = transition_state(
        state,
        valuation=1,
        A=1,
        m=1,
        suffix_length=4,
        max_mod3_power=5,
    )
    assert next_state.mod2_power == 2
    assert next_state.mod3_power == 2
    assert next_state.m == 1
    assert next_state.A == 1


def test_mixed_automaton_smoke_report():
    report = explore_mixed_automaton(
        initial_mod2_power=3,
        mod3_power=1,
        max_mod2_power=8,
        max_states=500,
        max_steps=20,
        max_mod3_power=5,
    )
    assert report.states_explored > 0
    assert report.transitions > 0
    assert report.terminal_certified > 0
    assert report.dominated_pruned >= 0
