import fitz  # PyMuPDF
import json

def is_white(color_int):
    """
    spanのcolor（整数値）を16進数文字列に変換し、
    白（ffffff）ならTrueを返す
    """
    if color_int is None:
        return False
    hex_color = format(color_int, '06x')
    return hex_color.lower() == "ffffff"

def finalize_paragraph(segments):
    """
    segments: [(テキスト, is_white), ...]
    → question: 各白色部分は "()" に置換し、非白色部分はそのまま連結
       answer: 白色テキストをリスト化
    """
    if not segments:
        return None
    question = ""
    answer = []
    for text, white in segments:
        if white:
            question += "()"
            answer.append(text)
        else:
            question += text
    return {"question": question.strip(), "answer": answer}

def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    dataset = []  # セクション毎のリスト（最終的に出力するデータセット）
    
    # セクションがまだなければ default を用意（最初の9ptテキストが前にある場合用）
    default_section = {"section": "default", "paragraphs": []}
    current_section = default_section

    # ページ番号はユーザー指定が「3～48ページ」
    # PyMuPDFではページ番号は0始まりなので、ここでは index 2～47 とする
    current_paragraph_segments = []  # 現在のパラグラフの(テキスト, is_white)リスト

    for page_num in range(2, 48):
        page = doc.load_page(page_num)
        page_dict = page.get_text("dict")
        # 各テキストブロック、行、spanを順次処理
        for block in page_dict["blocks"]:
            if block["type"] != 0:
                continue  # テキストブロック以外はスキップ
            for line in block["lines"]:
                for span in line["spans"]:
                    font_size = span["size"]
                    # 9.0ptと11.0pt以外は無視する
                    if font_size not in [9.0, 11.039999961853027]:
                        continue
                    text = span["text"]
                    # 指定文字列 "Q-Assist © MEDIC MEDIA" は削除
                    text = text.replace("Q-Assist © MEDIC MEDIA", "")
                    # 余分な空白を取り除く
                    text = text.strip()
                    if not text:
                        continue
                    
                    if 10.9 <= font_size <= 11.1:
    # もし現在のパラグラフに内容があれば、確定して現在のセクションに追加
                        if current_paragraph_segments:
                            paragraph_obj = finalize_paragraph(current_paragraph_segments)
                            if paragraph_obj:
                                current_section["paragraphs"].append(paragraph_obj)
                            current_paragraph_segments = []
    # 新規セクションを作成（このspanのテキストをセクションタイトルとする）
                        new_section = {"section": text, "paragraphs": []}
                        dataset.append(new_section)
                        current_section = new_section
                    # 9ptの文字はパラグラフの内容として扱う
                    elif abs(font_size - 9.0) < 0.001:
                        # もしパラグラフ内に「□」が含まれていれば、分割して新たなパラグラフ開始
                        parts = text.split("□")
                        for i, part in enumerate(parts):
                            # 「□」で分割された場合、最初の部分は現在のパラグラフに追加、
                            # それ以降は現在のパラグラフを確定してから新規パラグラフにする
                            if i > 0:
                                paragraph_obj = finalize_paragraph(current_paragraph_segments)
                                if paragraph_obj:
                                    current_section["paragraphs"].append(paragraph_obj)
                                current_paragraph_segments = []
                            if part:
                                # span全体の色は一律なので、ここでis_whiteを判定
                                white_flag = is_white(span.get("color", 0))
                                current_paragraph_segments.append((part, white_flag))
    # すべてのページ処理後、未確定のパラグラフがあれば追加
    if current_paragraph_segments:
        paragraph_obj = finalize_paragraph(current_paragraph_segments)
        if paragraph_obj:
            current_section["paragraphs"].append(paragraph_obj)
        current_paragraph_segments = []
    # datasetが空の場合は default セクションを利用
    if not dataset:
        dataset.append(default_section)
    # 各パラグラフに一意のidを付与（idは "c" + 順番）
    counter = 1
    for section in dataset:
        for paragraph in section["paragraphs"]:
            paragraph["id"] = "c" + str(counter)
            counter += 1
    return dataset

if __name__ == "__main__":
    pdf_path = "mondai_c.pdf"
    dataset = process_pdf(pdf_path)
    # JSONファイルとして保存（Webアプリ等への組み込みが容易な形式）
    with open("output_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print("Dataset saved to output_dataset.json")