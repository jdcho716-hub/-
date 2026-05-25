from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


class KRXHTTPForbiddenError(Exception):
    pass


class KRXClient:
    OTP_URL = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
    DOWNLOAD_URL = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"

    def __init__(self, raw_dir: Path, timeout: int = 30) -> None:
        self.raw_dir = raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout

    def fetch_stock_master_csv_web(self, market: str = "ALL") -> str:
        payload = {
            "locale": "ko_KR",
            "mktId": "ALL" if market == "ALL" else market,
            "share": "1",
            "csvxls_isNo": "false",
            "name": "fileDown",
            "url": "dbms/MDC/STAT/standard/MDCSTAT01901",
        }
        try:
            otp = self._post_text(self.OTP_URL, payload).strip()
            csv_text = self._post_bytes(self.DOWNLOAD_URL, {"code": otp}).decode("euc-kr", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code == 403:
                raise KRXHTTPForbiddenError("KRX web endpoint blocked with HTTP 403") from exc
            raise

        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        raw_file = self.raw_dir / f"krx_stock_master_web_{market}_{ts}.csv"
        raw_file.write_text(csv_text, encoding="utf-8")
        return csv_text

    def fetch_stock_master_csv_openapi(self, api_key: str, market: str = "ALL") -> str:
        """Placeholder interface for KRX Open API key mode.

        TODO:
        - Replace URL/params with official KRX Open API endpoint spec.
        - Attach authorization headers using api_key.
        - Save raw response into logs/raw_api_response/krx/.
        """
        raise NotImplementedError(
            "KRX Open API key mode is scaffolded only in this phase. Use manual CSV import now."
        )

    def _post_text(self, url: str, data: dict[str, Any]) -> str:
        return self._post_bytes(url, data).decode("utf-8", errors="replace")

    def _post_bytes(self, url: str, data: dict[str, Any]) -> bytes:
        body = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url=url, data=body, method="POST")
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read()
