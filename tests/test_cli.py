import json
import subprocess
import sys

from pypdf import PdfWriter


def _create_pdf(path, with_outline=True):
    writer = PdfWriter()
    for _ in range(3):
        writer.add_blank_page(width=100, height=100)
    if with_outline:
        writer.add_outline_item("Chapter 1", 0)
        writer.add_outline_item("Chapter 2", 1)
    with open(path, "wb") as file_handle:
        writer.write(file_handle)


def test_cli_dry_run(tmp_path):
    pdf_path = tmp_path / "book.pdf"
    _create_pdf(pdf_path)

    cmd = [
        sys.executable,
        "-m",
        "src.cli",
        str(pdf_path),
        "--dry-run",
    ]
    result = subprocess.run(
        cmd, cwd="/workspace/pdf-splitter", capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "Dry run" in result.stderr
    assert not (tmp_path / "book_split").exists()


def test_cli_config_json(tmp_path):
    pdf_path = tmp_path / "book.pdf"
    _create_pdf(pdf_path)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "front_matter": "skip",
                "output_dir": str(tmp_path / "out"),
                "include_regex": "Chapter",
            }
        ),
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "src.cli", str(pdf_path), "--config", str(config_path)]
    result = subprocess.run(
        cmd, cwd="/workspace/pdf-splitter", capture_output=True, text=True
    )

    assert result.returncode == 0
    assert (tmp_path / "out").exists()


def test_cli_returns_error_for_missing_input(tmp_path):
    cmd = [sys.executable, "-m", "src.cli", str(tmp_path / "missing.pdf")]
    result = subprocess.run(
        cmd, cwd="/workspace/pdf-splitter", capture_output=True, text=True
    )

    assert result.returncode == 3
    assert "not found" in result.stderr
