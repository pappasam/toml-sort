"""Fixtures shared across tests."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List

import pytest


@pytest.fixture(name="fixture_path")
def get_fixture_path() -> Path:
    """Path for where TOML files for the tests."""
    return Path(__file__).parent / "examples"


@pytest.fixture()
def get_fixture(fixture_path: Path) -> Callable[[str | List[str]], Path]:
    """Callable for fixture file Path object."""

    def getter(fixture_names: str | List[str]) -> Path:
        if isinstance(fixture_names, str):
            fixture_names = [fixture_names]

        fixture_names[-1] = f"{fixture_names[-1]}.toml"

        path = fixture_path
        for name in fixture_names:
            path /= name

        return path

    return getter
