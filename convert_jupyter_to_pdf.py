# convert_jupyter_to_pdf.py

import sys
import asyncio
from pathlib import Path

# IMPORTANT FOR WINDOWS:
# The nbconvert command-line interface forces the use of "SelectorEventLoop" on Windows.
# That event loop does not support asynchronous subprocesses, causing Playwright (webpdf) to fail with a NotImplementedError.
# By using the Python API directly, we can force the use of "ProactorEventLoop", which provides full support for asynchronous subprocesses.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

try:
    import nbformat
    from nbconvert import WebPDFExporter, HTMLExporter
    from traitlets.config import Config
except ImportError as err:
    print(f"✗ Error: Missing dependencies in your virtual environment: {err}")
    print("Please ensure they are installed by running:")
    print("  pip install nbconvert nbformat")
    print("  pip install \"nbconvert[webpdf]\"")
    sys.exit(1)


def main():
    notebook_path = input("Enter the path to the Jupyter notebook file (.ipynb): ").strip()
    if not notebook_path:
        print("No path provided. Exiting.")
        return

    # Limpiar comillas del path
    notebook_path = notebook_path.strip('"').strip("'")

    notebook_file = Path(notebook_path)
    if not notebook_file.exists() or not notebook_file.is_file():
        print(f"File not found: {notebook_file}")
        return

    if notebook_file.suffix.lower() != ".ipynb":
        print(f"The selected file is not a Jupyter notebook: {notebook_file.name}")
        return

    pdf_file = notebook_file.with_suffix(".pdf")
    html_file = notebook_file.with_suffix(".html")

    print(f"Converting '{notebook_file}' to PDF...")
    print("This may take a minute on first run...")

    try:
        # Leer el contenido del notebook con nbformat
        with open(notebook_file, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        # 1. Intentar conversión webpdf mediante API interna
        print("\n1. Attempting webpdf conversion (using browser rendering)...")
        
        config = Config()
        config.WebPDFExporter.allow_chromium_download = True
        
        pdf_exporter = WebPDFExporter(config=config)
        
        # Generar el PDF en memoria utilizando el ProactorEventLoop configurado
        pdf_data, _ = pdf_exporter.from_notebook_node(nb)

        # Escribir los bytes del PDF
        with open(pdf_file, "wb") as f:
            f.write(pdf_data)

        print(f"✓ Done! Saved as: {pdf_file}")
        return

    except Exception as exc:
        print("\nℹ Webpdf conversion failed with the following error:")
        print(f"  {exc}")
        
        # 2. Si falla webpdf, intentar la conversión a HTML como alternativa
        print("\n2. Attempting HTML conversion as a fallback...")
        try:
            html_exporter = HTMLExporter()
            html_data, _ = html_exporter.from_notebook_node(nb)
            
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_data)

            print(f"✓ Converted to HTML: {html_file}")
            print(f"\nTo convert HTML to PDF, you can:")
            print(f"  - Open '{html_file}' in your browser and use Print -> Save as PDF")
            print(f"  - Or install wkhtmltopdf: https://wkhtmltopdf.org/")

        except Exception as html_exc:
            print(f"\n✗ HTML fallback conversion also failed: {html_exc}")
            print("\nTo fix this, make sure 'nbformat' and 'nbconvert' are correctly installed.")


if __name__ == "__main__":
    main()