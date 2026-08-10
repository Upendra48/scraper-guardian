from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class SnapshotCollector:
    """Collect and store a webpage snapshot."""

    def __init__(
        self,
        output_dir: str | Path = "snapshots",
        timeout: int = 30,
    ):
        self.output_dir = Path(output_dir)
        self.timeout = timeout

    def collect(self, url: str, site_name: str | None = None) -> Path:
        """Fetch a webpage and save its snapshot."""

        response = requests.get(
            url,
            timeout=self.timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                )
            },
        )

        response.raise_for_status()

        html = response.text

        site_name = site_name or self._get_site_name(url)

        timestamp = datetime.now(timezone.utc)
        snapshot_id = timestamp.strftime("%Y%m%d_%H%M%S")

        snapshot_dir = (
            self.output_dir
            / site_name
            / timestamp.strftime("%Y-%m-%d")
            / snapshot_id
        )

        snapshot_dir.mkdir(parents=True, exist_ok=True)

        raw_path = snapshot_dir / "raw.html"
        normalized_path = snapshot_dir / "normalized.html"
        metadata_path = snapshot_dir / "metadata.json"

        raw_path.write_text(html, encoding="utf-8")

        normalized_html = self._normalize_html(html)
        normalized_path.write_text(
            normalized_html,
            encoding="utf-8",
        )

        metadata = {
            "snapshot_id":snapshot_id,
            "site_name": site_name,
            "url": url,
            "timestamp": timestamp.isoformat(),
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "content_length": len(html),
            "raw_html_sha256": self._sha256(html),
            "normalized_html_sha256": self._sha256(normalized_html),
        }

        metadata_path.write_text(
            json.dumps(metadata, indent=4),
            encoding="utf-8",
        )

        return snapshot_dir

    @staticmethod
    def _normalize_html(html: str) -> str:
        """
        Create a normalized HTML representation suitable for structureal comparison.
        
        Dynamic JavaScript, CSS, and non-content elements
        are removed. Whitespace is normalized while keeping
        the HTML readable.
        """

        soup = BeautifulSoup(html, "html.parser")

        # Remove elements that commonly contain dynamic content.
        for comment in soup.find_all(
            string=lambda text: isinstance(text, str)
            and text.strip().startswith("<!--")
        ):
            comment.extract()

        normalized = soup.prettify()

        # Normalize whitespace.
        normalized = re.sub(
            r"[ \t]+",
            " ",
            normalized,
        )
        
        normalized = re.sub(
            r"\n\s*\n+",
            "\n",
            normalized,
        ).strip()

        return normalized

    @staticmethod
    def _sha256(content: str) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _get_site_name(url: str) -> str:
        hostname = urlparse(url).hostname or "unknown-site"

        hostname = hostname.lower()
        hostname = hostname.replace("www.", "")

        return re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            hostname,
        )