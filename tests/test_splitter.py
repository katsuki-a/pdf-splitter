import os
import pytest
from pypdf import PdfWriter, PdfReader
from src.splitter import PDFSplitter

@pytest.fixture
def dummy_pdf_with_outline(tmp_path):
    """
    テスト用にアウトライン付きの単純なPDFを作成してパスを返すフィクスチャ
    構成:
    - Page 0: Title Page
    - Page 1: Chapter 1 Start (Bookmark: "Chapter 1")
    - Page 2: Chapter 1 End
    - Page 3: Chapter 2 Start (Bookmark: "Chapter 2")
    - Page 4: Chapter 2 End
    """
    pdf_path = tmp_path / "test_book.pdf"
    writer = PdfWriter()

    # 5ページ分の空白ページを追加
    for _ in range(5):
        writer.add_blank_page(width=100, height=100)

    # アウトライン（ブックマーク）を追加
    # add_outline_item(title, page_number)
    writer.add_outline_item("Chapter 1", 1)
    writer.add_outline_item("Chapter 2", 3)

    with open(pdf_path, "wb") as f:
        writer.write(f)

    return str(pdf_path)

def test_split_creates_files(dummy_pdf_with_outline, tmp_path):
    """分割処理が実行され、ファイルが生成されるかテスト"""
    output_dir = tmp_path / "output"
    
    splitter = PDFSplitter(dummy_pdf_with_outline, str(output_dir))
    splitter.split()

    # 出力ディレクトリが作成されているか
    assert output_dir.exists()

    # 生成されたファイルを確認
    files = sorted(list(output_dir.glob("*.pdf")))
    assert len(files) == 2
    
    # ファイル名のチェック
    assert "00_Chapter 1.pdf" in files[0].name
    assert "01_Chapter 2.pdf" in files[1].name

def test_split_content_pages(dummy_pdf_with_outline, tmp_path):
    """分割されたPDFのページ数が正しいか検証"""
    output_dir = tmp_path / "output_content"
    
    splitter = PDFSplitter(dummy_pdf_with_outline, str(output_dir))
    splitter.split()

    files = sorted(list(output_dir.glob("*.pdf")))
    
    # Chapter 1: Page 1 to 3 (Total 2 pages: 1, 2)
    # Book structure: 0, [1, 2], [3, 4]
    # Chapter 1 starts at 1. Next starts at 3. So it covers 1, 2.
    reader1 = PdfReader(files[0])
    assert len(reader1.pages) == 2

    # Chapter 2: Page 3 to End (Total 2 pages: 3, 4)
    reader2 = PdfReader(files[1])
    assert len(reader2.pages) == 2

def test_no_outline_handling(tmp_path):
    """アウトラインがないPDFを処理した場合の挙動テスト"""
    # アウトラインなしPDF作成
    pdf_path = tmp_path / "no_outline.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    output_dir = tmp_path / "output_none"
    
    splitter = PDFSplitter(str(pdf_path), str(output_dir))
    splitter.split()

    # 出力ディレクトリは作成されるが、ファイルは空のはず（またはログが出るだけ）
    if output_dir.exists():
        assert len(list(output_dir.glob("*.pdf"))) == 0
