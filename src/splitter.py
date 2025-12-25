import os
from typing import List, Tuple, Optional, Any
from pypdf import PdfReader, PdfWriter
from src.utils import sanitize_filename

class PDFSplitter:
    def __init__(self, pdf_path: str, output_dir: str):
        self.pdf_path = pdf_path
        self.output_dir = output_dir

    def split(self) -> None:
        """
        PDFのアウトラインに基づいてファイルを分割する。
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")

        try:
            reader = PdfReader(self.pdf_path)
            total_pages = len(reader.pages)
            outline = reader.outline
            
            if not outline:
                print("No outline found. Cannot split by chapters.")
                return

            sections = self._parse_outline(reader, outline)
            self._write_sections(reader, sections, total_pages)
            print("Split complete.")

        except Exception as e:
            print(f"An error occurred during splitting: {e}")
            raise e

    def _parse_outline(self, reader: PdfReader, outline: List[Any]) -> List[Tuple[str, int]]:
        """
        アウトラインを解析し、(タイトル, 開始ページ) のリストを返す。
        現在はトップレベルの項目のみを対象とする。
        """
        sections = []
        for item in outline:
            if isinstance(item, list):
                # ネストされた項目はスキップ (将来的な拡張ポイント)
                continue
            
            try:
                title = item.title
                page_num = reader.get_destination_page_number(item)
                sections.append((title, page_num))
            except Exception as e:
                print(f"Skipping outline item due to error: {e}")
                continue
        
        # ページ番号順にソート
        sections.sort(key=lambda x: x[1])
        return sections

    def _write_sections(self, reader: PdfReader, sections: List[Tuple[str, int]], total_pages: int) -> None:
        """
        抽出されたセクション情報に基づいてPDFファイルを書き出す。
        """
        print(f"Found {len(sections)} sections. Starting split...")

        for i in range(len(sections)):
            title, start_page = sections[i]
            
            # 終了ページの決定
            if i < len(sections) - 1:
                end_page = sections[i+1][1]
            else:
                end_page = total_pages
            
            # 無効なセクションのスキップ
            if start_page >= end_page:
                print(f"Skipping empty or invalid section: {title} (Pages {start_page}-{end_page})")
                continue

            output_filename = f"{i:02d}_{sanitize_filename(title)}.pdf"
            output_path = os.path.join(self.output_dir, output_filename)
            
            self._write_single_pdf(reader, start_page, end_page, output_path)
            print(f"Saved: {output_filename} (Pages {start_page + 1}-{end_page})")

    def _write_single_pdf(self, reader: PdfReader, start_page: int, end_page: int, output_path: str) -> None:
        """
        指定されたページ範囲を新しいPDFファイルとして保存する。
        """
        writer = PdfWriter()
        for page_idx in range(start_page, end_page):
            writer.add_page(reader.pages[page_idx])
        
        with open(output_path, "wb") as f_out:
            writer.write(f_out)
