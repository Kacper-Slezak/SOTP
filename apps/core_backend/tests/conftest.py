"""
conftest.py — shared pytest configuration for core_backend tests.

Place this file at:  apps/core_backend/tests/conftest.py
"""

import pytest


# ---------------------------------------------------------------------------
# Make pytest-asyncio work in "auto" mode for the entire test suite so that
# you don't have to mark every async test manually.
# ---------------------------------------------------------------------------
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: mark a test as an integration test (needs a live DB).",
    )
