# Nested Outline Support Specification

## 1. Background & Problem
Currently, the PDF splitter only processes the **top-level** items of the PDF outline (bookmarks). 
For books structured as **Parts -> Chapters -> Sections** (e.g., *Fundamentals of Software Architecture*), this results in large PDF files containing entire "Parts" instead of individual "Chapters".

**Goal:** Enable the tool to parse nested outlines and split the PDF into more granular units (e.g., Chapters), providing a better reading experience.

## 2. Core Requirements

### 2.1. Recursive Outline Parsing
*   The parser must traverse nested lists in the PDF outline.
*   It should identify specific content sections even if they are deep in the hierarchy.

### 2.2. Splitting Strategy: Hierarchical Flattening
To support books like *Fundamentals of Software Architecture* where chapters are nested at different levels (e.g., Chapter 1 at Depth 0, Chapter 2 at Depth 1), the tool will follow these rules:

1.  **Recursive Discovery**: Traverse all levels of the outline.
2.  **Depth Limit (`--max-depth`)**: Only consider items whose depth is less than or equal to the specified value. 
    *   Example: `--max-depth 1` (default) captures Root and its direct children.
3.  **Same-Page Conflict Resolution**:
    *   If multiple outline items point to the **same page number**, only the **highest-level item** (smallest depth) is kept as a split point.
    *   *Rationale:* If "Chapter 2" and "Section 2.1" both start on Page 44, splitting at both would create a 0-page file for "Chapter 2". Keeping only "Chapter 2" results in a single file containing the whole chapter.
4.  **Sequential Range Calculation**: 
    *   After filtering and sorting items by page number, each section's range is `[current_item.page, next_item.page)`.

### 2.3. CLI Parameters
*   `--max-depth <int>`: (Default: 1) The maximum nesting level to explore.
*   `--min-pages <int>`: (Default: 1) Skip sections that would result in fewer than this many pages (helps ignore empty "Part" covers if desired, though current resolution usually handles this).

## 3. Implementation Plan

### 3.1. Update `src/splitter.py`
*   Replace `_parse_outline` with a recursive collector.
*   Implement `_resolve_conflicts` to handle the "Same-Page" rule.

### 3.2. Duplicate & Overlap Handling
*   **Challenge:** Sometimes a parent item (e.g., "Part 1") points to the same page as its first child (e.g., "Chapter 1").
*   **Solution:**
    *   If `Parent.page == Child.page`, prefer the **Child** (more specific) or keep both?
    *   **Strategy:** If specific CLI flag is set, or by default, if a parent has children and points to the same page as the first child, we might want to skip saving the "Parent" as a separate file, OR save it as a 1-page wrapper. 
    *   **Simplest Approach:** Save everything. If "Part 1" is on page 50 and "Chapter 1" is on page 50, "Part 1" file will be 0 pages (or handled as invalid).
    *   **Refined Rule:** A section is valid if `start_page < end_page`. `end_page` is determined by the `start_page` of the *next* item in the flattened list.

### 3.3. CLI Update
*   Update `src/cli.py` to accept arguments for depth or mode if necessary. For now, we might just make recursive parsing the default behavior if it's robust enough.

## 4. User Experience Example

**Input:**
*   Part I (Page 10)
    *   Chapter 1 (Page 12)
    *   Chapter 2 (Page 30)

**Current Output:**
*   `01_Part I.pdf` (Pages 10-End)

**New Output (Target):**
*   `01_Part I.pdf` (Pages 10-11) -> *Intro to Part I*
*   `02_Chapter 1.pdf` (Pages 12-29)
*   `03_Chapter 2.pdf` (Pages 30-End)
