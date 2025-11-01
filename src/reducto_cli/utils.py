"""Utility functions for the CLI."""

import json
import sys
import time
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

console = Console()


def is_local_file(input_str: str) -> bool:
    """
    Check if the input string is a local file path.

    Args:
        input_str: The input string to check

    Returns:
        True if the input is a local file, False otherwise
    """
    return Path(input_str).exists()


def output_json(data: Any) -> None:
    """
    Output data as JSON to stdout.

    Args:
        data: The data to output (must be JSON serializable)
    """
    # Convert Pydantic models to dict
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "to_dict"):
        data = data.to_dict()

    json.dump(data, sys.stdout, indent=2)
    print()  # Add newline at the end


def save_json_to_file(data: Any, file_path: Path) -> None:
    """
    Save data as JSON to a file.

    Args:
        data: The data to save (must be JSON serializable)
        file_path: The path where the file should be saved
    """
    # Convert Pydantic models to dict
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "to_dict"):
        data = data.to_dict()

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def output_error(message: str, error: Optional[Exception] = None) -> None:
    """
    Output an error message as JSON to stdout.

    Args:
        message: The error message
        error: Optional exception object
    """
    error_data = {"error": message}

    if error:
        error_data["details"] = str(error)
        if hasattr(error, "status_code"):
            error_data["status_code"] = error.status_code
        if hasattr(error, "response"):
            try:
                error_data["response"] = error.response.json()
            except Exception:
                error_data["response"] = str(error.response)

    output_json(error_data)


def format_elapsed_time(seconds: float) -> str:
    """
    Format elapsed time in seconds to a human-readable string.

    Args:
        seconds: The number of seconds elapsed

    Returns:
        Formatted time string (e.g., "45s" or "1m 23s")
    """
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds}s"


def get_job_status(client, job_id: str) -> Any:
    """
    Get the status of a job.

    Args:
        client: The Reducto client
        job_id: The job ID to check

    Returns:
        The job status object
    """
    return client.job.get(job_id)


def poll_job(client, job_id: str, timeout: Optional[int] = None) -> Any:
    """
    Poll a job until it completes, showing a spinner.

    Args:
        client: The Reducto client
        job_id: The job ID to poll
        timeout: Optional timeout in seconds

    Returns:
        The job result

    Raises:
        TimeoutError: If the timeout is reached
        Exception: If the job fails
    """
    spinner = Spinner("dots", text=f"Processing job {job_id}...")
    start_time = time.time()

    with Live(spinner, console=console, transient=True) as live:
        while True:
            job_status = get_job_status(client, job_id)
            elapsed = time.time() - start_time
            elapsed_str = format_elapsed_time(elapsed)

            if job_status.status.lower() == "completed":
                live.stop()
                console.print(f"✓ Parsing completed in {elapsed_str}", style="green")
                return job_status

            if job_status.status.lower() == "failed":
                live.stop()
                error_msg = getattr(job_status, "error", "Unknown error")
                raise Exception(f"Job failed: {error_msg}")

            # Check timeout
            if timeout is not None:
                if elapsed >= timeout:
                    live.stop()
                    raise TimeoutError(f"Job timed out after {timeout} seconds")

            # Update spinner text with job ID and elapsed time
            status_text = getattr(job_status, "status", "processing")
            live.update(Spinner("dots", text=f"Processing job {job_id}... {elapsed_str}"))

            time.sleep(5)  # Poll every 5 seconds
