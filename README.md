# AI-Based PDF Articles Generator

Generate your own text-only PDF datasets using AI. This tool is compatible with Ollama (local/cloud), OpenAI API, and any OpenAI-compatible API.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Scripts](#scripts)
  - [Generate Articles](#generate-articles-script)
  - [Duplicate Files](#duplicate-files-script)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Command-Line Arguments](#command-line-arguments)
- [Example Files](#example-files)
- [License](#license)

## Features

- **AI-Powered Generation**: Uses Ollama, OpenAI, or any OpenAI-compatible API
- **200 Topics**: 10 categories with 20 topics each
- **PDF Output**: Clean, text-only PDF documents
- **Metadata Tracking**: Automatic JSON metadata generation
- **Error Handling**: Failed PDF parsing saved as Markdown
- **Flexible Configuration**: Environment variables or command-line arguments

## Requirements

- Python 3.10+
- API access (Ollama, OpenAI, or compatible provider)

See [`requirements.txt`](requirements.txt) for Python dependencies.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kela4/ai-based-articles-generator.git
cd ai-based-articles-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```


## Quick Start

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# Generate 5 PDF articles using OpenAI
python src/generate_articles.py --num_pdfs 5 --model_name gpt-4o-mini

# Generate 3 PDF articles using Ollama Cloud
export OLLAMA_API_KEY=your-key...
python src/generate_articles.py \
    --api_variant ollama \
    --model_name ministral-3:3b-cloud \
    --num_pdfs 3
```

## Scripts

### Generate Articles Script

The main script generates AI-written articles on random topics from 200 predefined topics across 10 categories.

**Usage:**

```bash
# Using environment variables - OpenAI
export OPENAI_API_KEY=your-key-here
export API_VARIANT=openai
export MODEL_NAME=gpt-4o-mini
export NUM_PDFS=3
export OUTPUT_DIR=output_files
python src/generate_articles.py

# Using environment variables - Ollama
export OLLAMA_API_KEY=your-key-here
export API_VARIANT=ollama
export MODEL_NAME=ministral-3:3b-cloud
export MODEL_API_BASE_URL=https://ollama.com
export NUM_PDFS=3
export OUTPUT_DIR=output_files
python src/generate_articles.py

# Using command-line arguments - OpenAI
python src/generate_articles.py \
    --api_variant openai \
    --model_name gpt-4o-mini \
    --num_pdfs 3 \
    --output_dir output_files

# Using command-line arguments - Ollama
export OLLAMA_API_KEY=your-key-here
python src/generate_articles.py \
    --api_variant ollama \
    --model_name ministral-3:3b-cloud \
    --model_api_base_url https://ollama.com \
    --num_pdfs 3 \
    --output_dir output_files
```

**Output:**
- **PDF Files**: Text-only PDF documents in the output directory
- **Metadata File**: `metadata.json` in the output directory

*Metadata Format*

```json
[
  {
    "pdf_filename": "aazl6410ivli.pdf",
    "topic": "the history of coffee",
    "model_used": "gpt-4o-mini",
    "generated_at": "2026-02-25T20:28:20.099085"
  }
]
```

**Error Handling:**

If the model response cannot be parsed into a PDF, the script saves the text as a Markdown file. To skip failed parsing entirely and not save the text to markdown files, set `SKIP_FAILED_PARSING_FILES` to `true`:

```bash
export SKIP_FAILED_PARSING_FILES=true
python src/generate_articles.py --skip_failed_parsing_files true
```

### Duplicate Files Script

Create multiple copies of files for generating large datasets. (If the uniqueness of the documents is not so important.)

**Usage:**

```bash
# Using environment variables
export SOURCE_DIR=./input
export DESTINATION_DIR=./result
export NUM_COPIES=5
python src/duplicate_files.py

# Using command-line arguments
python src/duplicate_files.py \
    --source ./input \
    --dest ./output \
    --copies 7
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required for OpenAI variant |
| `OLLAMA_API_KEY` | Your Ollama API key | Required for Ollama variant |
| `API_VARIANT` | API provider: `openai`, `ollama`, or `openai_compatible` | `openai` |
| `MODEL_NAME` | Model identifier | empty - required to set model |
| `MODEL_API_BASE_URL` | API base URL | empty string - use default API url for API variants |
| `NUM_PDFS` | Number of PDFs to generate | `3` |
| `OUTPUT_DIR` | Output directory | `output_files` |
| `SKIP_FAILED_PARSING_FILES` | Skip failed parsing (save as Markdown if false) | `false` |

### Command-Line Arguments

#### Generate Articles Script

```bash
python src/generate_articles.py [OPTIONS]
```

| Argument | Description | Default |
|----------|-------------|---------|
| `--api_variant` | API provider (openai, ollama, compatible) | `openai` |
| `--model_name` |  Model name |  empty - required to set model |
| `--model_api_base_url` | API base URL | use default API url for API variants |
| `--num_pdfs` | Number of PDFs to generate | `3` |
| `--output_dir` | Output directory | `output_files` |
| `--skip_failed_parsing_files` | Skip failed parsing (true/false) | `false` |

#### Duplicate Files Script

```bash
python src/duplicate_files.py [OPTIONS]
```

| Argument | Description | Default |
|----------|-------------|---------|
| `--source` | Source directory | `./input` |
| `--dest` | Destination directory | `./output` |
| `--copies` | Number of copies per file | `10` |

## Example Files

In the folder [examples](examples) are some example PDFs generated with the src/generate_articles.py script.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) file for details.
