import json
import random

from collatz_exp.renewal_correlation import (
    dfa_alpha,
    pooled_autocorrelation,
    renewal_correlation_report,
)


def _iid_series(seed: int, orbits: int, length: int) -> list[list[float]]:
    rng = random.Random(seed)
    return [
        [rng.gauss(0.0, 1.0) for _ in range(length)] for _ in range(orbits)
    ]


def _persistent_series(seed: int, orbits: int, length: int) -> list[list[float]]:
    rng = random.Random(seed)
    series_list = []
    for _ in range(orbits):
        value = 0.0
        series = []
        for _ in range(length):
            value = 0.9 * value + rng.gauss(0.0, 1.0)
            series.append(value)
        series_list.append(series)
    return series_list


def test_pooled_acf_iid_is_small():
    acf, pair_counts = pooled_autocorrelation(_iid_series(1, 8, 512), max_lag=10)
    assert len(acf) == 10
    assert all(count > 0 for count in pair_counts)
    assert max(abs(value) for value in acf) < 0.1


def test_pooled_acf_detects_persistence():
    acf, _ = pooled_autocorrelation(_persistent_series(2, 8, 512), max_lag=10)
    assert acf[0] > 0.6
    assert acf[1] > acf[5]


def test_dfa_alpha_iid_near_half():
    alpha, sizes, log_f = dfa_alpha(_iid_series(3, 8, 1024))
    assert alpha is not None
    assert len(sizes) == len(log_f)
    assert abs(alpha - 0.5) < 0.15


def test_dfa_alpha_persistent_above_half():
    alpha, _, _ = dfa_alpha(_persistent_series(4, 8, 1024))
    assert alpha is not None
    assert alpha > 0.6


def test_renewal_correlation_report_structure():
    report = renewal_correlation_report(
        orbit_count=4,
        start_bits=64,
        random_seed=0,
        max_lag=5,
    )
    assert report.orbit_count == 4
    assert report.completed_orbits + report.truncated_orbits == 4
    assert report.total_excursions > 0
    assert report.total_steps >= report.total_excursions
    names = [item.name for item in report.series]
    assert names == [
        "excursion_delta_log2",
        "excursion_step_count",
        "step_valuation",
    ]
    for item in report.series:
        assert len(item.acf) == 5
        assert item.status in {
            "iid_consistent",
            "short_range_correlations_only",
            "long_range_persistent_candidate",
            "anti_persistent_candidate",
        }
    payload = json.loads(report.to_json())
    assert payload["orbit_count"] == 4
    assert len(payload["series"]) == 3


def test_renewal_correlation_report_deterministic():
    first = renewal_correlation_report(
        orbit_count=3, start_bits=64, random_seed=7, max_lag=4
    )
    second = renewal_correlation_report(
        orbit_count=3, start_bits=64, random_seed=7, max_lag=4
    )
    assert first.to_json() == second.to_json()
