from __future__ import annotations

from pathlib import Path


class SnapshotHistory:
    """Find and manage snapshots for a website."""

    def __init__(
        self,
        snapshots_dir: str | Path = "snapshots",
    ):
        self.snapshots_dir = Path(snapshots_dir)

    def get_site_snapshots(
        self,
        site_name: str,
    ) -> list[Path]:
        """
        Return all snapshots for a site,
        ordered from oldest to newest.
        """

        site_dir = self.snapshots_dir / site_name

        if not site_dir.exists():
            return []

        snapshots = []

        for metadata_path in site_dir.rglob("metadata.json"):
            snapshots.append(metadata_path.parent)

        return sorted(snapshots)

    def get_latest(
        self,
        site_name: str,
    ) -> Path | None:
        """Return the newest snapshot."""

        snapshots = self.get_site_snapshots(site_name)

        if not snapshots:
            return None

        return snapshots[-1]

    def get_previous(
        self,
        site_name: str,
    ) -> Path | None:
        """Return the snapshot immediately before the latest."""

        snapshots = self.get_site_snapshots(site_name)

        if len(snapshots) < 2:
            return None

        return snapshots[-2]