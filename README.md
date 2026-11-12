# PDF to DOCX Converter

A simple Python script to convert a PDF file into a DOCX document using `pdf2docx`.

## Files

- `convert_pdf_to_docx.py` - Converts PDF files to DOCX format
- `convert_pdf_to_md.py` - Converts PDF files to Markdown format
- `convert_pdf_to_json.py` - Converts PDF files to JSON format
- `convert_docx_to_md.py` - Converts DOCX files to Markdown format
- `convert_jupyter_to_pdf.py` - Converts Jupyter notebooks to PDF format
- `requirements.txt` - Python package dependencies

## Requirements

- Python 3.8 or newer
- `pdf2docx`
- `PyMuPDF`
- `nbconvert`
- `jupyter`
- `pyppeteer` - for Jupyter to PDF conversion (downloads Chromium on first run)

## Installation

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Convert PDF to DOCX

Run the DOCX conversion script and provide the path to the PDF file when prompted:

```bash
python convert_pdf_to_docx.py
```

### Convert PDF to Markdown

Run the Markdown conversion script and provide the path to the PDF file when prompted:

```bash
python convert_pdf_to_md.py
```

### Convert DOCX to Markdown

Run the DOCX to Markdown conversion script and provide the path to the DOCX file when prompted:

```bash
python convert_docx_to_md.py
```

### Convert Jupyter Notebook to PDF

Run the Jupyter to PDF conversion script and provide the path to the notebook file when prompted:

```bash
python convert_jupyter_to_pdf.py
```

The script will attempt conversion using the best available method:
- **webpdf** - Renders with browser engine (better quality, downloads Chromium on first run)
- **HTML fallback** - Converts to HTML if PDF conversion fails (can be opened in browser)
- If both fail, the script provides instructions for installing additional tools

## Notes

- All scripts check whether the file exists and have the correct file extension
- The Jupyter to PDF converter uses `nbconvert` with the `webpdf` exporter (requires Chromium/browser engine)
- If webpdf fails, the script will convert to HTML as an alternative
