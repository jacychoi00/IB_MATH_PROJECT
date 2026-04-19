from transformers import pipeline
import fitz
import re

# ============================================================
# 1) 커스텀 카테고리
# ============================================================
CUSTOM_LABELS = [
    "Sequence & Series",
    "Compound Interest & Depreciation",
    "Permutations & Combinations",
    "Binomial Theorem",
    "Proof",
    "Proof – Contradiction (HL)",
    "Mathematical Induction (HL)",
    "Counting Principle (HL)",
    "Complex Numbers – Cartesian Form (HL)",
    "Complex Numbers – Polar Form (HL)",
    "Systems of Linear Equations (HL)",

    "Linear & Quadratic Functions & Graphs",
    "Functions - Composite & Inverse",
    "Reciprocal & Rational Functions",
    "Exponential & Logs",
    "Translations of Graphs",
    "Polynomial Functions (HL)",
    "Other Functions Graph (HL)",

    "Geometry of 3D Shapes",
    "Arc & Area of Sector",
    "Trigonometric Identities",
    "Trigonometric Equations",
    "Trigonometric Functions & Graphs",
    "Inverse & Reciprocal Trigonometric Functions (HL)",
    "Vector Properties (HL)",
    "Vector Equations of Lines (HL)",
    "Vector Equations of Planes (HL)",

    "Statistics",
    "Correlation & Regression",
    "Probability",
    "Venn Diagram",
    "Tree Diagram",
    "Discrete Random Variables",
    "The Binomial Distribution",
    "The Normal Distribution",
    "Continuous Random Variables (HL)",

    "Differentiation Rules",
    "Tangent & Normal Equation",
    "Calculus Curves – Min, Max, Inflexion",
    "Optimization",
    "Integration Rules",
    "Area & Volume of Integration",
    "Kinematics",
    "Basic Limits & Continuity (HL)",
    "Further Differentiation (HL)",
    "Further Integration (HL)",
    "Differential Equations (HL)",
    "Maclaurin Series (HL)",
    "Limits using L'Hopital’s Rule & Maclaurin Series (HL)"
]

# ============================================================
# 2) 모델 캐싱 (전역에서 한 번만 로딩)
# ============================================================

# 빠른 모델 (1차 필터링)
distilbart_classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-1",
    device="cpu"
)

# 정확한 모델 (필요할 때만 실행)
bart_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device="cpu"
)

# ============================================================
# 3) PDF 텍스트 추출 + 정제
# ============================================================
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    doc.close()
    return text

def clean_text(text, max_chars=3000):
    # 1) 공백 정리
    text = " ".join(text.split())

    # 2) 페이지 번호 제거
    text = re.sub(r"Page\s*\d+|\d+\s*/\s*\d+|–\s*\d+\s*–", "", text)

    # 3) Maximum mark: 이전 텍스트 제거 (문제 시작점 찾기)
    mm_index = text.lower().find("maximum mark")
    if mm_index != -1:
        # "Maximum mark:" 포함한 이후 텍스트만 사용
        text = text[mm_index:]

    # 4) 길이 제한
    return text[:max_chars]

# ============================================================
# 4) 두 모델 비교 + 속도 최적화
# ============================================================
def classify_question_from_pdf(pdf_path):
    raw_text = extract_text_from_pdf(pdf_path)
    text = clean_text(raw_text)

    # -----------------------------
    # 1) distilbart (빠른 모델)
    # -----------------------------
    distil_raw = distilbart_classifier(text, CUSTOM_LABELS, multi_label=False)
    distil_label = distil_raw["labels"][0]
    distil_score = float(distil_raw["scores"][0])

    # -----------------------------
    # 2) bart는 distilbart와 다를 때만 실행
    # -----------------------------
    bart_raw = bart_classifier(text, CUSTOM_LABELS, multi_label=False)
    bart_label = bart_raw["labels"][0]
    bart_score = float(bart_raw["scores"][0])

    # -----------------------------
    # 3) 결과 비교
    # -----------------------------
    if bart_label == distil_label:
        final_label = bart_label
    else:
        final_label = f"jacy_check: {bart_label} vs {distil_label}"

    return {
        "final": final_label,
        "bart_label": bart_label,
        "bart_score": bart_score,
        "distil_label": distil_label,
        "distil_score": distil_score
    }
