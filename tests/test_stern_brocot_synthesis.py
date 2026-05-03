from collatz_exp.stern_brocot_synthesis import (
    cf_convergents_log2,
    megasynthesis_executive_summary,
    six_reduction_cross_tabulation,
    stern_brocot_alignment_table,
    stern_brocot_megasynthesis_report,
    tao_discrepancy,
    tao_tier_test,
)


def test_cf_convergents_normalize_log2_3_shape():
    rows = cf_convergents_log2(3, depth=5)
    assert rows[1]["fraction"] == "2/1"
    assert rows[2]["fraction"] == "3/2"
    assert {row["side"] for row in rows} >= {"above", "below"}


def test_tao_discrepancy_computes_small_nondegenerate_pair():
    row = tao_discrepancy(5, 3, max_admissible=1000)
    assert row["status"] == "computed_exact"
    assert row["admissible_count"] == 6
    assert 0.0 <= row["discrepancy"] <= 1.0


def test_tao_tier_test_smoke_with_small_parameters():
    result = tao_tier_test(
        max_m=5,
        random_count=10,
        bootstrap_samples=20,
        max_admissible=1000,
    )
    assert set(result["tiers"]) == {
        "cf_convergent",
        "intermediate_fraction",
        "random_rational",
    }
    assert result["tiers"]["random_rational"]["candidate_count"] == 10
    assert "tao_tier_hypothesis_supported" in result


def test_alignment_table_recovers_elementary_slope_match():
    rows = stern_brocot_alignment_table(
        cf_depth=4,
        rozier_n_max=25,
        chang_max_K=20,
    )
    row_2_over_1 = next(row for row in rows if row["fraction"] == "2/1")
    assert any(
        match["valuation_word"] == [2]
        and match["classification"] == "positive_integer_cycle"
        for match in row_2_over_1["slope_realizability_matches"]
    )


def test_six_reduction_table_has_expected_entries():
    table = six_reduction_cross_tabulation()
    assert len(table["reductions"]) == 6
    assert "Tao_2019" in table["reductions"]
    assert table["six_reduction_unification_meta_claim"] is False


def test_megasynthesis_report_and_summary_smoke():
    report = stern_brocot_megasynthesis_report(
        q_values=(3,),
        cf_depth=5,
        tao_max_m=5,
        tao_random_count=10,
        tao_bootstrap_samples=20,
        tao_max_admissible=1000,
        rozier_n_max=25,
        chang_max_K=20,
    )
    assert report.type == "stern_brocot_megasynthesis"
    assert report.verdict["overall"] == "partial_or_negative_empirical_megasynthesis"
    summary = megasynthesis_executive_summary(report)
    assert "Stern-Brocot Megasynthesis Executive Summary" in summary
    assert "finite empirical synthesis" in summary
