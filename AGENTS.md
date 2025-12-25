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
The core CLI structure is implemented using a modular approach.

*   **CLI Framework:** `argparse` is used for argument parsing.
*   **Modular Design:**
    *   `src/cli.py`: Entry point handling user input and configuration.
    *   `src/splitter.py`: Core logic for recursive outline parsing, conflict resolution, and PDF writing.
    *   `src/utils.py`: Filename sanitization and string manipulation.
*   **Dependency Management:** `requirements.txt` is maintained (primary dependency: `pypdf`).

## 4. Development Standards
*   **Language:** Python 3.9+
*   **Style:** Follow PEP 8.
*   **Documentation:** Use Google-style docstrings.
*   **Typing:** Use Python type hints (`typing` module) for all functions.
*   **Testing:** Unit tests are implemented using `pytest`. Run tests with `python -m pytest`.

## 5. Current State vs. Desired State
*   **Current:** 
    *   Modular CLI tool with `argparse` support.
    *   **Recursive Outline Support:** Can traverse nested bookmarks with configurable depth (`--max-depth`).
    *   **Smart Conflict Resolution:** Handles multiple outline items pointing to the same page by prioritizing higher-level items.
    *   **Automated Sanitization:** Generates safe filenames from chapter titles.
    *   **Test Suite:** Unit tests cover core splitting logic and utilities.
*   **Desired:** 
    *   **Selective Splitting:** Support for regex-based title exclusion or inclusion (e.g., skip "Front Matter").
    *   **Configuration Files:** Support for per-book configuration (YAML/JSON) to save preferred depth and exclusion rules.
    *   **Enhanced Metadata:** Preservation of original metadata and internal links in split files where possible.
    *   **Progress Visualization:** Add a progress bar (e.g., `tqdm`) for processing large PDF files.
    *   **Error Robustness:** Better handling of malformed PDF outlines or missing destinations.
    *   **CI Integration:** GitHub Actions for automated linting and testing.

