import os
import sys
import fitz

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project_config import INPUT_DIR, OUTPUT_DIR
from pdf_utils.metadata_parser import parse_pdf_metadata
from pdf_utils.question_splitter import find_question_starts, split_questions
from pdf_utils.image_cropper import crop_and_generate_metadata

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=== IB PDF Processing Pipeline Started ===")

for year_season in os.listdir(INPUT_DIR):
    year_season_path = os.path.join(INPUT_DIR, year_season)
    if not os.path.isdir(year_season_path):
        continue

    YEAR, SEASON = year_season.split()
    YEAR = int(YEAR)

    print(f"\n📁 Processing folder: {year_season}")

    for pdf_file in os.listdir(year_season_path):
        if "markscheme" in pdf_file.lower():
            continue
        if not pdf_file.endswith(".pdf"):
            continue

        pdf_path = os.path.join(year_season_path, pdf_file)

        print(f"  ➤ Opening PDF: {year_season}/{pdf_file}")

        pdf = fitz.open(pdf_path)

        LEVEL, PAPER, TIMEZONE = parse_pdf_metadata(pdf_file)
        out_root = f"{OUTPUT_DIR}/{YEAR}_{SEASON}_{LEVEL}_{PAPER}_{TIMEZONE}"
        os.makedirs(out_root, exist_ok=True)

        print(f"    → Output folder: {out_root}")

        start_pages = find_question_starts(pdf)
        print(f"    → Found {len(start_pages)} questions")

        split_questions(pdf, start_pages, out_root)
        print("    → Split into individual question PDFs")

        crop_and_generate_metadata(start_pages, out_root, YEAR, SEASON, LEVEL, PAPER, TIMEZONE)
        print("    → Cropped images + metadata.json created")

print("\n=== Pipeline Completed Successfully ===")
