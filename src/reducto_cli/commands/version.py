"""Version command implementation."""

import typer
import reducto

from ..client import get_client
from ..utils import output_json, output_error

app = typer.Typer()


@app.command()
def version(
    environment: str = typer.Option(
        "production",
        help="API environment (production, eu, or au)",
    ),
):
    """Get the API version information."""
    try:
        client = get_client(environment=environment)
        version_info = client.api_version()
        output_json(version_info)
    except reducto.APIError as error:
        output_error("API error", error)
        raise typer.Exit(code=1)
    except Exception as error:
        output_error("Failed to get version", error)
        raise typer.Exit(code=1)
