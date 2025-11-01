"""Parse command implementation."""

import json
from pathlib import Path
from typing import Optional, List

import typer
import reducto
from reducto._types import omit

from ..client import get_client
from ..utils import is_local_file, output_json, output_error, poll_job, save_json_to_file, console

app = typer.Typer()


def validate_return_images(values: Optional[List[str]]) -> Optional[List[str]]:
    """
    Validate that return_images values are only 'figure' or 'table'.

    Args:
        values: List of return_images values

    Returns:
        The validated values

    Raises:
        typer.BadParameter: If any value is not 'figure' or 'table'
    """
    if values is None:
        return None

    valid_values = {'figure', 'table'}
    for value in values:
        if value not in valid_values:
            raise typer.BadParameter(
                f"Invalid value '{value}'. "
                f"Only 'figure' and 'table' are allowed for --settings-return-images.\n"
                f"Example: --settings-return-images figure --settings-return-images table"
            )
    return values


def upload_file(client, file_path: Path):
    """
    Upload a file to Reducto.

    Args:
        client: The Reducto client
        file_path: Path to the file to upload

    Returns:
        Upload result with file_id
    """
    return client.upload(file=file_path)


def create_parse_job(client, **kwargs):
    """
    Create a parse job.

    Args:
        client: The Reducto client
        **kwargs: Arguments to pass to client.parse.run_job

    Returns:
        Job response with job_id
    """
    return client.parse.run_job(**kwargs)


@app.command()
def parse(
    input_source: str = typer.Argument(..., help="Input: file path, URL, or reducto:// prefix"),
    # Environment
    environment: str = typer.Option(
        "production",
        help="API environment (production, eu, or au)",
    ),
    # Enhance options
    enhance_summarize_figures: Optional[bool] = typer.Option(
        None,
        "--enhance-summarize-figures/--no-enhance-summarize-figures",
        help="Summarize figures using vision language model",
    ),
    enhance_agentic_table: Optional[bool] = typer.Option(
        None,
        "--enhance-agentic-table/--no-enhance-agentic-table",
        help="Enable table agentic enhancement",
    ),
    enhance_agentic_table_prompt: Optional[str] = typer.Option(
        None,
        "--enhance-agentic-table-prompt",
        help="Custom prompt for table agentic",
    ),
    enhance_agentic_figure: Optional[bool] = typer.Option(
        None,
        "--enhance-agentic-figure/--no-enhance-agentic-figure",
        help="Enable figure agentic enhancement",
    ),
    enhance_agentic_figure_prompt: Optional[str] = typer.Option(
        None,
        "--enhance-agentic-figure-prompt",
        help="Custom prompt for figure agentic",
    ),
    enhance_agentic_text: Optional[bool] = typer.Option(
        None,
        "--enhance-agentic-text/--no-enhance-agentic-text",
        help="Enable text agentic enhancement",
    ),
    # Formatting options
    formatting_add_page_markers: Optional[bool] = typer.Option(
        None,
        "--formatting-add-page-markers/--no-formatting-add-page-markers",
        help="Add page markers to output",
    ),
    formatting_merge_tables: Optional[bool] = typer.Option(
        None,
        "--formatting-merge-tables/--no-formatting-merge-tables",
        help="Merge consecutive tables with same column count",
    ),
    formatting_table_output_format: Optional[str] = typer.Option(
        None,
        "--formatting-table-output-format",
        help="Table output format: html, json, md, jsonbbox, dynamic, csv",
    ),
    formatting_include: Optional[List[str]] = typer.Option(
        None,
        "--formatting-include",
        help="Formatting to include: change_tracking, highlight, comments",
    ),
    # Retrieval options
    retrieval_embedding_optimized: Optional[bool] = typer.Option(
        None,
        "--retrieval-embedding-optimized/--no-retrieval-embedding-optimized",
        help="Use embedding optimized mode",
    ),
    retrieval_filter_blocks: Optional[List[str]] = typer.Option(
        None,
        "--retrieval-filter-blocks",
        help="Block types to filter out (e.g., Header, Footer, Table)",
    ),
    retrieval_chunking_mode: Optional[str] = typer.Option(
        None,
        "--retrieval-chunking-mode",
        help="Chunking mode: variable, section, page, disabled, block, page_sections",
    ),
    retrieval_chunking_size: Optional[int] = typer.Option(
        None,
        "--retrieval-chunking-size",
        help="Approximate chunk size in characters (250-1500 default if mode is variable)",
    ),
    # Spreadsheet options
    spreadsheet_split_large_tables: Optional[bool] = typer.Option(
        None,
        "--spreadsheet-split-large-tables/--no-spreadsheet-split-large-tables",
        help="Split large tables into smaller tables",
    ),
    spreadsheet_split_large_tables_size: Optional[int] = typer.Option(
        None,
        "--spreadsheet-split-large-tables-size",
        help="Size to split large tables into (default: 50)",
    ),
    spreadsheet_include: Optional[List[str]] = typer.Option(
        None,
        "--spreadsheet-include",
        help="Include options: cell_colors, formula",
    ),
    spreadsheet_clustering: Optional[str] = typer.Option(
        None,
        "--spreadsheet-clustering",
        help="Table clustering mode: accurate, fast, disabled (default: accurate)",
    ),
    spreadsheet_exclude: Optional[List[str]] = typer.Option(
        None,
        "--spreadsheet-exclude",
        help="Exclude options: hidden_sheets, hidden_rows, hidden_cols",
    ),
    # Settings options
    settings_document_password: Optional[str] = typer.Option(
        None,
        "--settings-document-password",
        help="Password for password-protected documents",
    ),
    settings_page_range: Optional[List[int]] = typer.Option(
        None,
        "--settings-page-range",
        help="Page range to process (1-indexed, e.g., --settings-page-range 1 --settings-page-range 5)",
    ),
    settings_return_images: Optional[List[str]] = typer.Option(
        None,
        "--settings-return-images",
        help="Return images for block types (allowed values: 'figure', 'table'). Can be specified multiple times.",
        callback=validate_return_images,
    ),
    settings_return_ocr_data: Optional[bool] = typer.Option(
        None,
        "--settings-return-ocr-data/--no-settings-return-ocr-data",
        help="Return OCR data in result",
    ),
    settings_timeout: Optional[int] = typer.Option(
        None,
        "--settings-timeout",
        help="Timeout in seconds (also used for CLI job polling timeout)",
    ),
    settings_ocr_system: Optional[str] = typer.Option(
        None,
        "--settings-ocr-system",
        help="OCR system: standard (best multilingual) or legacy",
    ),
    settings_persist_results: Optional[bool] = typer.Option(
        False,
        "--settings-persist-results/--no-settings-persist-results",
        help="Persist results indefinitely (default: False)",
    ),
    settings_force_url_result: Optional[bool] = typer.Option(
        None,
        "--settings-force-url-result/--no-settings-force-url-result",
        help="Force result to be returned as URL",
    ),
    settings_embed_pdf_metadata: Optional[bool] = typer.Option(
        None,
        "--settings-embed-pdf-metadata/--no-settings-embed-pdf-metadata",
        help="Embed OCR metadata into returned PDF",
    ),
    settings_force_file_extension: Optional[str] = typer.Option(
        None,
        "--settings-force-file-extension",
        help="Force URL to be downloaded as specific file extension",
    ),
    # Output options
    output: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output file path (default: {basename}.json for files, reducto_{job_id}.json for URLs)",
    ),
):
    """
    Parse a document using Reducto API.

    Automatically uploads local files before parsing.
    Uses async parsing with job polling.
    """
    try:
        client = get_client(environment=environment)

        # Auto-upload local files
        parse_input = input_source
        if is_local_file(input_source):
            file_path = Path(input_source)
            upload_result = upload_file(client, file_path)
            parse_input = upload_result.file_id

        # Build options dictionaries
        enhance = omit
        enhance_dict = {}
        if enhance_summarize_figures is not None:
            enhance_dict["summarize_figures"] = enhance_summarize_figures

        # Build agentic array
        agentic = []
        if enhance_agentic_table:
            table_agentic = {"scope": "table"}
            if enhance_agentic_table_prompt:
                table_agentic["prompt"] = enhance_agentic_table_prompt
            agentic.append(table_agentic)
        if enhance_agentic_figure:
            figure_agentic = {"scope": "figure"}
            if enhance_agentic_figure_prompt:
                figure_agentic["prompt"] = enhance_agentic_figure_prompt
            agentic.append(figure_agentic)
        if enhance_agentic_text:
            agentic.append({"scope": "text"})
        if agentic:
            enhance_dict["agentic"] = agentic

        if enhance_dict:
            enhance = enhance_dict

        formatting = omit
        formatting_dict = {}
        if formatting_add_page_markers is not None:
            formatting_dict["add_page_markers"] = formatting_add_page_markers
        if formatting_merge_tables is not None:
            formatting_dict["merge_tables"] = formatting_merge_tables
        if formatting_table_output_format is not None:
            formatting_dict["table_output_format"] = formatting_table_output_format
        if formatting_include is not None:
            formatting_dict["include"] = formatting_include
        if formatting_dict:
            formatting = formatting_dict

        retrieval = omit
        retrieval_dict = {}
        if retrieval_embedding_optimized is not None:
            retrieval_dict["embedding_optimized"] = retrieval_embedding_optimized
        if retrieval_filter_blocks is not None:
            retrieval_dict["filter_blocks"] = retrieval_filter_blocks

        # Build chunking dict
        chunking_dict = {}
        if retrieval_chunking_mode is not None:
            chunking_dict["chunk_mode"] = retrieval_chunking_mode
        if retrieval_chunking_size is not None:
            chunking_dict["chunk_size"] = retrieval_chunking_size
        if chunking_dict:
            retrieval_dict["chunking"] = chunking_dict

        if retrieval_dict:
            retrieval = retrieval_dict

        settings = omit
        settings_dict = {}
        if settings_document_password is not None:
            settings_dict["document_password"] = settings_document_password
        if settings_page_range is not None:
            settings_dict["page_range"] = settings_page_range
        if settings_return_images is not None:
            settings_dict["return_images"] = settings_return_images
        if settings_return_ocr_data is not None:
            settings_dict["return_ocr_data"] = settings_return_ocr_data
        if settings_timeout is not None:
            settings_dict["timeout"] = float(settings_timeout)
        if settings_ocr_system is not None:
            settings_dict["ocr_system"] = settings_ocr_system
        if settings_persist_results is not None:
            settings_dict["persist_results"] = settings_persist_results
        if settings_force_url_result is not None:
            settings_dict["force_url_result"] = settings_force_url_result
        if settings_embed_pdf_metadata is not None:
            settings_dict["embed_pdf_metadata"] = settings_embed_pdf_metadata
        if settings_force_file_extension is not None:
            settings_dict["force_file_extension"] = settings_force_file_extension
        if settings_dict:
            settings = settings_dict

        spreadsheet = omit
        spreadsheet_dict = {}

        # Build split_large_tables dict
        split_large_tables_dict = {}
        if spreadsheet_split_large_tables is not None:
            split_large_tables_dict["enabled"] = spreadsheet_split_large_tables
        if spreadsheet_split_large_tables_size is not None:
            split_large_tables_dict["size"] = spreadsheet_split_large_tables_size
        if split_large_tables_dict:
            spreadsheet_dict["split_large_tables"] = split_large_tables_dict

        if spreadsheet_include is not None:
            spreadsheet_dict["include"] = spreadsheet_include
        if spreadsheet_clustering is not None:
            spreadsheet_dict["clustering"] = spreadsheet_clustering
        if spreadsheet_exclude is not None:
            spreadsheet_dict["exclude"] = spreadsheet_exclude

        if spreadsheet_dict:
            spreadsheet = spreadsheet_dict

        # Start async parse job
        job_response = create_parse_job(
            client,
            input=parse_input,
            enhance=enhance,
            formatting=formatting,
            retrieval=retrieval,
            settings=settings,
            spreadsheet=spreadsheet,
        )

        # Poll until complete
        job_result = poll_job(client, job_response.job_id, timeout=settings_timeout)

        # Determine output filename
        if output:
            output_file = Path(output)
        elif is_local_file(input_source):
            # Use basename of input file
            input_path = Path(input_source)
            output_file = Path(f"{input_path.stem}.json")
        else:
            # Use job_id for URLs or reducto:// IDs
            output_file = Path(f"reducto_{job_response.job_id}.json")

        # Save the result to file
        save_json_to_file(job_result, output_file)
        console.print(f"✓ Saved to {output_file}", style="green")

    except reducto.APIError as error:
        output_error("API error", error)
        raise typer.Exit(code=1)
    except TimeoutError as error:
        output_error("Timeout", error)
        raise typer.Exit(code=1)
    except Exception as error:
        output_error("Failed to parse document", error)
        raise typer.Exit(code=1)
