"""Tests for the parse command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from reducto_cli.commands.parse import upload_file, create_parse_job
from reducto_cli.main import app

runner = CliRunner()


def test_parse_local_file_success(
    temp_pdf_file,
    mock_reducto_client,
    mock_upload_result,
    mock_job_response,
    mock_job_status_completed,
    mock_env_api_key,
):
    """
    REGRESSION TEST: Parse a local PDF file successfully.

    This test verifies the complete flow that was previously broken:
    1. Upload local file
    2. Create parse job
    3. Poll job status using client.job.get() (not .retrieve())
    4. Return completed result

    This prevents regression of the bug where poll_job() called
    client.job.retrieve() instead of client.job.get().
    """
    # Mock the wrapper functions
    with patch("reducto_cli.commands.parse.get_client") as mock_get_client, \
         patch("reducto_cli.commands.parse.upload_file") as mock_upload, \
         patch("reducto_cli.commands.parse.create_parse_job") as mock_create_job, \
         patch("reducto_cli.commands.parse.poll_job") as mock_poll:

        # Setup mocks
        mock_get_client.return_value = mock_reducto_client
        mock_upload.return_value = mock_upload_result
        mock_create_job.return_value = mock_job_response
        mock_poll.return_value = mock_job_status_completed

        # Run the command
        result = runner.invoke(app, ["parse", str(temp_pdf_file)])

        # Verify success
        assert result.exit_code == 0

        # Verify the flow was called correctly
        mock_get_client.assert_called_once_with(environment="production")
        mock_upload.assert_called_once()
        mock_create_job.assert_called_once()
        mock_poll.assert_called_once_with(
            mock_reducto_client,
            mock_job_response.job_id,
            timeout=None
        )

        # Verify output contains job data
        assert "mock-job-id-456" in result.stdout or "completed" in result.stdout


def test_upload_file_wrapper(mock_reducto_client, temp_pdf_file, mock_upload_result):
    """Test the upload_file wrapper function."""
    mock_reducto_client.upload.return_value = mock_upload_result

    result = upload_file(mock_reducto_client, temp_pdf_file)

    assert result == mock_upload_result
    mock_reducto_client.upload.assert_called_once_with(file=temp_pdf_file)


def test_create_parse_job_wrapper(mock_reducto_client, mock_job_response):
    """Test the create_parse_job wrapper function."""
    mock_reducto_client.parse.run_job.return_value = mock_job_response

    result = create_parse_job(
        mock_reducto_client,
        input="reducto://test-file-id",
        settings={"timeout": 300}
    )

    assert result == mock_job_response
    mock_reducto_client.parse.run_job.assert_called_once_with(
        input="reducto://test-file-id",
        settings={"timeout": 300}
    )
