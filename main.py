import argparse
import logging
from pathlib import Path
from typing import List

from extractor import extract_text_and_tables
from io_utils import ensure_output_dir, save_errors_csv, save_results_csv, save_results_json
from rules import RulesConfig, apply_rules, create_example_rules, load_rules
from text_utils import normalize_text, parse_pages


def gather_pdfs(input_path: Path) -> List[Path]:
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        return [input_path]
    if input_path.is_dir():
        return sorted([p for p in input_path.rglob("*.pdf")])
    return []


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PDF 텍스트 스캔/값 추출기")
    parser.add_argument("--input", required=True, help="PDF 파일 또는 폴더 경로")
    parser.add_argument("--output", required=True, help="결과 저장 폴더")
    parser.add_argument("--rules", required=True, help="추출 규칙 JSON 파일 경로")
    parser.add_argument("--ocr", choices=["on", "off"], default="off", help="OCR 사용 여부")
    parser.add_argument("--pages", help='예: "1-3,5" 형식으로 특정 페이지만 처리')
    parser.add_argument("--verbose", action="store_true", help="상세 로그")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    input_path = Path(args.input)
    output_dir = Path(args.output)
    rules_path = Path(args.rules)
    ensure_output_dir(output_dir)

    if not rules_path.exists():
        logging.info("규칙 파일이 없어서 예시 rules.json을 생성합니다: %s", rules_path)
        create_example_rules(rules_path)

    rules_config: RulesConfig = load_rules(rules_path)
    pages = parse_pages(args.pages) if args.pages else None

    pdf_files = gather_pdfs(input_path)
    if not pdf_files:
        logging.error("입력 경로에 PDF가 없습니다: %s", input_path)
        return

    results = []
    errors = []

    for pdf_path in pdf_files:
        logging.info("처리 중: %s", pdf_path)
        try:
            extracted = extract_text_and_tables(
                pdf_path,
                pages=pages,
                enable_ocr=args.ocr == "on",
            )
            normalized_text = normalize_text(extracted.text)
            record = apply_rules(
                normalized_text,
                extracted.tables,
                rules_config,
                pdf_path.name,
            )
            results.append(record)
        except Exception as exc:
            logging.exception("PDF 처리 실패: %s", pdf_path)
            errors.append({
                "file": str(pdf_path),
                "reason": str(exc),
                "stack": repr(exc),
            })

    save_results_json(output_dir / "results.json", results)
    save_results_csv(output_dir / "results.csv", results)
    save_errors_csv(output_dir / "errors.csv", errors)


if __name__ == "__main__":
    main()
