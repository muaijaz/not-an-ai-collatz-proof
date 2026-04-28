from collatz_exp.divider_patterns import divider_pattern_report
from collatz_exp.parity import (
    affine_for_parity,
    parity_affine,
    parity_layer_report,
    parity_vector,
    residue_for_parity,
    terras_step,
)


def test_terras_step_and_parity_vector():
    assert terras_step(7) == 11
    assert parity_vector(7, 4) == (1, 1, 1, 0)


def test_parity_affine_residue_is_realized():
    bits = (1, 0, 1, 1)
    q, k, offset = affine_for_parity(bits)
    residue = residue_for_parity(bits)
    assert k == len(bits)
    assert q == sum(bits)
    assert parity_vector(residue if residue else 1 << k, k) == bits
    artifact = parity_affine(bits)
    assert artifact.residue == residue
    assert (3**q * residue + offset) % (1 << k) == 0


def test_parity_layer_report_smoke():
    report = parity_layer_report(length=6, top_n=3)
    assert report.type == "parity_layer_report"
    assert report.vectors == 64
    assert report.favorable_vectors > 0
    assert report.top_thresholds


def test_divider_pattern_report_smoke():
    report = divider_pattern_report(modulus_power=6, lookahead=4)
    assert report.type == "divider_pattern_report"
    assert report.odd_residues == 32
    assert report.counts.single_to_multiple > 0
    assert report.longest_single_run >= 1
