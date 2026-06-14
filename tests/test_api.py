"""
API endpoint tests.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.core.database import init_db

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_create_session():
    """Test session creation."""
    payload = {
        "agent_type": "claude",
        "agent_version": "3.5",
        "project_name": "test-project",
        "tags": "test,dev",
    }
    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_type"] == "claude"
    assert data["project_name"] == "test-project"
    assert len(data["session_id"]) == 16
    return data["session_id"]


def test_list_sessions():
    """Test listing sessions."""
    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_session():
    """Test getting a specific session."""
    session_id = test_create_session()
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id


def test_update_session():
    """Test updating session."""
    session_id = test_create_session()
    payload = {
        "input_tokens": 1000,
        "output_tokens": 500,
        "command_count": 10,
    }
    response = client.patch(f"/api/v1/sessions/{session_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tokens"] == 1500
    assert data["command_count"] == 10
    assert data["estimated_cost"] > 0


def test_delete_session():
    """Test deleting a session."""
    session_id = test_create_session()
    response = client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 404


def test_log_command():
    """Test logging a command."""
    session_id = test_create_session()
    payload = {
        "session_id": session_id,
        "command": "git status",
        "response": "On branch main",
        "tokens_used": 50,
        "command_type": "git",
    }
    response = client.post("/api/v1/commands", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["command"] == "git status"


def test_cost_estimate():
    """Test cost estimation."""
    payload = {
        "input_tokens": 1000,
        "output_tokens": 500,
        "price_per_1k_input": 0.01,
        "price_per_1k_output": 0.03,
    }
    response = client.post("/api/v1/cost/estimate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["estimated_cost"] == 0.025
    assert data["currency"] == "USD"


def test_analytics_summary():
    """Test analytics summary endpoint."""
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "total_tokens" in data
    assert "top_agents" in data
