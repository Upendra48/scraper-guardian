from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ChangeResult:
    changed: bool
    previous_hash: str | None
    current_hash: str
    reason: str


class HashChangeDetector:
    """Detect changes between two webpage snapshots."""

    def compare(
        self,
        previous_snapshot: str | Path,
        current_snapshot: str | Path,
    ) -> ChangeResult:

        previous_snapshot = Path(previous_snapshot)
        current_snapshot = Path(current_snapshot)

        previous_metadata = self._load_metadata(
            previous_snapshot
        )

        current_metadata = self._load_metadata(
            current_snapshot
        )

        previous_hash = previous_metadata.get(
            "normalized_html_sha256"
        )

        current_hash = current_metadata[
            "normalized_html_sha256"
        ]

        if previous_hash == current_hash:
            return ChangeResult(
                changed=False,
                previous_hash=previous_hash,
                current_hash=current_hash,
                reason="Normalized HTML is unchanged.",
            )

        return ChangeResult(
            changed=True,
            previous_hash=previous_hash,
            current_hash=current_hash,
            reason="Normalized HTML hash changed.",
        )

    @staticmethod
    def _load_metadata(
        snapshot_dir: Path,
    ) -> dict:

        metadata_path = snapshot_dir / "metadata.json"

        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata not found: {metadata_path}"
            )

        return json.loads(
            metadata_path.read_text(
                encoding="utf-8"
            )
        )