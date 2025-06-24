import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from PyPDF2 import PdfReader

# Azure configuration
AZURE_ENDPOINT = "https://formrecogocr.cognitiveservices.azure.com/"
AZURE_KEY      = "CaclGvzIwuOdWBnDsm5BSuQmZfNJug3xh1O1BJuul08jb8aYwH6nJQQJ99BFACGhslBXJ3w3AAALACOG6Egv"
PDF_FILE_PATH  = r"D:\bitsg\Finbraine_Intern\Azure AI\PDFs\PRAKASH MAKKAN CHAUDHARI.pdf"

# 1. Count pages and build pages string
def get_pages_string(path):
    reader    = PdfReader(path)
    num_pages = len(reader.pages)
    return reader, f"1-{num_pages}", num_pages

reader, pages_string, num_pages = get_pages_string(PDF_FILE_PATH)
print(f"PDF has {num_pages} pages; requesting pages='{pages_string}'")

# 2. Read PDF as bytes
def read_pdf_bytes(path):
    with open(path, "rb") as file:
        return file.read()

pdf_bytes = read_pdf_bytes(PDF_FILE_PATH)

# 3. Initialize client and submit analysis
client = DocumentAnalysisClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_KEY)
)

poller = client.begin_analyze_document(
    model_id="prebuilt-document",
    document=pdf_bytes,
    pages=pages_string
)
result = poller.result()

# 4. Fallback to per-page if incomplete
if len(result.pages) < num_pages:
    print(f"Warning: got {len(result.pages)} pages back; falling back to per-page requests.")
    all_pages  = []
    all_tables = []
    for p in range(1, num_pages + 1):
        sub_poller = client.begin_analyze_document(
            model_id="prebuilt-document",
            document=pdf_bytes,
            pages=str(p)
        )
        resp = sub_poller.result()
        all_pages.extend(resp.pages)
        all_tables.extend(resp.tables)
    result.pages  = all_pages
    result.tables = all_tables

# 5. Extract lines
all_lines = []
for page in result.pages:
    for idx, line in enumerate(page.lines):
        all_lines.append({
            "page_number":  page.page_number,
            "line_number":  idx + 1,
            "content":      line.content,
            "bounding_box":[[pt.x, pt.y] for pt in getattr(line, "polygon", [])]
        })

# 6. Extract tables
all_tables = []
for ti, table in enumerate(result.tables):
    br       = table.bounding_regions[0] if table.bounding_regions else None
    page_num = br.page_number if br else 1
    cells    = []
    for cell in table.cells:
        cells.append({
            "row_index":    cell.row_index,
            "column_index": cell.column_index,
            "content":      cell.content,
            "is_header":    getattr(cell, "kind", "") == "columnHeader"
        })
    all_tables.append({
        "table_number": ti + 1,
        "page_number":  page_num,
        "row_count":    table.row_count,
        "column_count": table.column_count,
        "cells":        cells
    })

# 7. Build final result
result_dict = {
    "pages": [
        {
            "page_number": page.page_number,
            "angle":       getattr(page, "angle", 0.0),
            "width":       getattr(page, "width", 0.0),
            "height":      getattr(page, "height", 0.0),
            "unit":        getattr(page, "unit", "pixel"),
            "lines":       [
                {"content": l.content,
                 "bounding_box": [[pt.x, pt.y] for pt in getattr(l, "polygon", [])]}
                for l in page.lines
            ]
        }
        for page in result.pages
    ],
    "all_lines":   all_lines,
    "tables":      all_tables,
    "total_pages": len(result.pages),
    "total_lines": len(all_lines),
    "total_tables":len(all_tables)
}

# 8. Save to JSON
output_path = "document_analysis.json"
with open(output_path, "w", encoding="utf-8") as out_file:
    json.dump(result_dict, out_file, ensure_ascii=False, indent=2)
print(f"Analysis results saved to {output_path}")

# Convert tables into model-readable flat format
flat_rows = []
for table in result_dict["tables"]:
    rows = {}
    for cell in table["cells"]:
        rows.setdefault(cell["row_index"], {})[cell["column_index"]] = cell["content"]

    header = rows.get(0, {})
    for r_idx, row_cells in rows.items():
        if r_idx == 0:
            continue  # skip header row
        row_obj = {header.get(ci, f"Column_{ci}"): row_cells.get(ci, "") for ci in row_cells}
        flat_rows.append(row_obj)

# Save it as tables_data.json
with open("tables_document_data.json", "w", encoding="utf-8") as f:
    json.dump(flat_rows, f, ensure_ascii=False, indent=2)

print("Formatted flat table saved as tables_document_data.json")
