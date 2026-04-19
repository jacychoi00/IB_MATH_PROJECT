import fitz
import os
import json
# no more needed
# from pdf_utils.question_classifier import classify_question_from_pdf

# -----------------------------
# Maximum mark y좌표 찾기
# -----------------------------
def get_maximum_mark_y(page):
    blocks = page.get_text("blocks")
    for b in blocks:
        if "Maximum mark:" in b[4]:
            return b[1]
    return None

# -----------------------------
# continued y좌표 찾기
# -----------------------------
def get_continued_y(page, q_num):
    patterns = [
        f"Question {q_num} (continued)",
        f"Question {q_num} continued",
        f"{q_num} (continued)"
    ]
    blocks = page.get_text("blocks")
    for b in blocks:
        for p in patterns:
            if p in b[4]:
                return b[1]
    return None

# -----------------------------
# 이미지 크롭 + metadata 생성
# -----------------------------
def crop_and_generate_metadata(start_pages, out_root, YEAR, SEASON, LEVEL, PAPER, TIMEZONE):

    for q_num, start_page, _ in start_pages:
        qpdf_path = f"{out_root}/Q{q_num}.pdf"
        if not os.path.exists(qpdf_path):
            continue

        # 🔥 AI 분류 수행
        #ai_result = classify_question_from_pdf(qpdf_path)

        qpdf = fitz.open(qpdf_path)
        folder = f"{out_root}/Q{q_num}"
        os.makedirs(folder, exist_ok=True)

        metadata_list = []

        # 첫 페이지 top_y
        first_page = qpdf[0]
        max_y = get_maximum_mark_y(first_page)
        first_top_y = max(max_y - 10, 0) if max_y else 0

        for i, page in enumerate(qpdf):
            rect = page.rect
            bottom_y = rect.y1 - 70

            if i == 0:
                top_y = first_top_y
            else:
                cont_y = get_continued_y(page, q_num)
                top_y = max(cont_y - 10, 0) if cont_y else 0

            crop_rect = fitz.Rect(rect.x0 + 30, top_y, rect.x1 - 30, bottom_y)
            page.set_cropbox(crop_rect)
            pix = page.get_pixmap(dpi=200)

            img_path = f"{folder}/Q{q_num}_page{i+1}.png"
            pix.save(img_path)

            metadata_list.append({
                "year": YEAR,
                "season": SEASON,
                "level": LEVEL,
                "paper": PAPER,
                "timezone": TIMEZONE,
                "question_no": q_num,
                "page_no": i + 1,
                "image_path": img_path,

                # AI 분류 결과
                #"type": ai_result["final"],
                #"bart_label": ai_result["bart_label"],
                #"bart_score": ai_result["bart_score"],
                #"distil_label": ai_result["distil_label"],
                #"distil_score": ai_result["distil_score"]
                "type": "unclassified",
                "bart_label": None,
                "bart_score": None,
                "distil_label": None,
                "distil_score": None
            })

        with open(f"{folder}/Q{q_num}_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata_list, f, indent=4, ensure_ascii=False)

        qpdf.close()
