# PDF 텍스트 스캔/값 추출기

PDF 파일에서 텍스트를 추출하고, 규칙(JSON)에 따라 값을 구조화하여 CSV/JSON으로 저장하는 CLI 도구입니다.

## 기능
- PDF 텍스트 레이어 추출 (기본)
- 텍스트가 부족한 경우 OCR 폴백 (`--ocr on`)
- 정규식/키워드 기반/테이블 기반 추출
- 결과를 `results.json`, `results.csv`, 실패 로그를 `errors.csv`로 저장

## 설치
```bash
python -m venv .venv
source .venv/bin/activate
pip install pdfplumber pypdf pdf2image pytesseract pytest
```

### OCR 설치 안내
- `pdf2image`는 시스템에 poppler가 필요합니다.
  - macOS: `brew install poppler`
  - Ubuntu: `sudo apt-get install poppler-utils`
- `pytesseract`는 Tesseract 설치가 필요합니다.
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt-get install tesseract-ocr`

## 실행 예시
```bash
python main.py --input ./samples --output ./output --rules ./rules.json --ocr off
python main.py --input ./samples/invoice.pdf --output ./output --rules ./rules.json --ocr on
python main.py --input ./samples --output ./output --rules ./rules.json --pages "1-2,5" --verbose
```

## rules.json 예시
```json
{
  "fields": [
    {
      "name": "invoice_number",
      "type": "regex",
      "pattern": "Invoice\\s*No\\.\\s*([A-Z0-9-]+)",
      "postprocess": ["strip"]
    },
    {
      "name": "total_amount",
      "type": "keyword_window",
      "keywords": ["Total", "합계"],
      "window": 40,
      "pattern": "([0-9,]+\\.?[0-9]{0,2})",
      "postprocess": ["remove_commas", "strip"]
    },
    {
      "name": "issue_date",
      "type": "regex",
      "pattern": "(\\d{4}[.-/]\\d{1,2}[.-/]\\d{1,2})",
      "postprocess": ["date_yyyymmdd"]
    },
    {
      "name": "item_total",
      "type": "table",
      "table": {
        "header_match": "Amount",
        "column_index": 3,
        "row_index": -1
      },
      "postprocess": ["remove_commas", "strip"]
    }
  ]
}
```

## 문제 해결 가이드
- **텍스트 PDF**: 텍스트 레이어가 있는 PDF는 `pdfplumber`가 직접 텍스트를 추출합니다.
- **스캔 PDF**: 텍스트가 거의 없는 PDF는 `--ocr on`을 켜면 OCR로 텍스트를 추출합니다.
- **실패 로그**: 처리 실패 PDF는 `output/errors.csv`에 파일 경로와 사유가 기록됩니다.

