import os

import pytest
from pypdf import PdfReader, PdfWriter

from src.splitter import EXIT_NO_SECTIONS, EXIT_OK, PDFSplitter, SplitOptions


@pytest.fixture
def dummy_pdf_with_outline(tmp_path):
    """Create a small outline PDF for tests."""
    pdf_path = tmp_path / "test_book.pdf"
    writer = PdfWriter()

    for _ in range(5):
        writer.add_blank_page(width=100, height=100)

    writer.add_outline_item("Preface", 0)
    writer.add_outline_item("Chapter 1", 1)
    writer.add_outline_item("Chapter 2", 3)

    with open(pdf_path, "wb") as f:
        writer.write(f)

    return str(pdf_path)


def test_split_creates_files(dummy_pdf_with_outline, tmp_path):
    """Split operation should generate chapter PDF files."""
    output_dir = tmp_path / "output"

    splitter = PDFSplitter(dummy_pdf_with_outline, str(output_dir))
    exit_code = splitter.split(SplitOptions())

    assert exit_code == EXIT_OK
    assert output_dir.exists()

    files = sorted(output_dir.glob("*.pdf"))
    assert len(files) == 3
    assert files[0].name == "00_Preface.pdf"
    assert files[1].name == "01_Chapter 1.pdf"
    assert files[2].name == "02_Chapter 2.pdf"


def test_split_content_pages(dummy_pdf_with_outline, tmp_path):
    """Generated split PDFs should have expected page counts."""
    output_dir = tmp_path / "output_content"

    splitter = PDFSplitter(dummy_pdf_with_outline, str(output_dir))
    exit_code = splitter.split(SplitOptions())

    assert exit_code == EXIT_OK
    files = sorted(output_dir.glob("*.pdf"))

    reader_preface = PdfReader(files[0])
    reader_ch1 = PdfReader(files[1])
    reader_ch2 = PdfReader(files[2])

    assert len(reader_preface.pages) == 1
    assert len(reader_ch1.pages) == 2
    assert len(reader_ch2.pages) == 2


def test_no_outline_handling(tmp_path):
    """PDF without outline should return no-section exit code."""
    pdf_path = tmp_path / "no_outline.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    output_dir = tmp_path / "output_none"
    splitter = PDFSplitter(str(pdf_path), str(output_dir))
    exit_code = splitter.split(SplitOptions())

    assert exit_code == EXIT_NO_SECTIONS
    assert not output_dir.exists()


def test_nested_split_conflict_resolution(tmp_path):
    """Conflict resolution should keep shallower section for same page."""
    pdf_path = tmp_path / "nested_test.pdf"
    writer = PdfWriter()
    for _ in range(10):
        writer.add_blank_page(width=100, height=100)

    writer.add_outline_item("Root 1", 0)
    part_1 = writer.add_outline_item("Part 1", 2)
    writer.add_outline_item("Chapter 1", 2, parent=part_1)
    chapter_2 = writer.add_outline_item("Chapter 2", 4)
    writer.add_outline_item("Section 2.1", 4, parent=chapter_2)

    with open(pdf_path, "wb") as f:
        writer.write(f)

    output_dir = tmp_path / "output_nested"
    splitter = PDFSplitter(str(pdf_path), str(output_dir))

    exit_code = splitter.split(SplitOptions(max_depth=2))

    assert exit_code == EXIT_OK
    files = sorted(output_dir.glob("*.pdf"))

    assert len(files) == 3
    assert "00_Root 1.pdf" in files[0].name
    assert "01_Part 1.pdf" in files[1].name
    assert "02_Chapter 2.pdf" in files[2].name

    for file_path in files:
        assert "Section 2.1" not in file_path.name


def test_regex_filters_and_case_insensitive(dummy_pdf_with_outline, tmp_path):
    """Regex include and exclude should filter section names."""
    output_dir = tmp_path / "output_filter"
    splitter = PDFSplitter(dummy_pdf_with_outline, str(output_dir))

    exit_code = splitter.split(
        SplitOptions(
            include_regex="chapter",
            exclude_regex="2",
            ignore_case=True,
        )
    )

    assert exit_code == EXIT_OK
    files = sorted(output_dir.glob("*.pdf"))
    assert len(files) == 1
    assert files[0].name == "00_Chapter 1.pdf"


def test_front_matter_skip(dummy_pdf_with_outline, tmp_path):
    """Skipping front matter should remove preface output."""
    output_dir = tmp_path / "output_front_skip"
    splitter = PDFSplitter(dummy_pdf_with_outline, str(output_dir))

    exit_code = splitter.split(SplitOptions(front_matter="skip"))

    assert exit_code == EXIT_OK
    files = sorted(output_dir.glob("*.pdf"))
    assert len(files) == 2
    assert files[0].name == "00_Chapter 1.pdf"


def test_dry_run_generates_no_output_files(dummy_pdf_with_outline, tmp_path):
    """Dry run mode should not write any PDF output."""
    output_dir = tmp_path / "output_dry"
    splitter = PDFSplitter(dummy_pdf_with_outline, str(output_dir))

    exit_code = splitter.split(SplitOptions(dry_run=True))

    assert exit_code == EXIT_OK
    assert not os.path.exists(output_dir)
