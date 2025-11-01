"""Main CLI entry point."""

import typer

from .commands import version, upload, parse

app = typer.Typer(
    name="reducto",
    help="A CLI wrapper for the Reducto API",
    no_args_is_help=True,
)

# Register commands
app.command(name="version")(version.version)
app.command(name="upload")(upload.upload)
app.command(name="parse")(parse.parse)


if __name__ == "__main__":
    app()
