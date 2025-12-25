import sys
from pypdf import PdfReader

def check_structure(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        print(f"Total pages: {len(reader.pages)}")
        
        outline = reader.outline
        if not outline:
            print("No outline found in this PDF.")
            return

        print("Outline found. Top level items:")
        for i, item in enumerate(outline):
            if isinstance(item, list):
                print(f"  [Item {i}] is a nested list (subprocess needed for full recursion)")
            else:
                # pypdfのDestinationオブジェクトからタイトルとページ番号を取得
                try:
                    title = item.title
                    # ページ番号の取得は少し複雑な場合がありますが、まずはタイトルだけでも
                    print(f"  - {title}")
                except AttributeError:
                    print(f"  [Item {i}] (AttributeError accessing title)")

    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    pdf_file = "Googleのソフトウェアエンジニアリング.pdf"
    check_structure(pdf_file)
