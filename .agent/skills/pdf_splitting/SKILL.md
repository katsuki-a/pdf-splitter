---
name: pdf_splitting
description: >
    プロジェクト独自のPDF分割ツールを使用してPDFファイルを分割する方法です。
    このスキルでは、環境設定、スプリッターCLIコマンドの実行（入力パス、出力ディレクトリ、
    分割深度などの適切な引数を使用）、およびModuleNotFoundErrorなどの一般的な問題のトラブルシューティングについて解説します。
---

# PDF分割スキル

## 概要
このスキルは、`pdf-splitter`ツールを使用して、アウトライン（しおり）に基づいてPDFファイルを複数の小さなファイルに分割する方法を説明します。大きな技術書を個別の章や節に分割する場合に特に便利です。

## 前提条件
- Python 3.9以上
- プロジェクトルートに仮想環境 (`.venv`) がセットアップされていること。
- 依存関係がインストールされていること (`pip install -r requirements.txt`)。

## コマンドの使用方法

スプリッターを実行するには、プロジェクトのルートディレクトリから以下のコマンド形式を使用してください：

```bash
PYTHONPATH=. .venv/bin/python src/cli.py <input_pdf_path> [-o <output_directory>] [-d <max_depth>]
```

### 引数:
- `<input_pdf_path>`: (必須) 元のPDFファイルへのパス。
- `-o`, `--output`: (任意) 分割されたファイルを保存するディレクトリ。デフォルトは `<input_filename>_split` です。
- `-d`, `--max-depth`: (任意) 処理するアウトラインの最大深度。`1` はトップレベルの章のみを意味します。`2` はサブチャプターを含みます。デフォルトは `1` です。

## 使用例

### 章ごとに分割（トップレベルのみ）
PDFをトップレベルの章（例：第1章、第2章）に分割します。

```bash
PYTHONPATH=. .venv/bin/python src/cli.py "pdf/book/my_book.pdf" -o "pdf/book/my_book_chapters" -d 1
```

### 節ごとに分割（サブチャプター）
PDFをより細かいセクション（例：セクション1.1、セクション1.2）に分割します。

```bash
PYTHONPATH=. .venv/bin/python src/cli.py "pdf/book/my_book.pdf" -o "pdf/book/my_book_sections" -d 2
```

## トラブルシューティング

### ModuleNotFoundError: No module named 'src'
`ModuleNotFoundError: No module named 'src'` というエラーが発生した場合、Pythonが `src` パッケージを見つけられないことを意味します。コマンドをプロジェクトルートから実行し、`PYTHONPATH=.` が設定されていることを確認してください。

**正しい例:**
```bash
PYTHONPATH=. .venv/bin/python src/cli.py ...
```

**誤った例:**
```bash
python src/cli.py ...  # PYTHONPATHを設定していない
cd src && python cli.py ... # 間違ったディレクトリから実行している
```
