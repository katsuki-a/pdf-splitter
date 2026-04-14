"""Utility command to inspect PDF outline structure."""

from __future__ import annotations

import sys
from typing import Any

from pypdf import PdfReader


def inspect_outline(pdf_path: str) -> int:
    """Print outline details for a PDF.

    Args:
        pdf_path: Path to input PDF.

    Returns:
        Process-style exit code.
    """
    try:
        reader = PdfReader(pdf_path)
    except OSError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"File: {pdf_path}")
    print(f"Total Pages: {len(reader.pages)}")

    outline = reader.outline
    if not outline:
        print("No outline found.")
        return 0

    print("\n--- Outline Structure ---")
    _print_outline_recursive(reader, outline)
    return 0


def _print_outline_recursive(
    reader: PdfReader,
    outline_items: list[Any],
    level: int = 0,
) -> None:
    for item in outline_items:
        indent = "  " * level

        if isinstance(item, list):
            _print_outline_recursive(reader, item, level + 1)
            continue

        try:
            title = item.title
            page_num = reader.get_destination_page_number(item)
            print(f"{indent}- {title} (Page: {page_num})")
        except (AttributeError, ValueError, TypeError) as exc:
            print(f"{indent}- [Error reading item]: {exc}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.inspect_pdf <pdf_file>")
        sys.exit(1)

    sys.exit(inspect_outline(sys.argv[1]))
