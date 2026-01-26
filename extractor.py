from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pdfplumber


@dataclass
class ExtractedContent:
    text: str
    tables: List[List[List[str]]]


def _page_indices(pages: Optional[List[int]], total_pages: int) -> List[int]:
    if not pages:
        return list(range(total_pages))
    indices = []
    for page in pages:
        if 1 <= page <= total_pages:
            indices.append(page - 1)
    return indices


def _extract_text(pdf: pdfplumber.PDF, page_indices: List[int]) -> str:
    parts = []
    for index in page_indices:
        page_text = pdf.pages[index].extract_text() or ""
        parts.append(page_text)
    return "\n".join(parts).strip()


def _extract_tables(pdf: pdfplumber.PDF, page_indices: List[int]) -> List[List[List[str]]]:
    tables: List[List[List[str]]] = []
    for index in page_indices:
        page_tables = pdf.pages[index].extract_tables()
        for table in page_tables:
            if table:
                tables.append(table)
    return tables


def _ocr_pdf(path: Path, pages: Optional[List[int]]) -> str:
    from pdf2image import convert_from_path
    import pytesseract

    images = convert_from_path(str(path), fmt="png")
    page_indices = _page_indices(pages, len(images))
    texts = []
    for index in page_indices:
        text = pytesseract.image_to_string(images[index])
        texts.append(text)
    return "\n".join(texts).strip()


def extract_text_and_tables(
    path: Path,
    pages: Optional[List[int]] = None,
    enable_ocr: bool = False,
    min_text_chars: int = 30,
) -> ExtractedContent:
    with pdfplumber.open(str(path)) as pdf:
        page_indices = _page_indices(pages, len(pdf.pages))
        text = _extract_text(pdf, page_indices)
        tables = _extract_tables(pdf, page_indices)

    if enable_ocr and len(text) < min_text_chars:
        try:
            ocr_text = _ocr_pdf(path, pages)
        except ImportError as exc:
            raise RuntimeError(
                "OCR 모듈이 설치되지 않았습니다. pdf2image, pytesseract를 설치하세요."
            ) from exc
        if ocr_text:
            text = ocr_text

    return ExtractedContent(text=text, tables=tables)
