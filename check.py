import fitz  # PyMuPDF

def list_font_sizes(pdf_path):
    doc = fitz.open(pdf_path)
    font_sizes = {}
    # すべてのページを走査
    for page in doc:
        page_dict = page.get_text("dict")
        for block in page_dict["blocks"]:
            if block["type"] != 0:
                continue  # テキストブロック以外はスキップ
            for line in block["lines"]:
                for span in line["spans"]:
                    size = span["size"]
                    font_sizes[size] = font_sizes.get(size, 0) + 1
    return font_sizes

if __name__ == "__main__":
    pdf_path = "mondai_c.pdf"
    font_sizes = list_font_sizes(pdf_path)
    print("PDF内で検出されたフォントサイズと出現回数:")
    for size, count in sorted(font_sizes.items()):
        print(f"フォントサイズ {size}: {count} 回")