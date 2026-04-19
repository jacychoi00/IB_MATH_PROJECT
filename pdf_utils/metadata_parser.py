import re

def parse_pdf_metadata(filename):
    level_match = re.search(r"_(HL|SL)", filename)
    level = level_match.group(1) if level_match else "HL"

    paper_match = re.search(r"paper[_ ]?(\d)", filename, re.IGNORECASE)
    paper = f"P{paper_match.group(1)}" if paper_match else "P1"

    tz_match = re.search(r"(TZ\d)", filename)
    timezone = tz_match.group(1) if tz_match else "TZ0"

    return level, paper, timezone
