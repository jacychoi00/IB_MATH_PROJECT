def page_has_continue_bottom(page):
    full_text = page.get_text().replace("\n", " ")
    return "(This question continues on the following page)" in full_text


def page_has_continue_top(page, q_num):
    full_text = page.get_text().replace("\n", " ")
    return f"(Question {q_num} continued)" in full_text
