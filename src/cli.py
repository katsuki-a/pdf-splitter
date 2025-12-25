import argparse
import os
import sys
from src.splitter import PDFSplitter

def main():
    parser = argparse.ArgumentParser(
        description="Split a PDF file into multiple files based on its outline (bookmarks)."
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the input PDF file."
    )
    
    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        help="Directory to save the split PDF files. Defaults to a folder named after the input file."
    )

    parser.add_argument(
        "-d", "--max-depth",
        type=int,
        default=1,
        help="Maximum depth of the outline to process. Default is 1 (top-level items only)."
    )

    args = parser.parse_args()
    
    input_path = args.input_file
    output_dir = args.output_dir
    max_depth = args.max_depth

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # 出力ディレクトリが指定されていない場合、入力ファイル名（拡張子なし）を使用
    if not output_dir:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = os.path.join(os.path.dirname(input_path), base_name + "_split")

    print(f"Input File: {input_path}")
    print(f"Output Directory: {output_dir}")
    print(f"Max Depth: {max_depth}")

    splitter = PDFSplitter(input_path, output_dir)
    splitter.split(max_depth=max_depth)

if __name__ == "__main__":
    main()
