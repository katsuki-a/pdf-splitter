# PDF Splitter CLI

A simple and efficient Python CLI tool for splitting PDF files based on their outline (bookmarks). 

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
    git clone https://github.com/katsuki-a/pdf-splitter.git
    cd pdf-splitter
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

To split a PDF file, you can run the tool as a module from the project root directory.

### Basic Usage

```bash
# Ensure you are in the project root directory
# and your virtual environment is activated
python -m src.cli <input_file_path> [-o <output_directory>] [-d <max_depth>]
```

Alternatively, if you encounter module import errors, you can explicitly set the `PYTHONPATH`:

```bash
PYTHONPATH=. python src/cli.py <input_file_path> ...
```

### Arguments

*   `input_file`: Path to the input PDF file (Required).
*   `-o`, `--output`: Directory to save the split PDF files. If omitted, a directory named `<input_filename>_split` will be created in the same location as the input file.
*   `-d`, `--max-depth`: Maximum depth of the outline to process. 
    *   `1`: Top-level chapters only (default).
    *   `2`: Chapters and sub-sections.

### Examples

**1. Split a file using default settings (top-level chapters only):**
```bash
python -m src.cli my_book.pdf
```

**2. Split a file including nested sections (up to depth 2):**
```bash
python -m src.cli my_book.pdf --max-depth 2
```

**3. Split a file and save to a specific directory:**
```bash
python -m src.cli my_book.pdf --output ./chapters/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
