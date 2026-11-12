# convert_pdf_to_docx.py

from pathlib import Path
from pdf2docx import Converter


def main():
    pdf_path = input("Enter the path to the PDF file: ").strip()
    if not pdf_path:
        print("No path provided. Exiting.")
        return

    # Remove surrounding quotes if the user pasted a quoted path.
    pdf_path = pdf_path.strip('"').strip("'")

    pdf_file = Path(pdf_path)
    if not pdf_file.exists() or not pdf_file.is_file():
        print(f"File not found: {pdf_file}")
        return

    if pdf_file.suffix.lower() != ".pdf":
        print(f"The selected file is not a PDF: {pdf_file.name}")
        return

    docx_file = pdf_file.with_suffix(".docx")

    print(f"Converting '{pdf_file}' to '{docx_file}'...")
    try:
        cv = Converter(str(pdf_file))
        cv.convert(str(docx_file))
        cv.close()
        print(f"Done! Saved as: {docx_file}")
    except Exception as exc:
        print(f"Conversion failed: {exc}")


if __name__ == "__main__":
    main()
