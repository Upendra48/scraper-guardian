from pathlib import Path
import hashlib
import json
import shutil


SOURCE = Path(
    "snapshots/coffeyville_kansas/"
    "2026-08-10/20260810_054940"
)

TARGET = Path(
    "snapshots/coffeyville_kansas/"
    "2026-08-10/TEST_BID_LINK_CHANGED"
)


OLD_HREF = "bids.aspx?bidID=287"
NEW_HREF = "/procurement/bid/287"


def sha256(content: str) -> str:
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def main():

    if TARGET.exists():
        shutil.rmtree(TARGET)

    shutil.copytree(SOURCE, TARGET)

    html_file = TARGET / "normalized.html"
    metadata_file = TARGET / "metadata.json"

    html = html_file.read_text(
        encoding="utf-8"
    )

    if OLD_HREF not in html:
        raise RuntimeError(
            f"Could not find href: {OLD_HREF}"
        )

    html = html.replace(
        OLD_HREF,
        NEW_HREF,
        1,
    )

    html_file.write_text(
        html,
        encoding="utf-8",
    )

    metadata = json.loads(
        metadata_file.read_text(
            encoding="utf-8"
        )
    )

    metadata["snapshot_id"] = (
        "TEST_BID_LINK_CHANGED"
    )

    metadata["normalized_html_sha256"] = (
        sha256(html)
    )

    metadata_file.write_text(
        json.dumps(
            metadata,
            indent=4,
        ),
        encoding="utf-8",
    )

    print("=" * 60)
    print("BID LINK CHANGE TEST CREATED")
    print("=" * 60)
    print()
    print("Old:")
    print(f"    {OLD_HREF}")
    print()
    print("New:")
    print(f"    {NEW_HREF}")
    print()
    print(f"Snapshot: {TARGET}")


if __name__ == "__main__":
    main()