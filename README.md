# Reducto CLI

A command-line interface wrapper for the [Reducto API](https://docs.reducto.ai/), built with Python.

## Features

- **Auto-upload**: Parse command automatically uploads local files
- **Async parsing**: Uses async parsing with job polling and progress spinner
- **Full API support**: Exposes all parse configuration options as CLI flags
- **Environment support**: Load API key from `.env` file or environment variables

## Installation

```bash
# Clone the repository
cd reductoai-cli

# Install with uv
uv sync

# Run with uv
uv run reducto
```

## Configuration

Set your Reducto API key in one of two ways:

**Option 1: Environment variable**
```bash
export REDUCTO_API_KEY="your-api-key-here"
```

**Option 2: .env file** (recommended)
```bash
# Edit .env and add your API key
REDUCTO_API_KEY=your-api-key-here
```

## Usage

### Parse Command

Parse a document (URL, local file, or `reducto://` prefix):

```bash
# Parse a URL
reducto parse https://example.com/document.pdf

# Parse a local file (auto-uploads first)
reducto parse path/to/document.pdf

# Parse using a reducto:// prefix from upload
reducto parse reducto://file-id-here
```

**Examples:**

```bash
# Parse with timeout and page range
reducto parse document.pdf \
  --settings-timeout 600 \
  --settings-page-range 1 --settings-page-range 10

# Parse with image extraction
reducto parse document.pdf \
  --settings-return-images figure \
  --settings-return-images table

# Parse with OCR data and specific format
reducto parse document.pdf \
  --settings-return-ocr-data \
  --formatting-table-output-format html
```

## Output

All commands output JSON to stdout, making it easy to pipe to other tools:

```bash
# Parse and save to file
reducto parse document.pdf > result.json

# Parse and extract job_id with jq
reducto parse document.pdf | jq -r '.job_id'

# Upload and get file_id
reducto upload document.pdf | jq -r '.file_id'
```

## License

See LICENSE file for details.

## Links

- [Reducto API Documentation](https://docs.reducto.ai/)
- [Reducto Python SDK](https://github.com/reductoai/reducto-python-sdk)
