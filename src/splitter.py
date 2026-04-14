"""Core PDF splitting logic."""

from __future__ import annotations

import logging
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from pypdf import PdfReader, PdfWriter

from src.utils import sanitize_filename

EXIT_OK = 0
EXIT_INPUT_ERROR = 3
EXIT_OUTPUT_ERROR = 4
EXIT_NO_SECTIONS = 5
EXIT_UNEXPECTED_ERROR = 6

_FRONT_MATTER_PATTERN = re.compile(
    r"^(preface|foreword|introduction|toc|table of contents|about this book)",
    re.IGNORECASE,
)
_BACK_MATTER_PATTERN = re.compile(
    r"^(appendix|index|colophon|acknowledgments?|references?)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Section:
    """A flattened outline section.

    Attributes:
        title: Section title.
        page: 0-indexed start page.
        depth: Outline depth. Lower is shallower.
    """

    title: str
    page: int
    depth: int


@dataclass(frozen=True)
class SplitOptions:
    """Options controlling split behavior."""

    max_depth: int = 1
    dry_run: bool = False
    include_regex: str | None = None
    exclude_regex: str | None = None
    ignore_case: bool = False
    front_matter: str = "keep"
    back_matter: str = "keep"


class PDFSplitter:
    """Split PDF files using outline bookmarks."""

    def __init__(
        self,
        pdf_path: str,
        output_dir: str,
        *,
        verbose: bool = False,
        quiet: bool = False,
        log_file: str | None = None,
    ) -> None:
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.logger = self._build_logger(
            verbose=verbose, quiet=quiet, log_file=log_file
        )

    def split(self, options: SplitOptions) -> int:
        """Run the split workflow.

        Args:
            options: Runtime splitting options.

        Returns:
            Exit code that the CLI can propagate.
        """
        if options.max_depth < 1:
            self.logger.error("max_depth must be >= 1")
            return EXIT_INPUT_ERROR

        try:
            reader = PdfReader(self.pdf_path)
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Failed to read input PDF: %s", exc)
            return EXIT_INPUT_ERROR

        outline = reader.outline
        total_pages = len(reader.pages)

        if not outline:
            self.logger.error("No outline found. Cannot split by chapters.")
            return EXIT_NO_SECTIONS

        raw_sections: list[Section] = []
        self._collect_outline_items(reader, outline, 0, raw_sections)
        sections = self._process_sections(raw_sections, options)

        if not sections:
            self.logger.error("No sections found after filtering.")
            return EXIT_NO_SECTIONS

        plans = self._build_plan(sections, total_pages)
        if not plans:
            self.logger.error("No valid section ranges found after filtering.")
            return EXIT_NO_SECTIONS

        if options.dry_run:
            self._print_plan(plans, total_pages)
            return EXIT_OK

        try:
            self._ensure_output_dir()
            self._write_sections(reader, plans)
        except OSError as exc:
            self.logger.error("Failed to write output files: %s", exc)
            return EXIT_OUTPUT_ERROR
        except Exception as exc:  # noqa: BLE001
            self.logger.error("Unexpected error during splitting: %s", exc)
            return EXIT_UNEXPECTED_ERROR

        self.logger.info("Split complete.")
        return EXIT_OK

    def _build_logger(
        self,
        *,
        verbose: bool,
        quiet: bool,
        log_file: str | None,
    ) -> logging.Logger:
        logger = logging.getLogger(f"pdf_splitter.{id(self)}")
        logger.handlers = []
        logger.propagate = False

        level = logging.INFO
        if verbose:
            level = logging.DEBUG
        if quiet:
            level = logging.ERROR

        logger.setLevel(level)
        formatter = logging.Formatter("%(levelname)s: %(message)s")

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            logger.addHandler(file_handler)

        return logger

    def _ensure_output_dir(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.debug("Output directory ready: %s", self.output_dir)

    def _collect_outline_items(
        self,
        reader: PdfReader,
        outline_items: Iterable[Any],
        current_depth: int,
        result: list[Section],
    ) -> None:
        """Recursively collect bookmark items."""
        for item in outline_items:
            if isinstance(item, list):
                self._collect_outline_items(reader, item, current_depth + 1, result)
                continue

            try:
                title = item.title
                page_num = reader.get_destination_page_number(item)
                result.append(Section(title=title, page=page_num, depth=current_depth))
            except Exception as exc:  # noqa: BLE001
                self.logger.debug("Skipping outline item due to error: %s", exc)

    def _process_sections(
        self, raw_sections: list[Section], options: SplitOptions
    ) -> list[Section]:
        """Apply depth, dedupe, regex filtering, and front/back policies."""
        filtered = [s for s in raw_sections if s.depth < options.max_depth]
        filtered.sort(key=lambda section: (section.page, section.depth))

        deduped: list[Section] = []
        last_page = -1
        for section in filtered:
            if section.page == last_page:
                continue
            deduped.append(section)
            last_page = section.page

        regex_filtered = self._apply_regex_filters(deduped, options)
        if not regex_filtered:
            return []

        front_applied = self._apply_matter_policy(
            regex_filtered,
            policy=options.front_matter,
            is_target=lambda title: bool(_FRONT_MATTER_PATTERN.search(title.strip())),
            merged_title="Front Matter",
            from_start=True,
        )
        return self._apply_matter_policy(
            front_applied,
            policy=options.back_matter,
            is_target=lambda title: bool(_BACK_MATTER_PATTERN.search(title.strip())),
            merged_title="Back Matter",
            from_start=False,
        )

    def _apply_regex_filters(
        self,
        sections: list[Section],
        options: SplitOptions,
    ) -> list[Section]:
        flags = re.IGNORECASE if options.ignore_case else 0
        include_pattern = (
            re.compile(options.include_regex, flags) if options.include_regex else None
        )
        exclude_pattern = (
            re.compile(options.exclude_regex, flags) if options.exclude_regex else None
        )

        result: list[Section] = []
        for section in sections:
            title = section.title
            if include_pattern and not include_pattern.search(title):
                continue
            if exclude_pattern and exclude_pattern.search(title):
                continue
            result.append(section)
        return result

    def _apply_matter_policy(
        self,
        sections: list[Section],
        *,
        policy: str,
        is_target: Any,
        merged_title: str,
        from_start: bool,
    ) -> list[Section]:
        if policy == "keep":
            return sections

        if not sections:
            return sections

        if policy == "skip":
            if from_start:
                idx = 0
                while idx < len(sections) and is_target(sections[idx].title):
                    idx += 1
                return sections[idx:]

            idx = len(sections)
            while idx > 0 and is_target(sections[idx - 1].title):
                idx -= 1
            return sections[:idx]

        if policy == "merge":
            if from_start:
                idx = 0
                while idx < len(sections) and is_target(sections[idx].title):
                    idx += 1
                if idx <= 1:
                    return sections
                merged = Section(merged_title, sections[0].page, sections[0].depth)
                return [merged, *sections[idx:]]

            idx = len(sections)
            while idx > 0 and is_target(sections[idx - 1].title):
                idx -= 1
            if idx >= len(sections) - 1:
                return sections
            merged = Section(merged_title, sections[idx].page, sections[idx].depth)
            return [*sections[:idx], merged]

        raise ValueError(f"Unsupported matter policy: {policy}")

    def _build_plan(
        self, sections: list[Section], total_pages: int
    ) -> list[tuple[str, int, int]]:
        plans: list[tuple[str, int, int]] = []

        for idx, section in enumerate(sections):
            start_page = section.page
            end_page = (
                sections[idx + 1].page if idx + 1 < len(sections) else total_pages
            )
            if start_page >= end_page:
                self.logger.debug(
                    "Skipping invalid section range: %s (%s-%s)",
                    section.title,
                    start_page,
                    end_page,
                )
                continue
            plans.append((section.title, start_page, end_page))

        return plans

    def _print_plan(self, plans: list[tuple[str, int, int]], total_pages: int) -> None:
        self.logger.info("Dry run: %d section(s) would be generated.", len(plans))
        self.logger.info("Input page count: %d", total_pages)
        for index, (title, start_page, end_page) in enumerate(plans):
            output_filename = f"{index:02d}_{sanitize_filename(title)}.pdf"
            self.logger.info(
                "[%02d] %s | pages %d-%d | %s",
                index,
                title,
                start_page + 1,
                end_page,
                output_filename,
            )

    def _write_sections(
        self, reader: PdfReader, plans: list[tuple[str, int, int]]
    ) -> None:
        self.logger.info("Found %d sections. Starting split...", len(plans))

        for index, (title, start_page, end_page) in enumerate(plans):
            output_filename = f"{index:02d}_{sanitize_filename(title)}.pdf"
            output_path = os.path.join(self.output_dir, output_filename)
            self._write_single_pdf(reader, start_page, end_page, output_path)
            self.logger.info(
                "Saved: %s (Pages %d-%d)",
                output_filename,
                start_page + 1,
                end_page,
            )

    def _write_single_pdf(
        self,
        reader: PdfReader,
        start_page: int,
        end_page: int,
        output_path: str,
    ) -> None:
        writer = PdfWriter()
        for page_idx in range(start_page, end_page):
            writer.add_page(reader.pages[page_idx])

        with open(output_path, "wb") as f_out:
            writer.write(f_out)
