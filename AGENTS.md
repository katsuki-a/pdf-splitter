# AGENTS.md - Project Directive

## 1. Project Mission
**Goal:** Transform the current prototype into a robust, general-purpose **Python CLI Tool** for splitting PDF files.
**Target:** Specifically optimized for **O'Reilly-style technical books** (which often contain nested outlines like Parts -> Chapters -> Sections), but usable for any PDF with a valid outline.

## 2. Core Functionality
The tool must support the following features via Command Line Interface:

*   **Input Handling:** Accept an arbitrary PDF file path as an argument.
*   **Output Management:** Accept a destination directory (defaulting to a folder named after the PDF).
*   **Smart Splitting:**
    *   Read the PDF outline (bookmarks).
    *   Handle hierarchical structures (e.g., decide whether to split at "Part" level or "Chapter" level, or flatten them).
    *   Handle "Front Matter" (Preface, Foreword) and "Back Matter" (Index, Colophon).
*   **Sanitization:** Automatically generate safe filenames from chapter titles (removing illegal characters like `/`, `:`, etc.).

## 3. Architecture & Refactoring Plan
The current codebase consists of hardcoded scripts (`split_pdf_by_outline.py`). The next phase involves refactoring into a proper Python package structure:

*   **CLI Framework:** Use `click` or `argparse` for argument parsing.
*   **Modular Design:**
    *   `src/cli.py`: Entry point handling user input.
    *   `src/splitter.py`: Core logic for parsing outlines and writing PDF pages.
    *   `src/utils.py`: Filename sanitization and string manipulation.
*   **Dependency Management:** Maintain `requirements.txt` or `pyproject.toml` (currently using `pypdf`).

## 4. Development Standards
*   **Language:** Python 3.9+
*   **Style:** Follow PEP 8.
*   **Documentation:** Use Google-style docstrings.
*   **Typing:** Use Python type hints (`typing` module) for all functions.
*   **Testing:** Implement unit tests using `pytest` (future scope).

## 5. Current State vs. Desired State
*   **Current:** `split_pdf_by_outline.py` hardcodes "Googleのソフトウェアエンジニアリング.pdf".
*   **Desired:** `pdf-splitter <input_file.pdf> --output <dir>` runs the tool on any file.
