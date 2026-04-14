"""CLI entry point for pdf splitting."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from src.splitter import PDFSplitter, SplitOptions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Split a PDF file into multiple files based on its outline.",
    )
    parser.add_argument("input_file", help="Path to the input PDF file.")
    parser.add_argument(
        "-o",
        "--output",
        dest="output_dir",
        help=(
            "Directory to save split PDF files. Defaults to <input_file_stem>_split "
            "in the same directory as the input PDF."
        ),
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=None,
        help="Maximum outline depth to process. 1 means top-level only.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned split result without writing files.",
    )
    parser.add_argument(
        "--include-regex",
        help="Only keep sections whose titles match this regex.",
    )
    parser.add_argument(
        "--exclude-regex",
        help="Exclude sections whose titles match this regex.",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Use case-insensitive matching for include/exclude regex.",
    )
    parser.add_argument(
        "--front-matter",
        choices=["keep", "merge", "skip"],
        default=None,
        help="How to handle front matter sections.",
    )
    parser.add_argument(
        "--back-matter",
        choices=["keep", "merge", "skip"],
        default=None,
        help="How to handle back matter sections.",
    )
    parser.add_argument(
        "--config",
        help="Path to a JSON or YAML config file.",
    )
    parser.add_argument("--verbose", action="store_true", help="Show debug logs.")
    parser.add_argument("--quiet", action="store_true", help="Only show errors.")
    parser.add_argument("--log-file", help="Write logs to the specified file path.")
    return parser


def _load_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}

    with open(path, encoding="utf-8") as config_file:
        if path.endswith(".json"):
            return json.load(config_file)

        if path.endswith((".yaml", ".yml")):
            try:
                import yaml  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "YAML config requested but PyYAML is not installed."
                ) from exc
            data = yaml.safe_load(config_file)
            return data or {}

    raise ValueError("Config file must be .json, .yaml, or .yml")


def _resolve_option(
    cli_value: Any, config: dict[str, Any], key: str, default: Any
) -> Any:
    if cli_value is not None:
        return cli_value
    if key in config:
        return config[key]
    return default


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet cannot be used together.")

    try:
        config = _load_config(args.config)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: failed to load config: {exc}", file=sys.stderr)
        sys.exit(2)

    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"Error: input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(3)

    output_dir = _resolve_option(args.output_dir, config, "output_dir", None)
    if not output_dir:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = os.path.join(os.path.dirname(input_path), f"{base_name}_split")

    splitter = PDFSplitter(
        input_path,
        output_dir,
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=args.log_file,
    )

    options = SplitOptions(
        max_depth=_resolve_option(args.max_depth, config, "max_depth", 1),
        dry_run=bool(args.dry_run or config.get("dry_run", False)),
        include_regex=_resolve_option(
            args.include_regex,
            config,
            "include_regex",
            None,
        ),
        exclude_regex=_resolve_option(
            args.exclude_regex,
            config,
            "exclude_regex",
            None,
        ),
        ignore_case=bool(args.ignore_case or config.get("ignore_case", False)),
        front_matter=_resolve_option(args.front_matter, config, "front_matter", "keep"),
        back_matter=_resolve_option(args.back_matter, config, "back_matter", "keep"),
    )

    exit_code = splitter.split(options)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
