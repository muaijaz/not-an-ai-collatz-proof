from collatz_exp.certificates import (
    certificate_from_residue,
    certificate_from_word,
    residue_for_word,
    verify_descent_certificate,
)


KNOWN_WORD = (
    1,
    2,
    1,
    1,
    1,
    1,
    2,
    2,
    1,
    2,
    1,
    1,
    2,
    1,
    1,
    1,
    2,
    3,
    1,
    1,
    2,
    1,
    2,
    1,
    1,
    1,
    1,
    1,
    3,
    1,
    1,
    1,
    4,
    2,
    2,
    4,
    3,
)


def test_known_word_residue_and_certificate():
    assert sum(KNOWN_WORD) == 59
    assert residue_for_word(KNOWN_WORD) == 27

    certificate = certificate_from_word(KNOWN_WORD)
    assert certificate.residue == 27
    assert certificate.modulus_power == 59
    assert certificate.m == 37
    assert certificate.A == 59
    assert verify_descent_certificate(certificate)


def test_find_known_certificate_from_residue():
    certificate = certificate_from_residue(27, 59)
    assert certificate is not None
    assert certificate.word == KNOWN_WORD
    assert verify_descent_certificate(certificate)


def test_certificate_json_uses_string_bigints():
    certificate = certificate_from_word(KNOWN_WORD)
    data = certificate.to_json_dict()
    assert data["type"] == "descent_certificate"
    assert data["residue"] == "27"
    assert isinstance(data["word"], list)
    assert isinstance(data["B"], str)
