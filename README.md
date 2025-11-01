# Reducto CLI

A command-line interface wrapper for the [Reducto API](https://docs.reducto.ai/), built with Python.

## Features

- **Auto-upload**: Parse command automatically uploads local files
- **Async parsing**: Uses async parsing with job polling and progress spinner
- **Full API support**: Exposes all parse configuration options as CLI flags
- **Environment support**: Load API key from `.env` file or environment variables

## Installation

Run directly from GitHub using `uvx` (no installation required):

```bash
# Parse a document
uvx --from git+https://github.com/hawkling-ai/reductoai-cli reducto parse document.pdf
```

## Configuration

Set your Reducto API key in one of two ways:

**Option 1: Environment variable**
```bash
export REDUCTO_API_KEY="your-api-key-here"
```

**Option 2: .env file**
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
```

## Output

All commands output a JSON file.

## License

See LICENSE file for details.

## Links

- [Reducto API Documentation](https://docs.reducto.ai/)
- [Reducto Python SDK](https://github.com/reductoai/reducto-python-sdk)
