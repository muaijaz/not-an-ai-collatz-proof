import math

from collatz_exp.rozier_abc_audit import (
    enumerate_N_j,
    is_mu_hit,
    mu,
    n239_family_extension,
    theorem_4_1_audit,
    theorem_4_1_check,
)


def test_mu_and_small_mu_hit_examples():
    assert mu(1) == 0.0
    assert math.isclose(mu(12), math.log(2) + math.log(2) + math.log(3))
    assert is_mu_hit(1, 239**2, 2 * 13**4)


def test_enumerate_N_10_matches_rozier_example():
    assert sorted(enumerate_N_j(10)) == [
        159,
        239,
        447,
        511,
        639,
        681,
        767,
        795,
        871,
        1022,
    ]


def test_theorem_4_1_check_has_no_small_violations():
    summaries, violations = theorem_4_1_audit(10, 12)
    assert violations == []
    assert summaries["10"]["n_count"] == 10
    assert all(
        summary["theorem_4_1_violation_count"] == 0
        for summary in summaries.values()
    )


def test_theorem_4_1_check_records_unique_even_position():
    check = theorem_4_1_check(239, 10)
    assert check["k"] == 4
    assert check["T_k_n"] == 1214
    assert not check["theorem_4_1_violation"]


def test_n239_family_first_entry_is_exact_mu_hit():
    entry = n239_family_extension(2, 2)[0]
    assert entry["mu_hit"] is True
    assert entry["partial_factorization_complete"]
    assert entry["gain"] > 0
