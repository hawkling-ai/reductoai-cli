"""Upload command implementation."""

from pathlib import Path
from typing import Optional

import typer
import reducto

from ..client import get_client
from ..utils import output_json, output_error

app = typer.Typer()


@app.command()
def upload(
    file: str = typer.Argument(..., help="Path to the file to upload"),
    extension: Optional[str] = typer.Option(
        None,
        help="Force file extension (e.g., pdf, docx)",
    ),
    environment: str = typer.Option(
        "production",
        help="API environment (production, eu, or au)",
    ),
):
    """Upload a file to Reducto."""
    file_path = Path(file)

    if not file_path.exists():
        output_error(f"File not found: {file}")
        raise typer.Exit(code=1)

    if not file_path.is_file():
        output_error(f"Not a file: {file}")
        raise typer.Exit(code=1)

    try:
        client = get_client(environment=environment)
        upload_result = client.upload(file=file_path, extension=extension)
        output_json(upload_result)
    except reducto.APIError as error:
        output_error("API error", error)
        raise typer.Exit(code=1)
    except Exception as error:
        output_error("Failed to upload file", error)
        raise typer.Exit(code=1)
