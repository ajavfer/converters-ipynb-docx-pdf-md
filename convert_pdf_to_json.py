"""
PDF to JSON Converter.

This script converts a local PDF file into a structured JSON file. 
It utilizes 'pymupdf4llm' to extract high-level layout elements, metadata, 
text spans, and bounding boxes in a structured format. If 'pymupdf4llm' 
is not installed, it falls back to extracting raw character block structures 
using standard 'pymupdf'.

Features:
    * Supports drag-and-drop terminal paths (automatically strips enclosing quotes).
    * Operates either interactively or via command-line arguments.
    * Outputs formatted, pretty-printed JSON with UTF-8 encoding.

Usage (Interactive):
    $ python convert_pdf_to_json.py

Usage (Command Line):
    $ python convert_pdf_to_json.py path/to/document.pdf

Dependencies:
    * pymupdf (formerly fitz)
    * pymupdf4llm (optional, recommended for layout-aware semantic structures)
"""

from pathlib import Path
import json
import sys
import pymupdf

try:
    import pymupdf4llm
except ImportError:
    pymupdf4llm = None


def extract_json_from_pdf(pdf_file: Path) -> str:
    """
    Extracts structural layout information from a PDF file.

    This function attempts to use 'pymupdf4llm' to generate a structured 
    JSON representation of the document. If 'pymupdf4llm' is not available, 
    it falls back to basic coordinate block JSON extraction page by page.

    Args:
        pdf_file (Path): The path to the PDF file to parse.

    Returns:
        str: A pretty-printed JSON string containing the extracted information.
    """
    if pymupdf4llm:
        print("-> Usando pymupdf4llm para una extracción JSON estructurada...")
        # pymupdf4llm.to_json returns a raw JSON string
        raw_json_str = pymupdf4llm.to_json(str(pdf_file))
        
        # Parse and re-dump to ensure clean formatting and pretty indentation
        parsed_data = json.loads(raw_json_str)
        return json.dumps(parsed_data, indent=2, ensure_ascii=False)
    
    print("-> pymupdf4llm no está instalado. Usando extracción de coordenadas base...")
    with pymupdf.open(pdf_file) as doc:
        pages_data = []
        for index, page in enumerate(doc):
            page_json = page.get_text("json")
            if page_json:
                # Store pages individually in a structured dictionary list
                pages_data.append({
                    "page_number": index + 1,
                    "layout": json.loads(page_json)
                })
        
        return json.dumps({"document": pdf_file.name, "pages": pages_data}, indent=2, ensure_ascii=False)


def main():
    """
    Main entry point for the script.

    Retrieves the target PDF path from sys.argv or from interactive prompt input, 
    validates the file path and extension, triggers extraction, and writes the 
    resulting text to a structured JSON (.json) file.
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

    json_file = pdf_file.with_suffix(".json")

    # 4. Conversion Process
    print(f"Convirtiendo '{pdf_file.name}' a '{json_file.name}'...")
    try:
        json_text = extract_json_from_pdf(pdf_file)
        if not json_text:
            print("No se pudo extraer ningún dato del PDF.")
            sys.exit(1)

        json_file.write_text(json_text, encoding="utf-8")
        print(f"¡Listo! Archivo guardado con éxito: {json_file}")
        
    except Exception as exc:
        print(f"La conversión falló debido a un error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()