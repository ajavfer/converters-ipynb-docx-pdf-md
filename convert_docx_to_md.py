
"""
# convert_docx_to_md.py

DOCX to Markdown Converter.

This script converts a local DOCX (.docx) file into a Markdown (.md) document.
It uses 'python-docx' to walk the document body in order and preserves
structural elements such as headings, paragraphs, bold/italic text,
lists, and tables in Markdown syntax.

Features:
    * Supports drag-and-drop terminal paths (automatically strips enclosing quotes).
    * Operates either interactively or via command-line arguments.
    * Automatically saves the output in the same directory as the input DOCX.

Usage (Interactive):
    $ python convert_docx_to_md.py

Usage (Command Line):
    $ python convert_docx_to_md.py path/to/document.docx

Dependencies:
    * python-docx
"""

from pathlib import Path
from docx import Document
from docx.document import Document as _Doc
from docx.table import Table
from docx.text.paragraph import Paragraph
import sys


def iter_block_items(parent):
    """
    Iterates over paragraphs and tables in document order.

    Args:
        parent: The document or a table cell containing body elements.

    Yields:
        Paragraph or Table objects in the order they appear in the document.
    """
    from docx.oxml.ns import qn
    if isinstance(parent, _Doc):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element
    for child in parent_elm.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def paragraph_to_markdown(paragraph: Paragraph, list_counters: dict) -> str:
    """
    Converts a single DOCX paragraph to its Markdown representation.

    Handles headings, bulleted/numbered lists, and inline bold/italic
    formatting from the paragraph's runs.

    Args:
        paragraph (Paragraph): The python-docx paragraph to convert.
        list_counters (dict): Mutable counters tracking ordered list numbering.

    Returns:
        str: The Markdown line(s) for this paragraph, or "" if empty.
    """
    style_name = (paragraph.style.name or "").lower() if paragraph.style else ""

    # Inline formatting: bold and italic from runs
    parts = []
    for run in paragraph.runs:
        text = run.text
        if not text:
            continue
        if run.bold:
            text = f"**{text}**"
        if run.italic:
            text = f"*{text}*"
        parts.append(text)
    line = "".join(parts).strip()

    if not line:
        return ""

    # Headings
    if style_name.startswith("heading") or style_name.startswith("título") or style_name.startswith("titulo"):
        try:
            level = int(style_name.split()[-1])
        except (ValueError, IndexError):
            level = 1
        level = max(1, min(6, level))
        return f"{'#' * level} {line}"

    # Lists
    if "list bullet" in style_name:
        list_counters["bullet"] = True
        list_counters["number"] = 0
        return f"- {line}"
    if "list number" in style_name or "list decimal" in style_name:
        list_counters["number"] += 1
        list_counters["bullet"] = False
        return f"{list_counters['number']}. {line}"

    # Any other paragraph ends an active list sequence
    list_counters["number"] = 0
    list_counters["bullet"] = False
    return line


def table_to_markdown(table: Table) -> str:
    """
    Converts a DOCX table to a Markdown table.

    The first row is treated as the header. Cell text is flattened to a
    single line with pipes escaped.

    Args:
        table (Table): The python-docx table to convert.

    Returns:
        str: The Markdown table representation.
    """
    rows = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            cell_text = " ".join(p.text.strip() for p in cell.paragraphs if p.text.strip())
            cells.append(cell_text.replace("|", "\\|").replace("\n", " "))
        rows.append(cells)

    if not rows:
        return ""

    # Normalize column count
    num_cols = max(len(r) for r in rows)
    rows = [r + [""] * (num_cols - len(r)) for r in rows]

    header = rows[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * num_cols) + " |",
    ]
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def convert_docx_to_markdown(docx_file: Path) -> str:
    """
    Converts a DOCX file to a Markdown string.

    Walks the document body in order, converting paragraphs and tables.

    Args:
        docx_file (Path): The path to the DOCX file to parse.

    Returns:
        str: The generated Markdown document.
    """
    doc = Document(docx_file)
    blocks = []
    list_counters = {"number": 0, "bullet": False}

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            md = paragraph_to_markdown(block, list_counters)
            if md:
                blocks.append(md)
        elif isinstance(block, Table):
            list_counters["number"] = 0
            list_counters["bullet"] = False
            md = table_to_markdown(block)
            if md:
                blocks.append(md)

    return "\n\n".join(blocks).strip() + "\n"


def main():
    """
    Main entry point for the script.

    Retrieves the target DOCX path from sys.argv or from interactive prompt input,
    validates the file path and extension, triggers conversion, and writes the
    resulting Markdown to a .md file alongside the original document.
    """
    # 1. Get path from command line arguments, or fall back to user input
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        docx_path = input("Enter the path to the DOCX file: ").strip()

    if not docx_path:
        print("No path provided. Exiting.")
        sys.exit(1)

    # 2. Clean paths (handles drag-and-drop quotes)
    docx_path = docx_path.strip('"').strip("'")
    docx_file = Path(docx_path)

    # 3. Validations
    if not docx_file.exists() or not docx_file.is_file():
        print(f"Error: File not found at: {docx_file}")
        sys.exit(1)

    if docx_file.suffix.lower() != ".docx":
        print(f"Error: The selected file is not a DOCX: {docx_file.name}")
        sys.exit(1)

    md_file = docx_file.with_suffix(".md")

    # 4. Conversion Process
    print(f"Converting '{docx_file.name}' to '{md_file.name}'...")
    try:
        markdown_text = convert_docx_to_markdown(docx_file)
        if not markdown_text.strip():
            print("No content could be extracted from the DOCX.")
            sys.exit(1)

        md_file.write_text(markdown_text, encoding="utf-8")
        print(f"Done! File saved successfully: {md_file}")

    except Exception as exc:
        print(f"Conversion failed due to an error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
