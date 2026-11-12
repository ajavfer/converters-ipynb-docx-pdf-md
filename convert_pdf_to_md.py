
"""
# convert_pdf_to_md.py

PDF to Markdown Converter.

This script converts a local PDF file into a Markdown (.md) document. 
It utilizes 'pymupdf4llm' if available to preserve structural layout features 
(such as headers, lists, and tables) in Markdown syntax. If 'pymupdf4llm' is not 
installed, the script falls back to raw text extraction using 'pymupdf'.

Features:
    * Supports drag-and-drop terminal paths (automatically strips enclosing quotes).
    * Operates either interactively or via command-line arguments.
    * Automatically saves the output in the same directory as the input PDF.

Usage (Interactive):
    $ python convert_pdf_to_md.py

Usage (Command Line):
    $ python convert_pdf_to_md.py path/to/document.pdf

Dependencies:
    * pymupdf (formerly fitz)
    * pymupdf4llm (optional, recommended for layout-aware Markdown extraction)
"""

from pathlib import Path
import sys
import pymupdf  # Modern import instead of 'import fitz'

# Try to import the specialized Markdown converter
try:
    import pymupdf4llm
except ImportError:
    pymupdf4llm = None


def extract_text_from_pdf(pdf_file: Path) -> str:
    """
    Extracts text content from a PDF file.

    This function attempts to use 'pymupdf4llm' to generate a structured 
    Markdown representation of the document. If 'pymupdf4llm' is not available, 
    it falls back to basic plain-text extraction page by page.

    Args:
        pdf_file (Path): The path to the PDF file to parse.

    Returns:
        str: The extracted Markdown or plain-text string.
    """
    if pymupdf4llm:
        print("-> Usando pymupdf4llm para una conversión estructurada a Markdown...")
        # to_markdown automatically handles headers, lists, and tables
        return pymupdf4llm.to_markdown(str(pdf_file))
    
    # Fallback to plain text extraction if companion library is missing
    print("-> pymupdf4llm no está instalado. Usando extracción de texto plano...")
    with pymupdf.open(pdf_file) as doc:
        pages = []
        for page in doc:
            text = page.get_text("text")
            if text:
                pages.append(text.rstrip())
        return "\n\n".join(pages).strip()


def main():
    """
    Main entry point for the script.

    Retrieves the target PDF path from sys.argv or from interactive prompt input, 
    validates the file path and extension, triggers extraction, and writes the 
    resulting text to a Markdown (.md) file alongside the original document.
    """
    # 1. Get path from command line arguments, or fall back to user input
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("Introduce la ruta del archivo PDF: ").strip()

    if not pdf_path:
        print("No se proporcionó ninguna ruta. Saliendo.")
        sys.exit(1)

    # 2. Clean paths (handles drag-and-drop quotes)
    pdf_path = pdf_path.strip('"').strip("'")
    pdf_file = Path(pdf_path)

    # 3. Validations
    if not pdf_file.exists() or not pdf_file.is_file():
        print(f"Error: Archivo no encontrado en: {pdf_file}")
        sys.exit(1)

    if pdf_file.suffix.lower() != ".pdf":
        print(f"Error: El archivo seleccionado no es un PDF: {pdf_file.name}")
        sys.exit(1)

    md_file = pdf_file.with_suffix(".md")

    # 4. Conversion Process
    print(f"Convirtiendo '{pdf_file.name}' a '{md_file.name}'...")
    try:
        markdown_text = extract_text_from_pdf(pdf_file)
        if not markdown_text:
            print("No se pudo extraer ningún texto del PDF.")
            sys.exit(1)

        md_file.write_text(markdown_text, encoding="utf-8")
        print(f"¡Listo! Archivo guardado con éxito: {md_file}")
        
    except Exception as exc:
        print(f"La conversión falló debido a un error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()