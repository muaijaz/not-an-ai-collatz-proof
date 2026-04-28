"""Experimental Collatz certificate-search tools.

This package supports reproducible proof-search experiments. It does not
claim a proof of the Collatz conjecture.
"""

from .core import accelerated_step, affine_from_word, first_descent, is_shrink_favorable, v2
from .certificates import DescentCertificate, verify_descent_certificate
from .cycles import classify_cycle_word
from .cycles_eliahou import cycle_length_screen
from .density_lp import density_bound
from .mersenne import initial_mersenne_run, profile_mersenne

__all__ = [
    "DescentCertificate",
    "accelerated_step",
    "affine_from_word",
    "classify_cycle_word",
    "cycle_length_screen",
    "density_bound",
    "first_descent",
    "initial_mersenne_run",
    "is_shrink_favorable",
    "profile_mersenne",
    "v2",
    "verify_descent_certificate",
]
