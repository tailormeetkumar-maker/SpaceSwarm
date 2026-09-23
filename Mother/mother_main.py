"""Compatibility entry point for creating a Mother spacecraft."""

from Mother.mother_algorithm import Mother


def create_mother(*args, **kwargs) -> Mother:
    return Mother(*args, **kwargs)
