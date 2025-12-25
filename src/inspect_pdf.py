import sys
from pypdf import PdfReader

def inspect_outline(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        print(f"File: {pdf_path}")
        print(f"Total Pages: {len(reader.pages)}")
        
        outline = reader.outline
        if not outline:
            print("No outline found.")
            return

        print("\n--- Outline Structure ---")
        _print_outline_recursive(reader, outline)

    except Exception as e:
        print(f"Error: {e}")

def _print_outline_recursive(reader, outline_items, level=0):
    for item in outline_items:
        indent = "  " * level
        
        if isinstance(item, list):
            # 入れ子のリスト（サブチャプター）
            _print_outline_recursive(reader, item, level + 1)
        else:
            try:
                title = item.title
                # ページ番号を取得
                page_num = reader.get_destination_page_number(item)
                print(f"{indent}- {title} (Page: {page_num})")
            except Exception as e:
                # 何らかの理由でページ番号が取得できない、またはタイトルがない場合
                print(f"{indent}- [Error reading item]: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.inspect_pdf <pdf_file>")
        sys.exit(1)
    
    inspect_outline(sys.argv[1])
