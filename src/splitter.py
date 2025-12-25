import os
from typing import List, Tuple, Optional, Any
from pypdf import PdfReader, PdfWriter
from src.utils import sanitize_filename

class PDFSplitter:
    def __init__(self, pdf_path: str, output_dir: str):
        self.pdf_path = pdf_path
        self.output_dir = output_dir

    def split(self, max_depth: int = 1) -> None:
        """
        PDFのアウトラインに基づいてファイルを分割する。
        
        Args:
            max_depth (int): 解析するアウトラインの最大深度。1はトップレベルのみ。
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

            # 再帰的にアウトラインを収集
            raw_sections = []
            self._collect_outline_items(reader, outline, 0, raw_sections)
            
            # 深度制限と重複解決
            sections = self._process_sections(raw_sections, max_depth)
            
            if not sections:
                print("No sections found after filtering.")
                return

            self._write_sections(reader, sections, total_pages)
            print("Split complete.")

        except Exception as e:
            print(f"An error occurred during splitting: {e}")
            raise e

    def _collect_outline_items(self, reader: PdfReader, outline_items: List[Any], current_depth: int, result: List[dict]) -> None:
        """
        アウトラインを再帰的に走査して項目を収集する。
        """
        for item in outline_items:
            if isinstance(item, list):
                self._collect_outline_items(reader, item, current_depth + 1, result)
            else:
                try:
                    title = item.title
                    page_num = reader.get_destination_page_number(item)
                    result.append({
                        "title": title,
                        "page": page_num,
                        "depth": current_depth
                    })
                except Exception as e:
                    print(f"Skipping outline item due to error: {e}")
                    continue

    def _process_sections(self, raw_sections: List[dict], max_depth: int) -> List[Tuple[str, int]]:
        """
        収集したセクションを処理する：
        1. 深度でフィルタリング
        2. ページ番号順にソート
        3. 同じページを指す項目は、最も階層が浅い（depthが小さい）ものを優先
        """
        # 1. フィルタリング (max_depthは1-indexed)
        filtered = [s for s in raw_sections if s["depth"] < max_depth]
        
        # 2. ソート
        filtered.sort(key=lambda x: (x["page"], x["depth"]))
        
        # 3. 重複解決
        unique_sections = []
        if not filtered:
            return []

        last_page = -1
        for s in filtered:
            if s["page"] != last_page:
                unique_sections.append((s["title"], s["page"]))
                last_page = s["page"]
            else:
                # 同じページの場合は、ソート済みなので既に最小depthのものが追加されているはず
                continue
                
        return unique_sections

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
