# PDF Splitter CLI

A practical Python CLI tool for splitting PDF files using outline bookmarks.

The tool is optimized for O'Reilly-style technical books with nested outlines, while remaining usable for any PDF with a valid outline.

## Features

- **Smart splitting by outline** with configurable depth (`--max-depth`).
- **Dry-run planning** (`--dry-run`) so you can inspect output before writing files.
- **Regex filtering** (`--include-regex`, `--exclude-regex`, `--ignore-case`).
- **Front/back matter policies** (`keep`, `merge`, `skip`).
- **Config file support** (`--config` with JSON or YAML).
- **Safe filenames** via sanitization.
- **Operational logging** (`--verbose`, `--quiet`, `--log-file`).

## Requirements

- Python 3.9+
- Dependencies in `requirements.txt`

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python -m src.cli <input_file> [options]
```

### Main options

- `-o, --output`: Output directory. Defaults to `<input_stem>_split`.
- `-d, --max-depth`: Max outline depth (default: `1`).
- `--dry-run`: Print planned splits only.
- `--include-regex`: Include only matching section titles.
- `--exclude-regex`: Exclude matching section titles.
- `--ignore-case`: Case-insensitive regex matching.
- `--front-matter {keep,merge,skip}`
- `--back-matter {keep,merge,skip}`
- `--config`: Path to `.json`/`.yaml` config.
- `--verbose`: Debug logs.
- `--quiet`: Errors only.
- `--log-file`: Write logs to a file.

### Examples

```bash
# Basic split
python -m src.cli my_book.pdf

# Dry run with depth 2
python -m src.cli my_book.pdf --max-depth 2 --dry-run

# Exclude front matter-like titles and write to custom folder
python -m src.cli my_book.pdf --exclude-regex "^(Preface|Foreword)" --ignore-case -o ./chapters

# Use config file
python -m src.cli my_book.pdf --config ./configs/oreilly.yaml
```

## Config file example

```yaml
max_depth: 2
front_matter: skip
back_matter: merge
include_regex: "Chapter|Part"
ignore_case: true
```

## Exit codes

- `0`: Success
- `2`: CLI argument or config parsing error
- `3`: Input read error (missing/invalid PDF)
- `4`: Output write error
- `5`: No usable outline sections after filtering
- `6`: Unexpected runtime error

## Quality checks

```bash
ruff format .
ruff check .
python -m pytest -q
```

## License

MIT License. See [LICENSE](LICENSE).
