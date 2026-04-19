import fitz
from .page_filters import is_removable_page
from .continue_detector import page_has_continue_bottom, page_has_continue_top

def find_question_starts(pdf):
    start_pages = []
    q_num = 1

    for page_num, page in enumerate(pdf):
        text = page.get_text()
        if "[Maximum mark:" in text:
            y = page.get_text("blocks")[0][1]
            start_pages.append((q_num, page_num, y))
            q_num += 1

    return start_pages


def split_questions(pdf, start_pages, out_root):
    for i in range(len(start_pages)):
        q_num, start_page, start_y = start_pages[i]

        if i < len(start_pages) - 1:
            next_start_page = start_pages[i + 1][1]
        else:
            next_start_page = pdf.page_count

        new_pdf = fitz.open()
        p = start_page

        while p < next_start_page:
            page = pdf[p]

            if not is_removable_page(page):
                new_pdf.insert_pdf(pdf, from_page=p, to_page=p)

            if page_has_continue_bottom(page):
                p += 1
                continue

            if p + 1 < next_start_page and page_has_continue_top(pdf[p + 1], q_num):
                p += 1
                continue

            p += 1

        if new_pdf.page_count > 0:
            new_pdf.save(f"{out_root}/Q{q_num}.pdf")

        new_pdf.close()
