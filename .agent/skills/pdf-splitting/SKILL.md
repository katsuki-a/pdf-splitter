---
name: pdf-splitting
description: Split PDFs with this repository's outline-based CLI. Use when Codex needs to run, preview, validate, or troubleshoot PDF splitting in this project, including input/output paths, max depth, dry-run previews, uv setup, and local Ruff/pytest checks.
---

# PDF Splitting

Use commands from the repository root.

## Setup

- Prefer `uv`.
- Install runtime dependencies with `uv venv && uv pip install -r requirements.txt`.
- Install development tooling with `uv pip install -r requirements-dev.txt`.

## Run

```bash
uv run python -m src.cli "<input_pdf_path>" [-o "<output_directory>"] [-d <max_depth>] [--dry-run]
```

- Use `--dry-run` first when checking an unfamiliar PDF outline. It prints the planned files and page ranges without writing PDFs.
- Use `-d 1` for top-level outline entries; use `-d 2` when chapters are nested under parts.
- Omit `-o` to write to `<input_filename>_split` next to the input PDF.
- Use dry-run as the supported preview path for outline-derived output.

## Examples

Preview:

```bash
uv run python -m src.cli "pdf/book/my_book.pdf" --dry-run -d 1
```

Split to a specific directory:

```bash
uv run python -m src.cli "pdf/book/my_book.pdf" -o "pdf/book/my_book_chapters" -d 1
```

## Validate

```bash
uv run ruff check .
uv run ruff format --check .
uv run python -m pytest
```

If module imports fail, verify the command is running from the repository root with `python -m src.cli`.
