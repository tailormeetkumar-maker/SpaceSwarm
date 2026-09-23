"""Compatibility entry point for creating a Bee agent."""

from Bee.bee_algorithm import Bee


def create_bee(*args, **kwargs) -> Bee:
    return Bee(*args, **kwargs)
