"""
Pytest configuration and fixtures
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        "source": "test",
        "content": "Sample financial data",
        "timestamp": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_factors():
    """Sample factors for testing."""
    return {
        "momentum": 0.5,
        "volatility": 0.3,
        "value": 0.7,
        "quality": 0.6,
        "growth": 0.4,
    }
