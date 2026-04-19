def is_removable_page(page):
    text = page.get_text()
    page_height = page.rect.height

    if "Please do not write on this page" in text:
        return True

    if "Do not write solutions on this page" in text:
        return False

    return False
