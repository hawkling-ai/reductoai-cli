"""Tests for utility functions."""

import time
from unittest.mock import MagicMock, patch

import pytest

from reducto_cli.utils import get_job_status, poll_job, is_local_file


def test_get_job_status_wrapper(mock_reducto_client, mock_job_status_completed):
    """
    Test that get_job_status wrapper calls client.job.get().

    This verifies we're using the correct SDK method name (.get not .retrieve).
    """
    mock_reducto_client.job.get.return_value = mock_job_status_completed

    result = get_job_status(mock_reducto_client, "test-job-id")

    assert result == mock_job_status_completed
    mock_reducto_client.job.get.assert_called_once_with("test-job-id")


def test_poll_job_success(mock_reducto_client, mock_job_status_completed):
    """Test that poll_job successfully polls until completion."""
    # Mock get_job_status to return completed status
    with patch("reducto_cli.utils.get_job_status") as mock_get_status:
        mock_get_status.return_value = mock_job_status_completed

        result = poll_job(mock_reducto_client, "test-job-id", timeout=10)

        assert result == mock_job_status_completed
        mock_get_status.assert_called_once_with(mock_reducto_client, "test-job-id")


def test_poll_job_with_processing_then_completed(
    mock_reducto_client,
    mock_job_status_processing,
    mock_job_status_completed
):
    """Test poll_job when job is processing then completes."""
    with patch("reducto_cli.utils.get_job_status") as mock_get_status, \
         patch("time.sleep"):  # Mock sleep to speed up test

        # First call returns processing, second returns completed
        mock_get_status.side_effect = [
            mock_job_status_processing,
            mock_job_status_completed
        ]

        result = poll_job(mock_reducto_client, "test-job-id", timeout=30)

        assert result == mock_job_status_completed
        assert mock_get_status.call_count == 2


def test_poll_job_timeout(mock_reducto_client, mock_job_status_processing):
    """Test that poll_job raises TimeoutError when timeout is reached."""
    with patch("reducto_cli.utils.get_job_status") as mock_get_status, \
         patch("time.time") as mock_time, \
         patch("time.sleep"):

        mock_get_status.return_value = mock_job_status_processing
        # Simulate time passing
        mock_time.side_effect = [0, 0, 11]  # Start, first check, timeout exceeded

        with pytest.raises(TimeoutError, match="Job timed out after 10 seconds"):
            poll_job(mock_reducto_client, "test-job-id", timeout=10)


def test_poll_job_failed(mock_reducto_client, mock_job_status_failed):
    """Test that poll_job raises exception when job fails."""
    with patch("reducto_cli.utils.get_job_status") as mock_get_status:
        mock_get_status.return_value = mock_job_status_failed

        with pytest.raises(Exception, match="Job failed: Processing failed"):
            poll_job(mock_reducto_client, "test-job-id")


def test_is_local_file_exists(temp_pdf_file):
    """Test is_local_file returns True for existing files."""
    assert is_local_file(str(temp_pdf_file)) is True


def test_is_local_file_not_exists():
    """Test is_local_file returns False for non-existent files."""
    assert is_local_file("/path/to/nonexistent/file.pdf") is False


def test_is_local_file_url():
    """Test is_local_file returns False for URLs."""
    assert is_local_file("https://example.com/document.pdf") is False


def test_is_local_file_reducto_prefix():
    """Test is_local_file returns False for reducto:// prefixes."""
    assert is_local_file("reducto://file-id-123") is False
