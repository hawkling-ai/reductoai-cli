"""Pytest configuration and fixtures."""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_pdf_file(tmp_path):
    """Create a temporary PDF file for testing."""
    pdf_file = tmp_path / "test_document.pdf"
    pdf_file.write_text("Mock PDF content")
    return pdf_file


@pytest.fixture
def mock_reducto_client():
    """Create a mock Reducto client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_upload_result():
    """Create a mock upload result."""
    result = MagicMock()
    result.file_id = "reducto://mock-file-id-123"
    return result


@pytest.fixture
def mock_job_response():
    """Create a mock job response."""
    response = MagicMock()
    response.job_id = "mock-job-id-456"
    return response


@pytest.fixture
def mock_job_status_completed():
    """Create a mock completed job status."""
    status = MagicMock()
    status.status = "completed"
    status.job_id = "mock-job-id-456"
    status.result = {"chunks": [], "blocks": []}
    # Make model_dump return a dict for JSON serialization
    status.model_dump.return_value = {
        "status": "completed",
        "job_id": "mock-job-id-456",
        "result": {"chunks": [], "blocks": []}
    }
    return status


@pytest.fixture
def mock_job_status_processing():
    """Create a mock processing job status."""
    status = MagicMock()
    status.status = "processing"
    status.job_id = "mock-job-id-456"
    return status


@pytest.fixture
def mock_job_status_failed():
    """Create a mock failed job status."""
    status = MagicMock()
    status.status = "failed"
    status.job_id = "mock-job-id-456"
    status.error = "Processing failed"
    return status


@pytest.fixture
def mock_env_api_key(monkeypatch):
    """Set the REDUCTO_API_KEY environment variable."""
    monkeypatch.setenv("REDUCTO_API_KEY", "test-api-key-123")
