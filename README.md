# PDF Splitter CLI

A robust, general-purpose Python CLI tool for splitting PDF files based on their outline (bookmarks). 

Originally optimized for O'Reilly-style technical books (handling structures like Parts -> Chapters), this tool can be used with any PDF that has a valid outline.

## Features

*   **Smart Splitting:** Automatically detects the PDF outline and splits the document into separate files for each section.
*   **Filename Sanitization:** Generates safe filenames from chapter titles, removing illegal characters.
*   **Flexible Output:** Allows specifying a custom output directory. Defaults to a folder named after the input file.
*   **Cross-Platform:** Works on Windows, macOS, and Linux (Python based).

## Requirements

*   Python 3.9+
*   `pypdf`

## Installation

1.  Clone this repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  Create and activate a virtual environment (recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To split a PDF file, run the `src.cli` module using Python:

```bash
python -m src.cli <input_file_path> [-o <output_directory>]
```

### Arguments

*   `input_file`: Path to the input PDF file (Required).
*   `-o`, `--output`: Directory to save the split PDF files. If omitted, a directory named `<input_filename>_split` will be created in the same location as the input file.

### Examples

Split a file using default output settings:
```bash
python -m src.cli my_book.pdf
```

Split a file and save to a specific directory:
```bash
python -m src.cli my_book.pdf --output ./chapters/
```

## Project Structure

*   `src/`: Source code directory.
    *   `cli.py`: Entry point for the CLI.
    *   `splitter.py`: Core logic for PDF splitting.
    *   `utils.py`: Utility functions (e.g., filename sanitization).
*   `requirements.txt`: Python dependencies.
*   `AGENTS.md`: Project directives and architectural plans.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
