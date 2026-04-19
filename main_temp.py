import os
import requests
import json

CLASSIFIER_URL = "http://localhost:5173/api/classify"
INPUT_DIR = "input"

def get_pdf_files(input_dir):
    """input 폴더에서 PDF 파일 목록 가져오기"""
    return [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".pdf")
    ]

def send_to_classifier(pdf_path):
    """classifier 서버로 PDF 절대경로 전송"""
    abs_path = os.path.abspath(pdf_path)

    payload = {
        "filename": abs_path
    }

    print(f"[splitter] POST {CLASSIFIER_URL} ({abs_path})")

    response = requests.post(CLASSIFIER_URL, json=payload)
    return response.json()

def main():
    print("=== Splitter → Classifier 테스트 시작 ===\n")

    pdf_files = get_pdf_files(INPUT_DIR)

    if not pdf_files:
        print("[splitter] input 폴더에 PDF 파일이 없습니다.")
        return

    for pdf_path in pdf_files:
        print(f"[splitter] Sending {pdf_path} to classifier...")

        result = send_to_classifier(pdf_path)

        print(f"[splitter] classifier response for {pdf_path}: {result}")
        print(f"[classifier response] {result}\n")

    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    main()
