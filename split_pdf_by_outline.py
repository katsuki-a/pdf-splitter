import os
import re
from pypdf import PdfReader, PdfWriter

def sanitize_filename(filename):
    """ファイル名として使用できない文字を置換する"""
    return re.sub(r'[\\/*?:":<>|]', "_", filename)

def split_pdf_by_outline(pdf_path, output_dir="split_output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        outline = reader.outline
        
        if not outline:
            print("No outline found. Cannot split by chapters.")
            return

        # フラットな (タイトル, 開始ページ) のリストを作成する
        # ここではトップレベルの章立てのみを対象とする
        sections = []
        
        for item in outline:
            if isinstance(item, list):
                # ネストされた項目（節など）は今回は分割単位としない
                continue
            
            try:
                title = item.title
                page_num = reader.get_destination_page_number(item)
                sections.append((title, page_num))
            except Exception as e:
                print(f"Skipping item due to error: {e}")
                continue

        # ページ番号順にソート（念のため）
        sections.sort(key=lambda x: x[1])

        print(f"Found {len(sections)} sections. Starting split...")

        for i in range(len(sections)):
            title, start_page = sections[i]
            
            # 終了ページを決定
            if i < len(sections) - 1:
                end_page = sections[i+1][1]
            else:
                end_page = total_pages
            
            # 開始ページと終了ページが同じ（空の章など）場合や逆転している場合はスキップ
            if start_page >= end_page:
                print(f"Skipping empty or invalid section: {title} (Pages {start_page}-{end_page})")
                continue

            output_filename = f"{i:02d}_{sanitize_filename(title)}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            writer = PdfWriter()
            # ページを追加
            for page_idx in range(start_page, end_page):
                writer.add_page(reader.pages[page_idx])
            
            with open(output_path, "wb") as f_out:
                writer.write(f_out)
            
            print(f"Saved: {output_filename} (Pages {start_page + 1}-{end_page})")

        print("Split complete.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pdf_file = "Googleのソフトウェアエンジニアリング.pdf"
    split_pdf_by_outline(pdf_file)
