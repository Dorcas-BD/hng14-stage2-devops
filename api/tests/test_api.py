"""
Unit tests for the API service.
Redis is mocked so no real Redis instance is needed.
"""
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

# Patch redis.Redis before importing app so the module-level connection
# never tries to reach a real server
with patch("redis.Redis") as mock_redis_class:
    mock_redis_instance = MagicMock()
    mock_redis_class.return_value = mock_redis_instance
    from main import app

client = TestClient(app)


def setup_function():
    """Reset all mocks before each test."""
    mock_redis_instance.reset_mock()


# --- Test 1: Submitting a job returns a job_id and queues it in Redis ---
def test_create_job_returns_job_id():
    mock_redis_instance.lpush = MagicMock()
    mock_redis_instance.hset = MagicMock()

    response = client.post("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format
    # Verify job was pushed to the queue and status was set
    mock_redis_instance.lpush.assert_called_once()
    mock_redis_instance.hset.assert_called_once()


# --- Test 2: Getting a known job returns its status ---
def test_get_existing_job_returns_status():
    mock_redis_instance.hget = MagicMock(return_value=b"queued")

    response = client.get("/jobs/test-job-123")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "queued"


# --- Test 3: Getting an unknown job returns 404, not 200 with error body ---
def test_get_nonexistent_job_returns_404():
    mock_redis_instance.hget = MagicMock(return_value=None)

    response = client.get("/jobs/does-not-exist")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data  # FastAPI HTTPException format
