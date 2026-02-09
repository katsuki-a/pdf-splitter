---
name: pdf_splitting
description: >
    Splitting PDF files using the project's custom PDF splitter tool.
    This skill covers setting up the environment, running the splitter CLI commands
    (with appropriate arguments for input path, output directory, and split depth),
    and troubleshooting common issues like ModuleNotFoundError.
---

# PDF Splitting Skill

## Overview
This skill outlines how to use the `pdf-splitter` tool to divide a PDF file into multiple smaller files based on its outline (bookmarks). It is particularly useful for splitting large technical books into individual chapters or sections.

## Prerequisites
- Python 3.9+
- A virtual environment (`.venv`) set up in the project root.
- Dependencies installed (`pip install -r requirements.txt`).

## Command Usage

To run the splitter, use the following command format from the project root directory:

```bash
PYTHONPATH=. .venv/bin/python src/cli.py <input_pdf_path> [-o <output_directory>] [-d <max_depth>]
```

### Arguments:
- `<input_pdf_path>`: (Required) Path to the source PDF file.
- `-o`, `--output`: (Optional) Directory to save the split files. Defaults to `<input_filename>_split`.
- `-d`, `--max-depth`: (Optional) Maximum depth of the outline to process. `1` means top-level chapters only. `2` includes sub-chapters. Default is `1`.

## Examples

### Split by Chapters (Top-Level Only)
Splits the PDF into top-level chapters (e.g., Chapter 1, Chapter 2).

```bash
PYTHONPATH=. .venv/bin/python src/cli.py "pdf/book/my_book.pdf" -o "pdf/book/my_book_chapters" -d 1
```

### Split by Sections (Sub-Chapters)
Splits the PDF into finer sections (e.g., Section 1.1, Section 1.2).

```bash
PYTHONPATH=. .venv/bin/python src/cli.py "pdf/book/my_book.pdf" -o "pdf/book/my_book_sections" -d 2
```

## Troubleshooting

### ModuleNotFoundError: No module named 'src'
If you encounter `ModuleNotFoundError: No module named 'src'`, it means Python cannot find the `src` package. Ensure you are running the command from the project root and have set `PYTHONPATH=.`.

**Correct:**
```bash
PYTHONPATH=. .venv/bin/python src/cli.py ...
```

**Incorrect:**
```bash
python src/cli.py ...  # Failing to set PYTHONPATH
cd src && python cli.py ... # Running from the wrong directory
```
